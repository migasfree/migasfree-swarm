# PostgreSQL Deployment Strategies

Migasfree Swarm offers three distinct strategies for database deployment, controlled by the `POSTGRES_HOST` variable in your `env.py`.

## Comparison Matrix

| Strategy | `POSTGRES_HOST` Value | Internal Services | Best For... | Key Advantage |
| :--- | :--- | :--- | :--- | :--- |
| **High Availability** | `'pgpool'` | `database` + `pgpool` | **Production Clusters** | Load balancing & Auto-failover |
| **Direct Internal** | `'database'` | `database` only | **Single Node / Dev** | Minimal overhead (no pgpool) |
| **External DB** | `IP` or `FQDN` | None | **Managed Services** | Amazon RDS, CloudSQL, or Physical servers |

---

## 1. High Availability (The 'pgpool' Mode)

This is the **default and recommended** mode for production Swarm clusters.

* **How it works**: The application talks to Pgpool-II, which intelligently routes writes to the Primary node and reads to Replicas.
* **Benefits**:
  * Connection pooling (faster connections).
  * Transparent failover.
  * Automatic reintegration of recovered nodes (Auto-Attach).
* **Documentation**: See [PostgreSQL Replication Guide](./postgresql_replication.md)

## 2. Direct Internal (The 'database' Mode)

A simpler internal setup where the application bypasses the gateway.

* **How it works**: The application connects directly to the `database` service. In a multi-node cluster, Docker Swarm will route traffic to any available database instance.
* **Caveat**: It does not distinguish between Primary and Replicas. If Docker routes a write request to a Standby node, it will fail.
* **Benefits**: Lowest latency and resource usage for simple, single-node deployments.

> **WARNING**: This mode should **ONLY** be used in Swarm clusters consisting of a **single node**. In multi-node environments, the lack of role-aware routing will lead to random write failures on Standby instances. For multi-node production, always use the `pgpool` strategy.

## 3. External Database (The 'Cloud' Mode)

Offload the database management to a specialized provider.

* **How it works**: Migasfree Swarm will not deploy any database containers. Your application will connect directly to the provided external host.
* **Benefits**:
  * Saves CPU/RAM in the Swarm cluster.
  * Leverages managed backup and scaling solutions.
* **Documentation**: See [External Database Configuration](./external_database_configuration.md)

---

## Decision Flowchart

1. **Do I have a managed DB (RDS/CloudSQL)?**
    * Yes → Use **Strategy 3 (External)**.
2. **Is this a multi-node cluster for production?**
    * Yes → Use **Strategy 1 (High Availability)**.
3. **Is this a small server or personal dev environment?**
    * Yes → Use **Strategy 2 (Direct Internal)**.
