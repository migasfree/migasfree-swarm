
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import redis.asyncio as redis
import websockets
import json
import asyncio
import uuid
import os
import logging
from typing import Dict, List, Optional
from core.config import API_VERSION, FQDN

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_VERSION}/private/tunnel",
    tags=["tunnel"]
)

# Use os.getenv to avoid crash at import time if not set
REDIS_URL = os.getenv('REDIS_URL')

# Templates configuration
templates = Jinja2Templates(directory="/usr/share/manager/templates")

async def get_redis():
    if not REDIS_URL:
        logger.error("REDIS_URL environment variable is not set")
        raise Exception("REDIS_URL not configured")
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


@router.get("/console", response_class=HTMLResponse)
async def tunnel_console(request: Request):
    """Web-based remote access console"""
    return templates.TemplateResponse("tunnel.html", {"request": request})


class AgentRegister(BaseModel):
    agent_id: str
    hostname: str
    info: Dict

@router.post("/register")
async def register_agent(agent: AgentRegister, r: redis.Redis = Depends(get_redis)):
    # Determine Relay URL
    relay_public = None
    try:
        keys = []
        async for key in r.scan_iter("tunnel:*"):
            keys.append(key)
        
        if keys:
            tunnels_data = await r.mget(keys)
            candidates = []
            for t_json in tunnels_data:
                if t_json:
                    try:
                        data = json.loads(t_json)
                        if 'url' in data:
                            candidates.append(data)
                    except json.JSONDecodeError:
                        pass
            
            if candidates:
                # Select relay with minimum load
                # We interpret 'load' as active connections
                candidates.sort(key=lambda x: x.get('load', 0))
                best_relay = candidates[0]
                # Use public URL - HAProxy will handle load balancing with leastconn
                relay_public = best_relay.get('url')
                logger.info(f"Selected best relay: {best_relay.get('hostname')} "
                           f"(load: {best_relay.get('load', 0)}/{best_relay.get('max_connections', 0)}) "
                           f"URL: {relay_public}")

    except Exception as e:
        logger.error(f"Error selecting best relay: {e}")

    # Fallback to default URL if no relay was found in Redis
    if not relay_public:
        relay_public = f'wss://{FQDN}/tunnel'
        logger.warning(f"No relay found in Redis, using fallback: {relay_public}")


    # Store in Redis
    agent_data = agent.dict()
    agent_data['relay_url'] = relay_public 

    # Expiration? Maybe agents should send heartbeats.
    # For now, we just set it.
    await r.set(f"agent:{agent.agent_id}", json.dumps(agent_data))

    logger.info(f"Agent registered: {agent.agent_id} -> {relay_public}")

    return {"relay_url": relay_public}

async def _list_agents(r: redis.Redis, page: int = 1, limit: int = 2, search: str = None) -> Dict:
    """Lists connected agents from Redis with pagination"""
    try:
        # Get all keys first (keys are small, efficient enough for 100k)
        # For production with >1M agents, a secondary index (Redis Search) is recommended.
        all_keys = []
        async for key in r.scan_iter("agent:*"):
            all_keys.append(key)
        
        # Filter keys based on search (Not ideal without index, but functional for now)
        # Note: We can't filter by hostname easily without fetching values. 
        # Strategy: Fetch paginated keys, then load values.
        
        total_count = len(all_keys)
        
        # Calculate slices
        start = (page - 1) * limit
        end = start + limit
        
        # If we have a simple slice without search
        paged_keys = all_keys[start:end]
        
        agents = []
        if paged_keys:
            # MGET only the slice (efficient)
            values = await r.mget(paged_keys)
            for val in values:
                if val:
                    try:
                        agent_data = json.loads(val)
                        # Basic textual search on Client Side (or filtered here if we fetched all)
                        # For true scalability with Search, we need a Redis Index.
                        # Here we just return the paginated chunk.
                        # If 'search' is provided, this pagination strategy breaks because we don't know
                        # which keys contain the search term.
                        # REVISITED STRATEGY for this task:
                        # 1. Ignore text search on backend for now to keep it efficient O(1) page access
                        # 2. Or iterate all keys (slow).
                        # Let's stick to simple pagination for performance.
                        
                        if search:
                             if search.lower() in agent_data.get('hostname', '').lower():
                                 agents.append(agent_data)
                             # Note: Search + Pagination without Index is hard. 
                             # We will fallback to returning the page, and frontend search won't span all pages.
                        else:
                            agents.append(agent_data)
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to decode agent data: {e}")
                        
        return {
            'agents': agents, 
            'total': total_count,
            'page': page,
            'limit': limit
        }
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return {'error': str(e), 'agents': [], 'total': 0}

