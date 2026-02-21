import json
import logging
import socket
import time
import requests
import urllib3
import os

import asyncio
import msgpack
import websockets

from core.config import (
    SYNC_MAX_DB_LATENCY,
    SYNC_MAX_CORE_LOAD,
    SYNC_MAX_CONCURRENCY,
    SYNC_QUEUE_PROCESS_INTERVAL,
    METRICS_RECORDING_INTERVAL,
    METRICS_RETENTION_LIMIT,
    ROOT_PATH,
    API_VERSION,
    POSTGRES_HOST,
)
from core.database import get_db_connection
from core.redis import get_redis_connection

# Disable warning for self-signed certs just in case, though we use http internal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

PORTAINER_URL = "http://portainer:9000/api"
PORTAINER_TOKEN_FILE = "/mnt/cluster/credentials/portainer-token"

_portainer_endpoint_id = None
_prev_stats_cache = {}  # {container_id: {'cpu': val, 'system': val}}


def get_portainer_headers():
    try:
        if not os.path.exists(PORTAINER_TOKEN_FILE):
            logger.error(f"Portainer token not found at {PORTAINER_TOKEN_FILE}")
            return None
        with open(PORTAINER_TOKEN_FILE, "r") as f:
            token = f.read().strip()
        return {"X-API-Key": token}
    except Exception as e:
        logger.error(f"Error reading Portainer token: {e}")
        return None


def get_portainer_endpoint_id(headers):
    global _portainer_endpoint_id
    if _portainer_endpoint_id:
        return _portainer_endpoint_id

    try:
        # We look for the primary endpoint. Usually there is only one in this setup or it's named 'primary'
        resp = requests.get(f"{PORTAINER_URL}/endpoints", headers=headers, timeout=5)
        if resp.status_code == 200:
            endpoints = resp.json()
            # Heuristic: pick the first Swarm/Docker endpoint
            for ep in endpoints:
                # Type 1=Docker, 2=Agent
                if ep.get("Type") in [1, 2]:
                    _portainer_endpoint_id = ep["Id"]
                    return _portainer_endpoint_id
    except Exception as e:
        logger.error(f"Error getting Portainer endpoints: {e}")
    return None


