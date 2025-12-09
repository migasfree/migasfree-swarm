
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Request
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
    prefix=f"{API_VERSION}/public/tunnel",  # TODO private
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
    return redis.from_url(REDIS_URL, decode_responses=True)


@router.get("/console", response_class=HTMLResponse)
async def tunnel_console(request: Request):
    """Web-based remote access console"""
    return templates.TemplateResponse("tunnel.html", {"request": request})


class AgentRegister(BaseModel):
    agent_id: str
    hostname: str
    info: Dict

@router.post("/register")
async def register_agent(agent: AgentRegister):
    try:
        r = await get_redis()
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable (Redis)")

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
    await r.close()

    logger.info(f"Agent registered: {agent.agent_id} -> {relay_public}")

    return {"relay_url": relay_public}

async def _list_agents(page: int = 1, limit: int = 2, search: str = None) -> Dict:
    """Lists connected agents from Redis with pagination"""
    try:
        r = await get_redis()
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return {'error': str(e), 'agents': [], 'total': 0}

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
    finally:
        await r.close()

@router.get("/agents", response_model=Dict)
async def list_agents_endpoint(page: int = 1, limit: int = 2, q: Optional[str] = None):
    result = await _list_agents(page=page, limit=limit, search=q)
    if 'error' in result:
        # Log the error detail
        logger.error(f"Returning 503 due to error: {result['error']}")
        raise HTTPException(status_code=503, detail=f"Redis error: {result['error']}")
    return result

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    try:
        r = await get_redis()
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service Unavailable (Redis)")

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
    finally:
        await r.close()