@router.get("/agents", response_model=Dict)
async def list_agents_endpoint(page: int = 1, limit: int = 2, q: Optional[str] = None, r: redis.Redis = Depends(get_redis)):
    result = await _list_agents(r, page=page, limit=limit, search=q)
    if 'error' in result:
        # Log the error detail
        logger.error(f"Returning 503 due to error: {result['error']}")
        raise HTTPException(status_code=503, detail=f"Redis error: {result['error']}")
    return result

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str, r: redis.Redis = Depends(get_redis)):
    try:
        data = await r.get(f"agent:{agent_id}")
        if not data:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        return json.loads(data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(r: redis.Redis = Depends(get_redis)):
    try:
        result = await _list_agents(r)
        redis_ok = 'error' not in result
        return {
            "status": "healthy" if redis_ok else "degraded",
            "api": "ok",
            "redis": "ok" if redis_ok else "error",
            "connected_agents": len(result.get('agents', []))
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "api": "ok",
            "redis": "error",
            "error": str(e)
        }

@router.websocket("/ws/agents/{agent_id}")
@router.websocket("/ws/agents/{agent_id}")
async def service_websocket(websocket: WebSocket, agent_id: str, service: str = 'ssh', username: str = None):
    """WebSocket endpoint for generic TCP tunneling (SSH/VNC/RDP)"""
    await websocket.accept()
    
    if service not in ['ssh', 'vnc', 'rdp']:
        await websocket.send_json({'error': f'Service {service} not supported'})
        await websocket.close()
        return
    
    if service == 'ssh' and not username:
        username = 'root'  # Default username

    ssh_process = None
    local_server = None
    
    try:
        # 1. Get agent info from Redis (Short-lived connection)
        try:
             client = redis.from_url(REDIS_URL, decode_responses=True)
             try:
                 agent_json = await client.get(f"agent:{agent_id}")
             finally:
                 await client.close()
        except Exception as e:
            logger.error(f"WS: Redis connection failed: {e}")
            await websocket.send_json({'error': 'Internal Service Error (Redis)'})
            await websocket.close()
            return
            
        if not agent_json:
            await websocket.send_json({'error': 'Agent not found'})
            await websocket.close()
            return

        agent_data = json.loads(agent_json)
        hostname = agent_data.get('hostname', 'unknown')
        
        # Get server info for tunnel
        server_ip = agent_data.get('server_ip')
        server_url = agent_data.get('server_url') or agent_data.get('tunnel_url')

        target_url = None
        if server_ip:
            target_url = f"ws://{server_ip}:8080"
        elif server_url:
            target_url = server_url

        if not target_url:
            await websocket.send_json({'error': 'Agent has no server_url/ip registered'})
            await websocket.close()
            return

        logger.info(f"Web Console ({service.upper()}): {username if username else 'N/A'}@{hostname} (agent: {agent_id})")
        logger.info(f"Attempting to connect to relay at: {target_url}")

        # 2. Connect to tunnel relay
        async with websockets.connect(target_url, open_timeout=10, ping_interval=None) as ws_server:
            logger.info(f"Successfully connected to relay: {target_url}")
            
            # Identify as client
            await ws_server.send(json.dumps({'type': 'connect_client'}))
            resp_ident = await ws_server.recv()
            logger.debug(f"Relay identification response: {resp_ident}")

            # Start TCP tunnel
            tunnel_id = f"web-{uuid.uuid4()}"
            await ws_server.send(json.dumps({
                'type': 'start_tcp_tunnel',
                'agent_id': agent_id,
                'tunnel_id': tunnel_id,
                'service': service
            }))

            resp = json.loads(await ws_server.recv())
            if resp.get('type') != 'tunnel_started':
                await websocket.send_json({'error': resp.get('message', 'Failed to start tunnel')})
                return

            if service == 'ssh':
                # --- SSH SPECIFIC LOGIC (PTY + Local Proxy) ---
                
                # ... (Existing SSH logic here, reusing local_server and ssh_process vars) ...
                # Re-implementing explicitly to ensure scope matching
                
                import socket
                import pty
                import subprocess
                import termios
                import struct
                import fcntl

                # Create a local TCP server on random port
                local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                local_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                local_sock.bind(('127.0.0.1', 0))
                local_sock.listen(1)
                local_port = local_sock.getsockname()[1]
                local_server = local_sock # Keep ref for cleanup
                
                logger.info(f"Local SSH proxy listening on port {local_port}")

                master_fd, slave_fd = pty.openpty()
                
                def make_controlling_tty():
                    try:
                        fcntl.ioctl(0, termios.TIOCSCTTY, 1)
                    except Exception:
                        pass

                ssh_cmd = [
                    'ssh', '-tt', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'PreferredAuthentications=password,keyboard-interactive,publickey',
                    '-o', 'ServerAliveInterval=30', '-o', 'ServerAliveCountMax=3',
                    '-p', str(local_port), f'{username}@127.0.0.1'
                ]
                
                ssh_env = os.environ.copy()
                ssh_env['TERM'] = 'xterm-256color'
                ssh_env['LANG'] = 'C.UTF-8'
                ssh_env['LC_ALL'] = 'C.UTF-8'

                ssh_process = subprocess.Popen(
                    ssh_cmd, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
                    start_new_session=True, preexec_fn=make_controlling_tty, close_fds=True, env=ssh_env
                )
                
                os.close(slave_fd)
                fcntl.fcntl(master_fd, fcntl.F_SETFL, os.O_NONBLOCK)

                await websocket.send_json({'status': 'connected', 'tunnel_id': tunnel_id})

                async def accept_and_bridge():
                    loop = asyncio.get_event_loop()
                    client_sock, _ = await loop.sock_accept(local_sock)
                    
                    async def local_to_tunnel():
                        try:
                            while True:
                                data = await loop.sock_recv(client_sock, 4096)
                                if not data: break
                                await ws_server.send(json.dumps({
                                    'type': 'tunnel_data', 'tunnel_id': tunnel_id, 'data': data.hex()
                                }))
                        except Exception: pass
                        finally:
                           try: client_sock.close()
                           except: pass

                    async def tunnel_to_local():
                        try:
                            async for msg in ws_server:
                                msg_json = json.loads(msg)
                                if msg_json.get('type') == 'tunnel_data':
                                    data = bytes.fromhex(msg_json.get('data', ''))
                                    await loop.sock_sendall(client_sock, data)
                                elif msg_json.get('type') == 'tunnel_closed':
                                    break
                        except Exception: pass
                        finally:
                           try: client_sock.close()
                           except: pass

                    await asyncio.gather(local_to_tunnel(), tunnel_to_local(), return_exceptions=True)

                async def pty_to_browser():
                    loop = asyncio.get_event_loop()
                    queue = asyncio.Queue()
                    def reader():
                        try:
                            data = os.read(master_fd, 4096)
                            if data: queue.put_nowait(data)
                            else: queue.put_nowait(None)
                        except Exception: queue.put_nowait(None)
                    
                    loop.add_reader(master_fd, reader)
                    try:
                        while True:
                            data = await queue.get()
                            if data is None: break
                            await websocket.send_json({'type': 'data', 'data': data.hex()})
                    except Exception: pass
                    finally: loop.remove_reader(master_fd)

                async def browser_to_pty():
                    try:
                        while ssh_process.poll() is None:
                            data = await websocket.receive_json()
                            if data.get('type') == 'resize':
                                try:
                                    winsize = struct.pack("HHHH", data.get('rows', 24), data.get('cols', 80), 0, 0)
                                    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
                                except Exception: pass
                                continue
                            
                            hex_data = data.get('data')
                            if hex_data:
                                try: os.write(master_fd, bytes.fromhex(hex_data))
                                except OSError: break
                    except Exception: pass

                # Execute SSH tasks
                bridge_task = asyncio.create_task(accept_and_bridge())
                pty_reader_task = asyncio.create_task(pty_to_browser())
                browser_writer_task = asyncio.create_task(browser_to_pty())

                done, pending = await asyncio.wait(
                    [bridge_task, pty_reader_task, browser_writer_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending: task.cancel()

            else:
                # --- GENERIC TCP PROXY (VNC/RDP) ---
                # Direct bridge: Browser (Binary/JSON) <-> Relay (JSON with hex)
                
                # Notify client connected
                await websocket.send_json({'status': 'connected', 'tunnel_id': tunnel_id})
                
                async def browser_to_tunnel():
                    """Browser WebSocket -> Tunnel Relay"""
                    try:
                        while True:
                            # We accept both text (JSON) and binary (Raw protocol)
                            # noVNC sends binary arraybuffers.
                            message = await websocket.receive()
                            
                            data_to_send = None
                            
                            if "bytes" in message:
                                data = message["bytes"]
                                if data:
                                    data_to_send = data.hex()
                            
                            elif "text" in message:
                                # Sometimes clients might send JSON control messages
                                try:
                                    text_data = message["text"]
                                    json_data = json.loads(text_data)
                                    if 'data' in json_data:
                                        data_to_send = json_data['data'] # Already hex?
                                except:
                                    pass

                            if data_to_send:
                                await ws_server.send(json.dumps({
                                    'type': 'tunnel_data',
                                    'tunnel_id': tunnel_id,
                                    'data': data_to_send
                                }))
                            
                    except Exception as e:
                        logger.debug(f"Browser to tunnel error: {e}")

                async def tunnel_to_browser():
                    """Tunnel Relay -> Browser WebSocket"""
                    try:
                        async for msg in ws_server:
                            try:
                                msg_json = json.loads(msg)
                                if msg_json.get('type') == 'tunnel_data':
                                    hex_data = msg_json.get('data', '')
                                    if hex_data:
                                        data = bytes.fromhex(hex_data)
                                        await websocket.send_bytes(data)
                                elif msg_json.get('type') == 'tunnel_closed':
                                    break
                            except Exception as e:
                                logger.warning(f"Error forwarding to browser: {e}")
                    except Exception as e:
                        logger.debug(f"Tunnel to browser error: {e}")

                # Run VNC tasks
                t_up = asyncio.create_task(browser_to_tunnel())
                t_down = asyncio.create_task(tunnel_to_browser())
                
                done, pending = await asyncio.wait(
                    [t_up, t_down],
                    return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending: task.cancel()

    except Exception as e:
        logger.error(f"Service WebSocket error: {e}", exc_info=True)
        try: await websocket.send_json({'error': str(e)})
        except: pass
    finally:
        # Cleanup
        if ssh_process:
            try: ssh_process.terminate(); ssh_process.wait(timeout=2)
            except: pass
        if local_server:
            try: local_server.close()
            except: pass
        try: await websocket.close()
        except: pass
        logger.info(f"Session ended: {username if username else service}@{hostname}")

