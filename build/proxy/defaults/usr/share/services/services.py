#!/usr/bin/python3

import os
import json
import socket
import subprocess
import fcntl
import select
import asyncio
import re
from datetime import datetime
from collections import deque
from typing import List, Dict, Any
from contextlib import asynccontextmanager

import httpx
import dns.resolver
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Template
from sse_starlette.sse import EventSourceResponse

import logging
from logging.handlers import RotatingFileHandler

# Logging configuration
logger = logging.getLogger('services')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/var/log/services.log', maxBytes=1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Configuration
FILECONFIG = '/etc/haproxy/haproxy.cfg'
FILECONFIG_TEMPLATE = '/etc/haproxy/haproxy.template'
with open(FILECONFIG_TEMPLATE, encoding='utf-8') as f:
    HAPROXY_TEMPLATE = f.read()

FQDN = os.environ['FQDN']
STACK = os.environ['STACK']
PORT_HTTPS = os.environ['PORT_HTTPS']
HTTPSMODE = os.environ['HTTPSMODE']
MTLS = os.environ['MTLS']
TAG = os.environ['TAG']
NETWORK_MNG = os.environ['NETWORK_MNG']

MESSAGES_LOG = deque(maxlen=500)

PATH_MTLS = '/mnt/cluster/certificates/mtls'
PATH_MTLS_CERTS = f'{PATH_MTLS}/certs'
PATH_MTLS_TOKEN = f'{PATH_MTLS}/token'
PATH_CONF = f'/mnt/cluster/datashares/{STACK}/conf'

# Global data
global_data = {'services': {}, 'message': '', 'need_reload': True, 'extensions': [], 'ok': False, 'now': datetime.now()}

USERLIST_CLUSTER = ''
USERLIST_STACK = ''


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info('Starting application...')
    render_error_pages()
    USERLIST_CLUSTER = userlist_cluster()
    USERLIST_STACK = userlist_stack()
    config_haproxy()
    logger.info('Application started successfully')

    yield

    # Shutdown
    logger.info('Shutting down application...')
    # Cleanup code here if needed


# FastAPI app
app = FastAPI(title='Services API', lifespan=lifespan)

# Static files and templates
app.mount('/services-static', StaticFiles(directory='services-static'), name='static')
templates = Jinja2Templates(directory='services-static/templates')


def get_organization() -> str:
    """Extract organization from settings file"""
    try:
        with open(f'{PATH_CONF}/settings.py', 'r') as file:
            content = file.read()

        variable_name = 'MIGASFREE_ORGANIZATION'
        pattern = rf'{variable_name}\s*=\s*(.+)'
        result = re.search(pattern, content)
        if result:
            return result.group(1)[1:-1]
    except Exception as e:
        logger.error(f'Error reading organization: {e}')

    return ''


