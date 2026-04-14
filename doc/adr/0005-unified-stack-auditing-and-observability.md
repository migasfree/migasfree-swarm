# ADR-0005: Unified Stack Auditing and Observability

## Status

Accepted

## Context

As the Migasfree Swarm infrastructure scales from single-node to multi-node clusters with multiple stacks, administrators lose visibility into:

1. **Node Health**: Roles and status of members in the cluster.
2. **Stack Exposure**: Access URLs (FQDNs) and associated services.
3. **Execution State**: Which services are truly running vs. merely desired.

Relying on raw `docker node ls` and `docker stack services` requires manual correlation and high expertise.

## Decision

We decided to implement a **Unified Auditing CLI Tool** (`info`) that provides a correlated view of the cluster and stack state.

1. **Technology Choice**: Python + `docker` SDK (Official).
   * Provides consistent, structured access to Swarm metadata without parsing variable shell output.
2. **Integration**: Embedded in the `swarm` management image.
   * Accessible via `./migasfree-swarm info`.
3. **Output Structure**:
   * **Cluster Level**: Node count, manager role, and readiness.
   * **Stack Level**: Correlation between `FQDN` (from `env.py`) and actual service replicas.

## Consequences

### Positive

* **Immediate Visibility**: Single command to verify if a deployment was successful across all layers.
* **Lower Cognitive Load**: No need to memorize complex Docker formatting strings.
* **Auditability**: Provides a snapshot that can be piped to logs for governance.

### Negative

* **Image Size**: Adding the `docker` python library increases the size of the `swarm` management image (negligible compared to its value).
* **Dependency**: Relies on the Docker socket being correctly mounted (which is already a requirement for management).

## Alternatives Considered

* **Prometheus/Grafana**: Too heavy for simple infrastructure auditing; remains as a "Higher Level" monitoring option.
* **Shell-based awk/sed scripts**: Rejected due to fragility and poor readability when dealing with complex JSON metadata.
