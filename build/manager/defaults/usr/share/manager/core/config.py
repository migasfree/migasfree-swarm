from pathlib import Path
import os

ROOT_PATH = "/manager"
API_VERSION = "/v1"

PATH_CERTIFICATES = Path("/mnt/cluster/certificates")
PATH_DATASHARES = Path("/mnt/cluster/datashares")

MAX_TOKEN_AGE_HOURS = 72

FQDN = os.environ["FQDN"]
FQDN_IP = os.environ.get("FQDN_IP", "")
STACK = os.environ["STACK"]

# Database
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

# Redis
REDIS_URL = os.environ.get("REDIS_URL")

# Saturation
SYNC_MAX_DB_LATENCY = float(os.environ.get("SYNC_MAX_DB_LATENCY", 0.5))
SYNC_MAX_CORE_LOAD = float(os.environ.get("SYNC_MAX_CORE_LOAD", 90.0))
SYNC_QUEUE_PROCESS_INTERVAL = int(os.environ.get("SYNC_QUEUE_PROCESS_INTERVAL", 30))
SYNC_MAX_CONCURRENCY = int(os.environ.get("SYNC_MAX_CONCURRENCY", 50))
METRICS_RECORDING_INTERVAL = int(os.environ.get("METRICS_RECORDING_INTERVAL", 15))
METRICS_RETENTION_LIMIT = int(os.environ.get("METRICS_RETENTION_LIMIT", 4 * 3600))

CORE_URL = "http://core:8080"
CORE_LOGIN_URL = f"{CORE_URL}/rest-auth/login/"
CORE_USER_URL = f"{CORE_URL}/rest-auth/user/"
CORE_TOKEN_URL = f"{CORE_URL}/api/v1/token"
CORE_AUTH_URL = f"{CORE_URL}/token-auth/"

# MCI (Migasfree Clone Image) build config
MCI_POOL_DIR = PATH_DATASHARES / os.environ["STACK"] / "pool" / "mci"
MCI_TEMP_DIR = Path("/tmp/mci-build")
MCI_PREFIX = os.environ.get("MCI_PREFIX", "mci")
local_templates_dir = PATH_DATASHARES / STACK / "pool" / "mci-templates"

if local_templates_dir.exists() and local_templates_dir.is_dir():
    MCI_TEMPLATES_URL = "http://proxy/pool/mci-templates"
else:
    MCI_TEMPLATES_URL = "https://raw.githubusercontent.com/migasfree/mci-templates/main"

# MCS (Migasfree Clone System) build config
MCS_POOL_DIR = PATH_DATASHARES / os.environ["STACK"] / "pool" / "mcs"
HOST_VOLUME_BASE = Path("/var/lib/docker/volumes/migasfree-swarm/_data")
HOST_STACK_DIR = HOST_VOLUME_BASE / "datashares" / os.environ["STACK"]