def execute(cmd: str, verbose: bool = False, interactive: bool = True):
    """Execute shell command"""
    _output_buffer = ''
    if verbose:
        print(cmd)

    if interactive:
        _process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
    else:
        _process = subprocess.Popen(
            cmd, shell=True, executable='/bin/bash', stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        if verbose:
            fcntl.fcntl(
                _process.stdout.fileno(),
                fcntl.F_SETFL,
                fcntl.fcntl(_process.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
            )
            while _process.poll() is None:
                readx = select.select([_process.stdout.fileno()], [], [])[0]
                if readx:
                    chunk = _process.stdout.read()
                    if chunk and chunk != '\n':
                        print(chunk)
                    _output_buffer = f'{_output_buffer}{chunk}'

    _output, _error = _process.communicate()
    if not interactive and _output_buffer:
        _output = _output_buffer

    return _process.returncode, _output, _error


def get_extensions() -> List[str]:
    """Get PMS extensions"""
    pms_enabled = os.environ['PMS_ENABLED']
    extensions = []
    _code, _out, _err = execute('curl -X GET core:8080/api/v1/public/pms/', interactive=False)
    if _code == 0:
        try:
            all_pms = json.loads(_out.decode('utf-8'))
        except Exception:
            return list(set(extensions))
        for pms in all_pms:
            if f'pms-{pms}' in pms_enabled:
                for extension in all_pms[pms]['extensions']:
                    extensions.append(extension)

    return list(set(extensions))


def get_nodes(service: str) -> List[str]:
    """Get service nodes"""
    nodes = []
    _code, _out, _err = execute(f"dig tasks.{service} | grep ^tasks.{service} | awk '{{print $5}}'", interactive=False)
    if _code == 0:
        for node in _out.decode('utf-8').replace('\n', ' ').split(' '):
            if node:
                nodes.append(node)

    return nodes


def check_server(host: str, port: int) -> bool:
    """Check if server is reachable"""
    try:
        args = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    except Exception:
        return False

    for family, socktype, proto, _, sockaddr in args:
        s = socket.socket(family, socktype, proto)
        try:
            s.connect(sockaddr)
        except socket.error:
            return False
        else:
            s.close()
            return True


def make_global_data(data: Dict[str, Any]):
    """Update global data with service information"""
    global_data['ok'] = False

    if 'service' in data:
        if data['service'] not in global_data['services']:
            global_data['services'][data['service']] = {'message': '', 'node': '', 'container': '', 'missing': True}

        if 'text' in data:
            global_data['services'][data['service']]['message'] = data['text']
            global_data['last_message'] = data['service']
        if 'node' in data:
            global_data['services'][data['service']]['node'] = data['node']
        if 'container' in data:
            global_data['services'][data['service']]['container'] = data['container']


def config_haproxy():
    """Configure HAProxy"""
    context = {
        'FQDN': FQDN,
        'STACK': STACK,
        'certbot': HTTPSMODE == 'auto',
        'PORT_HTTPS': PORT_HTTPS,
        'USERLIST_STACK': USERLIST_STACK,
        'USERLIST_CLUSTER': USERLIST_CLUSTER,
        'NETWORK_MNG': NETWORK_MNG,
        'MTLS': MTLS == 'True',
    }

    global_data['extensions'] = get_extensions()

    if len(global_data['extensions']) == 0:
        context['extensions'] = '.deb .rpm'
    else:
        context['extensions'] = '.' + ' .'.join(global_data['extensions'])

    logger.info(context['extensions'])

    payload = {'haproxy.cfg': Template(HAPROXY_TEMPLATE).render(context)}
    if not os.path.exists(FILECONFIG):
        with open(FILECONFIG, 'w') as f:
            f.write(payload['haproxy.cfg'])
            f.write('\n')
    else:
        try:
            ips = dns.resolver.resolve('tasks.proxy', 'A')
            for ip in ips:
                httpx.post(f'http://{str(ip)}:8001/services/update_haproxy', json=payload)
        except Exception as e:
            logger.error(f'Error updating haproxy: {e}')


def reload_haproxy():
    """Reload HAProxy"""
    _code, _out, _err = execute('/usr/bin/reload', interactive=False)


def render_error_pages():
    """Render custom error pages"""
    context = {'FQDN': os.environ['FQDN']}
    _path = '/etc/haproxy/errors-custom'
    _path_template = '/etc/haproxy/errors-custom/templates'
    for f_template in os.listdir(_path_template):
        _file = os.path.join(_path, os.path.basename(f_template))
        if _file.endswith('.http'):
            with open(os.path.join(_path_template, f_template), 'r', encoding='utf-8') as f:
                content = f.read()
            with open(_file, 'w', encoding='utf-8') as f:
                f.write(Template(content).render(context))
                f.write('\n')


def userlist_stack() -> str:
    """Generate userlist for stack"""
    with open(f'/run/secrets/{STACK}_superadmin_name', 'r', encoding='utf-8') as f:
        username = f.read()
    with open(f'/run/secrets/{STACK}_superadmin_pass', 'r', encoding='utf-8') as f:
        password = f.read()

    _code, _out, _err = execute(f'mkpasswd -m sha-512 {password}', interactive=False)

    return f'    user {username} password {_out.decode("utf-8")}'


def userlist_cluster() -> str:
    """Generate userlist for cluster"""
    with open('/run/secrets/swarm-credential', 'r', encoding='utf-8') as f:
        username, password = f.read().split(':')

    _code, _out, _err = execute(f'mkpasswd -m sha-512 {password}', interactive=False)

    return f'    user {username} password {_out.decode("utf-8")}'


# Routes
@app.get('/favicon.ico')
async def favicon():
    """Redirect to logo"""
    return RedirectResponse(url=f'https://{FQDN}/services-static/img/logo.svg')


@app.get('/services/status/', response_class=HTMLResponse)
async def status_page(request: Request):
    """Status page"""
    return templates.TemplateResponse('status.html', {'request': request, **global_data})


@app.get('/services/manifest', response_class=PlainTextResponse)
async def manifest():
    """Cache manifest"""
    template = """CACHE MANIFEST
/services/status
/services-static/*
/services/logs
    """
    return Template(template).render({})


@app.get('/services/logs', response_class=HTMLResponse)
async def logs(request: Request):
    """Logs page"""
    columns = ['time', 'text', 'service', 'node', 'container']
    return templates.TemplateResponse('logs.html', {'request': request, 'columns': columns})


@app.get('/services/logs/json')
async def logs_json():
    """Get logs as JSON"""
    return JSONResponse(content=list(MESSAGES_LOG))


@app.get('/services/message')
async def get_message():
    """Get current message status"""
    if int((datetime.now() - global_data['now']).total_seconds()) >= 1:
        global_data['now'] = datetime.now()

        pms = os.environ['PMS_ENABLED'].split(',')
        services = [
            'console',
            'core',
            'beat',
            'worker',
            'public',
            *pms,
            'database',
            'datastore',
            'database_console',
            'datastore_console',
            'datashare_console',
            'worker_console',
            'assistant',
            'proxy',
            'portainer',
            'certbot',
            'ca',
            'mcp-server',
        ]

        if 'services' not in global_data:
            global_data['services'] = {}

        if 'last_message' not in global_data:
            global_data['last_message'] = ''

        missing = False
        message = False

        for _service in services:
            if f'{STACK}_{_service}' not in global_data['services']:
                global_data['services'][f'{STACK}_{_service}'] = {
                    'message': '',
                    'node': '',
                    'container': '',
                    'missing': True,
                }

            nodes = len(get_nodes(_service))
            global_data['services'][f'{STACK}_{_service}']['missing'] = nodes < 1
            global_data['services'][f'{STACK}_{_service}']['nodes'] = nodes

            if global_data['services'][f'{STACK}_{_service}']['missing']:
                global_data['need_reload'] = True
                missing = True

            if global_data['services'][f'{STACK}_{_service}']['message']:
                message = True

            global_data['ok'] = False
            if not message:
                if missing:
                    global_data['need_reload'] = True
                else:
                    if global_data['need_reload']:
                        global_data['need_reload'] = False
                    global_data['ok'] = True

    disables = []
    if os.environ['HTTPSMODE'] == 'manual':
        disables.append('certbot')
    if os.environ['GOOGLE_API_KEY'] == '':
        disables.append('assistant')
        disables.append('mcp-server')

    return JSONResponse(
        content={
            'last_message': global_data.get('last_message', ''),
            'services': global_data['services'],
            'ok': global_data['ok'],
            'organization': get_organization(),
            'stack': STACK,
            'tag': TAG,
            'disables': disables,
        }
    )


@app.post('/services/message')
async def post_message(request: Request):
    """Post a new message"""
    try:
        data = await request.json()
    except Exception:
        data = {}

    data['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    MESSAGES_LOG.append(data)

    try:
        ips = dns.resolver.resolve('tasks.proxy', 'A')
        async with httpx.AsyncClient() as client:
            for ip in ips:
                await client.post(f'http://{str(ip)}:8001/services/update_message', json=data)
    except Exception as e:
        logger.error('Error posting message: %s', str(e))

    return JSONResponse(content={'status': 'ok'})


@app.post('/services/update_message')
async def update_message(request: Request):
    """Update message from other proxy"""
    data = await request.json()
    make_global_data(data)

    return JSONResponse(content={'status': 'ok'})


@app.post('/services/reconfigure')
async def reconfigure():
    """Reconfigure services"""
    data = {
        'text': 'reconfigure',
        'service': os.environ['SERVICE'],
        'node': os.environ['NODE'],
        'container': os.environ['HOSTNAME'],
    }

    make_global_data(data)
    config_haproxy()

    return JSONResponse(content={'status': 'ok'})


@app.get('/services/nginx_extensions', response_class=PlainTextResponse)
async def nginx_extensions():
    """Get nginx extensions configuration"""
    template = """
        # External Deployments. Auto-generated from proxy (in services.py -> config_nginx)
        # ========================================================================
    {% for extension in extensions %}
        location ~* /src/?(.*){{extension}}$ {
            alias /var/migasfree/public/$1{{extension}};
            error_page 404 = @backend;
        }
    {% endfor %}
        # ========================================================================
    """

    if len(global_data['extensions']) > 0:
        return Template(template).render({'extensions': global_data['extensions']})

    return ''


@app.post('/services/update_haproxy')
async def update_haproxy(request: Request):
    """Update HAProxy configuration"""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={'status': 'error', 'message': 'Invalid JSON'})

    if 'haproxy.cfg' in data:
        with open(FILECONFIG, 'w', encoding='utf-8') as f:
            f.write(data['haproxy.cfg'])
            f.write('\n')
        reload_haproxy()

    await asyncio.sleep(1)
    _data = {
        'text': '',
        'service': os.environ['SERVICE'],
        'node': os.environ['NODE'],
        'container': os.environ['HOSTNAME'],
    }
    make_global_data(_data)

    return JSONResponse(content={'status': 'ok'})


# SSE endpoint for real-time updates
@app.get('/services/stream')
async def message_stream(request: Request):
    """Server-Sent Events endpoint for real-time updates"""

    async def event_generator():
        last_state_hash = None
        while True:
            if await request.is_disconnected():
                break

            # Get current state (without timestamp for comparison)
            current_state = {
                'last_message': global_data.get('last_message', ''),
                'services': global_data['services'].copy(),
                'ok': global_data['ok'],
                'organization': get_organization(),
                'stack': STACK,
                'tag': TAG,
                'disables': [],
            }

            # Add disables
            if HTTPSMODE == 'manual':
                current_state['disables'].append('certbot')
            if os.environ.get('GOOGLE_API_KEY', '') == '':
                current_state['disables'].extend(['assistant', 'mcp-server'])

            # Create hash of state for comparison (excluding timestamp)
            state_hash = json.dumps(current_state, sort_keys=True)

            # Only send if state changed
            if state_hash != last_state_hash:
                # Add timestamp only when sending
                current_state['timestamp'] = datetime.now().isoformat()

                yield {'event': 'message', 'data': json.dumps(current_state)}
                last_state_hash = state_hash

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return templates.TemplateResponse('status.html', {'request': request, **global_data}, status_code=404)


@app.exception_handler(503)
async def service_unavailable_handler(request: Request, exc: HTTPException):
    """Custom 503 handler"""
    return templates.TemplateResponse('status.html', {'request': request, **global_data}, status_code=503)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8001, log_level='debug')
