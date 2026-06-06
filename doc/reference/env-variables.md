# Configuration Variables

This document provides a comprehensive reference of all configuration variables.

> [!NOTE]
> There are two levels of configuration files:
>
> 1. **Cluster level** (`/etc/migasfree-swarm/cluster.conf`): Configuration for storage and shared infrastructure.
> 2. **Stack level** (`/mnt/cluster/datashares/<stack_name>/stack.conf`): Configuration specific to each deployed stack.

---

## 🏗️ Cluster Configuration Variables

These variables are defined during the cluster initialization and affect the entire infrastructure.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATASHARE_FS` | Volume type: `local` (single node) or `nfs` (multi-node). | `local` |
| `DATASHARE_SERVER` | IP address or FQDN of the NFS server (Required if `DATASHARE_FS=nfs`). | `x.x.x.x` |
| `DATASHARE_PATH` | Exported path on the NFS server. | `/exports/migasfree-swarm` |
| `DATASHARE_PORT` | Port for the NFS service. | `2049` |

---

## 🚀 Stack Configuration Variables

These variables customize the behavior of a specific Migasfree stack.

### 🌐 General & Networking

| Variable | Description | Default |
| :--- | :--- | :--- |
| `FQDN` | Fully Qualified Domain Name for the stack access. | `migasfree.acme.com` |
| `TZ` | System time zone for all containers. | `Europe/Madrid` |
| `PORT_HTTP` | Port where the cluster serves HTTP traffic. | `80` |
| `PORT_HTTPS` | Port where the cluster serves HTTPS traffic. | `443` |
| `NETWORK_MNG` | Networks/hosts allowed to access administrative consoles. Space-separated List. | `127.0.0.1` |
| `NETWORK_MCP` | Networks/hosts allowed to access the MCP server (Model Context Protocol). | `127.0.0.1` |
| `RATE_LIMIT` | Max request rate per 10s from a single IP and URL to prevent DDoS. | `100` |

### 🔒 SSL/TLS & Authentication

| Variable | Description | Options |
| :--- | :--- | :--- |
| `HTTPSMODE` | Certificate generation mode. | `manual` (self-signed) / `auto` (Let's Encrypt) |
| `MTLS` | Enforce Mutual TLS (client certificates) for console access. | `True` / `False` |

### 📁 Database (PostgreSQL)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `POSTGRES_HOST` | Database host. Use `pgpool` for HA, `database` for direct, or an IP for external. | `pgpool` |
| `POSTGRES_PORT` | Internal port for PostgreSQL/Pgpool. | `5432` |
| `PORT_DATABASE` | Port to publish PostgreSQL instances on the host nodes (dangerous if public). | `5432` |
| `POSTGRES_DB` | Name of the database. | `migasfree` |
| `POSTGRES_USER` | Primary database user. | `migasfree` |
| `REPLICATION_USER` | User for PostgreSQL streaming replication. | `repuser` |
| `MCP_RO_USER` | Read-only user for MCP tool access. | `mcp_ro` |
| `POSTGRES_PRIMARY_NODE` | Hostname of the Swarm node acting as Primary for replication. | `node-1` |
| `POSTGRESQL_CONF` | Pipe-separated list of custom PG settings (e.g. `work_mem=32MB\|max_connections=100`). | `work_mem=32MB` |

### 🧠 Datastore (Redis)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `REDIS_HOST` | Redis server host. Use `datastore` for the internal service. | `datastore` |
| `REDIS_PORT` | Port for the Redis service. | `6379` |
| `REDIS_DB` | Redis database index. | `0` |

### ⚖️ Scalability (Replicas)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `REPLICAS_core` | Number of core API instances. | `1` |
| `REPLICAS_public` | Number of public-facing instances. | `1` |
| `REPLICAS_worker` | Number of background task worker instances. | `1` |
| `REPLICAS_tunnel` | Number of Multi-Protocol Tunnel Relay instances. | `1` |
| `REPLICAS_console` | Number of Migasfree administrative console instances. | `1` |
| `REPLICAS_database_console` | Availability of the DB admin console (set to `0` for production). | `1` |
| `REPLICAS_datastore_console` | Availability of the Redis admin console (set to `0` for production). | `1` |
| `REPLICAS_worker_console` | Availability of the Celery Flower console (set to `0` for production). | `1` |

### 🛠️ Advanced Features

| Variable | Description | Default |
| :--- | :--- | :--- |
| `PMS_ENABLED` | Comma-separated list of enabled Package Management Systems (apt, yum, pacman, apk, wpt). | `pms-apt,...` |
| `TUNNEL_CONNECTIONS` | Max concurrent connections for the Tunnel Relay (adjust ulimits accordingly). | `50000` |
| `BACKUP_CRON` | Crontab syntax for scheduling database backups. | `00 00 * * *` |
| `DEBUG` | Enable verbose (DEBUG level) logging for the manager and status services. | `false` |

### 📉 Sync Optimization (Saturation Strategy)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SYNC_MAX_DB_LATENCY` | Threshold (seconds) to consider the database saturated. | `0.5` |
| `SYNC_MAX_CORE_LOAD` | Max CPU load (%) to consider core instances saturated. | `90` |
| `SYNC_MAX_CONCURRENCY` | Max concurrent sync processes from the queue. | `50` |
| `SYNC_QUEUE_PROCESS_INTERVAL` | Interval (seconds) to process the synchronization queue. | `30` |
| `METRICS_RECORDING_INTERVAL` | Interval (seconds) to record server performance metrics. | `15` |
| `METRICS_RETENTION_LIMIT` | Duration (seconds) to keep metrics history in memory. | `14400` |
