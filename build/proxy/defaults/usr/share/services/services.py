#!/usr/bin/python3

import os
import json
import socket
import subprocess
import fcntl
import select
import asyncio
import re
import threading
from datetime import datetime
from collections import deque
from typing import List, Dict, Any
from contextlib import asynccontextmanager

import httpx
import dns.resolver
import docker
from fastapi import FastAPI, Request, Response, HTTPException
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
global_data = {
    'services': {},
    'message': '',
    'need_reload': True,
    'extensions': [],
    'ok': False,
    'now': datetime.now()
}

# Docker monitor
docker_monitor = None
monitor_lock = threading.Lock()


class DockerSwarmMonitor:
    def __init__(self):
        self.client = docker.from_env()
        self.running = False
        self.service_states = {}
        self.lock = threading.Lock()
        self.monitor_thread = None
        self.checker_thread = None

        # Check that we are in a manager
        try:
            info = self.client.info()
            swarm = info.get('Swarm', {})

            if not swarm.get('ControlAvailable', False):
                logger.warning("Not running on a Swarm manager node - Docker monitoring disabled")
                self.client = None
                return

            logger.info(f"Connected to Swarm cluster ID: {swarm.get('Cluster', {}).get('ID', 'unknown')[:12]}")
            logger.info(f"Nodes: {swarm.get('Nodes', 0)} | Managers: {swarm.get('Managers', 0)}")
        except Exception as e:
            logger.error(f"Error connecting to Docker: {e}")
            self.client = None

    def get_active_nodes_count(self):
        if not self.client:
            return 0
        try:
            nodes = self.client.nodes.list()
            active = len([n for n in nodes
                         if n.attrs['Status']['State'] == 'ready'
                         and n.attrs['Spec']['Availability'] == 'active'])
            return active
        except Exception as e:
            logger.warning(f"Error counting nodes: {e}")
            return 0

    def get_service_status(self, service_name):
        if not self.client:
            return None

        try:
            service = self.client.services.get(service_name)
            tasks = service.tasks()

            running_tasks = [t for t in tasks if t['Status']['State'] == 'running']
            running = len(running_tasks)
            preparing = len([t for t in tasks if t['Status']['State'] in ['preparing', 'starting', 'assigned', 'accepted', 'ready']])
            failed = len([t for t in tasks if t['Status']['State'] in ['failed', 'rejected', 'shutdown', 'orphaned']])

            nodes_info = []
            containers_info = []

            for task in running_tasks:
                node_id = task.get('NodeID', '')
                if node_id:
                    try:
                        node = self.client.nodes.get(node_id)
                        node_name = node.attrs['Description']['Hostname']
                        nodes_info.append(node_name)
                    except Exception:
                        nodes_info.append(node_id[:12])

                container_id = task['Status'].get('ContainerStatus', {}).get('ContainerID', '')
                if container_id:
                    containers_info.append(container_id[:12])

            mode = service.attrs['Spec'].get('Mode', {})

            if 'Replicated' in mode:
                desired = mode['Replicated']['Replicas']
                mode_type = 'replicated'
            else:
                desired = self.get_active_nodes_count()
                mode_type = 'global'

            if running == desired and desired > 0:
                status = 'healthy'
            elif running > 0 and running < desired:
                status = 'degraded'
            elif running == 0 and preparing > 0:
                status = 'starting'
            elif running == 0 and desired > 0:
                status = 'down'
            else:
                status = 'unknown'

            return {
                'running': running,
                'desired': desired,
                'preparing': preparing,
                'failed': failed,
                'status': status,
                'mode': mode_type,
                'nodes': nodes_info,
                'containers': containers_info,
            }
        except docker.errors.NotFound:
            return None
        except Exception as e:
            logger.warning(f"Error getting status for {service_name}: {e}")
            return None

    def update_global_data(self, service_name, status_info, action='update'):
        with monitor_lock:
            if service_name not in global_data['services']:
                global_data['services'][service_name] = {
                    'message': '',
                    'node': '',
                    'container': '',
                    'missing': True,
                    'nodes': 0
                }

            if status_info:
                global_data['services'][service_name]['nodes'] = status_info['running']
                global_data['services'][service_name]['missing'] = status_info['status'] in ['down', 'starting']

                if 'nodes' in status_info and status_info['nodes']:
                    global_data['services'][service_name]['node'] = ', '.join(status_info['nodes'])
                if 'containers' in status_info and status_info['containers']:
                    global_data['services'][service_name]['container'] = ', '.join(status_info['containers'])

                emoji_map = {
                    'healthy': '✅',
                    'degraded': '⚠️',
                    'starting': '🔄',
                    'down': '❌',
                    'unknown': '❓'
                }
                emoji = emoji_map.get(status_info['status'], '❓')

                message = f"{emoji} {status_info['running']}/{status_info['desired']} {status_info['status']}"
                if status_info['preparing'] > 0:
                    message += f" (preparing: {status_info['preparing']})"
                if status_info['failed'] > 0:
                    message += f" (failed: {status_info['failed']})"

                global_data['services'][service_name]['message'] = message
            else:
                # Removed service
                global_data['services'][service_name]['missing'] = True
                global_data['services'][service_name]['nodes'] = 0

    def check_all_services(self):
        while self.running and self.client:
            try:
                services = self.client.services.list()

                for service in services:
                    service_name = service.name

                    # Only monitor current stack services
                    if not service_name.startswith(f"{STACK}_"):
                        continue

                    current_status = self.get_service_status(service_name)

                    if not current_status:
                        continue

                    with self.lock:
                        prev_status = self.service_states.get(service_name)

                        if prev_status is None:
                            self.service_states[service_name] = current_status
                            self.update_global_data(service_name, current_status, 'initial')
                        elif (prev_status['status'] != current_status['status'] or
                              prev_status['running'] != current_status['running']):

                            logger.info(
                                f"Service {service_name}: {prev_status['status']} "
                                f"({prev_status['running']}/{prev_status['desired']}) -> "
                                f"{current_status['status']} ({current_status['running']}/{current_status['desired']})"
                            )

                            self.service_states[service_name] = current_status
                            self.update_global_data(service_name, current_status, 'status_change')

                            nodes_str = ', '.join(current_status.get('nodes', [])) if current_status.get('nodes') else 'unknown'
                            containers_str = ', '.join(current_status.get('containers', [])) if current_status.get('containers') else 'unknown'

                            msg = {
                                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'service': service_name,
                                'text': f"Status: {current_status['status']} ({current_status['running']}/{current_status['desired']})",
                                'node': nodes_str,
                                'container': containers_str
                            }
                            MESSAGES_LOG.append(msg)

                asyncio.run(asyncio.sleep(5))

            except Exception as e:
                if self.running:
                    logger.error(f"Error in check_all_services: {e}")
                asyncio.run(asyncio.sleep(5))

    def monitor_events(self):
        """Monitor service events in real time"""
        if not self.client:
            return

        filters = {'type': 'service'}

        try:
            for event in self.client.events(decode=True, filters=filters):
                if not self.running:
                    break

                action = event.get('Action', 'unknown')
                attrs = event.get('Actor', {}).get('Attributes', {})
                service_name = attrs.get('name', 'unknown')

                # Only monitor current stack services
                if not service_name.startswith(f"{STACK}_"):
                    continue

                asyncio.run(asyncio.sleep(0.5))

                status_info = self.get_service_status(service_name)

                with self.lock:
                    # prev_status = self.service_states.get(service_name)

                    if status_info:
                        self.service_states[service_name] = status_info
                    elif service_name in self.service_states:
                        del self.service_states[service_name]

                    self.update_global_data(service_name, status_info, action)

                logger.info(f"Service event: {action} - {service_name}")

        except Exception as e:
            if self.running:
                logger.error(f"Error in monitor_events: {e}")

    def start(self):
        if not self.client:
            logger.warning("Docker monitor not available - skipping")
            return

        self.running = True

        # Loads initial state
        try:
            services = self.client.services.list()
            with self.lock:
                for service in services:
                    if not service.name.startswith(f"{STACK}_"):
                        continue

                    status = self.get_service_status(service.name)
                    if status:
                        self.service_states[service.name] = status
                        self.update_global_data(service.name, status, 'initial')
        except Exception as e:
            logger.error(f"Error loading initial state: {e}")

        # Iniciar threads
        self.checker_thread = threading.Thread(target=self.check_all_services, daemon=True)
        self.checker_thread.start()

        self.monitor_thread = threading.Thread(target=self.monitor_events, daemon=True)
        self.monitor_thread.start()

        logger.info("Docker Swarm monitor started")

    def stop(self):
        logger.info("Stopping Docker monitor...")
        self.running = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        if self.checker_thread:
            self.checker_thread.join(timeout=5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global docker_monitor

    # Startup
    logger.info('Starting application...')
    render_error_pages()
    config_haproxy()

    docker_monitor = DockerSwarmMonitor()
    docker_monitor.start()

    logger.info('Application started successfully')

    yield

    # Shutdown
    logger.info('Shutting down application...')
    if docker_monitor:
        docker_monitor.stop()


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
        logger.error('Error reading organization: %s', str(e))

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
    """Get service nodes - legacy fallback"""
    nodes = []
    cmd = f"dig tasks.{service} | grep ^tasks.{service} | awk '{{print $5}}'"
    _code, _out, _err = execute(cmd, interactive=False)
    logger.debug(f"dig command: {cmd}, output: {_out}, error: {_err}")
    if _code == 0:
        for node in _out.decode('utf-8').replace('\n', ' ').split(' '):
            if node:
                nodes.append(node)

    logger.debug(f'nodes for {service}: {nodes}')
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
        'USERLIST_STACK': userlist_stack(),
        'USERLIST_CLUSTER': userlist_cluster(),
        'NETWORK_MNG': NETWORK_MNG,
        'MTLS': MTLS == 'True',
    }

    payload = {'haproxy.cfg': Template(HAPROXY_TEMPLATE).render(context)}
    with open(FILECONFIG, 'w') as f:
        f.write(payload['haproxy.cfg'])
        f.write('\n')


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


