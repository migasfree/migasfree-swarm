# migasfree v5 — Semantic Technical Reference for AI Agents

> **Context**: Comprehensive, zero-redundancy technical specification of migasfree v5 (Architecture, Swarm Orchestration, Server & Client Configurations, REST API, MCP Integration, CLI Reference, and Troubleshooting).

---

## 1. System Architecture & Model

### 1.1 Conceptual Model
- **SCM Paradigm**: Software Configuration Management via native package management systems (PMS: apt, yum, pacman, apk, wpt) and declarative state convergence.
- **Client Triad**:
  - `migasfree-client`: Convergence engine, attribute evaluation, hardware/software inventory upload, scheduled via systemd timer (`OnBootSec=5min`, `OnUnitActiveSec=2h`, `RandomizedDelaySec=10min`).
  - `migasfree-agent`: Outbound resident service for encrypted TCP/WebSocket tunneling (SSH 22, VNC 5900, RDP 3389) with zero port-forwarding requirements and automatic mTLS certificate reuse.
  - `migasfree-play`: Graphical desktop self-service software catalog (Quasar/Vite) requiring no superuser privileges.
- **Server Topology (migasfree-swarm)**:
  - **Docker Swarm** multi-service orchestration with HAProxy edge load-balancer (HTTPS / mTLS), FastAPI (`core` + `manager`), Django backend, Celery workers (`worker`), Redis datastore (`datastore`), PostgreSQL (`database` with streaming replication) and Pgpool-II gateway.
  - **Datashare Storage**: Shared filesystem (`local` or `nfs` at `/exports/migasfree-swarm`).
- **Logical Configuration Entities**:
  - **Project**: Root container matching base OS distribution/flavour (e.g., `Debian-12`).
  - **Attribute**: Key/Value characteristic evaluated on client (Dynamic Formula via Python/Bash) or server (Static / Server-side tag).
  - **Deployment**: Package delivery policy (Internal / External / Application Catalog / Available / Migration).
  - **Singularity**: Computer ID (CID) override for granular rule targeting.

## 2. Server Configuration Reference (`cluster.conf`, `stack.conf`, `settings.py`)

# Server

> Order and simplification are the first steps toward the mastery of a subject.
![image](_static/chapter23/tool.png)

Proper sizing and operational stability of migasfree depend on how the various infrastructure layers are configured. A production deployment is not a static block: it requires calibrating network parameters, saturation thresholds, access policies, database engine, and backend settings to match organizational scale.

In this chapter, we will analyze in depth all server and migasfree-swarm orchestration configuration files, structured across three fundamental layers:

1. **The infrastructure and cluster layer** (`cluster.conf`).
2. **The service stack and orchestration layer** (`stack.conf`).
3. **The backend layer** (`settings.py`).

