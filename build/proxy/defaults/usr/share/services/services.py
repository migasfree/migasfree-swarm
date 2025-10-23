#!/usr/bin/python3

import os
import sys
import json
import asyncio
import re
import logging
import subprocess
import docker

from datetime import datetime
from collections import deque
from typing import List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Template
from sse_starlette.sse import EventSourceResponse

# Logging configuration
logger = logging.getLogger('services')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

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

# Use asyncio.Queue for SSE clients to avoid blocking and support concurrency
sse_clients: Dict[int, asyncio.Queue] = {}
client_id_counter = 0
client_id_lock = asyncio.Lock()

service_states_cache = {}
cache_lock = asyncio.Lock()


def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class DockerSwarmMonitor:
    def __init__(self):
        self.client = None
        try:
            self.client = docker.from_env()
            info = self.client.info()
            swarm = info.get('Swarm', {})
            if not swarm.get('ControlAvailable', False):
                logger.warning('Not running on a Swarm manager node - Docker monitoring disabled')
                self.client = None
                return

            logger.info(f'Connected to Swarm cluster ID: {swarm.get("Cluster", {}).get("ID", "unknown")[:12]}')
            logger.info(f'Nodes: {swarm.get("Nodes", 0)} | Managers: {swarm.get("Managers", 0)}')
        except Exception as e:
            logger.error(f'Error connecting to Docker: {e}')
            self.client = None

        self.service_states = {}
        self.lock = asyncio.Lock()
        self.running = False

    async def get_active_nodes_count(self):
        if not self.client:
            return 0

        try:
            nodes = self.client.nodes.list()
            active = len(
                [
                    n
                    for n in nodes
                    if n.attrs['Status']['State'] == 'ready' and n.attrs['Spec']['Availability'] == 'active'
                ]
            )
            return active
        except Exception as e:
            logger.warning(f'Error counting nodes: {e}')
            return 0

    async def get_service_status(self, service_name):
        if not self.client:
            return None

        logger.debug('service_name: %s', service_name)
        try:
            service = self.client.services.get(service_name)
            tasks = service.tasks()
            # logger.debug('tasks: %s', str(tasks))

            running_tasks = [t for t in tasks if t['Status']['State'] == 'running']
            running = len(running_tasks)
            preparing = len(
                [t for t in tasks if t['Status']['State'] in ['preparing', 'starting', 'assigned', 'accepted', 'ready']]
            )
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
                desired = await self.get_active_nodes_count()
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

            ret = {
                'running': running,
                'desired': desired,
                'preparing': preparing,
                'failed': failed,
                'status': status,
                'mode': mode_type,
                'nodes': nodes_info,
                'containers': containers_info,
            }
            logger.debug(ret)

            return ret
        except docker.errors.NotFound:
            return None
        except Exception as e:
            logger.warning(f'Error getting status for {service_name}: {e}')
            return None

    async def broadcast_to_sse_clients(self, service_name, status_info):
        if not status_info:
            return

        event_data = {
            'service': service_name,
            'status': status_info,
            'timestamp': get_timestamp(),
        }
        logger.debug('event_data: %s', event_data)

        to_remove = []
        async with client_id_lock:
            for cid, client_queue in sse_clients.items():
                try:
                    client_queue.put_nowait(event_data)
                except asyncio.QueueFull:
                    logger.warning(f'SSE client {cid} queue full, removing client.')
                    to_remove.append(cid)
        async with client_id_lock:
            for cid in to_remove:
                sse_clients.pop(cid, None)

    async def update_service_cache(self, service_name, status_info):
        async with cache_lock:
            if service_name not in service_states_cache:
                service_states_cache[service_name] = {
                    'message': '',
                    'status': '',
                    'node': '',
                    'container': '',
                    'nodes': 0,
                }

            if status_info:
                service_states_cache[service_name]['nodes'] = status_info['running']
                service_states_cache[service_name]['status'] = status_info['status']

                if 'nodes' in status_info and status_info['nodes']:
                    service_states_cache[service_name]['node'] = ', '.join(status_info['nodes'])
                if 'containers' in status_info and status_info['containers']:
                    service_states_cache[service_name]['container'] = ', '.join(status_info['containers'])

                emoji_map = {'healthy': '✅', 'degraded': '⚠️', 'starting': '🔄', 'down': '❌', 'unknown': '❓'}
                emoji = emoji_map.get(status_info['status'], '❓')

                message = f'{emoji} {status_info["running"]}/{status_info["desired"]} {status_info["status"]}'
                if status_info['preparing'] > 0:
                    message += f' (preparing: {status_info["preparing"]})'
                if status_info['failed'] > 0:
                    message += f' (failed: {status_info["failed"]})'

                service_states_cache[service_name]['message'] = message
            else:
                # Removed service
                service_states_cache[service_name]['nodes'] = 0

    async def check_all_services(self):
        while self.running and self.client:
            try:
                services = self.client.services.list()
                for service in services:
                    service_name = service.name
                    if not service_name.startswith(f'{STACK}_') and not service_name.startswith('infra_'):
                        continue
                    current_status = await self.get_service_status(service_name)
                    logger.debug('current_status service %s: %s', service_name, current_status)
                    if not current_status:
                        continue

                    async with self.lock:
                        prev_status = self.service_states.get(service_name)
                        if prev_status is None:
                            self.service_states[service_name] = current_status
                            await self.update_service_cache(service_name, current_status)
                            await self.broadcast_to_sse_clients(service_name, current_status)
                        elif (
                            prev_status['status'] != current_status['status']
                            or prev_status['running'] != current_status['running']
                        ):
                            logger.info(
                                f'Service {service_name}: {prev_status["status"]} ({prev_status["running"]}/{prev_status["desired"]}) -> {current_status["status"]} ({current_status["running"]}/{current_status["desired"]})'
                            )
                            self.service_states[service_name] = current_status
                            await self.update_service_cache(service_name, current_status)
                            await self.broadcast_to_sse_clients(service_name, current_status)
                            msg = {
                                'timestamp': get_timestamp(),
                                'service': service_name,
                                'text': f'Status: {current_status["status"]} ({current_status["running"]}/{current_status["desired"]})',
                                'node': ', '.join(current_status.get('nodes', []))
                                if current_status.get('nodes')
                                else 'unknown',
                                'container': ', '.join(current_status.get('containers', []))
                                if current_status.get('containers')
                                else 'unknown',
                            }
                            MESSAGES_LOG.append(msg)
                            logger.debug('service %s, message %s', service_name, msg)
                            await self.broadcast_to_sse_clients(service_name, msg)

                await asyncio.sleep(5)
            except Exception as e:
                if self.running:
                    logger.error(f'Error in check_all_services: {e}')
                await asyncio.sleep(5)

    async def monitor_events(self):
        if not self.client:
            return

        filters = {'type': 'service'}

        try:
            event_stream = self.client.events(decode=True, filters=filters)
            loop = asyncio.get_event_loop()
            while self.running:
                event = await loop.run_in_executor(None, lambda: next(event_stream, None))
                if event is None:
                    await asyncio.sleep(1)
                    continue
                action = event.get('Action', 'unknown')
                attrs = event.get('Actor', {}).get('Attributes', {})
                service_name = attrs.get('name', 'unknown')
                if not service_name.startswith(f'{STACK}_') and not service_name.startswith('infra_'):
                    continue
                status_info = await self.get_service_status(service_name)
                async with self.lock:
                    if status_info:
                        self.service_states[service_name] = status_info
                    elif service_name in self.service_states:
                        del self.service_states[service_name]
                await self.update_service_cache(service_name, status_info)
                await self.broadcast_to_sse_clients(service_name, status_info)
                logger.info(f'Service event: {action} - {service_name}')
        except Exception as e:
            if self.running:
                logger.error(f'Error in monitor_events: {e}')

    async def start(self):
        if not self.client:
            logger.warning('Docker monitor not available - skipping')
            return

        self.running = True

        # Loads initial state
        try:
            services = self.client.services.list()
            async with self.lock:
                for service in services:
                    if not service.name.startswith(f'{STACK}_') and not service.name.startswith('infra_'):
                        continue
                    status = await self.get_service_status(service.name)
                    if status:
                        self.service_states[service.name] = status
                        await self.update_service_cache(service.name, status)
        except Exception as e:
            logger.error(f'Error loading initial state: {e}')

        # Run monitoring tasks asynchronously
        asyncio.create_task(self.check_all_services())
        asyncio.create_task(self.monitor_events())
        logger.info('Docker Swarm monitor started')

    async def stop(self):
        logger.info('Stopping Docker monitor...')
        self.running = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global docker_monitor
    logger.info('Starting application...')
    render_error_pages()
    config_haproxy()
    docker_monitor = DockerSwarmMonitor()
    await docker_monitor.start()
    logger.info('Application started successfully')
    yield
    logger.info('Shutting down application...')
    if docker_monitor:
        await docker_monitor.stop()