@app.get('/services/manifest')
async def manifest():
    """Cache manifest"""
    template = """CACHE MANIFEST
/services/status
/services-static/*
/services/logs
    """
    content = Template(template).render({})

    return Response(
        content=content,
        media_type='text/cache-manifest'
    )


@app.get('/services/logs', response_class=HTMLResponse)
async def logs(request: Request):
    """Logs page"""
    columns = ['time', 'service', 'text', 'node', 'container']
    return templates.TemplateResponse('logs.html', {'request': request, 'columns': columns})


@app.get('/services/logs/json')
async def logs_json():
    """Get logs as JSON"""
    return JSONResponse(content=list(MESSAGES_LOG))


@app.get('/services/message')
async def get_message():
    """Get current message status"""
    # Docker's monitor automatic updates global_data

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
            service_name = f'{STACK}_{_service}'

            if service_name not in global_data['services']:
                global_data['services'][service_name] = {
                    'message': '',
                    'node': '',
                    'container': '',
                    'missing': True,
                    'nodes': 0
                }

            if docker_monitor and docker_monitor.client:
                pass
            else:
                # Fallback method
                nodes = len(get_nodes(_service))
                global_data['services'][service_name]['missing'] = nodes < 1
                global_data['services'][service_name]['nodes'] = nodes

            if global_data['services'][service_name]['missing']:
                global_data['need_reload'] = True
                missing = True

            if global_data['services'][service_name]['message']:
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


@app.get('/services/extensions', response_class=PlainTextResponse)
async def extensions():
    return " ".join(get_extensions())


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

    extensions = get_extensions()
    if len(get_extensions()) > 0:
        return Template(template).render({'extensions': extensions})

    return ''


# SSE endpoint for real-time updates
@app.get('/services/stream')
async def message_stream(request: Request):
    """Server-Sent Events endpoint for real-time updates"""

    async def event_generator():
        last_state_hash = None
        while True:
            if await request.is_disconnected():
                break

            current_state = {
                'last_message': global_data.get('last_message', ''),
                'services': global_data['services'].copy(),
                'ok': global_data['ok'],
                'organization': get_organization(),
                'stack': STACK,
                'tag': TAG,
                'disables': [],
            }

            if HTTPSMODE == 'manual':
                current_state['disables'].append('certbot')
            if os.environ.get('GOOGLE_API_KEY', '') == '':
                current_state['disables'].extend(['assistant', 'mcp-server'])

            state_hash = json.dumps(current_state, sort_keys=True)

            if state_hash != last_state_hash:
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
