# 📊 Metrics Dashboard Guide

This dashboard provides real-time visibility into cluster health, database performance, and Migasfree synchronization processes.

## 📡 Tab: Synchronizations

Focused on backend performance and task processing capacity.

* **Server Status**:
  * `HEALTHY`: The system is operating within normal limits.
  * `SATURATED`: Security thresholds have been exceeded (CPU > 90% or DB Latency > 0.1s). In this state, the system pauses new synchronizations to protect stability.
* **Core CPU Avg**: Average CPU load of the containers running the Migasfree engine (`inv_manager`).
* **Sync Attempts**: Number of synchronization attempts processed per minute. Red bars indicate periods of saturation.

## ⛁ Tab: Database Cluster

Focused on PostgreSQL performance and load balancing (Pgpool-II).

### Global Metrics

* **Gateway Latency**: Response time (in seconds) for a simple query through Pgpool. A value > 0.1s usually indicates cluster congestion.
* **DB CPU Load**: Combined average CPU load of all database nodes.

### Cluster Status (Node Details)

| Metric | Description |
| :--- | :--- |
| **Role** | `PRIMARY` (Master - Read/Write) or `STANDBY` (Replica - Read Only). |
| **Status** | `Online` (Running) or `Offline` (Node down or disconnected from the cluster). |
| **CPU** | Individual CPU usage of the host hosting the database. *Colors: Orange (>50%), Red (>80%).* |
| **Replic. Lag** | Data distance (in Bytes) that the replica has pending to process. 0 B is perfect synchronization. |
| **Reads (QPM)** | Successful read queries per minute. |
| **Writes (WPM)** | Write operations (Insert/Update/Delete) per minute. These should only appear on the `PRIMARY` node. |
| **DB Errors (EPM)** | Database errors per minute. If > 0, the value is highlighted in red. |

## 🛠️ Interpretation FAQ

**Why does the replica CPU show a hyphen (-)?**
It means the Manager was unable to contact the Portainer Agent on that remote node. The cluster is still functional, but CPU telemetry for that specific node is unavailable at that moment.

**What does a Replica Lag of "0 B" mean?**
It is the ideal state. It means any data written to the Master is already available on the Replica to be read, with no delay.

**How are QPM/WPM/EPM calculated?**
These metrics are calculated by the Manager by comparing Pgpool-II's cumulative counters between two successive samples (every 15 seconds by default).