def get_service_cpu_load_via_portainer(service_suffix):
    """
    Calculate CPU load for containers of a service using Portainer API.
    Returns a dict: {'avg': float, 'nodes': {ip: load, ...}}
    """
    global _prev_stats_cache
    result = {"avg": 0.0, "nodes": {}}

    headers = get_portainer_headers()
    if not headers:
        return result
    endpoint_id = get_portainer_endpoint_id(headers)
    if not endpoint_id:
        return result

    try:
        # 1. Fetch Swarm Nodes to map NodeId -> HostIP
        nodes_map = {}
        try:
            nodes_resp = requests.get(
                f"{PORTAINER_URL}/endpoints/{endpoint_id}/docker/nodes",
                headers=headers,
                timeout=5,
            )
            if nodes_resp.status_code == 200:
                for n in nodes_resp.json():
                    nid = n.get("ID")
                    # 'Addr' is the typically reachable IP of the node in Swarm
                    ip = n.get("Status", {}).get("Addr")
                    # 'Hostname' is needed for X-PortainerAgent-Target
                    hostname = n.get("Description", {}).get("Hostname")
                    if nid and ip:
                        nodes_map[nid] = {"ip": ip, "hostname": hostname}
        except Exception as ne:
            logger.warning(f"Could not fetch Swarm nodes from Portainer: {ne}")

        # 2. Fetch containers
        filters = {"label": ["com.docker.swarm.service.name"]}
        resp = requests.get(
            f"{PORTAINER_URL}/endpoints/{endpoint_id}/docker/containers/json",
            headers=headers,
            params={"filters": json.dumps(filters), "status": "running"},
            timeout=10,
        )
        if resp.status_code != 200:
            logger.error(
                f"Portainer containers list failed: {resp.status_code} {resp.text}"
            )
            return result

        containers = resp.json()
        target_containers = []
        for c in containers:
            svc_name = c["Labels"].get("com.docker.swarm.service.name", "")
            if svc_name.endswith(service_suffix):
                target_containers.append(c)

        if not target_containers:
            return result

        total_load = 0.0
        valid_samples = 0

        for container in target_containers:
            cid = container["Id"]
            labels = container.get("Labels", {})
            node_id = labels.get("com.docker.swarm.node.id")

            # Map container to an IP and Hostname
            node_info = nodes_map.get(node_id, {})
            node_ip = node_info.get("ip") if isinstance(node_info, dict) else node_info
            node_hostname = (
                node_info.get("hostname") if isinstance(node_info, dict) else None
            )

            if not node_ip:
                networks = container.get("NetworkSettings", {}).get("Networks", {})
                for net_name in ["inv_network", "infra_network"]:
                    if net_name in networks:
                        node_ip = networks[net_name].get("IPAddress")
                        break
                if not node_ip and networks:
                    node_ip = next(iter(networks.values())).get("IPAddress")

            try:
                # Add target header for cross-node stats proxying
                stats_headers = headers.copy()
                if node_hostname:
                    stats_headers["X-PortainerAgent-Target"] = node_hostname

                stats_resp = requests.get(
                    f"{PORTAINER_URL}/endpoints/{endpoint_id}/docker/containers/{cid}/stats?stream=false",
                    headers=stats_headers,
                    timeout=5,
                )
                if stats_resp.status_code != 200:
                    continue

                stats = stats_resp.json()

                # Resilient check: ensure we have the necessary stats keys
                if not isinstance(stats, dict) or "cpu_stats" not in stats:
                    continue

                cpu_usage_data = stats["cpu_stats"].get("cpu_usage", {})
                cpu_usage = cpu_usage_data.get("total_usage")
                system_usage = stats["cpu_stats"].get("system_cpu_usage")

                if cpu_usage is None or system_usage is None:
                    continue

                online_cpus = stats["cpu_stats"].get("online_cpus")
                if not online_cpus:
                    per_cpu = cpu_usage_data.get("percpu_usage")
                    online_cpus = len(per_cpu) if per_cpu else 1

                if cid in _prev_stats_cache:
                    prev = _prev_stats_cache[cid]
                    cpu_delta = cpu_usage - prev["cpu"]
                    system_delta = system_usage - prev["system"]

                    if system_delta > 0 and cpu_delta >= 0:
                        current_load = (cpu_delta / system_delta) * online_cpus * 100.0
                        total_load += current_load
                        valid_samples += 1
                        if node_ip:
                            # Store the CPU load associated with the host IP
                            result["nodes"][node_ip] = current_load
                else:
                    pass  # Container not in cache yet, no load calculation for this cycle

                _prev_stats_cache[cid] = {"cpu": cpu_usage, "system": system_usage}
            except Exception:
                continue

        # Clean cache of old containers? optional.
        # For simplicity, we just keep growing/updating. Redis restart clears it anyway.

        if valid_samples > 0:
            result["avg"] = total_load / valid_samples

    except Exception as e:
        logger.error(f"Error calculating stats via Portainer for {service_suffix}: {e}")

    return result


def get_saturation_metrics():
    """
    Get server saturation metrics (DB latency and CPU load) from Redis cache.
    Returns default values if cache is empty.
    """
    hostname = socket.gethostname()
    host_value = (os.environ.get("POSTGRES_HOST") or "").strip()
    key = "manager:metric:actual"
    con = get_redis_connection()

    # Try to get cached metrics for this host
    data = con.hgetall(key)
    if data:
        metrics = {
            "host": hostname,
            "ts": float(data.get("ts", time.time())),
            "saturated": data.get("saturated") == "1",
            "db_latency": float(data.get("db_latency", 0)),
            "core_cpu": float(data.get("core_cpu", 0)),
            "db_cpu": float(data.get("db_cpu", 0)),
            "queued": int(data.get("queued", 0)),
            "cluster_nodes": json.loads(data.get("cluster_nodes", "[]")),
            "is_pgpool": host_value == "pgpool",
        }
        return metrics

    # Return default "safe" values if no data yet (or saturated to be safe?)
    # If no data, we assume not saturated or wait for background task.
    # Here we return a safe default to avoid breaking callers, but log it.
    logger.warning("No saturation metrics found in Redis. Returning defaults.")
    return {
        "host": hostname,
        "saturated": False,
        "db_latency": 0.0,
        "core_cpu": 0.0,
        "db_cpu": 0.0,
        "cluster_nodes": [],
    }


