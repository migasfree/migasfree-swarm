#!/usr/bin/python3

# remote-ssh.py - Script for multi-protocol tunnel (SSH, VNC, RDP, etc.)

import asyncio
import websockets
import json
import sys
import subprocess
import signal
import os
import ssl
from typing import Optional

import requests

class MultiProtocolTunnel:
    def __init__(self, manager_url: str, user: str = None, agent_id: Optional[str] = None, 
                 local_port: int = 0, service: str = 'ssh'):
        self.manager_url = manager_url
        self.user = user
        self.target_agent_id = agent_id
        self.local_port = local_port or self._find_free_port()
        self.service = service  # 'ssh', 'vnc', 'rdp', etc.
        self.tunnel_task = None
        self.server = None
        self.client_process = None
        self.active = False
        self.selected_agent = None
        self.relay_url = None

    def _find_free_port(self):
        """Finds a free port automatically"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    async def select_agent(self):
        """Selects an agent from the manager"""
        print(f"📋 Querying Manager at {self.manager_url}...")
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            resp = requests.get(f"{self.manager_url}/manager/v1/public/tunnel/agents", timeout=5, verify=False)
            resp.raise_for_status()
            data = resp.json()
            agents = data.get('agents', [])
        except Exception as e:
            print(f"❌ Error contacting Manager: {e}")
            return None

        if not agents:
            print("❌ No agents available")
            return None

        # If an agent was specified, search for it immediately
        if self.target_agent_id:
            for agent in agents:
                if self.target_agent_id in agent['agent_id']:
                    print(f"\n✅ Agent selected: {agent['hostname']}")
                    return agent
            print(f"❌ Agent {self.target_agent_id} not found in current list")
            # Note: If pagination is active on server, we might miss it.
            return None

        print(f"\n📊 Available Agents ({len(agents)}):")
        for idx, agent in enumerate(agents, 1):
            info = agent.get('info', {})
            services = info.get('available_services', [])
            services_str = f" [{', '.join(services)}]" if services else ""
            print(f"   [{idx}] {agent['hostname']}{services_str}")
            print(f"       ID: {agent['agent_id'][:24]}...")
            print(f"       OS: {info.get('system', 'N/A')} {info.get('architecture', '')}")

        # If there is only one agent, use it automatically
        if len(agents) == 1:
            agent = agents[0]
            print(f"\n✅ Using: {agent['hostname']}")
            return agent

        # Multiple agents: ask for selection
        while True:
            try:
                selection = input(f"\n👉 Select an agent [1-{len(agents)}]: ").strip()
                idx = int(selection) - 1
                if 0 <= idx < len(agents):
                    agent = agents[idx]
                    print(f"✅ Selected: {agent['hostname']}")
                    return agent
                else:
                    print("❌ Invalid number")
            except ValueError:
                print("❌ Enter a valid number")
            except KeyboardInterrupt:
                print("\n❌ Cancelled by user")
                return None

    async def handle_tcp_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handles the TCP tunnel"""
        addr = writer.get_extra_info('peername')
        tunnel_id = f"{addr[0]}:{addr[1]}"

        print(f"🔗 Tunnel established: {tunnel_id}")

        ws = None

        try:
            # Prepare headers for HAProxy sticky sessions
            extra_headers = {}
            if self.selected_agent:
                # X-Agent-ID is critical for HAProxy to route to the correct relay
                extra_headers['X-Agent-ID'] = self.selected_agent['agent_id']
                if 'server_ip' in self.selected_agent:
                    extra_headers['X-Server-IP'] = self.selected_agent['server_ip']

            # Connect to WebSocket (Relay)
            print(f"🔌 Connecting to Relay: {self.relay_url}")
            
            # Prepare connection kwargs
            connect_kwargs = {
                'ping_interval': 20,      # Send ping every 20 seconds
                'ping_timeout': 60,       # Wait up to 60 seconds for pong
                'close_timeout': 10,      # Wait up to 10 seconds for close handshake
                'max_size': 10**7
            }
            
            # Disable SSL verification for wss:// (for testing with self-signed certs)
            if self.relay_url.startswith('wss://'):
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                connect_kwargs['ssl'] = ssl_context
            
            # Try to connect with headers - handle different websockets versions
            if extra_headers:
                try:
                    # Try extra_headers first (older versions)
                    connect_kwargs['extra_headers'] = extra_headers
                    ws = await asyncio.wait_for(
                        websockets.connect(self.relay_url, **connect_kwargs),
                        timeout=5
                    )
                except TypeError as e:
                    if 'extra_headers' in str(e):
                        # Fallback to additional_headers (newer versions)
                        del connect_kwargs['extra_headers']
                        connect_kwargs['additional_headers'] = extra_headers
                        ws = await asyncio.wait_for(
                            websockets.connect(self.relay_url, **connect_kwargs),
                            timeout=5
                        )
                    else:
                        raise
            else:
                ws = await asyncio.wait_for(
                    websockets.connect(self.relay_url, **connect_kwargs),
                    timeout=5
                )

            # Identify as tunnel client
            await ws.send(json.dumps({
                'type': 'connect_client',
                'mode': 'tcp_tunnel'
            }))
            await ws.recv()

            if not self.selected_agent:
                print("❌ No agent selected")
                writer.close()
                await writer.wait_closed()
                return

            agent_id = self.selected_agent['agent_id']

            # Request TCP tunnel with specified service
            await ws.send(json.dumps({
                'type': 'start_tcp_tunnel',
                'agent_id': agent_id,
                'tunnel_id': tunnel_id,
                'service': self.service
            }))

            resp = await asyncio.wait_for(ws.recv(), timeout=10)
            resp_data = json.loads(resp)

            if resp_data.get('type') != 'tunnel_started':
                print(f"❌ Error starting tunnel: {resp_data.get('message')}")
                writer.close()
                await writer.wait_closed()
                return

            # Bidirectional forwarding
            async def tcp_to_ws():
                try:
                    while self.active:
                        data = await reader.read(8192)
                        if not data:
                            break

                        await ws.send(json.dumps({
                            'type': 'tunnel_data',
                            'tunnel_id': tunnel_id,
                            'data': data.hex()
                        }))
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass

            async def ws_to_tcp():
                try:
                    async for msg in ws:
                        if not self.active:
                            break

                        message = json.loads(msg)

                        if message.get('type') == 'tunnel_data':
                            data_hex = message.get('data', '')
                            if data_hex:
                                data = bytes.fromhex(data_hex)
                                writer.write(data)
                                await writer.drain()

                        elif message.get('type') == 'tunnel_closed':
                            break
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass

            await asyncio.gather(
                tcp_to_ws(),
                ws_to_tcp(),
                return_exceptions=True
            )

        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self.active:  # Only show errors if we are still active
                print(f"❌ Error in tunnel: {e}")
        finally:
            # Close WebSocket
            if ws is not None:
                try:
                    if hasattr(ws, 'open') and ws.open:
                        await ws.send(json.dumps({
                            'type': 'close_tunnel',
                            'tunnel_id': tunnel_id
                        }))
                    await ws.close()
                except Exception:
                    pass

            # Close TCP
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def start_tunnel(self):
        """Starts the tunnel server"""
        self.server = await asyncio.start_server(
            self.handle_tcp_client,
            '127.0.0.1',
            self.local_port
        )

        self.active = True
        print(f"✅ Tunnel listening on port {self.local_port}")

    async def stop_tunnel(self):
        """Stops the tunnel server"""
        self.active = False

        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("🔌 Tunnel closed")

    def execute_client(self, extra_command: list = None):
        """Executes the appropriate client according to the service"""
        
        if self.service == 'ssh':
            if not self.user:
                print("❌ User required for SSH")
                return 1
                
            cmd = [
                'ssh',
                '-p', str(self.local_port),
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'LogLevel=ERROR',
                '-o', 'ServerAliveInterval=30',  # Send keep-alive every 30 seconds
                '-o', 'ServerAliveCountMax=3',   # Allow 3 missed keep-alives before disconnect
                '-o', 'TCPKeepAlive=yes',        # Enable TCP keep-alive
                f'{self.user}@127.0.0.1'
            ]
            if extra_command:
                cmd.extend(extra_command)
            print(f"\n🚀 Connecting SSH...")
            
        elif self.service == 'vnc':
            cmd = ['vncviewer', f'localhost:{self.local_port}']
            print(f"\n🖥️  Connecting VNC...")
            
        elif self.service == 'rdp':
            # Modern xfreerdp arguments: /v:server /u:user ...
            cmd = ['xfreerdp', f'/v:localhost:{self.local_port}', '/cert-ignore', '/clipboard', '/sound']
            if self.user:
                cmd.append(f'/u:{self.user}')
            print(f"\n🖥️  Connecting RDP...")
            
        else:
            print(f"⚠️  Service '{self.service}' has no predefined client")
            print(f"   Tunnel available at localhost:{self.local_port}")
            print("   Press Ctrl+C to close...")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                return 0
            return 0

        print(f"   Command: {' '.join(cmd)}\n")
        print("="*70)

        try:
            self.client_process = subprocess.Popen(cmd)
            return self.client_process.wait()
        except KeyboardInterrupt:
            print("\n⚠️  Connection interrupted by user")
            if self.client_process:
                self.client_process.terminate()
            return 1
        except FileNotFoundError:
            print(f"❌ Client {self.service.upper()} not found")
            if self.service == 'vnc':
                print("   👉 Please install a VNC viewer: sudo apt install xtightvncviewer")
            elif self.service == 'rdp':
                print("   👉 Please install FreeRDP: sudo apt install freerdp2-x11")
            return 1

    async def connect(self, extra_command: list = None):
        """Complete flow: select agent, open tunnel, connect client, close tunnel"""

        print("="*70)
        print(f"🔐 Tunnel {self.service.upper()} over WebSocket")
        print("="*70)

        try:
            # 1. Select agent via Manager
            agent = await self.select_agent()
            if not agent:
                return 1

            self.target_agent_id = agent['agent_id']
            self.selected_agent = agent
            
            # 2. Get Relay URL from agent data
            # The agent data contains the relay_url where this specific agent is connected
            self.relay_url = agent.get('relay_url')
            if not self.relay_url:
                # Fallback to server_url from agent if legacy
                self.relay_url = agent.get('server_url')
            
            if not self.relay_url:
                print("❌ Agent has no registered Relay URL")
                return 1
                
            print(f"✅ Route: Client -> {self.relay_url} -> Agent")

            # 3. Start tunnel
            print(f"\n🔧 Starting TCP tunnel on port {self.local_port}...")
            await self.start_tunnel()

            # 4. Give time for tunnel to be ready
            await asyncio.sleep(0.5)

            # 5. Execute client in a separate thread
            loop = asyncio.get_event_loop()
            exit_code = await loop.run_in_executor(
                None,
                self.execute_client,
                extra_command
            )

            print("\n" + "="*70)
            print(f"✅ Session {self.service.upper()} finished")

            return exit_code

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            # 6. Close tunnel on exit
            await self.stop_tunnel()
            print("="*70)


