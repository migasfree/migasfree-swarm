# ADR 0001: Root-Init, User-Run Pattern

## Status

Accepted

## Context

In the Migasfree Swarm infrastructure, several services (such as `proxy`, `database-console`, and `datastore-console`) require dynamic initialization during the container startup phase. These tasks include:

* Correcting file ownership (`chown`) for certificates mounted from the host or secrets.
* Initializing local volumes with specific folder structures.
* Performing system-level setup (e.g., certificate generation or validation) that requires administrative privileges.

Standardizing on a static non-root user in the Dockerfile (`USER 1000`) prevents these initialization scripts from functioning correctly when host permissions do not match the container's internal UID/GID mapping, especially in diverse deployment environments (Production vs. Testing).

## Decision

We implement the **Root-Init, User-Run** pattern across the infrastructure.

1. **Dockerfile**: Containers remain with `USER root` (or omit the `USER` instruction, defaulting to root) to allow the entrypoint script to execute with full privileges.
2. **Entrypoint**: The `docker-entrypoint.sh` performs all necessary root-only setup tasks (certificates, permissions, volume checks).
3. **Privilege Drop**: Upon completion of setup, the entrypoint transitions to the application user (e.g., `haproxy`, `pgadmin`, `www-data`) using a secure execution wrapper or service-specific mechanism.

## Consequences

### Positive

* **Deployment Flexibility**: Containers automatically adapt to host volume permissions without manual intervention.
* **Simplified Certificate Management**: Standardizes the handling of mTLS certificates across the cluster.
* **Operational Robustness**: Reduces initialization failures in air-gapped or restricted environments where UID/GID synchronization is difficult.

### Negative

* **Security Scanning**: Explicit `USER root` declarations are flagged by security linters (e.g., Hadolint) as a high-risk violation of best practices.
* **Implementation Complexity**: Requires robust and standardized entrypoint scripts (already implemented in `common.sh`) to ensure the privilege drop is never bypassed.