def increment_sync_attempt():
    """
    Increment the sync attempt counter in Redis.
    """
    key = "manager:metric:actual"
    con = get_redis_connection()
    con.hincrby(key, "attempts", 1)


def get_sync_attempts():
    """
    Get the sync attempt counter from Redis.
    """
    con = get_redis_connection()
    return int(con.hget("manager:metric:actual", "attempts") or 0)


def is_server_saturated():
    """
    Check if the server is saturated based on DB latency and CPU load.
    Returns True if saturated, False otherwise.
    """
    metrics = get_saturation_metrics()
    return metrics["saturated"]


def refresh_server_metrics():
    """
    Calculate metrics, update current state, and append to history.
    """
    history_key = "manager:metric:history"
    key = "manager:metric:actual"

    # 0. Get previous metrics to calculate rates
    prev_metrics = get_saturation_metrics()
    prev_nodes = {node["id"]: node for node in prev_metrics.get("cluster_nodes", [])}
    now_ts = time.time()
    elapsed = now_ts - prev_metrics.get("ts", now_ts - 10)  # Fallback to 10s if no ts
    if elapsed <= 0:
        elapsed = 10

    con = get_redis_connection()

    # 1. Check Postgres latency
    start_time = time.time()
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        db_latency = time.time() - start_time
    except Exception:
        db_latency = 999.0

    # 2. Check Swarm CPU Load (Distributed via Portainer)
    core_stats = get_service_cpu_load_via_portainer("_core")
    load_percentage = core_stats["avg"]

    # 3. Check Database CPU Load (Distributed via Portainer)
    db_stats = get_service_cpu_load_via_portainer("_database")
    db_load_percentage = db_stats["avg"]
    db_node_loads = db_stats["nodes"]

    saturated = db_latency > SYNC_MAX_DB_LATENCY or load_percentage > SYNC_MAX_CORE_LOAD

    # 4. Check Pgpool-II Nodes status (if using pgpool)
    cluster_nodes = []
    host_value = (POSTGRES_HOST or "").strip()
    if host_value == "pgpool":
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 1. Get cluster status and replication delay
                    cursor.execute("SHOW pool_nodes")
                    cols_nodes = [desc[0] for desc in cursor.description]
                    node_data = {}
                    for row in cursor.fetchall():
                        d = dict(zip(cols_nodes, row))
                        node_data[str(d.get("node_id"))] = d

                    # 2. Get detailed stats for counters
                    cursor.execute("SHOW pool_backend_stats")
                    cols_stats = [desc[0] for desc in cursor.description]
                    for row in cursor.fetchall():
                        s = dict(zip(cols_stats, row))
                        nid = str(s.get("node_id"))
                        if nid in node_data:
                            node_data[nid].update(s)

                    for nid, node in node_data.items():
                        node_id = nid

                        # Helper to get value from dict with case-insensitive and fuzzy match fallback
                        def get_cnt(d, *search_terms):
                            for term in search_terms:
                                term_lower = term.lower()
                                # 1. Try exact/case-insensitive match
                                for dk in d:
                                    if dk.lower() == term_lower:
                                        return int(d[dk] or 0)
                                # 2. Try fuzzy match (if column contains the term)
                                for dk in d:
                                    if term_lower in dk.lower():
                                        return int(d[dk] or 0)
                            return 0

                        current_selects = get_cnt(node, "select_cnt", "select")
                        current_writes = (
                            get_cnt(node, "insert_cnt", "insert")
                            + get_cnt(node, "update_cnt", "update")
                            + get_cnt(node, "delete_cnt", "delete")
                            + get_cnt(node, "ddl_cnt", "ddl")
                            + get_cnt(node, "copy_cnt", "copy")
                        )
                        current_errors = get_cnt(node, "error_cnt", "error")

                        prev_selects = prev_nodes.get(node_id, {}).get(
                            "select_cnt", current_selects
                        )
                        prev_writes = prev_nodes.get(node_id, {}).get(
                            "write_cnt", current_writes
                        )
                        prev_errors = prev_nodes.get(node_id, {}).get(
                            "error_cnt", current_errors
                        )

                        # Delta calculation (handle resets)
                        delta_sel = max(0, current_selects - prev_selects)
                        delta_wri = max(0, current_writes - prev_writes)
                        delta_err = max(0, current_errors - prev_errors)

                        select_qpm = (delta_sel / elapsed) * 60
                        write_wpm = (delta_wri / elapsed) * 60
                        error_epm = (delta_err / elapsed) * 60

                        node_ip = node.get("hostname")
                        node_cpu = db_node_loads.get(node_ip)

                        cluster_nodes.append(
                            {
                                "id": node_id,
                                "host": node_ip,
                                "status": node.get("status"),
                                "role": node.get("role"),
                                "cpu_load": round(node_cpu, 1)
                                if node_cpu is not None
                                else None,
                                "select_cnt": current_selects,
                                "write_cnt": current_writes,
                                "error_cnt": current_errors,
                                "select_qpm": round(select_qpm, 2),
                                "write_wpm": round(write_wpm, 2),
                                "error_epm": round(error_epm, 2),
                                "replication_delay": int(
                                    node.get("replication_delay", 0)
                                ),
                            }
                        )
        except Exception as e:
            logger.warning(f"Could not fetch Pgpool nodes status: {e}")

    # 5. Get and reset counters (attempts)
    pipe = con.pipeline()
    pipe.hget(key, "attempts")
    pipe.hset(key, "attempts", 0)

    res = pipe.execute()
    sync_attempts = int(res[0] or 0)

    # 6. Update Current State (Actual)
    # We do NOT use expiration here anymore as per request
    con.hset(
        key,
        mapping={
            "ts": now_ts,
            "saturated": 1 if saturated else 0,
            "db_latency": db_latency,
            "core_cpu": load_percentage,
            "db_cpu": db_load_percentage,
            "cluster_nodes": json.dumps(cluster_nodes),
        },
    )

    # 7. Add to history (ZSET)
    history_entry = {
        "ts": now_ts,
        "saturated": 1 if saturated else 0,
        "db_latency": db_latency,
        "core_cpu": load_percentage,
        "db_cpu": db_load_percentage,
        "attempts": sync_attempts,
        "cluster_nodes": cluster_nodes,  # Store as list in history
    }

    pipe = con.pipeline()
    pipe.zadd(history_key, {json.dumps(history_entry): now_ts})

    # Trim history (keep last 4 hours)
    retention_limit = now_ts - METRICS_RETENTION_LIMIT
    pipe.zremrangebyscore(history_key, "-inf", retention_limit)

    pipe.execute()


