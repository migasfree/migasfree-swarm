#!/usr/bin/python3

# main.py - Multi-protocol Server (SSH, VNC, RDP, etc.)

import asyncio
import websockets
from websockets.http11 import Response, Headers
import json
import redis.asyncio as redis
import os
import resource
import uuid
import socket
import logging

class IgnoreHandshakeErrorFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # Ignora errores específicos de healthcheck/HAProxy probes
        if any(error in msg for error in [
            "did not receive a valid HTTP request",
            "line without CRLF",
            "connection closed while reading HTTP request line",
            "opening handshake failed",
            "InvalidMessage"
        ]):
            return False
        return True

for logger_name in [
    "websockets",
    "websockets.server",
    "websockets.protocol",
    "websockets.http11",
    "websockets.server"
]:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.addFilter(IgnoreHandshakeErrorFilter())
    logger.propagate = False


REDIS_URL = os.environ["REDIS_URL"]
FQDN = os.environ["FQDN"]
TUNNEL_CONNECTIONS = int(os.environ["TUNNEL_CONNECTIONS"])


class MultiProtocolServer:
    def __init__(self, host='0.0.0.0', port=8080, max_connections=TUNNEL_CONNECTIONS, redis_url='redis://localhost'):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.redis_url = redis_url
        self.redis = None
        self.connected_agents = {}
        self.tcp_tunnels = {}
        self.active_connections = 0

        # Public URL (through HAProxy) for clients
        self.server_url = f"wss://{FQDN}/tunnel"
        
        # Internal URL (direct to container) for agents
        # This allows proper load balancing across multiple relay instances
        self.server_internal_url = f"ws://{socket.gethostname()}:{self.port}"

        self.server_id = str(uuid.uuid4())

        self._configure_limits()

    async def _init_redis(self):
        if not self.redis:
            try:
                self.redis = redis.from_url(self.redis_url, decode_responses=True)
                await self.redis.ping()
                print(f"✅ Connected to Redis")
            except Exception as e:
                # Only print error once or if verbose
                print(f"⚠️  Redis not available: {e}")
                self.redis = None

    def _configure_limits(self):
        """Configures system limits for high concurrency"""
        try:
            soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)

            requested = self.max_connections * 2
            new_soft = min(requested, hard)
            new_hard = hard

            resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, new_hard))
            print(f"✅ File descriptors: {soft}→{new_soft} (max {new_hard})")

            # Verify
            current_soft, current_hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            if current_soft >= TUNNEL_CONNECTIONS:
                print("🚀 High concurrency ready!")
            else:
                print(f"⚠️  Limited to {current_soft}")

        except Exception as e:
            print(f"⚠️  Limits unchanged: {e}")

    async def _report_heartbeat(self):
        """Reports server load and presence to Redis"""
        while True:
            if self.redis:
                try:
                    data = {
                        'id': self.server_id,
                        'url': self.server_url,              # Public URL for clients
                        'internal_url': self.server_internal_url,  # Internal URL for agents
                        'load': self.active_connections,
                        'max_connections': self.max_connections,
                        'hostname': socket.gethostname()
                    }
                    # Set with TTL of 10 seconds
                    await self.redis.set(f"tunnel:{self.server_id}", json.dumps(data), ex=10)
                except Exception as e:
                    print(f"⚠️  Redis heartbeat error: {e}")
            await asyncio.sleep(5)

    async def register_agent(self, websocket, message):
        """Registers a new agent with connection limit"""
        if self.active_connections >= self.max_connections:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Connection limit reached ({self.max_connections})'
            }))
            await websocket.close()
            return False

        agent_id = message.get('agent_id')
        hostname = message.get('hostname')

        agent_info = message.get('info', {})

        agent_data = {
            'agent_id': agent_id,
            'hostname': hostname,
            'info': agent_info,
            'timestamp': asyncio.get_event_loop().time(),
            'mode': message.get('mode', 'tcp_tunnel'),
            'relay_url': self.server_url,       # Public URL for clients to connect
            'tunnel_url': self.server_url,      # Legacy compatibility
            'tunnel_id': self.server_id,
            'server_ip': socket.gethostbyname(socket.gethostname())
        }

        self.connected_agents[agent_id] = {
            'websocket': websocket,
            'data': agent_data
        }

        self.active_connections += 1

        # Register in Redis
        await self._init_redis()
        if self.redis:
            try:
                await self.redis.set(f"agent:{agent_id}", json.dumps(agent_data), ex=300) # 5 min TTL
            except Exception as e:
                print(f"⚠️  Redis error: {e}")

        # Show available services if they exist
        services = agent_info.get('available_services', [])
        services_str = f" [{', '.join(services)}]" if services else ""

        print(f"✅ Agent {self.active_connections}/{self.max_connections}: {hostname} ({agent_id}){services_str}")

        await websocket.send(json.dumps({
            'type': 'registration_ok',
            'message': 'Agent registered successfully'
        }))

        return True

    async def start_tcp_tunnel(self, websocket, message):
        """Starts a transparent TCP tunnel for any protocol"""
        agent_id = message.get('agent_id')
        tunnel_id = message.get('tunnel_id')
        service = message.get('service', 'ssh')  # Default SSH

        if agent_id in self.connected_agents:
            # Local agent
            self.tcp_tunnels[tunnel_id] = {
                'type': 'local',
                'agent_id': agent_id,
                'client_ws': websocket,
                'agent_ws': self.connected_agents[agent_id]['websocket'],
                'service': service
            }

            # Notify agent
            agent_ws = self.connected_agents[agent_id]['websocket']
            await agent_ws.send(json.dumps({
                'type': 'start_tcp_tunnel',
                'tunnel_id': tunnel_id,
                'service': service
            }))

            # Confirm to client
            await websocket.send(json.dumps({
                'type': 'tunnel_started',
                'tunnel_id': tunnel_id,
                'agent_id': agent_id,
                'service': service
            }))

            print(f"🔗 Local Tunnel {service.upper()} started: {tunnel_id}")

        else:
            # Agent not found locally
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Agent {agent_id} not found on this server'
            }))

    async def forward_tunnel_data(self, message):
        """Forwards TCP tunnel data between client and agent"""
        tunnel_id = message.get('tunnel_id')
        origin = message.get('origin', 'client')

        if tunnel_id not in self.tcp_tunnels:
            return

        tunnel = self.tcp_tunnels[tunnel_id]

        try:
            if origin == 'client':
                # Client -> Agent
                await tunnel['agent_ws'].send(json.dumps(message))
            else:
                # Agent -> Client
                await tunnel['client_ws'].send(json.dumps(message))

        except Exception as e:
            print(f"❌ Error forwarding tunnel data {tunnel_id}: {e}")
            await self.close_tcp_tunnel(tunnel_id)

    async def close_tcp_tunnel(self, tunnel_id):
        """Closes a TCP tunnel"""
        if tunnel_id in self.tcp_tunnels:
            tunnel = self.tcp_tunnels[tunnel_id]

            # Notify local websockets
            if 'client_ws' in tunnel:
                try:
                    await tunnel['client_ws'].send(json.dumps({
                        'type': 'tunnel_closed',
                        'tunnel_id': tunnel_id
                    }))
                except: pass

            if 'agent_ws' in tunnel:
                try:
                    await tunnel['agent_ws'].send(json.dumps({
                        'type': 'close_tcp_tunnel',
                        'tunnel_id': tunnel_id
                    }))
                except: pass

            del self.tcp_tunnels[tunnel_id]
            print(f"🔌 TCP tunnel closed: {tunnel_id}")

    async def list_agents(self, websocket):
        """Lists available agents from Redis (global view)"""
        agents = []
        if self.redis:
            try:
                keys = await self.redis.keys("agent:*")
                if keys:
                    agents_json = await self.redis.mget(keys)
                    agents = [json.loads(a) for a in agents_json if a]
            except Exception as e:
                print(f"⚠️  Error fetching agents from Redis: {e}")
                # Fallback to local agents
                for agent_id, data in self.connected_agents.items():
                    agents.append(data['data'])
        else:
            for agent_id, data in self.connected_agents.items():
                agents.append(data['data'])

        await websocket.send(json.dumps({
            'type': 'agent_list',
            'agents': agents,
            'total': len(agents)
        }))

    async def handle_connection(self, websocket):
        """Handles WebSocket connections"""
        connection_type = None
        agent_id = None

        try:
            async for message_raw in websocket:
                try:
                    message = json.loads(message_raw)
                    msg_type = message.get('type')

                    if msg_type == 'register_agent':
                        connection_type = 'agent'
                        agent_id = message.get('agent_id')
                        if not await self.register_agent(websocket, message):
                            return

                    elif msg_type == 'connect_client':
                        connection_type = 'client'
                        await websocket.send(json.dumps({
                            'type': 'connection_ok',
                            'message': 'Client connected'
                        }))

                    elif msg_type == 'list_agents':
                        await self.list_agents(websocket)

                    elif msg_type == 'start_tcp_tunnel':
                        await self.start_tcp_tunnel(websocket, message)

                    elif msg_type == 'tunnel_data':
                        await self.forward_tunnel_data(message)

                    elif msg_type == 'close_tunnel':
                        tunnel_id = message.get('tunnel_id')
                        await self.close_tcp_tunnel(tunnel_id)

                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"❌ Error: {e}")

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if connection_type == 'agent' and agent_id:
                if agent_id in self.connected_agents:
                    del self.connected_agents[agent_id]
                    self.active_connections -= 1
                    print(f"❌ Agent disconnected: {self.active_connections} active")

                    # Remove from Redis
                    if self.redis:
                        try:
                            await self.redis.delete(f"agent:{agent_id}")
                        except:
                            pass

                # Clean up TCP tunnels associated with disconnected agent
                tunnels_to_close = [
                    tid for tid, data in self.tcp_tunnels.items()
                    if data['agent_id'] == agent_id
                ]
                for tid in tunnels_to_close:
                    await self.close_tcp_tunnel(tid)

    async def monitor_stats(self):
        """Monitors server statistics and updates Redis TTL"""
        while True:
            await asyncio.sleep(30)
            print(f"\n📊 Stats: {self.active_connections} agents, "
                  f"{len(self.tcp_tunnels)} active TCP tunnels")

            # Update Redis TTL for all connected agents
            if self.redis and self.connected_agents:
                try:
                    for agent_id, data in self.connected_agents.items():
                        await self.redis.expire(f"agent:{agent_id}", 300)
                except Exception as e:
                    print(f"⚠️  Error updating Redis TTL: {e}")

    async def process_request(self, connection, request):
        """
        Intercepts the HTTP request handshake to handle health checks.
        """
        if request.path == "/health":
            # Response(status_code, reason_phrase, headers, body)
            headers = Headers([("Content-Type", "text/plain")])
            return Response(200, "OK", headers, b"OK\n")
        # Allow normal websocket handshake to proceed
        return None

    async def start(self):
        """Starts the server"""
        print("="*70)
        print("🚀 Multi-Protocol Tunnel Relay Server")
        print("="*70)
        print(f"🔗 Public URL: {self.server_url}")
        print(f"📦 websockets: {websockets.__version__}")
        print(f"📢 Max connections: {self.max_connections}")
        print("="*70 + "\n")

        await self._init_redis()
        asyncio.create_task(self.monitor_stats())
        asyncio.create_task(self._report_heartbeat())

        # Define the connection handler bound to self
        bound_handler = self.handle_connection

        async with websockets.serve(
            bound_handler,
            self.host,
            self.port,
            ping_interval=30,        # Send ping every 30 seconds
            ping_timeout=60,         # Wait up to 60 seconds for pong
            close_timeout=10,        # Wait up to 10 seconds for close handshake
            max_size=10**7,          # 10MB for binary data
            max_queue=100,
            process_request=self.process_request
        ):
            await asyncio.Future()

if __name__ == "__main__":

    server = MultiProtocolServer(max_connections=TUNNEL_CONNECTIONS, redis_url=REDIS_URL)

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n✅ Server stopped")