While in [Chapter 10 (Stack)](chapter10.md#stack) you learned the purpose of each service, here you will find the details of each directive, its default value, and practical guidance for choosing the right values for your fleet profile.

\

## Cluster

The `cluster.conf` file defines global storage properties and shared data support across the Docker Swarm cluster. This file resides on the manager node and is consulted during infrastructure deployment and initialization.

* **Standard location on manager node**: `/etc/migasfree-swarm/cluster.conf`

### Storage Directives

The migasfree infrastructure requires a shared storage space (*datashare*) hosting package repositories, stores, backups, and mTLS certificates.

| Variable           | Technical Description                                                                                                                                                   |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `DATASHARE_FS`     | Type of shared filesystem. Supported values: `local` (for single-node or lab environments) and `nfs` (for multi-node production clusters).  *(Default: \`\`local\`\`)*. |
| `DATASHARE_SERVER` | IP address or fully qualified domain name of the NFS server exporting shared volumes.  *(Mandatory when \`\`DATASHARE_FS=nfs\`\`)*.                                     |
| `DATASHARE_PATH`   | Absolute path exported on the NFS server where data for all stacks will reside.  *(Default: \`\`/exports/migasfree-swarm\`\`)*.                                         |
| `DATASHARE_PORT`   | TCP/UDP network port used for communication with the NFS service.  *(Default: \`\`2049\`\`)*.                                                                           |

### Production Configuration Example

In a high-availability cluster with network storage, `cluster.conf` adopts the following structure:

```ini
# /etc/migasfree-swarm/cluster.conf
DATASHARE_FS="nfs"
DATASHARE_SERVER="192.168.10.50"
DATASHARE_PATH="/srv/nfs/migasfree-cluster"
DATASHARE_PORT="2049"
```

#### NOTE
If `DATASHARE_FS="local"` is selected, migasfree-swarm will use local directories on the manager node (typically under `/var/lib/docker/volumes/`), which disables data container mobility across different compute nodes.

\

## Stack

Each service stack deployed in migasfree-swarm has its own `stack.conf` file. This file governs operational behavior, networking, security, and container sizing for that specific instance.

* **Location in Datashare console**: `/stack.conf` (at the root of the stack volume).

Below, we detail its directives grouped by operational domains.

### Identity, Network, and General Access

These govern public identity and ingress ports of the HAProxy edge load balancer:

| Variable     | Description                                                                                                                                                                           |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `STACK`      | Identifying name of the stack. Assigned during initial deployment; do not modify manually.                                                                                            |
| `FQDN`       | Fully qualified domain name through which clients and administrators access the server.  *(Default: \`\`migasfree.acme.com\`\`)*.                                                     |
| `FQDN_IP`    | IP address automatically captured from the host’s `/etc/hosts` file. Useful in dev environments or networks without a DNS server. If empty, standard DNS resolution is used.          |
| `TZ`         | Time zone applied to all stack containers to synchronize timestamps.  *(Default: \`\`Europe/Madrid\`\`)*.                                                                             |
| `PORT_HTTP`  | Port on which the cluster listens for incoming HTTP requests.  *(Default: \`\`80\`\`)*.                                                                                               |
| `PORT_HTTPS` | Port on which the cluster listens for secure HTTPS requests.  *(Default: \`\`443\`\`)*.                                                                                               |
| `RATE_LIMIT` | Maximum number of requests permitted within a 10-second window from the same IP and URL before returning an anti-DDoS HTTP 429 (*Too Many Requests*) code.  *(Default: \`\`100\`\`)*. |

### Edge Security and Certificates

| Variable      | Description                                                                                                                                                                                                                                         |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `HTTPSMODE`   | TLS certificate issuance and management mode. Supported options: `manual` (custom or locally generated self-signed certificates) or `auto` (automatic issuance and renewal via Let’s Encrypt ACME HTTP-01 challenge).  *(Default: \`\`manual\`\`)*. |
| `MTLS`        | When set to `True`, HAProxy requires mutual TLS authentication via browser X.509 client certificate to access administrative consoles and APIs.  *(Default: \`\`False\`\`)*.                                                                        |
| `NETWORK_MNG` | Space-separated list of IP addresses or CIDR networks authorized to access administrative consoles (Flower, pgAdmin, RedisInsight, HAProxy Stats).  *(Default: \`\`0.0.0.0/0\`\`)*.                                                                 |
| `NETWORK_MCP` | Addresses authorized to communicate with the MCP (*Model Context Protocol*) server. Restricted to local access (`127.0.0.1`) by default.                                                                                                            |

#### WARNING
In production environments exposed to open networks, always restrict `NETWORK_MNG` to your corporate management subnets to prevent public exposure of consoles.

### PostgreSQL Database and Replication

These directives control connections to the relational database engine and the Pgpool-II cluster:

| Variable                | Description                                                                                                                                                                                                                                                                                                   |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `POSTGRES_HOST`         | Database engine connection mode. Internal options: `pgpool` (high-availability gateway with read/write splitting) or `database` (direct single-node connection). If an external IP or FQDN is provided, internal services are not deployed and the remote host is connected to.  *(Default: \`\`pgpool\`\`)*. |
| `POSTGRES_PORT`         | Internal communication port for PostgreSQL or Pgpool.  *(Default: \`\`5432\`\`)*.                                                                                                                                                                                                                             |
| `PORT_DATABASE`         | Port published in *host* mode on cluster nodes. Required when using Pgpool-II with static IPs so the gateway can reach database nodes across the Swarm cluster.  *(Default: \`\`5432\`\`)*.                                                                                                                   |
| `POSTGRES_DB`           | Name of the main application database.  *(Default: \`\`migasfree\`\`)*.                                                                                                                                                                                                                                       |
| `POSTGRES_USER`         | Owner user of the migasfree database.  *(Default: \`\`migasfree\`\`)*.                                                                                                                                                                                                                                        |
| `REPLICATION_USER`      | Technical user used for streaming physical replication connections.  *(Default: \`\`repuser\`\`)*.                                                                                                                                                                                                            |
| `POSTGRES_PRIMARY_NODE` | Name of the Swarm cluster node acting as primary write node for PostgreSQL.  *(Default: \`\`node-1\`\`)*.                                                                                                                                                                                                     |
| `POSTGRESQL_CONF`       | Pipe-separated list of configuration parameters injected into `postgresql.conf` (e.g., `work_mem=64MB|max_connections=100`).  *(Default: \`\`work_mem=32MB\`\`)*.                                                                                                                                             |

### In-Memory Datastore (Redis)

| Variable     | Description                                                                                                                                                                   |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `REDIS_HOST` | Host of the Redis service. In standard setups, `datastore` is used; if using an external server outside the cluster, specify its IP or FQDN.  *(Default: \`\`datastore\`\`)*. |
| `REDIS_PORT` | Connection port to the Redis service.  *(Default: \`\`6379\`\`)*.                                                                                                             |
| `REDIS_DB`   | Logical database index within the Redis instance.  *(Default: \`\`0\`\`)*.                                                                                                    |

### Scalability and Replica Sizing

Allows configuring the number of running instances for each stack microservice:

| Variable                     | Microservice Function                                                                                         |
|------------------------------|---------------------------------------------------------------------------------------------------------------|
| `REPLICAS_core`              | Instances of the synchronization engine and core business logic (FastAPI / backend).  *(Default: \`\`1\`\`)*. |
| `REPLICAS_public`            | Nginx web servers for serving static files and package repositories.  *(Default: \`\`1\`\`)*.                 |
| `REPLICAS_worker`            | Celery background workers responsible for asynchronous processing.  *(Default: \`\`1\`\`)*.                   |
| `REPLICAS_tunnel`            | TCP/WebSocket tunnel relay servers for mTLS remote access.  *(Default: \`\`1\`\`)*.                           |
| `REPLICAS_console`           | Administrative management web frontend (Vue/Quasar frontend).  *(Default: \`\`1\`\`)*.                        |
| `REPLICAS_database_console`  | pgAdmin 4 console.  *(Default: \`\`1\`\` in development, set to \`\`0\`\` in production)*.                    |
| `REPLICAS_datastore_console` | RedisInsight console.  *(Default: \`\`1\`\` in development, set to \`\`0\`\` in production)*.                 |
| `REPLICAS_worker_console`    | Celery Flower console.  *(Default: \`\`1\`\` in development, set to \`\`0\`\` in production)*.                |

### Packaging, Analytics, Maintenance, and Proxy Services

| Variable             | Description                                                                                                                                                                                                    |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `PMS_ENABLED`        | Comma-separated list of package managers enabled on the server. Allows restricting managers based on distributions present in the fleet.  *(Default: \`\`pms-apt, pms-yum, pms-pacman, pms-apk, pms-wpt\`\`)*. |
| `TUNNEL_CONNECTIONS` | Maximum concurrent connection capacity of the multi-protocol relay tunnel (recommended between 10000 and 65000 with `ulimit -n 524288` in production).  *(Default: \`\`50000\`\`)*.                            |
| `BACKUP_CRON`        | Standard crontab syntax scheduling daily dumps of PostgreSQL and Redis databases (at midnight).  *(Default: \`\`00 00 \* \* \*\`\`)*.                                                                          |
| `HTTP_PROXY`         | HTTP proxy URL used for outbound connections during image and ISO building (e.g., `http://proxy.acme.com:8080`).  *(Default: empty)*.                                                                          |
| `HTTPS_PROXY`        | HTTPS proxy URL for outbound connections during build tasks.  *(Default: empty)*.                                                                                                                              |
| `NO_PROXY`           | Comma-separated list of hostnames or IP addresses that should bypass the proxy (e.g., `localhost,127.0.0.1,.acme.com`).  *(Default: empty)*.                                                                   |
| `HAS_KEYBOARD`       | Determines if the runtime environment has interactive keyboard/console input.  *(Default: \`\`true\`\`)*.                                                                                                      |
| `TDA_SCHEDULE`       | Standard crontab syntax scheduling the batch recalculation of Mapper topological graphs.  *(Default: \`\`0 3 \* \* \*\`\`)*.                                                                                   |

### Saturation Control and Queuing (Anti-Collapse Strategy)

These directives regulate concurrency when thousands of clients synchronize simultaneously, guaranteeing prompt responses without degrading the database engine:

| Variable                      | Behavior and Operational Thresholds                                                                                                                 |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `SYNC_MAX_DB_LATENCY`         | Maximum allowed database latency (seconds). If exceeded, incoming requests are automatically queued.  *(Default: \`\`0.5\`\`)*.                     |
| `SYNC_MAX_CORE_LOAD`          | Maximum CPU load percentage on `core` instances before considering the node saturated and diverting traffic to the queue.  *(Default: \`\`90\`\`)*. |
| `SYNC_MAX_CONCURRENCY`        | Maximum number of concurrent synchronizations processed simultaneously from the queue.  *(Default: \`\`50\`\`)*.                                    |
| `SYNC_QUEUE_PROCESS_INTERVAL` | Interval in seconds with which the dispatcher checks and drains queued requests.  *(Default: \`\`30\`\`)*.                                          |
| `METRICS_RECORDING_INTERVAL`  | Performance metrics sampling frequency in the cluster (seconds).  *(Default: \`\`15\`\`)*.                                                          |
| `METRICS_RETENTION_LIMIT`     | Metrics retention duration in Redis memory (4 hours).  *(Default: \`\`14400\`\`)*.                                                                  |
\

## Backend

The migasfree backend, built on Django and FastAPI, features a set of operational settings defined in its internal configuration package (`migasfree/settings/`).

### Configuration Override (settings.py)

Rather than modifying server source code, migasfree allows customizing both [standard Django (5.2) directives](https://docs.djangoproject.com/en/5.2/ref/settings/) (SMTP email, authentication, logging…) and migasfree-specific constants via an external override file:

* **Location in Datashare console**: `/conf/settings.py`

### Computer Registration and Lifecycle

These constants govern how the backend admits, catalogs, and inventories workstations:

| Directive                           | Default Value and Operational Purpose                                                                                                                         |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `MIGASFREE_AUTOREGISTER`            | **Default**: `True`. Allows new clients contacting the server for the first time to automatically register into inventory.                                    |
| `MIGASFREE_DEFAULT_COMPUTER_STATUS` | **Default**: `'assigned'`. Initial status assigned to new computers. Options: `assigned`, `reserved`, `unknown`, `in repair`, `available`, or `unsubscribed`. |
| `MIGASFREE_HW_PERIOD`               | **Default**: `30`. Interval in days after which the client re-gathers and uploads the complete hardware inventory.                                            |
| `MIGASFREE_INVALID_UUID`            | **Default**:  *(list of UUIDs)*. List of clone or factory-defective motherboard UUIDs that migasfree invalidates to avoid collisions.                         |
| `MIGASFREE_COMPUTER_SEARCH_FIELDS`  | **Default**: `('id', 'name')`. Fields used to index and search computers in public API queries.                                                               |

### Corporate Identity and Support

Defines contact info, branding, and visual notification timeout intervals:

| Directive                         | Default Value and Operational Purpose                                                                     |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------|
| `MIGASFREE_ORGANIZATION`          | **Default**: `'My Organization'`. Corporate name displayed in headers, reports, and public interfaces.    |
| `MIGASFREE_HELP_DESK`             | **Default**:  *(Contact text)*. Informative message, email, or support link displayed to users on error.  |
| `MIGASFREE_SECONDS_MESSAGE_ALERT` | **Default**: `1800`. Expiration timeout in seconds (30 minutes) for active dashboard messages and alerts. |

### Automatic Change Notifications

The server can automatically log and alert administrators upon changes in workstation identity or connectivity:

| Directive                       | Monitored Event (Default: False)                                                        |
|---------------------------------|-----------------------------------------------------------------------------------------|
| `MIGASFREE_NOTIFY_NEW_COMPUTER` | Alerts upon onboarding and registration of a new workstation.                           |
| `MIGASFREE_NOTIFY_CHANGE_UUID`  | Alerts if the computer’s motherboard or UUID changes compared to the registered value.  |
| `MIGASFREE_NOTIFY_CHANGE_NAME`  | Alerts if the operating system hostname is renamed.                                     |
| `MIGASFREE_NOTIFY_CHANGE_IP`    | Alerts if the computer contacts the server reporting a different IP address than usual. |

### Scripting Languages for Properties and Faults

The `MIGASFREE_PROGRAMMING_LANGUAGES` variable defines supported code interpreters to evaluate dynamic property formulas and fault diagnostic scripts:

```python
# Intérpretes soportados en /conf/settings.py
MIGASFREE_PROGRAMMING_LANGUAGES = (
    (0, 'bash'),
    (1, 'python'),
    (2, 'perl'),
    (3, 'php'),
    (4, 'ruby'),
    (5, 'cmd'),
    (6, 'powershell'),
)
```

### Cryptography and Key Names

Identifies public and private key files (hosted in the internal key store) used for package signing and cryptographic security:

| Directive                    | Default File and Purpose                                                                           |
|------------------------------|----------------------------------------------------------------------------------------------------|
| `MIGASFREE_PUBLIC_KEY`       | **File**: `'migasfree-server.pub'`. RSA/JWT public key of the server.                              |
| `MIGASFREE_PRIVATE_KEY`      | **File**: `'migasfree-server.pri'`. RSA/JWT private key of the server.                             |
| `MIGASFREE_PACKAGER_PUB_KEY` | **File**: `'migasfree-packager.pub'`. Public key for package verification.                         |
| `MIGASFREE_PACKAGER_PRI_KEY` | **File**: `'migasfree-packager.pri'`. Private key for digitally signing packages and repositories. |

### Microservices, Paths, and Rate Limiting

| Directive                            | Default Value and Purpose                                                                                          |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| `MIGASFREE_MANAGER_URL`              | **Default**: `'http://manager:8080'`. Address of the FastAPI Manager microservice for tunnels and remote commands. |
| `MIGASFREE_STORE_TRAILING_PATH`      | **Default**: `'stores'`. Relative subdirectory for file stores and deployments.                                    |
| `MIGASFREE_REPOSITORY_TRAILING_PATH` | **Default**: `'repos'`. Relative subdirectory for software package repositories.                                   |
| `MIGASFREE_EXTERNAL_TRAILING_PATH`   | **Default**: `'external'`. Relative subdirectory for external resources and repositories.                          |
| `MIGASFREE_TMP_TRAILING_PATH`        | **Default**: `'tmp'`. Internal temporary subdirectory.                                                             |
| `API_V4_REGISTER_RATE_LIMIT_MAX`     | **Default**: `50`. Allowed registration requests for v4 clients within the time window.                            |
| `API_V4_REGISTER_RATE_LIMIT_WINDOW`  | **Default**: `30`. Time window in seconds for registration rate calculation.                                       |

### Integrated External Actions (MIGASFREE_EXTERNAL_ACTIONS)

Allows embedding custom buttons and shortcuts in the migasfree web console to interact with computers directly from the browser:

```python
# Ejemplo de configuración de acciones remotas en /conf/settings.py
MIGASFREE_EXTERNAL_ACTIONS = {
    "computer": {
        "ping": {"title": "PING", "description": "Comprobar conectividad ICMP"},
        "ssh": {"title": "SSH", "description": "Conexión remota por consola segura"},
        "vnc": {"title": "VNC", "description": "Control remoto gráfico", "many": False},
        "sync": {"title": "SYNC", "description": "Forzar sincronización remota (migasfree sync)"},
        "install": {
            "title": "INSTALL",
            "description": "Instalar un paquete remoto",
            "related": ["deployment", "computer"],
        },
    },
    "error": {
        "clean": {"title": "Limpiar", "description": "Eliminar historial de fallos"},
    },
}
```

## Guidance by Deployment Profiles

With so many directives, a quick guide on which variables to adjust based on fleet characteristics is essential. The following recommendations complement the hardware sizing covered in [Part IV (Production)](part04.md#iv-produccion):

| Fleet Scenario                                                    | Directives to Review                                                                 | Practical Recommendation                                                                                                      |
|-------------------------------------------------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| **Homogeneous fleet** (Debian/Ubuntu only)                        | `PMS_ENABLED`                                                                        | Limit active managers to `'pms-apt'`: fewer services, smaller attack surface.                                                 |
| **Thousands of workstations syncing at the start of the workday** | `SYNC_MAX_*`, `METRICS_RECORDING_INTERVAL`                                           | Increase `SYNC_MAX_CONCURRENCY` and monitor latency with `SYNC_MAX_DB_LATENCY`: the queue strategy will protect the database. |
| **Server exposed to the Internet**                                | `HTTPSMODE`, `MTLS`, `NETWORK_MNG`, `RATE_LIMIT`                                     | Use `HTTPSMODE='auto'` (Let’s Encrypt) or `'self-signed'`, enable mTLS, and restrict management networks to your subnets.     |
| **Administrators connecting from a private subnet**               | `NETWORK_MNG`                                                                        | Replace `127.0.0.1` with the corporate subnet (e.g. `192.168.1.0/24`).                                                        |
| **Remote branches with slow WAN**                                 | `TUNNEL_CONNECTIONS`, `BACKUP_CRON`                                                  | Size the tunnel for expected concurrency and schedule backups during off-peak hours.                                          |
| **Unneeded development consoles**                                 | `REPLICAS_database_console`, `REPLICAS_datastore_console`, `REPLICAS_worker_console` | Set them to `0` in production to free memory.                                                                                 |
| **High notification and audit volume**                            | `MIGASFREE_*` (backend), `POSTGRESQL_CONF`                                           | Tune `MIGASFREE_HW_PERIOD` and change alerts, and optimize `work_mem`.                                                        |

## Summary

In this chapter, the canonical reference for server configuration, we covered the three adjustment layers of migasfree:

* **Cluster** (`cluster.conf`): Shared storage backing repositories, backups, and certificates (`DATASHARE_*`).
* **Stack** (`stack.conf`): Networking, edge security and mTLS, database and replicas, Redis, replica sizing, PMS, and saturation control.
* **Backend** (`settings.py`): Customization of constants, auto-registration, notifications, and external actions.

With the server tuned, only the final link in the chain remains: the client workstation. In the next chapter, we will cover the complete client configuration reference, from `migasfree.conf` to `migasfree-agent` whitelists.

Let’s dive in.

---

## 3. Client Configuration Reference (`migasfree.conf`, Env Vars, Lifecycle Hooks)

# Client

> The best way to predict the future is to invent it.
![image](_static/chapter24/tool.png)

Both workstations and managed servers are the destination where policies, configurations, and deployments orchestrated in migasfree come to life. Their local components provide the flexibility needed to adapt to any scenario: isolated computers behind a proxy, remote branch nodes with constrained links, or periodic hardware audits.

In this chapter, you will see in detail the settings and directives of the three fundamental components that coexist on client machines:

1. **The synchronization and inventory client** (`migasfree-client`).
2. **The application catalog graphical interface** (`migasfree-play`).
3. **The secure remote access and tunnel agent** (`migasfree-agent`).

\

## migasfree-client

`migasfree-client` governs attribute negotiation with the server, dynamic repository management, software installation, and hardware inventory collection. All its behavior is defined in the `migasfree.conf` file.

### Configuration File Location

The default location of the file depends on the operating system:

* **GNU/Linux**: `/etc/migasfree.conf`
* **Microsoft Windows**: `%PROGRAMDATA%\migasfree-client\migasfree.conf` (e.g., `C:\ProgramData\migasfree-client\migasfree.conf`).

#### TIP
It is possible to override the configuration file path at any time by defining the `MIGASFREE_CONF` environment variable prior to invoking client commands.

### Directives in the [client] Section

The primary `[client]` section contains the following operational directives:

| Parameter              | Technical Description                                                                                                                                                                                                         |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Server`               | Address of the migasfree server. Supports simple format (`migasfree.example.com`, where HTTPS is assumed), full URL (`https://migasfree.example.com:8443`), or HTTP for development.  *(Default: \`\`https://localhost\`\`)*. |
| `Project`              | Name of the deployment project. If unspecified, the client auto-detects the base OS distribution and version (e.g., `Debian-12` or `Ubuntu-24.04`).  *(Autodetected)*.                                                        |
| `Auto_Update_Packages` | When enabled (`True`), the client automatically updates packages during the regular synchronization process (`migasfree sync`).  *(Default: \`\`True\`\`)*.                                                                   |
| `Manage_Devices`       | Enables automatic management and configuration of peripheral devices and printers on the computer.  *(Default: \`\`True\`\`)*.                                                                                                |
| `Upload_Hardware`      | Enables physical collection and upload of hardware inventory to the server.  *(Default: \`\`True\`\`)*.                                                                                                                       |
| `Computer_Name`        | Overrides the computer’s logical name in the migasfree database, regardless of the network hostname returned by `platform.node()`.  *(Default: OS Hostname)*.                                                                 |
| `Debug`                | Enables detailed execution logging and trace outputs in log files.  *(Default: \`\`False\`\`)*.                                                                                                                               |
| `Proxy`                | Address and port of the corporate HTTP proxy server (e.g., `192.168.1.100:8080`).  *(Default: none)*.                                                                                                                         |
| `Package_Proxy_Cache`  | Address and port of the local or branch package caching server (e.g., `192.168.1.101:3142` with *apt-cacher-ng*).  *(Default: none)*.                                                                                         |

### Directives in the [packager] Section

This optional section stores packaging credentials for the `migasfree-upload` command:

| Parameter   | Function                                                                                        |
|-------------|-------------------------------------------------------------------------------------------------|
| `User`      | User with packager permissions on the migasfree server.  *(Prompted via CLI if not specified)*. |
| `Password`  | Password of the packager user.  *(Prompted via CLI if not specified)*.                          |
| `Project`   | Default target project for package uploads.  *(Prompted via CLI if not specified)*.             |
| `Store`     | Software store where generated binaries will be placed.  *(Prompted via CLI if not specified)*. |

### Complete Example of migasfree.conf

```ini
# /etc/migasfree.conf
[client]
Server = https://migasfree.acme.com
Project = Debian-12
Auto_Update_Packages = True
Manage_Devices = True
Upload_Hardware = True
Package_Proxy_Cache = 192.168.10.20:3142
Debug = False

[packager]
User = packager_admin
Project = Debian-12
Store = default
```

### Environment Variables (MIGASFREE_\*)

`migasfree-client` allows overriding any configuration directive via environment variables. This capability is especially useful in containerized deployments, continuous integration (CI/CD) pipelines, or one-off command-line tests without modifying the system’s `migasfree.conf` file.

| Environment Variable                    | Directive and Purpose                                                                       |
|-----------------------------------------|---------------------------------------------------------------------------------------------|
| `MIGASFREE_CONF`                        | Overrides the absolute path to the `migasfree.conf` file.                                   |
| `MIGASFREE_CLIENT_SERVER`               | Equivalent to `[client] Server`. Server URL or FQDN.                                        |
| `MIGASFREE_CLIENT_PROJECT`              | Equivalent to `[client] Project`. Assigned project name.                                    |
| `MIGASFREE_CLIENT_COMPUTER_NAME`        | Equivalent to `[client] Computer_Name`. Logical name for the computer.                      |
| `MIGASFREE_CLIENT_AUTO_UPDATE_PACKAGES` | Equivalent to `[client] Auto_Update_Packages`. Automatic updates (`True` / `False`).        |
| `MIGASFREE_CLIENT_MANAGE_DEVICES`       | Equivalent to `[client] Manage_Devices`. Peripheral management (`True` / `False`).          |
| `MIGASFREE_CLIENT_UPLOAD_HARDWARE`      | Equivalent to `[client] Upload_Hardware`. Physical inventory submission (`True` / `False`). |
| `MIGASFREE_CLIENT_PROXY`                | Equivalent to `[client] Proxy`. HTTP proxy server (`host:port`).                            |
| `MIGASFREE_CLIENT_PACKAGE_PROXY_CACHE`  | Equivalent to `[client] Package_Proxy_Cache`. Cache proxy server (`host:port`).             |
| `MIGASFREE_CLIENT_DEBUG`                | Equivalent to `[client] Debug`. Detailed debug traces (`True` / `False`).                   |
| `MIGASFREE_PACKAGER_USER`               | Equivalent to `[packager] User`. Packager user for uploading.                               |
| `MIGASFREE_PACKAGER_PASSWORD`           | Equivalent to `[packager] Password`. Packager user password.                                |
| `MIGASFREE_PACKAGER_PROJECT`            | Equivalent to `[packager] Project`. Target project for packaging.                           |
| `MIGASFREE_PACKAGER_STORE`              | Equivalent to `[packager] Store`. Target store for uploaded packages.                       |

#### Precedence Order

When a parameter is defined across multiple sources, the client applies the following resolution order (highest to lowest priority):

1. **Environment variables** (highest priority, override any other value).
2. **Command-line arguments** (parameters passed directly to the CLI).
3. **Configuration file** (directives read from `migasfree.conf`).
4. **Internal default values** (fallback mechanism in the absence of configuration).

```bash
# Ejemplo: Sincronización puntual contra un servidor de pruebas en modo debug
MIGASFREE_CLIENT_SERVER=https://test.migasfree.org MIGASFREE_CLIENT_DEBUG=True sudo migasfree sync

# Ejemplo: Subida automatizada de paquetes en un pipeline de CI/CD
MIGASFREE_PACKAGER_USER=ci_bot MIGASFREE_PACKAGER_PASSWORD=secret migasfree upload -f pkg.deb
```

### Data Paths and System Logs

The client keeps its working directories and logs organized by platform:

| Item               | System Storage Paths                                                                                                           |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------|
| Log file           | **GNU/Linux**: `/var/tmp/migasfree.log`<br/><br/>**Windows**: `%WINDIR%\temp\migasfree.log`                                    |
| Software inventory | **GNU/Linux**: `/var/tmp/installed_software.txt`<br/><br/>**Windows**: `%PROGRAMDATA%\migasfree-client\installed_software.txt` |
| Machine attributes | **GNU/Linux**: `/var/tmp/computer_traits.json`<br/><br/>**Windows**: `%PROGRAMDATA%\migasfree-client\computer_traits.json`     |
| mTLS certificates  | **GNU/Linux**: `/var/migasfree-client/mtls/`<br/><br/>**Windows**: `%PROGRAMDATA%\migasfree-client\mtls\`                      |

### Scheduled Execution with systemd

On servers or headless machines (where `migasfree-play` does not run), continuous unattended convergence is typically set up using a systemd service and timer:

```ini
# /etc/systemd/system/migasfree-sync.timer
[Unit]
Description=Temporizador de sincronización periódica de migasfree
ConditionVirtualization=false

[Timer]
OnBootSec=5min
OnUnitActiveSec=2h
RandomizedDelaySec=10min
Persistent=true

[Install]
WantedBy=timers.target
```

Using `RandomizedDelaySec` is an essential architectural practice: it randomly disperses requests across a time window (e.g., 10 or 15 minutes), preventing thousands of machines starting up at the same hour from overloading production servers.

### Extension Points and Lifecycle Hooks

`migasfree-client` provides directories where administrators can place executable scripts to extend client behavior at three key synchronization moments:

* `/usr/share/migasfree-client/pre-sync.d/`: Scripts executed before connecting to the migasfree server.
* `/usr/share/migasfree-client/post-sync.d/`: Scripts executed after completing synchronization and package installation or removal.
* `/usr/share/migasfree-client/events.d/`: Reactive event handlers triggered only when a consolidated computer characteristic (*trait*) changes compared to the previous synchronization.

#### Structure and Variables in events.d

Upon detecting a characteristic change, the client generates two context files in `/usr/share/migasfree-client/events.d/` and searches for scripts in the subfolder matching the modified prefix:

```text
/usr/share/migasfree-client/events.d/
├── .env                     # Variables del estado actual y previo
├── .json                    # Diferencias en formato JSON (diff)
└── USR/                     # Subcarpeta para eventos del prefijo USR
    └── notify-profile.sh    # Script ejecutable
```

The `.env` file exposes two variables for each characteristic:

* `TRAIT_<PREFIX>`: Contains the current value assigned after synchronization (e.g., `TRAIT_USR="teacher"`).
* `BEFORE_TRAIT_<PREFIX>`: Stores the value it held before synchronization (e.g., `BEFORE_TRAIT_USR="alumn"`).

Reactive Bash script example (`events.d/USR/notify-profile.sh`):

```bash
#!/bin/bash
# Cargar las variables de entorno del evento
source /usr/share/migasfree-client/events.d/.env

# Reaccionar si el usuario asignado al puesto ha cambiado
if [ "$TRAIT_USR" != "$BEFORE_TRAIT_USR" ]; then
    logger -t migasfree-event "Usuario cambiado: $BEFORE_TRAIT_USR -> $TRAIT_USR"
    # Ejecutar acciones operativas locales (ej. notificar en el escritorio o recargar un demonio)
fi
```

#### NOTE
Scripts within these directories are executed in alphanumeric order. If a script in `pre-sync.d` exits with an error code, synchronization terminates immediately to preserve workstation integrity.

\

## migasfree-play

migasfree-play is the desktop graphical application that allows users to install software and devices from the catalog without needing superuser privileges.

### Integration and Environment Variables

migasfree-play requires no complex manual configuration: it automatically discovers the server and project via the local client (`migasfree.conf`). For testing or dev environments, it supports the following environment variables:

| Variable               | Purpose                                                                                            |
|------------------------|----------------------------------------------------------------------------------------------------|
| `MFP_USER`             | Technical user to authenticate against the catalog REST API.  *(Default: \`\`migasfree-play\`\`)*. |
| `MFP_PASSWORD`         | Technical user password for access.  *(Default: \`\`migasfree-play\`\`)*.                          |
| `MFP_EXECUTIONS_LIMIT` | Simultaneous operations limit in the graphical execution queue.  *(Default: \`\`5\`\`)*.           |
| `MFP_QUASAR_PORT`      | Quasar/Vite development server port.  *(Default: \`\`9999\`\`)*.                                   |
\

## migasfree-agent

`migasfree-agent` is the background service responsible for establishing secure TCP tunnels over WebSocket with the relay server, allowing remote assistance to computers behind firewalls or NAT without opening ports or needing a public IP.

### Zero Configuration and mTLS Reuse

True to the philosophy of operational simplicity, `migasfree-agent` **has no dedicated configuration file**:

1. **Auto-discovery**: Upon startup, it queries client configuration (via `migasfree conf` and `migasfree info`) to obtain the server, computer ID (CID), and project.
2. **mTLS certificate reuse**: Automatically uses certificates issued in `/var/migasfree-client/mtls/` (or `%PROGRAMDATA%\migasfree-client\mtls\` on Windows) to establish the encrypted and authenticated tunnel.
3. **Multiplexed services without inbound port forwarding**: Multiplexes local support services over the outbound secure tunnel: **SSH** (port 22), **VNC** (port 5900), and **RDP** (port 3389). Since it is an outbound connection initiated by the agent towards the server (HTTPS/WSS traffic), no incoming open ports or port forwarding rules are needed on the workstation firewall or router.

\

## Summary

With this chapter, we conclude **Part V** and with it the migasfree configuration reference:

* **migasfree-client** (`migasfree.conf` and `MIGASFREE_*` variables): server, project, upgrade policies, hardware inventory, environment variables, data paths, scheduled execution, and lifecycle hooks.
* **migasfree-play**: catalog credentials and environment variables for testing and development.
* **migasfree-agent**: zero-configuration model via CLI introspection, tunnel services (SSH, VNC, RDP), and mTLS certificate reuse.

With server infrastructure and workstation configuration finely tuned, you have complete knowledge to operate migasfree at scale with robustness and elegance.

It has been a long, intense journey through systems architecture, automation, and governance. This chapter concludes the main body of *Fun with migasfree*.

I want to sincerely thank you for your interest in the project and the effort dedicated to reading along.

And finally, will you join me in sharing a final reflection in the [Epilogue](epilogue.md#epilogo)?

---

## 4. Command-Line Interface (CLI) Quick Reference

# CLI Reference

> > Make each program do one thing and do it well.

Throughout the book, migasfree command-line tools are repeatedly invoked. This annex brings together the main subcommands and options of each utility into a single reference point, so you can resolve any doubts without having to reopen the chapter where they were introduced.

\\newpage

## migasfree-client

The `migasfree` client is the workstation convergence tool. It combines a catalog of dedicated subcommands for each task with the global debugging mode `--debug` (see [Chapter 16 (Client Environment)](chapter16.md#entorno-cliente)):

| Command                                                     | Description                                                                                     |
|-------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `migasfree --help`                                          | Displays general help and available subcommands.                                                |
| `migasfree sync`                                            | Executes standard synchronization with the server (convergence cycle).                          |
| `migasfree sync --force-upgrade`                            | Forces package upgrades ignoring the `Auto_Update_Packages` setting.                            |
| `migasfree sync --hardware`                                 | Selectively synchronizes the hardware inventory subsystem.                                      |
| `migasfree sync --devices`                                  | Selectively synchronizes the device subsystem.                                                  |
| `migasfree info` / `migasfree info -j`                      | Queries computer info registered on the server (in JSON with `-j`).                             |
| `migasfree attributes`                                      | Queries assigned attributes and computer CID identifier (`-j` or `--cid`).                      |
| `migasfree tags --get` / `--set <tag>`                      | Queries or assigns tags to the computer from the command line.                                  |
| `migasfree label`                                           | Displays the computer ID label on screen (helpdesk support).                                    |
| `migasfree search <pattern>`                                | Searches available packages in assigned stores.                                                 |
| `migasfree install <package>` / `migasfree purge <package>` | Installs or uninstalls packages abstracting away the local [PMS](annex05-glossary.md#term-PMS). |
| `migasfree conf`                                            | Queries or modifies local configuration (`/etc/migasfree.conf`) with `--json`.                  |
| `migasfree import-mtls <file>`                              | Manually imports packaged mTLS certificates.                                                    |
| `migasfree upload -f <package> -j <project> -s <store>`     | Uploads a package to the server store from a packaging workstation.                             |
\\newpage

## migasfree-swarm

`migasfree-swarm` centralizes the Docker Swarm cluster lifecycle: stack deployment, security, topology, and backup (see [Chapter 9 (Infrastructure)](chapter09.md#infraestructura)):

| Command                                            | Description                                                                          |
|----------------------------------------------------|--------------------------------------------------------------------------------------|
| `migasfree-swarm config`                           | Generates initial cluster configuration (`cluster.conf`).                            |
| `migasfree-swarm deploy` / `undeploy` / `redeploy` | Deploys, tears down, or reinstalls a service stack (`-all` suffix for all).          |
| `migasfree-swarm pull`                             | Pulls all service images.                                                            |
| `migasfree-swarm consoles-dev` / `consoles-pro`    | Enables or disables development consoles (Portainer, Flower, pgAdmin, RedisInsight). |
| `migasfree-swarm secret`                           | Displays console access credentials.                                                 |
| `migasfree-swarm url-admin-certificate`            | Generates a one-time URL to issue the administration certificate.                    |
| `migasfree-swarm join-worker` / `leave`            | Adds a worker node to the cluster or leaves the current node.                        |
| `migasfree-swarm backup` / `restore`               | Performs or restores PostgreSQL and Redis dumps.                                     |
| `migasfree-swarm prune`                            | Removes dangling images from the node.                                               |
| `migasfree-swarm info`                             | Displays cluster and stack information.                                              |

## Packaging and Publishing Packages

Uploading packages to the server is done from an authorized packaging workstation via `migasfree upload` (or its binary `migasfree-upload`), specifying the file, project, and target store (see [Chapter 7 (Packaging)](chapter07.md#empaquetado)):

> ```bash
> migasfree upload -f mi-paquete_1.0_all.deb -j Proyecto-Base -s almacén
> ```
\\newpage

## migasfree-agent and migasfree-play

* **migasfree-agent**: servicio residente que abre túneles WebSocket inversos basados en mTLS para
  el acceso remoto (SSH, VNC, RDP). No dispone de órdenes directas; su ejecución remota queda
  restringida por la lista blanca `ALLOWED_COMMANDS` (ver [Capítulo 24 (Cliente)](chapter24.md#cliente)).
* **migasfree-play**: aplicación gráfica de autoservicio (Electron, Vue y Quasar) configurada por
  variables de entorno; no se administra por línea de órdenes (ver [Capítulo 16 (Entorno
  Cliente)](chapter16.md#entorno-cliente)).

---

## 5. REST API & Programmatic Automation Reference

# REST API

> > Automation is not just about doing things faster, but about making them reliable, repeatable, and scalable.

The REST API exposed by the `core` service constitutes migasfree’s most powerful programmatic interface. Through it, you can query inventory status, manage deployment policies, assign attributes, and automate any integration with third-party corporate systems (such as ticketing tools, CMDBs, or monitoring systems).

This annex describes authentication mechanisms, the structure of requests and responses, and complete practical examples in Bash (using `curl` and `jq`) and Python.

## Token-Based Authentication

To consume the API securely from external scripts or applications, migasfree uses user *token* authentication. Each request must include the `Authorization` HTTP header in the format:

> ```text
> Authorization: Token <tu_token_secreto>
> ```

### Obtaining the Access Token

There are two ways to obtain an API token:

1. **From the web management console**: By accessing your user profile in the web interface (`console`) and viewing or generating the API key (*API Token*).
2. **Via an HTTP request to the authentication endpoint**:
   ```bash
   curl -X POST https://<FQDN>/token-auth/ \
     -H "Content-Type: application/json" \
     -d '{"username": "tu_usuario", "password": "tu_password"}'
   ```

   The response will return a JSON object containing the access token:
   ```json
   {
     "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
   }
   ```

## Interactive Exploration with Swagger / OpenAPI

The migasfree server incorporates an interactive documentation interface based on OpenAPI (Swagger). To explore it, open in your browser:

> `https://<FQDN>/status` and click on the **core** option.

This interactive interface is an indispensable tool for development and programming integrations. Through it, developers can:

* **Perform live tests**: Execute real HTTP requests directly against the server from the browser to understand the JSON response structure.
* **Inspect data schemas**: Learn field data types, mandatory fields, and expected formats.
* **Debug status codes**: Become familiar with success responses (200, 201) and common errors (400 Bad Request, 401/403 Auth, 404 Not Found).
* **Copy payloads**: Obtain ready-to-use JSON templates for `POST` or `PUT` requests in external scripts.

### MCP Server

To maximize developer productivity, migasfree integrates an MCP (*Model Context Protocol*) server. This service exposes API documentation and database schemas directly to Artificial Intelligence agents.

This allows your AI development environment to dynamically query endpoints, resolve doubts about available filters, or inspect table fields in real time, generating more precise integration code and drastically reducing debugging time. For more configuration details, see [AI Integration](annex03-mcp-integration.md#anexo-mcp).

## API Structure and Conventions

* **Format**: All responses and payloads are exchanged in JSON format (`Content-Type: application/json`).
* **Pagination**: Resource lists accept the `limit` and `offset` query parameters to paginate large volumes of data:
  ```text
  https://<FQDN>/api/v1/token/computers/?limit=50&offset=100
  ```
* **Search and filtering**: Most endpoints support text searches via the `search` parameter (e.g., `?search=laptop-ventas`) and direct field filters (e.g., `?project=ACME-1` or `?status=synced`).

## Main Resources

The most commonly used endpoints for automated administration are:

* **\`\`/api/v1/token/computers/\`\`**: Query and manage computer inventory (hostname, IP, hardware, last synchronization timestamp, assigned attributes, etc.).
* **\`\`/api/v1/token/attributes/\`\`**: Creation and query of attributes (tags, logical formulas, and membership criteria).
* **\`\`/api/v1/token/deployments/\`\`**: Definition of package deployment policies and computer assignment rules.
* **\`\`/api/v1/token/packages/\`\`**: Catalog of software packages available in repositories.
* **\`\`/api/v1/token/projects/\`\`**: Projects and distributions managed by the server.

## Practical Examples

### Example 1: Querying Computers via Bash and curl

The following Bash script queries the list of registered computers and extracts their name, status, and last synchronization date by processing the JSON output with `jq`:

> ```bash
> #!/usr/bin/env bash
> set -euo pipefail

> FQDN="migasfree.acme.com"
> TOKEN="9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"

> curl -s -k \
>   -H "Authorization: Token ${TOKEN}" \
>   -H "Content-Type: application/json" \
>   "https://${FQDN}/api/v1/token/computers/?limit=20" \
>   | jq -r '.results[] | "\(.id)\t\(.name)\t\(.status)\t\(.sync_end_date)"'
> ```

You will get output similar to this:

> ```text
> 1   debian13        assigned        2026-08-24T12:57:02.792475+02:00
> 2   mci-builder     assigned        2026-08-21T10:30:19.336690+02:00
> ```

### Example 2: Automation in Python

The following Python script uses the `requests` library to query computers and display an inventory summary (including status):

> ```python
> import os
> import requests

> FQDN = "migasfree.acme.com"
> TOKEN = os.getenv("MIGASFREE_API_TOKEN", "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b")
> BASE_URL = f"https://{FQDN}/api/v1/token"

> headers = {
>     "Authorization": f"Token {TOKEN}",
>     "Content-Type": "application/json",
> }

> response = requests.get(f"{BASE_URL}/computers/", headers=headers, verify=False)
> response.raise_for_status()

> data = response.json()
> computers = data.get("results", [])

> print(f"Total computers retrieved: {len(computers)}")
> for pc in computers:
>     print(f"- ID: {pc.get('id')} | Name: {pc.get('name')} | Status: {pc.get('status')}")
> ```

You will get output similar to this:

> ```text
> Total computers retrieved: 2
> - ID: 1 | Name: debian13 | Status: assigned
> - ID: 2 | Name: mci-builder | Status: assigned
> ```

---

## 6. Model Context Protocol (MCP) AI Integration

# AI Integration

> Artificial intelligence is the new electricity.

In [Chapter 10 (Stack)](chapter10.md#stack) we introduced the `mcp-server` service, the platform component that implements the open [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) standard. Through it, artificial intelligence assistants (such as Antigravity, Claude Desktop, or Cursor) can query the fleet securely and in natural language. This annex details the capabilities exposed by the server, the steps to connect an assistant, and a collection of practical, ready-to-use queries.

## MCP Server Capabilities

The MCP server exposes three fundamental protocol primitives: **tools**, **resources**, and **instruction templates** (*prompts*).

### Tools

Tools allow the AI agent to perform dynamic queries against the infrastructure:

* **db_query**: Executes arbitrary SQL `SELECT` queries directly against the migasfree PostgreSQL database. The server strictly validates that the statement is read-only and enforces the restrictions of the `mcp_ro` role.
* **read_doc**: Compatibility tool for clients that do not support direct reading of MCP resources. Allows querying or listing server technical documents (such as database schemas, architecture, or API specifications).

### Resources

Resources provide live documentation and continuous technical context to language models via URI schemes (`<STACK>://docs/...`):

* **documentation_index.md**: Master index of available technical documentation.
* **db_schema.md**: Complete relational structure of the database (tables, columns, data types, and foreign keys).
* **migasfree-user-manual.md**: Official user manual converted to Markdown.
* **migasfree_architecture.md**: Technical description of service architecture and data flow.
* **github_repositories.md**: Catalog of all official repositories in the migasfree ecosystem.
* **api_core.md** and **api_manager.md**: OpenAPI specifications for server REST interfaces.
* **faq.md**: Troubleshooting guide and frequently asked questions about the platform.

### Instruction Templates (*Prompts*)

The server includes predefined templates that guide the assistant through common management tasks:

* **analyze_fleet**: Performs a comprehensive fleet analysis (distribution by status, assigned projects, recent activity, and unsynchronized computers).
* **find_sync_errors**: Diagnoses errors and disruptions in workstation synchronizations.
* **query_builder**: Assists in crafting accurate SQL queries from natural language questions.

## Configuring in Antigravity

Integrating the MCP server with Antigravity takes three steps:

1. **Enable network access in migasfree**: For security reasons, MCP server access is restricted to local connections (`127.0.0.1`) by default. To authorize connections from the machine running Antigravity, edit `stack.conf` by defining the allowed IP or CIDR range:
   ```python
   NETWORK_MCP = '192.168.1.50'  # O un rango CIDR como '192.168.1.0/24'
   ```

   Apply the changes to the cluster with:
   ```bash
   migasfree-swarm deploy
   ```
2. **Install the CA certificate (if using custom certificates)**: If the server uses a private CA rather than a public Let’s Encrypt certificate, install the CA on the host machine running Antigravity:
   ```bash
   sudo wget --no-check-certificate -O /usr/local/share/ca-certificates/ca-<FQDN>.crt https://<FQDN>/pool/install/ca-<FQDN>.crt
   sudo update-ca-certificates --fresh
   ```

   #### NOTE
   Since Node.js and Electron-based environments do not consult the OS system certificate store by default, you need to point Node.js to the certificate path using the `NODE_EXTRA_CA_CERTS` environment variable (e.g., in `~/.bashrc`):
   ```bash
   export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
   ```

   Alternatively, in lab environments or local testbeds without public domains, you can connect directly over unencrypted HTTP (`http://<FQDN>/mcp/sse`).
3. **Register the server in Antigravity**: The migasfree MCP server uses **SSE** (*Server-Sent Events*) transport. Add the server configuration to the MCP configuration file (globally in `~/.gemini/antigravity-ide/mcp_config.json` or at project level in `.agents/mcp_config.json`):
   ```json
   {
     "mcpServers": {
       "migasfree": {
         "serverUrl": "http://<FQDN>/mcp/sse"
       }
     }
   }
   ```

Once connected, Antigravity will automatically have access to all server tools, resources, and documentation to query the fleet status in real time.

![image](_static/chapter10/mcp.png)

## Use Cases and Natural Language Queries

Once the MCP server is connected, the AI assistant acts as a genuine analyst and expert co-pilot over the migasfree infrastructure. You can ask direct natural language questions without needing knowledge of SQL syntax, REST API calls, or internal database table schemas.

The language model queries context resources (such as `db_schema.md` or technical documentation), formulates the necessary read-only queries, executes them using `db_query`, and synthesizes answers into reports, tables, or actionable explanations.

Practical examples of what you can request span multiple operational domains:

* **Hardware audit and inventory**:
  * Show a list of computers with less than 16 GB of RAM.
  * What are the most common processor manufacturers and models in our computer fleet?
  * Identify computers that have more than one active network interface.
* **Software and deployment control**:
  * Which computers have the `nano` package installed and what version do they have?
* **Operational health and synchronization monitoring**:
  * Which computers haven’t synchronized with the server in over 30 days?
  * Analyze synchronization errors and failures recorded in the last 24 hours and summarize the main root causes.
  * Are there computers that started a synchronization but failed to finish it properly?
* **Segmentation, tags, and statistics**:
  * Generate a table showing the distribution of computers grouped by operating system, version, and architecture.
  * How many computers have the `FLV-LXDE` attribute assigned?
* **Documentation queries**:
  * Explain how migasfree works for a newcomer.
  * What does “fun with migasfree” say regarding a “fried egg”?
* **API queries**:
  * Which endpoint should I use to list projects, and what parameters does it accept?
  * Show an example using `curl` to authenticate via JWT token and query registered computers.
  * How is the JSON payload structured to create a new deployment via the API?
* **PostgreSQL database schema queries**:
  * Which tables store synchronization info and which foreign keys relate them to computers?
  * Describe the columns and data types of the computers table.
  * Which tables are related to hardware inventory?

With these capabilities, the assistant becomes a co-pilot capable of auditing the fleet, explaining the platform, and drafting diagnostics on the fly. To see how this server is used in operational incident troubleshooting, see [Chapter 22 (Observability)](chapter22.md#observabilidad-monitorizacion-y-resolucion-de-incidencias).

---

## 7. Practical Recipes & Deployment Playbooks

# Cookbook

This annex brings together a catalog of practical recipes to guide you through solving real-world scenarios, showing how to combine the various migasfree building blocks.

Although not an exhaustive catalog, these recipes provide the necessary mental and practical framework to approach systems management. To tackle them successfully, keep two key principles in mind:

* **Keep projects to a minimum**: Even though each recipe mentions a specific project, in real environments it is best to limit the number of projects to one per base distribution (such as Ubuntu 24.04 or Windows 11). Diversification by site, classroom, or department should be handled dynamically through **Attributes** and **Formulas**.
* **Follow a three-phase methodology**:
  1. **Client research**: First solve and validate the requirement on a test machine by identifying the affected commands and files.
  2. **Packaging**: Automate the solution by packaging it (as software or a formula) in the migasfree repository.
  3. **Deployment**: Design the server-side strategy by defining the targets (attributes and formulas) and execution schedule.

A final note: researching and packaging software takes time. Artificial Intelligence is an excellent ally to speed up both phases; take advantage of it without hesitation, while always ensuring full understanding and control over what you execute.

\\newpage

## Firefox ESR

* **Objective**: Ensure that all workstations have Firefox ESR configured with corporate bookmarks, telemetry disabled, and mandatory security extensions (such as uBlock Origin), without allowing the user to disable them.

  #### TIP
  You can copy and paste this objective directly into an AI agent: it will generate the appropriate `policies.json` file instantly. If anything fails or your Firefox version differs, describe the issue in the *prompt* and the AI will quickly adjust the structure.
* **Implementation with migasfree**:
  1. **Generating the policy file**: We create the browser’s `policies.json` file:
     ```json
     {
       "policies": {
         "DisableTelemetry": true,
         "DisableFirefoxStudies": true,
         "EnableTrackingProtection": {
           "Value": true,
           "Locked": true
         },
         "Bookmarks": [
           {
             "Title": "Portal del Empleado",
             "URL": "https://portal.acme.com",
             "Placement": "toolbar"
           }
         ],
         "ExtensionSettings": {
           "uBlock0@raymondhill.net": {
             "installation_mode": "force_installed",
             "install_url": "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi"
           }
         }
       }
     }
     ```
  2. **Packaging**: Create the `acme-firefox-policy_1.0_all.deb` package including this file so it gets installed at `/usr/lib/firefox-esr/distribution/policies.json`. Rely on what you learned in [Chapter 7](chapter07.md#empaquetado), where we created the `acme-test-files` package (or ask an AI agent to use `acme-test-files` as a base to generate it for you, but always make sure to understand its inner workings).
  3. **Release and deployment**: Upload the package to the server (`migasfree upload`) and assign it to the base deployment for all computers (`SET-All Systems`). On the next synchronization, all browsers will apply the policy in a unified and immutable manner.

  #### NOTE
  Keeping the packaging project in a version control repository (GitLab, GitHub, etc.) does not just centralize code: it provides complete historical traceability, eases teamwork, allows reverting any change in seconds, and opens the door to integrating CI/CD pipelines to build and upload packages automatically to multiple migasfree projects in a single run.

\\newpage

## Printers

* **Objective**: Ensure that any computer (laptop or desktop) automatically installs the `PRN-555` laser printer upon connecting to network segment 

  ```
  ``
  ```

  192.168.3.0/27\*\*.
* **Implementation with migasfree**:
  1. **formula**: The default server formula `Network` serves our purpose. When a computer connected to this segment synchronizes, the server automatically assigns it the attribute `NET-192.168.3.0/27`. We do not need to do anything here.
  2. **Association**: In **Devices > Devices**, edit printer `PRN-555` and, under its **Logical devices** section, assign the **Attribute** `NET-192.168.3.0/27` to the desired capabilities (e.g., Black/White and Duplex).
  3. **Automatic convergence**: Upon booting any computer, the migasfree client synchronizes, detects membership in the network segment, and installs the printer with its drivers and CUPS queues instantly, without technical intervention. If the computer later connects to another segment, that printer will be magically uninstalled.

  #### NOTE
  We achieved the objective by associating only the essential elements (the printer with the network segment), without having to craft complex rules or manual scripts. With migasfree you focus on the what, not the how.

\\newpage

## Zero-Day

* **Objective**: Following the publication of a critical vulnerability with an active exploit (*Zero-Day*) in OpenSSH ([RegreSSHion](https://www.qualys.com/2024/07/01/cve-2024-6387/regresshion.txt) - CVE-2024-6387, affecting versions **8.5p1 to 9.7p1**), automatically detect vulnerable computers and apply the urgent mitigation (`LoginGraceTime 0` in `sshd_config`).

* **Implementation with migasfree**:
  1. **Packaging the mitigation**: As a temporary workaround while the distribution releases the patched version, we create the package `acme-cve-2024-6387_1.0_all.deb`. It simply includes the file `/etc/ssh/sshd_config.d/00-cve-2024-6397.conf` in the package. Its contents will be:
     ```text
     LoginGraceTime 0
     ```

     In the package’s post-installation script (`postinst`), we restart the `sshd` service so that the new configuration takes effect immediately.
  2. **Detection formula**: We add a formula that evaluates the `openssh-server` package version on the client and creates the attribute `CVE-2024-6387` if found within the affected range:
     ```python
     from migasfree_client.utils import get_package_version

     version = get_package_version("openssh-server")[0]
     if version:
                 match = re.search(r'(\d+\.\d+)p\d+', version)
                 if match and 8.5 <= float(match.group(1)) < 9.8:
                    print('2024-6387~Vulnerable a RegreSSHion')
                    exit()

     print("None")
     ```
  3. **Deployment**: We upload the package to the server and create a deployment configuring the following parameters:
     * **Name**: `CVE-2024-6387`
     * **Project**: The one corresponding to our environment.
     * **Included attributes**: `CVE-2024-6387` (this indicates who is affected).
     * **Source**: Internal
     * **Available packages**: `acme-cve-2024-6387_1.0_all.deb` (to release the package).
     * **Packages to install**: `acme-cve-2024-6387` (to enforce its installation).
  4. **Synchronization**: We trigger the synchronization command from the web management console to the entire fleet. Only vulnerable workstations will apply the vaccine and restart `sshd` in real time.
  5. **Disabling**: Once the base distribution publishes the new package with the vulnerability fixed, the **Deployment** and **Formula** can be disabled to prevent unnecessary resource usage on both clients and server.

  #### NOTE
  By combining version detection formulas with the attribute assignment engine, you avoid modifying immune machines while maintaining precise control and traceability.

\\newpage

## Hardware Inventory (SSD vs. HDD)

* **Objective**: Obtain accurate fleet information by identifying which computers have solid-state drives (SSD) and which still retain rotational mechanical drives (HDD) to plan hardware renewal campaigns.
* **Implementation with migasfree**:
  1. **Inspection formula**: In **Configuration > Formulas**, we create a **List Class** formula named `Store` with prefix `STR` that inspects the computer’s disks and returns detected components separated by commas:
     ```python
     import glob
     import os

     disks = set()
     for disk in glob.glob('/sys/block/sd*') + glob.glob('/sys/block/nvme*'):
         # Ignorar dispositivos virtuales o bucles
         if os.path.exists(f'{disk}/queue/rotational'):
             try:
                 with open(f'{disk}/queue/rotational') as f:
                     if f.read().strip() == '1':
                         disks.add('HDD~Disco Mecánico')
                     else:
                         disks.add('SSD~Disco Estado Sólido')
             except OSError:
                 pass

     print(' , '.join(sorted(disks)))
     ```
  2. **Automatic inventory**: On the next synchronization, migasfree will automatically assign the corresponding attributes to the computer (e.g., if a machine has an SSD for the system and a secondary HDD for data, it will receive both attributes simultaneously).
  3. **List export**: Getting the precise list of computers still holding mechanical drives is as simple as navigating to **Configuration > Attributes**, editing the attribute `STR-HDD`, accessing its **Related Computers**, and exporting the result to a CSV file to work with in a spreadsheet.
  4. **Completion and cleanup**: Once the SSD replacement campaign is completed, the **Formula** can be disabled on the server to prevent unnecessary resource consumption during client synchronizations.

  #### NOTE
  By configuring the formula as **List Class**, the migasfree backend splits the comma-separated string returned by the script and increments/assigns each attribute independently. This allows recording hybrid configurations (SSD + HDD) cleanly and declaratively, facilitating quick list exports for decision making.

  #### TIP
  **Alternative with Artificial Intelligence and MCP**: Since the hardware inventory already resides in the migasfree database, a quick alternative is to ask an AI agent equipped with the migasfree MCP server directly. The assistant will generate and execute the appropriate SQL query in real time, returning the list to you without needing to create formulas.

\\newpage

## Proactive Health Diagnostics

* **Objective**: Proactively detect computers experiencing degradation in physical storage (disk S.M.A.R.T. attributes) before the user suffers data loss or service disruption, automatically notifying technical support.
* **Implementation with migasfree**:
  1. **Diagnostic script**: In **Configuration > Fault definitions**, we create a new definition named `Storage Health`. In the code field, we enter a Python script that audits disk S.M.A.R.T. counters:
     ```python
     import subprocess

     # Comprobación de salud S.M.A.R.T. si la utilidad smartctl está disponible
     try:
         res = subprocess.run(
             ['smartctl', '-H', '/dev/nvme0'],
             capture_output=True,
             text=True
         )
         if 'FAILED!' in res.stdout:
             print(
                 "ALERTA CRÍTICA: El disco /dev/nvme0 reporta fallos S.M.A.R.T. inminentes. "
                 "Acción: Programar sustitución física de la unidad de inmediato."
             )
     except FileNotFoundError:
         pass
     ```
  2. **Recipients and scope configuration**: We constrain execution by adding the included attribute `PLT-Linux`. Optionally, we assign the fault to the user profile group `Computer Checker` so that alerts reach the support technicians’ dashboard.
  3. **Silent evaluation and automatic alerting**: On each periodic synchronization, the client runs the test transparently:
     * If everything works correctly (exit code 0 and empty output), no alert is generated.
     * If an anomaly is detected, the script’s printed output is transmitted to the server, where it is logged under **Data > Faults** and increments the web console alert counter in real time.

  #### NOTE
  Unlike formulas (which classify computers by assigning them attributes), **Fault definitions** are designed to notify anomalies proactively. If the test passes, they generate no noise; if it fails, they immediately alert technicians indicating the root cause and suggested corrective action.

---

## 8. Technical Glossary

# Glossary

Alert
: Visual notice or notification log generated by the migasfree server for the administrator to give priority attention to a relevant event, technical fault, or operational drift on one or more fleet computers.

APK
: Alpine Package Keeper. Native, lightweight, and high-performance package manager used in Alpine Linux and in the MCS cloning system.

App Paths
: Microsoft Windows registry key where the WPT manager registers the primary application executables to allow clean invocation without polluting the PATH.

APT
: Advanced Package Tool. Standard high-level package manager in Debian and Ubuntu-based GNU/Linux distributions that resolves dependencies and interacts with deb repositories.

Apt-cacher-ng
: Specialized HTTP software package caching proxy server deployed in remote branch offices to drastically reduce WAN bandwidth consumption.

Attribute
: Concrete, evaluated, and typed value acquired by a formula after execution and introspection on a specific client computer during the synchronization cycle.

Attribute Set
: Declarative, reusable structure grouping multiple attributes with topological resolution, allowing complex operational profiles to be modeled while preventing circular dependencies.

Audit
: Systematic inspection, traceability, and continuous evaluation procedure regarding software changes, hardware status, and configurations applied across the fleet.

Auto-failover
: Automatic failover mechanism where a replica node immediately and transparently takes over the master node functions upon an unexpected failure.

AZLinux
: Corporate GNU/Linux distribution of the Zaragoza City Council based on Debian/Ubuntu and entirely managed with migasfree to support municipal workstations.

Base Deployment
: Highest-priority permanent deployment designed to establish the core, immutable operating system configuration across all linked machines.

Baseline
: Formal specification (*baseline*) or agreed set of SCI versions serving as a stable, frozen starting point for subsequent development or changes.

Bootstrap
: Initialization and autonomous initial installation process whereby the base management tool (such as `windows-package-tool`) is deployed onto a clean system to enable it to download and configure the rest of the suite.

CA
: Certificate Authority. Internal migasfree cryptographic entity responsible for issuing, signing, and revoking X.509 certificates for machines and services.

CCS
: Change Control System. Set of procedures and tools responsible for tracking, governing, validating, and auditing modifications made to systems and packages over time.

Celery
: Asynchronous task queue framework based on message passing used by migasfree to delegate heavy processing and concurrent synchronization to background workers.

Change
: Planned technical activity that modifies a Software Configuration Item (SCI), generating a new identifiable and traceable version within the change control system.

CID
: Computer Identifier. Unique, sequential, and immutable integer assigned by the server to a computer’s motherboard upon self-registration.

Closed-Loop Control
: Governance principle (*closed-loop governance*) according to which the actual state of client workstations is continuously and automatically inspected, reported, and remediated against the target state defined in server policies.

Command Whitelist
: Security directive (ALLOWED_COMMANDS) in `migasfree-agent` restricting remote executions exclusively to a closed, secure set of authorized binaries.

Computer Replacement
: Procedure whereby a new machine inherits the CID, attributes, history, and deployments of a replaced computer.

Computer Status
: Operational status assigned to a machine in the inventory (Assigned, Reserved, Unknown, In Repair, Available, or Decommissioned) governing its synchronization.

Configuration Package
: Software package (*config package*) specifically intended not to compile binaries, but to apply and version configuration directives, themes, or file diverts.

Convergence Cycle
: Sequential flow structured in phases (mTLS, introspection, directives, PMS execution, logical devices, and telemetry) executed by `migasfree-client` during each synchronization to align the workstation state with the server.

Core
: Central migasfree server microservice (built with Django) managing the data model, business logic, web administration console, and primary REST API.

CUPS
: Common UNIX Printing System. Standard modular print system and server for UNIX and Linux managed by migasfree to automatically deploy and configure print queues.

Datashares
: Shared storage volumes (local or NFS) where packages, software repositories, machine certificates, and server public keys are stored.

dd
: Classic UNIX utility for low-level block-by-block data copying and conversion, used in the MCS cloning engine.

Declarative Convergence
: Mechanism by which the migasfree client computes discrepancies between the computer’s current state and server directives, executing necessary package manager transactions to reach the target state without manual intervention.

Deployment
: Declarative directive associating a set of packages from a store with a target group of computers, conditioned by attributes, singularities, or tags.

Deployment Level
: Package assignment mode in a deployment determining whether installation is mandatory (Admin Level) or on-demand (User Level in migasfree-play).

Deployment Priority
: Numerical conflict-resolution criterion determining which deployment takes precedence when conflicting directives exist for the same package on a given computer.

Deployment Rollout Delay
: Time dispersion mechanism distributing the actual rollout of a deployment over a span of days, avoiding traffic spikes and WAN saturation.

Deployment Schedule
: Time rule establishing the start date, expiration date, and progressive rollout delay in days for the distributed application of a deployment.

Device Model
: Technical spec sheet in migasfree defining a specific peripheral along with its PPD drivers and supported configuration options.

Device Replacement
: Administrative action replacing a physical device with another, automatically inheriting its previous assignment and settings.

Disaster Recovery
: Planned set of technical procedures and policies aimed at restoring migasfree infrastructure, data, and service operations following a major disaster.

Domain
: Logical partition of the migasfree database isolating computer management and visibility according to delegated organizational or departmental scopes.

EFI Partition
: FAT32-formatted disk partition containing bootloader binaries for motherboards with UEFI architecture.

Error
: Syntax error, technical failure, or runtime exception detected during communication or package manager transactions on the client.

Fault
: Anomalous condition, functional issue, or system degradation actively detected on the client after evaluating a *Fault definition* directive.

File Diverts
: Packaging mechanism (*diverts*) allowing a corporate package to override an original OS configuration file without conflicting with the upstream maintainer’s package.

FileBrowser
: Web tool integrated into the operational consoles to visually browse, inspect, and manage files in migasfree shared storage.

Flower
: Real-time web monitoring console for Celery clusters allowing supervision of asynchronous task statuses, active workers, and execution rates.

Formula
: Executable code (Python or shell script) evaluated on the client workstation to inspect and return a specific hardware, software, or user attribute.

FQDN
: Fully Qualified Domain Name. Canonical, DNS-resolvable hostname of the migasfree server, essential for mTLS certificate validation.

GPG
: GNU Privacy Guard. Encryption and digital signature tool used by migasfree to cryptographically sign package repository metadata.

HAProxy
: High-performance load balancer and reverse proxy centralizing inbound traffic, SSL/TLS termination, and routing to stack microservices.

HOME Partition
: Dedicated disk partition (HOME.raw) storing users’ personal data and configurations decoupled from the operating system.

Idempotence
: Fundamental property whereby repeated execution of a configuration operation produces exactly the same system result without cumulative side effects.

Jaccard Distance
: Statistical dissimilarity metric for binary sets that evaluates actual coincidence while ignoring shared absences (*shared zeros bias*), ideal for comparing software inventories and attributes.

JWT
: JSON Web Token. Compact open standard used by migasfree for secure user and process authentication and authorization across the REST API.

Lens (TDA)
: Filter function or mathematical projection that reduces the dimensions of the fleet to examine it from a specific operational angle (health, obsolescence, software, migration, synchronization, or diversity).

Local Attribute
: Attribute calculated and stored locally in the client workstation database, used to optimize decision making without requiring continuous network queries.

Logical Device
: Abstract representation in migasfree of a physical peripheral (such as printers or scanners), decoupled from the specific computer it is connected to.

lshw
: Command-line utility for GNU/Linux generating a detailed hierarchical report on the computer’s physical components and hardware configuration.

lshw-windows-emulator
: Tool emulating the standard JSON output of `lshw` on Microsoft Windows systems, translating WMI/CIM hardware classes to enable homogeneous inventorying.

Machine Certificate
: X.509 cryptographic file (client.crt and client.key) securely and unambiguously binding a client workstation’s identity to the server’s corporate CA.

Manager
: High-performance microservice built with FastAPI responsible for reactive synchronization management, concurrency control, and remote tunnel orchestration.

Manufacturer
: Administrative entity cataloging supported commercial hardware and peripheral brands.

Mapper Algorithm
: Topological analysis method that transforms multidimensional data into a simplified graph through three stages: projection with a filter function (lens), overlapping region coverage, and clustering of similar elements into micro-clusters (nodes).

MCP
: Model Context Protocol. Interoperability protocol enabling AI models and agents to interact securely with migasfree data and APIs.

MCS
: Migasfree Clone System. Lightweight deployment OS based on Alpine Linux designed for master disk image cloning over network (HTTP streaming) or USB drive.

Metadata
: Structured data describing contents, dependencies, version, compatible architectures, and control directives of a package or software item.

MGI
: Migasfree Golden Image. Standardized, reproducible, and declarative golden master system image packaged as a base artifact for unattended cloning with MCS.

migasfree-agent
: Continuous background service establishing secure, mTLS-based reverse WebSocket tunnels with the server, enabling interactive remote support (SSH, VNC, RDP, web terminal).

migasfree-client
: Workstation synchronization engine responsible for negotiating secure mTLS channels, discovering inventory, evaluating directives, and converging state via the package manager.

migasfree-play
: Desktop graphical application (Electron, Vue, and Quasar) providing a corporate self-service app store where users install approved software.

migasfree-swarm
: Command-line orchestration tool to deploy, scale, back up, and manage the migasfree microservice cluster on Docker Swarm.

mTLS
: Mutual Transport Layer Security (*Mutual TLS*). Cryptographic protocol where both client and server authenticate each other using X.509 certificates.

NFS
: Network File System. Distributed file system protocol used in multi-node deployments to share data volumes among all swarm cluster nodes.

NSSM
: Non-Sucking Service Manager. Windows service wrapper used to run `migasfree-agent` as a native, resilient operating system service.

OpenAPI
: Standard, interactive specification for documenting and describing RESTful APIs (Swagger), accessible interactively at the server’s /docs path.

Operational Consoles
: Unified dashboard accessible at /status bringing together diagnostic tools, real-time metrics, and stack administration (Portainer, Flower, pgAdmin, RedisInsight).

Orphan Package
: Package hosted in a server store that is not linked to any active deployment.

Overlay
: Customization and script layer merged on top of the base system during MCS ISO image creation.

Package
: Standardized archive file (such as .deb, .rpm, .apk, or .wpt) encapsulating files, control scripts, and metadata ready for package manager processing.

Package Set
: Logical and versioned grouping of one or more packages within a store, designed to be assigned as a coherent atomic unit to software deployments.

Packaging Workstation
: Authorized workstation equipped with certificates and signing keys to upload packages to the server via the `migasfree upload` command.

Permanent Deployment
: Continuous deployment without an expiration date, ensuring assigned software and configurations remain active indefinitely across the fleet.

pgAdmin
: Web-based graphical administration and analytics environment for PostgreSQL database servers, integrated into development operational consoles.

Pgpool-II
: PostgreSQL middleware acting as a read query load balancer, connection pooling manager, and automatic failover switch.

Platform
: Definition of client operating system distribution and architecture (Debian, Ubuntu, Red Hat, Alpine, Windows) managed by a project.

PMS
: Package Management System. Native OS program (APT, DNF, Pacman, APK, WPT) responsible for resolving dependencies and installing software.

Portainer
: Container management web UI integrated into migasfree operational consoles to monitor resources and inspect live logs.

PostgreSQL
: Advanced transactional relational database management system used by migasfree as its primary structured data storage engine.

PPD
: PostScript Printer Description. Text file describing the capabilities, fonts, and advanced configuration options of a CUPS printer driver.

Project
: Primary organizational entity in migasfree defining the base OS, package stores, encryption keys, and directives for a fleet of workstations.

Python-Shell
: Node.js bridge module used in `migasfree-play` to safely run Python calls and commands from the Electron backend.

QEMU
: Hardware machine emulator and virtualizer used to test and validate golden master images and MCS cloning processes in dev environments.

RDP
: Remote Desktop Protocol. Microsoft remote desktop protocol natively supported through secure `migasfree-agent` tunnels on Windows workstations.

Redis
: In-memory data structure store used in the stack as a transactional caching datastore and messaging queue for Celery workers.

RedisInsight
: Interactive visual console for inspecting, memory analysis, and monitoring keys and queues in Redis.

Release
: Formal action of promoting and placing a specific package version into a software store, making it available for distribution via deployments.

REST API
: Application Programming Interface based on HTTP and REST principles, exposing migasfree resources and operations in JSON format for external integrations and automation.

Reverse Tunnel
: Secure communication channel initiated from the client towards port 443 of the server, allowing administrators remote access to the computer without opening local inbound ports.

Rolling Update
: Zero-downtime rolling update strategy where service replicas are replaced progressively without interrupting platform availability.

RPM
: RPM Package Manager. Standard package format and management system across the Red Hat distribution family (RHEL, Fedora, Rocky Linux).

RPO
: Recovery Point Objective. Metric of the maximum tolerable amount of data loss expressed in elapsed time since the last backup.

RTO
: Recovery Time Objective. Maximum allowable duration to restore full service operations following an outage.

SCI
: Software Configuration Item. Software entity (source code, configuration file, binary, or documentation) subject to SCM control, versioning, and tracking disciplines.

SCM
: Software Configuration Management (SCM). Software engineering discipline identifying, controlling, maintaining integrity, and auditing changes in computer systems throughout their lifecycle.

Scope
: Subset of computers defined within a domain to limit visibility, filtering, and delegated administration scope to specific operators.

Singularity
: Combined logical expression or boolean formula enabling surgical segmentation and identification of computer groups.

SMS
: Systems Management System. Comprehensive solution for managing, inventorying, configuring, and delivering software across computer fleets.

Store
: Centralized storage space and repository on the server hosting software packages and their control files (metadata) associated with a project, organized according to their release status.

Swarm
: Docker’s native clustering orchestration mode used by migasfree to coordinate high availability, load balancing, and microservice isolation.

System Formula
: Predefined formula built into the migasfree core to introspect universal hardware and operating system properties.

SYSTEM Partition
: Primary disk partition (SYSTEM.raw) hosting the OS root filesystem and applications in the MCS image structure.

Systemd Timer
: Native system timer used in Linux to schedule automatic `migasfree-client` synchronizations with randomized dispersion (*RandomizedDelaySec*).

Tag
: Administrative label (*tag*) assigned manually or automatically to a computer to classify it or dynamically condition deployment application.

Tag Category
: Taxonomic grouping used to classify and organize administrative tags (e.g., Sites, Departments, Classrooms, or User Profiles).

TDA
: Topological Data Analysis. Analytical methodology based on computational geometry that extracts the intrinsic shape of multidimensional datasets using the Mapper algorithm and projection functions (lenses).

Telemetry
: Set of performance metrics, usage statistics, status logs, and historical data gathered from each client during each sync session.

Temporary Deployment
: Deployment subject to a temporal schedule that automatically expires upon reaching its deadline, ideal for transient migration campaigns or one-off installations.

TLS/SSL Certificate
: Digital server certificate enabling HTTPS communication encryption and authenticating the web server’s FQDN to browsers and clients.

Topological Data Analysis
: See TDA.

Transactional Backup
: Consistent backup that preserves the exact state of relational databases (PostgreSQL) and in-memory structures (Redis) at a given point in time.

Triad
: Coordinated suite of the three migasfree client components (`migasfree-client`, `migasfree-agent`, and `migasfree-play`), covering configuration convergence, secure remote access, and the user self-service catalog, respectively.

Tunnel Multiplexing
: Technique used by `migasfree-agent` to carry multiple independent communication channels (control channels, SSH terminals, VNC or RDP sessions) over a single persistent WebSocket connection.

Turbo Clone
: High-speed cloning technique in MCS based on direct network streaming of raw disk images through pipeline streams (`wget | dd`).

User Formula
: Custom formula created by administrators to collect data or characteristics specific to the corporate or business environment.

User Profile
: Set of permissions and role restrictions assigned to a user account within the migasfree web management console.

UUID
: Universally Unique Identifier. 128-bit alphanumeric string used to unambiguously identify a client machine’s motherboard.

Virtualenv
: Isolated Python virtual environment (`venv`) encapsulating dependencies and interpreters independently of the host operating system.

Vitalinux
: Educational operating system of the Autonomous Community of Aragon based on Ubuntu and centrally governed via migasfree to support educational centers.

Wheel
: Standard binary packaging format for Python libraries (`.whl`), used by WPT to deploy dependencies in isolated virtual environments without compiling on the client machine.

WMI
: Windows Management Instrumentation. Microsoft Windows COM-based management and instrumentation infrastructure allowing inspection of hardware, devices, and OS state, used by `lshw-windows-emulator`.

WPT
: Windows Package Tool. Modular package manager for Microsoft Windows implementing isolated Python virtual environments (`venv`) and `App Paths` registry entries.

---
