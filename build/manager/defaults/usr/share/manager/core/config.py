from pathlib import Path
import os
import re

ROOT_PATH = "/manager"
API_VERSION = "/v1"

PATH_CERTIFICATES = Path("/mnt/cluster/certificates")
PATH_DATASHARES = Path("/mnt/cluster/datashares")

MAX_TOKEN_AGE_HOURS = 72

FQDN = os.environ["FQDN"]
FQDN_IP = os.environ.get("FQDN_IP", "")
STACK = os.environ["STACK"]

# Proxy settings for builders
HTTP_PROXY = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy", "")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy", "")
NO_PROXY = os.environ.get("NO_PROXY") or os.environ.get("no_proxy", "")

def get_dns_servers() -> list[str]:
    dns_servers = []
    # Try to read resolv.conf inside container to auto-detect DNS servers
    path = Path("/etc/resolv.conf")
    if path.exists():
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if line.startswith("nameserver"):
                    ip = line.split()[1]
                    if not ip.startswith("127."):
                        dns_servers.append(ip)
                elif "ExtServers:" in line:
                    # Parse host DNS servers from Docker comments e.g. '# ExtServers: [host(10.77.158.254)]'
                    ips = re.findall(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}", line)
                    for ip in ips:
                        if not ip.startswith("127."):
                            dns_servers.append(ip)
        except Exception:
            pass
    return dns_servers

# Database
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

# Redis
REDIS_URL = os.environ.get("REDIS_URL")

# Saturation
SYNC_MAX_DB_LATENCY = float(os.environ.get("SYNC_MAX_DB_LATENCY") or 0.5)
SYNC_MAX_CORE_LOAD = float(os.environ.get("SYNC_MAX_CORE_LOAD") or 90.0)
SYNC_QUEUE_PROCESS_INTERVAL = int(os.environ.get("SYNC_QUEUE_PROCESS_INTERVAL") or 30)
SYNC_MAX_CONCURRENCY = int(os.environ.get("SYNC_MAX_CONCURRENCY") or 50)
METRICS_RECORDING_INTERVAL = int(os.environ.get("METRICS_RECORDING_INTERVAL") or 15)
METRICS_RETENTION_LIMIT = int(os.environ.get("METRICS_RETENTION_LIMIT") or (4 * 3600))

CORE_URL = "http://core:8080"
CORE_LOGIN_URL = f"{CORE_URL}/rest-auth/login/"
CORE_USER_URL = f"{CORE_URL}/rest-auth/user/"
CORE_TOKEN_URL = f"{CORE_URL}/api/v1/token"
CORE_AUTH_URL = f"{CORE_URL}/token-auth/"

# MGI (Migasfree Golden Image) build config
MGI_POOL_DIR = PATH_DATASHARES / os.environ["STACK"] / "pool" / "mgi"
MGI_TEMP_DIR = Path("/tmp/mgi-build")
local_templates_dir = PATH_DATASHARES / STACK / "pool" / "project-templates"

MGI_TEMPLATES_GITHUB_URL = "https://raw.githubusercontent.com/migasfree/project-templates/main"

if local_templates_dir.exists() and local_templates_dir.is_dir():
    MGI_TEMPLATES_URL = "http://proxy/pool/project-templates"
else:
    MGI_TEMPLATES_URL = MGI_TEMPLATES_GITHUB_URL

# MCS (Migasfree Clone System) build config
MCS_POOL_DIR = PATH_DATASHARES / os.environ["STACK"] / "pool" / "mcs"
HOST_VOLUME_BASE = Path("/var/lib/docker/volumes/migasfree-swarm/_data")
HOST_STACK_DIR = HOST_VOLUME_BASE / "datashares" / os.environ["STACK"]