@router.get("/health")
async def health_check():
    try:
        result = await _list_agents()
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
async def ssh_websocket(websocket: WebSocket, agent_id: str, service: str = 'ssh', username: str = None):
    """WebSocket endpoint for interactive SSH terminal sessions through tunnel with PTY"""
    await websocket.accept()
    
    # Only SSH is supported for now
    if service != 'ssh':
        await websocket.send_json({'error': f'Service {service} not yet supported in web console'})
        await websocket.close()
        return
    
    if not username:
        username = 'root'  # Default username

    try:
        r = await get_redis()
    except Exception as e:
        logger.error(f"WS: Redis connection failed: {e}")
        await websocket.send_json({'error': 'Internal Service Error (Redis)'})
        await websocket.close()
        return

    ssh_process = None
    local_server = None
    tunnel_task = None

    try:
        # 1. Get agent info from Redis
        agent_json = await r.get(f"agent:{agent_id}")
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

        logger.info(f"SSH Web Console: {username}@{hostname} (agent: {agent_id})")
        logger.info(f"Attempting to connect to relay at: {target_url}")

        # 2. Connect to tunnel relay and establish TCP tunnel
        # Added timeouts to fail faster and clearer logs
        async with websockets.connect(target_url, open_timeout=10, ping_interval=None) as ws_server:
            logger.info(f"Successfully connected to relay: {target_url}")
            
            # Identify as client
            await ws_server.send(json.dumps({'type': 'connect_client'}))
            resp_ident = await ws_server.recv()
            logger.debug(f"Relay identification response: {resp_ident}")

            # Start TCP tunnel to SSH port
            tunnel_id = f"web-{uuid.uuid4()}"
            await ws_server.send(json.dumps({
                'type': 'start_tcp_tunnel',
                'agent_id': agent_id,
                'tunnel_id': tunnel_id,
                'service': 'ssh'
            }))

            resp = json.loads(await ws_server.recv())
            if resp.get('type') != 'tunnel_started':
                await websocket.send_json({'error': resp.get('message', 'Failed to start tunnel')})
                return

            # 3. Create local TCP server that bridges to WebSocket tunnel
            import socket
            import pty
            import subprocess
            import select
            import termios
            import struct
            import fcntl

            # Create a local TCP server on random port
            local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            local_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            local_sock.bind(('127.0.0.1', 0))
            local_sock.listen(1)
            local_port = local_sock.getsockname()[1]
            
            logger.info(f"Local SSH proxy listening on port {local_port}")

            # 4. Start SSH client process with PTY
            import os
            master_fd, slave_fd = pty.openpty()
            
            # Helper function to set controlling terminal
            def make_controlling_tty():
                # TIOCSCTTY = 0x540E
                try:
                    # Setsid is already called by start_new_session=True, 
                    # but we need to acquire the PTY as controlling terminal.
                    # On Linux, the first TTY opened by a session leader becomes its ctty,
                    # but since we inherit fds, we might need to force it.
                    # FD 0 is already the slave PTY because of Popen's stdin argument
                    fcntl.ioctl(0, termios.TIOCSCTTY, 1)
                except Exception:
                    pass

            # SSH command
            ssh_cmd = [
                'ssh',
                '-tt',  # Force pseudo-terminal usage
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'PreferredAuthentications=password,keyboard-interactive,publickey',
                '-o', 'ServerAliveInterval=30',
                '-o', 'ServerAliveCountMax=3',
                '-p', str(local_port),
                f'{username}@127.0.0.1'
            ]
            
            # Prepare environment with TERM and Locale settings
            ssh_env = os.environ.copy()
            ssh_env['TERM'] = 'xterm-256color'
            ssh_env['LANG'] = 'C.UTF-8'
            ssh_env['LC_ALL'] = 'C.UTF-8'

            # Start SSH process in background
            ssh_process = subprocess.Popen(
                ssh_cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                start_new_session=True, # Setsid
                preexec_fn=make_controlling_tty, # Force CTTY
                close_fds=True,
                env=ssh_env
            )
            
            os.close(slave_fd)  # Close slave in parent
            
            # Set master to non-blocking
            fcntl.fcntl(master_fd, fcntl.F_SETFL, os.O_NONBLOCK)

            # Send connection established
            await websocket.send_json({'status': 'connected', 'tunnel_id': tunnel_id})

            # 5. Accept SSH connection and bridge to WebSocket tunnel
            async def accept_and_bridge():
                """Accept local SSH connection and bridge to WebSocket tunnel"""
                loop = asyncio.get_event_loop()
                
                # Wait for SSH to connect
                client_sock, _ = await loop.sock_accept(local_sock)
                logger.info("SSH client connected to local proxy")
                
                async def local_to_tunnel():
                    """Forward data from local SSH client to WebSocket tunnel"""
                    try:
                        while True:
                            data = await loop.sock_recv(client_sock, 4096)
                            if not data:
                                break
                            
                            hex_data = data.hex()
                            await ws_server.send(json.dumps({
                                'type': 'tunnel_data',
                                'tunnel_id': tunnel_id,
                                'data': hex_data
                            }))
                    except Exception as e:
                        logger.debug(f"Local to tunnel closed: {e}")
                    finally:
                        try:
                            client_sock.close()
                        except:
                            pass

                async def tunnel_to_local():
                    """Forward data from WebSocket tunnel to local SSH client"""
                    try:
                        async for msg in ws_server:
                            msg_json = json.loads(msg)
                            
                            if msg_json.get('type') == 'tunnel_data':
                                hex_data = msg_json.get('data', '')
                                data = bytes.fromhex(hex_data)
                                await loop.sock_sendall(client_sock, data)
                            elif msg_json.get('type') == 'tunnel_closed':
                                break
                    except Exception as e:
                        logger.debug(f"Tunnel to local closed: {e}")
                    finally:
                        try:
                            client_sock.close()
                        except:
                            pass

                await asyncio.gather(
                    local_to_tunnel(),
                    tunnel_to_local(),
                    return_exceptions=True
                )

            # 6. Proxy PTY I/O to browser WebSocket
            async def pty_to_browser():
                """Read from PTY and send to browser"""
                loop = asyncio.get_event_loop()
                try:
                    while ssh_process.poll() is None:
                        # Use select to wait for data
                        ready, _, _ = select.select([master_fd], [], [], 0.1)
                        if ready:
                            try:
                                data = os.read(master_fd, 4096)
                                if data:
                                    hex_data = data.hex()
                                    await websocket.send_json({
                                        'type': 'data',
                                        'data': hex_data
                                    })
                            except OSError:
                                break
                        await asyncio.sleep(0.01)
                except Exception as e:
                    logger.debug(f"PTY to browser closed: {e}")

            async def browser_to_pty():
                """Read from browser and write to PTY"""
                try:
                    while ssh_process.poll() is None:
                        data = await websocket.receive_json()
                        
                        # Handle resize events
                        if data.get('type') == 'resize':
                            try:
                                cols = data.get('cols', 80)
                                rows = data.get('rows', 24)
                                # TIOCSWINSZ = 0x5414
                                import fcntl
                                import struct
                                import termios
                                winsize = struct.pack("HHHH", rows, cols, 0, 0)
                                fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
                                # Also update SSH client window size if possible? 
                                # The PTY resize should propagate to SSH client automatically via SIGWINCH
                            except Exception as e:
                                logger.error(f"Error resizing PTY: {e}")
                            continue

                        # Handle data events
                        hex_data = data.get('data')
                        if hex_data:
                            try:
                                bytes_data = bytes.fromhex(hex_data)
                                os.write(master_fd, bytes_data)
                            except OSError:
                                break
                except Exception as e:
                    logger.debug(f"Browser to PTY closed: {e}")

            # Run all tasks concurrently
            await asyncio.gather(
                accept_and_bridge(),
                pty_to_browser(),
                browser_to_pty(),
                return_exceptions=True
            )

    except Exception as e:
        logger.error(f"SSH WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({'error': str(e)})
        except:
            pass
    finally:
        # Cleanup
        if ssh_process:
            try:
                ssh_process.terminate()
                ssh_process.wait(timeout=2)
            except:
                try:
                    ssh_process.kill()
                except:
                    pass
        if local_server:
            try:
                local_server.close()
            except:
                pass
        try:
            await websocket.close()
        except:
            pass
        logger.info(f"SSH Web Console session ended: {username}@{hostname}")