def get_metrics_from_history(limit=1000):
    """
    Get historical metrics from Redis.
    Returns a list of dicts.
    """
    con = get_redis_connection()
    history_key = "manager:metric:history"

    # Get all elements (we rely on trimming to keep size manageable)
    # or just last 'limit'
    items = con.zrange(history_key, 0, -1)

    result = []
    for item in items:
        if isinstance(item, bytes):
            item = item.decode("utf-8")
        try:
            result.append(json.loads(item))
        except json.JSONDecodeError:
            pass

    return result


def _send_to_group(group_name, payload):
    """
    Send a message to a Django Channels group using Redis.
    Mimics channels_redis protocol (ASGI).
    """
    con = get_redis_connection()
    # 1. Get channel names from the group ZSET
    # Key: asgi:group:<group_name>
    group_key = f"asgi:group:{group_name}"

    # Check expiry/existence of group
    if not con.exists(group_key):
        return

    # Get all members
    channels = con.zrange(group_key, 0, -1)

    if not channels:
        return

    # Serialize payload with msgpack
    message = msgpack.packb(payload)

    # 2. Send to each channel
    pipe = con.pipeline()
    for channel in channels:
        channel_str = channel.decode("utf-8") if isinstance(channel, bytes) else channel
        # Push to channel list
        # Key: asgi:channel:<channel_name> (usually list)
        channel_key = f"asgi:channel:{channel_str}"
        pipe.rpush(channel_key, message)
        pipe.expire(channel_key, 60)

    # Refresh group expiry
    pipe.expire(group_key, 86400)
    pipe.execute()