async def main_async():
    import argparse

    parser = argparse.ArgumentParser(
        description='Multi-Protocol Client over WebSocket (SSH, VNC, RDP)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s root                              # SSH as root
  %(prog)s user -a abc-123                   # SSH to specific agent
  %(prog)s root -c "ls -la"                  # Execute remote SSH command
  %(prog)s -t vnc                            # Connect VNC
  %(prog)s -t rdp -u administrator           # Connect RDP
  %(prog)s -t ssh user -m http://localhost:8000  # Custom Manager
        """
    )

    parser.add_argument('user', nargs='?', help='User for SSH/RDP (optional for VNC)')
    parser.add_argument('-t', '--type', default='ssh', choices=['ssh', 'vnc', 'rdp'],
                       help='Service type (ssh, vnc, rdp)')
    parser.add_argument('-a', '--agent', help='Agent ID (or part of ID)')
    parser.add_argument('-m', '--manager', default='http://inv.org', help='Manager API URL')
    parser.add_argument('-p', '--port', type=int, default=0,
                       help='Local port for tunnel (0 = automatic)')
    parser.add_argument('-c', '--command', help='Command to execute remotely (SSH only)')

    args = parser.parse_args()

    # Validate user for SSH
    if args.type == 'ssh' and not args.user:
        parser.error("User required for SSH")

    # Prepare extra command
    extra_command = [args.command] if args.command else None

    # Create and execute tunnel
    tunnel = MultiProtocolTunnel(
        manager_url=args.manager,
        user=args.user,
        agent_id=args.agent,
        local_port=args.port,
        service=args.type
    )

    exit_code = await tunnel.connect(extra_command)
    return exit_code


def main():
    """Main wrapper to handle event loop correctly"""
    try:
        exit_code = asyncio.run(main_async())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n✅ Cancelled by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
