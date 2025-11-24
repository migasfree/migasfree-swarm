import os
import logging
import subprocess
import docker
import sys
import asyncio

from typing import Dict

from core.utils import get_timestamp


# Logging configuration
logger = logging.getLogger('services')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

service_states_cache = {}

STACK = os.environ['STACK']


class DockerSwarmMonitor:
    def __init__(self):
        self.client = None
        self.service_states = {}
        self.lock = asyncio.Lock()
        self.cache_lock = asyncio.Lock()  # Cache Lock
        self.client_id_lock = asyncio.Lock()  # SSE clients Lock
        self.running = False
        # Use asyncio.Queue for SSE clients to avoid blocking and support concurrency
        self.sse_clients: Dict[int, asyncio.Queue] = {}
        self.messages_log = []



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

    async def broadcast_to_sse_clients(self, event_data):
        """Broadcast event to all connected SSE clients"""
        logger.debug('Broadcasting event_data: %s', event_data)
        if not event_data:
            logger.warning('Empty event_data, skipping broadcast')
            return

        # Create snapshot without holding lock during broadcast
        async with self.client_id_lock:
            clients_snapshot = list(self.sse_clients.items())

        if not clients_snapshot:
            logger.debug('No SSE clients connected, skipping broadcast')
            return

        logger.debug(f'Broadcasting to {len(clients_snapshot)} client(s)')

        to_remove = []
        for cid, client_queue in clients_snapshot:
            try:
                client_queue.put_nowait(event_data)
                logger.debug(f'✅ Broadcasted to client {cid}')
            except asyncio.QueueFull:
                logger.warning(f'SSE client {cid} queue full, marking for removal')
                to_remove.append(cid)
            except Exception as e:
                logger.error(f'Error broadcasting to client {cid}: {e}')
                to_remove.append(cid)

        # Remove failed clients
        if to_remove:
            async with self.client_id_lock:
                for cid in to_remove:
                    removed = self.sse_clients.pop(cid, None)
                    if removed:
                        logger.info(f'Removed failed client {cid}')

    async def update_service_cache(self, service_name, status_info):
        async with self.cache_lock:
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
                        event_data = {
                            'service': service_name,
                            'status': current_status,
                            'timestamp': get_timestamp(),
                        }
                        if prev_status is None:
                            self.service_states[service_name] = current_status
                            await self.update_service_cache(service_name, current_status)
                            await self.broadcast_to_sse_clients({'event': 'status', 'data': event_data})
                        elif (
                            prev_status['status'] != current_status['status']
                            or prev_status['running'] != current_status['running']
                        ):
                            logger.info(
                                f'Service {service_name}: {prev_status["status"]} ({prev_status["running"]}/{prev_status["desired"]}) -> {current_status["status"]} ({current_status["running"]}/{current_status["desired"]})'
                            )
                            self.service_states[service_name] = current_status
                            await self.update_service_cache(service_name, current_status)
                            await self.broadcast_to_sse_clients({'event': 'status', 'data': event_data})
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
                            self.messages_log.append(msg)
                            logger.debug('service %s, message %s', service_name, msg)
                            await self.broadcast_to_sse_clients({'event': 'log', 'data': msg})

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
                event_data = {
                    'service': service_name,
                    'status': status_info,
                    'timestamp': get_timestamp(),
                }
                await self.update_service_cache(service_name, status_info)
                await self.broadcast_to_sse_clients({'event': 'status', 'data': event_data})
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

    async def cache(self):
        async with self.cache_lock:
            return service_states_cache.copy()

    async def stop(self):
        logger.info('Stopping Docker monitor...')
        self.running = False