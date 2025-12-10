#!/usr/bin/python3
# agent.py - Multi-protocol TCP Tunnel (SSH, VNC, RDP, etc.)
from http.client import PROCESSING
import asyncio
import websockets
import json
import socket
import platform
import uuid
import sys
import requests

import ssl


# Create SSL context that doesn't verify certificates (for testing only!)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class MultiProtocolAgent:
    def __init__(self, manager_url, agent_id=None, project=None, services=None):
        self.manager_url = manager_url.rstrip('/')
        self.server_url = None
        self.agent_id = agent_id or str(uuid.uuid4())
        self.project = project or 'Unknown'
        self.hostname = socket.gethostname()
        
        self.services = services or {
            'ssh': 22,
            'vnc': 5900
        }
        
        self.tcp_tunnels = {}
        self.websocket = None
    def is_port_open(self, port):
        """Checks if a port is open on localhost"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False

    def get_system_info(self):
        """Gets system information and active services"""
        # Filter services based on active ports
        active_services = []
        active_ports = {}
        
        for name, port in self.services.items():
            if self.is_port_open(port):
                active_services.append(name)
                active_ports[name] = port

        return {
            'system': platform.system(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python': sys.version,
            'available_services': active_services,
            'ports': active_ports,
            'project': self.project
        }
    async def register(self):
        """Registers the agent with the server via WebSocket"""
        message = {
            'type': 'register_agent',
            'agent_id': self.agent_id,
            'hostname': f'{self.hostname} [{self.agent_id}]',
            'info': self.get_system_info(),
            'mode': 'tcp_tunnel'
        }
        # Wait for WebSocket to be open (handled by connect logic)
        await self.websocket.send(json.dumps(message))
        print(f"✅ Agent registered: {self.agent_id}")
    async def handle_tcp_tunnel(self, tunnel_id, service='ssh'):
        """Handles a TCP tunnel to any local service"""
        if service not in self.services:
            print(f"❌ Service '{service}' not available.")
            return
        
        port = self.services[service]
        print(f"🔗 Starting tunnel {service.upper()}: {tunnel_id} -> port {port}")
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', port)
            self.tcp_tunnels[tunnel_id] = {
                'reader': reader,
                'writer': writer,
                'service': service,
                'port': port
            }
            async def service_to_ws():
                try:
                    while tunnel_id in self.tcp_tunnels:
                        data = await reader.read(8192)
                        if not data:
                            break
                        await self.websocket.send(json.dumps({
                            'type': 'tunnel_data',
                            'tunnel_id': tunnel_id,
                            'origin': 'agent',
                            'data': data.hex()
                        }))
                except Exception as e:
                    print(f"❌ Error reading service {service}: {e}")
                finally:
                    await self.close_tcp_tunnel(tunnel_id)
            asyncio.create_task(service_to_ws())
        except Exception as e:
            print(f"❌ Error connecting to local service {service}: {e}")
            await self.close_tcp_tunnel(tunnel_id)
    async def write_tcp_tunnel(self, tunnel_id, data_hex):
        if tunnel_id in self.tcp_tunnels:
            try:
                data = bytes.fromhex(data_hex)
                writer = self.tcp_tunnels[tunnel_id]['writer']
                writer.write(data)
                await writer.drain()
            except Exception as e:
                print(f"❌ Error writing to tunnel: {e}")
                await self.close_tcp_tunnel(tunnel_id)
    async def close_tcp_tunnel(self, tunnel_id):
        if tunnel_id in self.tcp_tunnels:
            try:
                writer = self.tcp_tunnels[tunnel_id]['writer']
                writer.close()
                await writer.wait_closed()
                del self.tcp_tunnels[tunnel_id]
                
                if self.websocket and self.websocket.open:
                    await self.websocket.send(json.dumps({
                        'type': 'tunnel_closed',
                        'tunnel_id': tunnel_id
                    }))
            except Exception:
                pass
    async def handle_messages(self):
        try:
            async for message_raw in self.websocket:
                message = json.loads(message_raw)
                msg_type = message.get('type')
                if msg_type == 'start_tcp_tunnel':
                    await self.handle_tcp_tunnel(message.get('tunnel_id'), message.get('service', 'ssh'))
                elif msg_type == 'tunnel_data':
                    await self.write_tcp_tunnel(message.get('tunnel_id'), message.get('data'))
                elif msg_type == 'close_tcp_tunnel':
                    await self.close_tcp_tunnel(message.get('tunnel_id'))
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    async def connect(self):
        while True:
            try:
                # 1. Get assignment from Manager (Non-blocking way)
                if not self.server_url:
                    print(f"🌐 Contacting Manager at {self.manager_url}...")
                    
                    # Run requests in a thread to avoid blocking the loop
                    def fetch_assignment():
                        msg = {
                            "agent_id": self.agent_id,
                            "hostname": self.hostname,
                            "info": self.get_system_info()
                        }
                        return requests.post(
                            f"{self.manager_url}/register", 
                            json=msg, 
                            timeout=5
                        )
                    try:
                        # Python 3.8 compatible: use run_in_executor instead of asyncio.to_thread
                        loop = asyncio.get_event_loop()
                        resp = await loop.run_in_executor(None, fetch_assignment)
                        resp.raise_for_status()
                        data = resp.json()            
                        self.server_url = data['relay_url']
                    except Exception as e:
                        print(f"❌ Manager error: {e}")
                        await asyncio.sleep(5)
                        continue
                # 2. Connect to Relay
                print(f"🔌 Connecting to {self.server_url}...")
                
                # Prepare connection kwargs
                connect_kwargs = {
                    'ping_interval': 20,      # Send ping every 20 seconds
                    'ping_timeout': 60,       # Wait up to 60 seconds for pong
                    'close_timeout': 10,      # Wait up to 10 seconds for close handshake
                    'max_size': 10**7
                }
                
                # Add SSL context for wss:// URLs
                if self.server_url.startswith('wss://'):
                    connect_kwargs['ssl'] = ssl_context
                
                # Try to add headers - different websockets versions use different parameter names
                headers = {'X-Agent-ID': self.agent_id}
                try:
                    # Try extra_headers first (older versions)
                    connect_kwargs['extra_headers'] = headers
                    async with websockets.connect(self.server_url, **connect_kwargs) as ws:
                        self.websocket = ws
                        print("✅ Connection established")
                        await self.register()
                        await self.handle_messages()
                except TypeError as e:
                    if 'extra_headers' in str(e):
                        # Fallback to additional_headers (newer versions)
                        del connect_kwargs['extra_headers']
                        connect_kwargs['additional_headers'] = headers
                        async with websockets.connect(self.server_url, **connect_kwargs) as ws:
                            self.websocket = ws
                            print("✅ Connection established")
                            await self.register()
                            await self.handle_messages()
                    else:
                        raise
                # If connection drops
                print("⚠️ Disconnected from Relay")
                self.server_url = None 
            except Exception as e:
                print(f"❌ Connection error: {e}")
                self.server_url = None
                await asyncio.sleep(5)
async def main():
    # UPDATED URL: Point to the specific API endpoint

    try:
        from migasfree_client import settings
        from migasfree_client.utils import get_config
        FQDN = get_config(settings.CONF_FILE, 'client').get('server', 'localhost')
    except Exception as e:
        print(f"❌ migasfree-client not found") 
        exit(0)

    MANAGER_URL = f"http://{FQDN}/manager/v1/public/tunnel"
  
    with open('/usr/share/migasfree-client/events.d/.json', 'r') as archivo:
        TRAITS = json.load(archivo)
        AGENT_ID = f'CID-{TRAITS["after"]["CID"][0]}'
        PROJECT = f'{TRAITS["after"]["PRJ"][0]}'   
    
    # Customize services
    SERVICES = {
        'ssh': 22,
        'vnc': 5900
    }
    agent = MultiProtocolAgent(MANAGER_URL, services=SERVICES, agent_id=AGENT_ID, project=PROJECT)
    await agent.connect()
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Agent stopped")
    