def process_sync_queue():
    """
    Process the sync queue with adaptive concurrency.
    """
    metrics = get_saturation_metrics()
    if metrics["saturated"]:
        return

    try:
        con = get_redis_connection()
        limit = SYNC_MAX_CONCURRENCY
        max_load = SYNC_MAX_CORE_LOAD

        # Adaptive Batch Sizing
        current_load = metrics["core_cpu"]
        utilization_ratio = current_load / max_load if max_load > 0 else 1.0
        capacity_factor = 1.0 - utilization_ratio
        capacity_factor = max(0.0, min(1.0, capacity_factor))

        batch_size = int(limit * capacity_factor)
        batch_size = max(1, batch_size) if capacity_factor > 0.05 else 0

        if batch_size > 0:
            logger.debug(
                f"Sync Queue: Processing {batch_size} clients (Load: {current_load:.1f}%)"
            )

        cids_to_sync = []
        count = 0
        while count < batch_size:
            uuid = con.lpop("manager:sync_queue")
            if not uuid:
                break

            if isinstance(uuid, bytes):
                uuid = uuid.decode("utf-8")

            cid = get_cid_from_uuid(uuid)

            if cid:
                cids_to_sync.append(cid)
            else:
                logger.warning(f"Could not resolve CID for UUID: {uuid}")

            count += 1

        if cids_to_sync:
            try:
                logger.info(
                    f"Triggering sync for {len(cids_to_sync)} clients in parallel"
                )
                asyncio.run(trigger_batch_sync(cids_to_sync))
            except Exception as e:
                logger.error(f"Error triggering batch sync: {e}")

    except Exception as e:
        logger.error(f"Error processing sync queue: {e}")


async def trigger_batch_sync(cids):
    """
    Triggers sync for a list of CIDs in parallel.
    """
    tasks = [trigger_sync_via_websocket(cid) for cid in cids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for cid, result in zip(cids, results):
        if isinstance(result, Exception):
            logger.error(f"Error triggering sync for CID {cid}: {result}")
        else:
            logger.info(f"Sync triggered for CID {cid} via WebSocket")


async def trigger_sync_via_websocket(cid):
    """
    Connects to the tunnel WebSocket as an admin and executes 'migasfree sync'.
    """
    url = f"ws://127.0.0.1:8080{ROOT_PATH}{API_VERSION}/private/tunnel/ws/agents/{cid}?service=exec"

    # We must provide the generic Admin CN to pass the check in tunnels.py
    headers = {"X-SSL-Client-CN": "CN=manager,OU=ADMINS,O=migasfree,C=ES"}

    async with websockets.connect(url, additional_headers=headers) as ws:
        logger.debug(f"Connected to WebSocket: {url}")

        # Send execute command
        # "type": "execute_command", "command": "migasfree sync"
        payload = {"type": "execute_command", "command": "migasfree sync"}
        await ws.send(json.dumps(payload))
        logger.debug(f"Sent command payload to {cid}")

        # Wait for completion or timeout
        # We expect a "command_complete" or "command_error" message
        try:
            async for message in ws:
                msg = json.loads(message)
                logger.debug(f"Received WS message from {cid}: {msg}")
                if msg.get("type") == "command_complete":
                    return True
                elif msg.get("type") == "command_error":
                    raise Exception(f"Command Error: {msg.get('error')}")
                # We can ignore 'output' messages unless we want to log them
        except Exception as e:
            # If connection closes we might get here
            raise e


def get_cid_from_uuid(uuid):
    """
    Get Computer ID (CID) from UUID.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM public.client_computer WHERE uuid = %s", (uuid,)
                )
                res = cursor.fetchone()
                if res:
                    return res[0]
    except Exception as e:
        logger.error(f"Error getting CID from UUID {uuid}: {e}")
    return None


_background_tasks = []


async def _metrics_loop():
    while True:
        try:
            # Run blocking I/O in executor
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, refresh_server_metrics)
        except Exception as e:
            logger.error(f"Error recording metrics: {e}")
        await asyncio.sleep(METRICS_RECORDING_INTERVAL)


async def _queue_loop():
    while True:
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, process_sync_queue)
        except Exception as e:
            logger.error(f"Error in queue loop: {e}")
        await asyncio.sleep(SYNC_QUEUE_PROCESS_INTERVAL)


def start_recording():
    """Starts background tasks (metrics and queue processing)"""
    global _background_tasks
    if not _background_tasks:
        _background_tasks.append(asyncio.create_task(_metrics_loop()))
        _background_tasks.append(asyncio.create_task(_queue_loop()))
        logger.info("Started background tasks")


async def stop_recording():
    """Stops background tasks"""
    global _background_tasks
    for task in _background_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    _background_tasks = []
    logger.info("Stopped background tasks")