app = FastAPI(title='Services API', lifespan=lifespan)
app.mount('/services-static', StaticFiles(directory='services-static'), name='static')
templates = Jinja2Templates(directory='services-static/templates')


async def get_organization() -> str:
    try:
        with open(f'{PATH_CONF}/settings.py', 'r', encoding='utf-8') as file:
            content = file.read()

        pattern = r'MIGASFREE_ORGANIZATION\s*=\s*(.+)'
        result = re.search(pattern, content)
        if result:
            return result.group(1)[1:-1]
    except Exception as e:
        logger.error(f'Error reading organization: {e}')

    return ''


def get_extensions() -> List[str]:
    pms_enabled = os.environ['PMS_ENABLED']
    extensions = []

    try:
        result = subprocess.run(
            ['curl', '-X', 'GET', 'core:8080/api/v1/public/pms/'],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        if result.returncode == 0:
            all_pms = json.loads(result.stdout)
            for pms in all_pms:
                if f'pms-{pms}' in pms_enabled:
                    for extension in all_pms[pms]['extensions']:
                        extensions.append(extension)
    except Exception as e:
        logger.error(f'Error getting extensions: {e}')

    return list(set(extensions))


def config_haproxy():
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
    with open(FILECONFIG, 'w', encoding='utf-8') as f:
        f.write(payload['haproxy.cfg'])
        f.write('\n')


def render_error_pages():
    context = {'FQDN': FQDN}
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
    with open(f'/run/secrets/{STACK}_superadmin_name', 'r', encoding='utf-8') as f:
        username = f.read()
    with open(f'/run/secrets/{STACK}_superadmin_pass', 'r', encoding='utf-8') as f:
        password = f.read()

    result = subprocess.run(['mkpasswd', '-m', 'sha-512', password], capture_output=True, text=True, check=True)

    return f'    user {username} password {result.stdout}'


def userlist_cluster() -> str:
    with open('/run/secrets/swarm-credential', 'r', encoding='utf-8') as f:
        username, password = f.read().split(':')

    result = subprocess.run(['mkpasswd', '-m', 'sha-512', password], capture_output=True, text=True, check=True)

    return f'    user {username} password {result.stdout}'


@app.get('/favicon.ico')
async def favicon():
    """Redirect to logo"""
    return RedirectResponse(url=f'https://{FQDN}/services-static/img/logo.svg')


@app.get('/services/status/', response_class=HTMLResponse)
async def status_page(request: Request):
    """Status page"""
    async with cache_lock:
        context = {'services': service_states_cache.copy(), 'request': request}

    return templates.TemplateResponse('status.html', context)


@app.get('/services/manifest')
async def manifest():
    """Cache manifest"""
    template = """CACHE MANIFEST
/services/status
/services-static/*
/services/logs
    """
    content = Template(template).render({})

    return Response(content=content, media_type='text/cache-manifest')


# SSE endpoint: logs stream with asyncio.Queue per client
@app.get('/services/logs/stream')
async def logs_stream(request: Request):
    global client_id_counter
    queue = asyncio.Queue(maxsize=100)
    async with client_id_lock:
        global client_id_counter
        client_id = client_id_counter
        client_id_counter += 1
        sse_clients[client_id] = queue

    logger.info(f'Logs SSE client {client_id} connected. Total clients: {len(sse_clients)}')

    async def event_generator():
        try:
            initial_messages = list(MESSAGES_LOG)[-50:]
            for message in initial_messages:
                yield {'event': 'log', 'data': json.dumps(message)}
                await asyncio.sleep(0.01)

            # Stream new log updates
            while True:
                if await request.is_disconnected():
                    break
                try:
                    log_data = await asyncio.wait_for(queue.get(), timeout=30)
                    yield {'event': 'log', 'data': json.dumps(log_data)}
                except asyncio.TimeoutError:
                    yield {
                        'event': 'ping',
                        'data': json.dumps({'timestamp': get_timestamp()}),
                    }
        finally:
            async with client_id_lock:
                sse_clients.pop(client_id, None)
            logger.info(f'Logs SSE client {client_id} disconnected. Remaining clients: {len(sse_clients)}')

    return EventSourceResponse(event_generator())


# Keep the JSON endpoint for compatibility (optional)
@app.get('/services/logs/json')
async def logs_json():
    """Get logs as JSON (deprecated - use /services/logs/stream instead)"""
    return JSONResponse(content=list(MESSAGES_LOG))


@app.get('/services/logs', response_class=HTMLResponse)
async def logs(request: Request):
    """Logs page"""
    columns = ['timestamp', 'service', 'text', 'node', 'container']

    return templates.TemplateResponse('logs.html', {'request': request, 'columns': columns})


@app.get('/services/info')
async def get_info():
    """Get static application info (organization, stack, tag, disabled)"""
    disabled = []
    if os.environ['HTTPSMODE'] == 'manual':
        disabled.append('certbot')
    if os.environ.get('GOOGLE_API_KEY', '') == '':
        disabled.append('assistant')
        disabled.append('mcp-server')

    return JSONResponse(
        content={
            'organization': await get_organization(),
            'stack': STACK,
            'tag': TAG,
            'disabled': disabled,
        }
    )


@app.post('/services/message')
async def post_message(request: Request):
    """Post a new message"""
    try:
        data = await request.json()
        logger.debug('post_message data: %s', data)
    except Exception:
        data = {}

    data['timestamp'] = get_timestamp()
    MESSAGES_LOG.append(data)

    # Notify all SSE clients about the new log message
    """
    to_remove = []
    async with client_id_lock:
        for cid, client_queue in sse_clients.items():
            try:
                client_queue.put_nowait(data)
            except asyncio.QueueFull:
                logger.warning(f'SSE client {cid} queue full, removing client.')
                to_remove.append(cid)
        async with client_id_lock:
            for cid in to_remove:
                sse_clients.pop(cid, None)
    """

    return JSONResponse(content={'status': 'ok'})


@app.get('/services/extensions', response_class=PlainTextResponse)
async def extensions():
    return ' '.join(get_extensions())


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


# SSE endpoint: services stream
@app.get('/services/stream')
async def service_stream(request: Request):
    global client_id_counter
    queue = asyncio.Queue(maxsize=100)
    async with client_id_lock:
        global client_id_counter
        client_id = client_id_counter
        client_id_counter += 1
        sse_clients[client_id] = queue

    logger.info(f'Service SSE client {client_id} connected. Total clients: {len(sse_clients)}')

    async def event_generator():
        try:
            async with cache_lock:
                for service_name, service_data in service_states_cache.items():
                    if 'nodes' in service_data:
                        initial_data = {
                            'service': service_name,
                            'status': {
                                'status': service_data.get('status', ''),  # FIXME
                                'running': service_data.get('nodes', 0),
                                'nodes': service_data.get('node', '').split(', ') if service_data.get('node') else [],
                                'containers': service_data.get('container', '').split(', ')
                                if service_data.get('container')
                                else [],
                            },
                            'timestamp': get_timestamp(),
                        }
                        yield {'event': 'status', 'data': json.dumps(initial_data)}
                        logger.debug('data: %s', initial_data)

            # Stream updates
            while True:
                if await request.is_disconnected():
                    break

                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=30)
                    yield {'event': 'status', 'data': json.dumps(event_data)}
                except asyncio.TimeoutError:
                    yield {
                        'event': 'ping',
                        'data': json.dumps({'timestamp': get_timestamp()}),
                    }
        finally:
            async with client_id_lock:
                sse_clients.pop(client_id, None)
            logger.info(f'Service SSE client {client_id} disconnected. Remaining clients: {len(sse_clients)}')

    return EventSourceResponse(event_generator())


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    async with cache_lock:
        context = {'services': service_states_cache.copy(), 'request': request}
    return templates.TemplateResponse('status.html', context, status_code=404)


@app.exception_handler(503)
async def service_unavailable_handler(request: Request, exc: HTTPException):
    """Custom 503 handler"""
    async with cache_lock:
        context = {'services': service_states_cache.copy(), 'request': request}
    return templates.TemplateResponse('status.html', context, status_code=503)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8001, log_level='debug')
