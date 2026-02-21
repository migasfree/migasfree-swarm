# External PostgreSQL Configuration

Migasfree Swarm is designed to be hybrid. While it includes a built-in High Availability cluster (Pgpool-II + Streaming Replication), you can easily choose to use an external PostgreSQL instance (such as Amazon RDS, Google Cloud SQL, or a dedicated physical server).

## How to Configure

To use an external database, you only need to modify your `env.py` file. The system will detect the external host and automatically adjust the deployment.

### 1. Update `env.py`

Set the following variables in your stack configuration:

```python
# The IP or Domain Name of your external server
POSTGRES_HOST='10.0.0.50' 

# The port where your external database is listening
POSTGRES_PORT='5432'

# Database and User names
POSTGRES_DB='migasfree'
POSTGRES_USER='migasfree_db_user'

# Leave this EMPTY for external databases
PORT_DATABASE='' 
```

### 2. Manage the Secret (Password)

Even if the database is external, the application containers in Swarm need a way to read the password securely. You must ensure the Docker secret is created in your Swarm cluster:

```bash
# Example: Create the superadmin password secret
echo "my_external_db_password" | docker secret create <stack_name>_superadmin_pass -
```

## Deployment Behavior

When `POSTGRES_HOST` is set to anything **other than** `'pgpool'` or `'database'`:

1. **Service Exclusion**: The internal `database` (PostgreSQL) and `pgpool` services will **NOT** be deployed. This saves CPU and RAM on your cluster nodes.
2. **Direct Connection**: Services like `core`, `worker`, and `manager` will attempt to connect directly to the IP/FQDN provided in `POSTGRES_HOST`.
3. **No Internal Volume**: The `database` volume will not be created on your host nodes.

## Technical Requirements

* **Network Reachability**: The Swarm nodes must have network access to the external database IP. If your database is behind a firewall, ensure you allow traffic from all Swarm node IPs on the database port.
* **Authentication**: The external database must be configured to allow connections from the Swarm network (using MD5, SCRAM-SHA-256, etc.), and the user provided must have enough permissions to manage the Migasfree schema.
* **SSL/TLS**: If your external provider requires SSL (like RDS), ensure you configure the corresponding environment variables in Migasfree (if supported) or adjust the `POSTGRESQL_CONF` settings.

## When to use an External Database?

* **Managed Services**: When you want to offload backups, patching, and scaling to a provider (RDS/CloudSQL).
* **Pre-existing Infrastructure**: When your organization already has a centralized and hardened PostgreSQL cluster.
* **Resource Optimization**: To release resources in the Swarm cluster for application workloads.
