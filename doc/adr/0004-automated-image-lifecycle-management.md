# ADR-0004: Automated Image Lifecycle Management

## Status

Accepted

## Context

In a Docker Swarm environment, particularly during active development or frequent updates, "dangling" images (untagged layers) accumulate rapidly. This causes:

1. **Disk Exhaustion**: Nodes can run out of space, leading to deployment failures.
2. **Operational Noise**: `docker image ls` becomes cluttered with `<none>` entries.
3. **Registry Inconsistency**: Unnecessary layers occupy space in local caches.

Previously, image cleaning was a manual task for the administrator.

## Decision

We decided to implement an **Automated Pruning Strategy** integrated into the core lifecycle scripts and provided a manual gateway via the CLI.

1. **Integrated Pruning**:
   * `build.sh`: Automatically runs `docker image prune -f` after successfully building the stack images.
   * `pull.sh`: Automatically runs `docker image prune -f` after pulling updated images for the stack.
2. **On-Demand Pruning**:
   * Added `migasfree-swarm prune` command to the management entrypoint to allow administrators to safely trigger cleanup across nodes.

## Consequences

### Positive

* **Zero-Maintenance Cleaning**: Administrators no longer need to worry about dangling images after routine updates.
* **Predictable Disk Usage**: Deployment volatility is reduced.
* **Cleaner Audits**: Image lists only show tagged, meaningful artifacts.

### Negative

* **Loss of Intermediate Layers**: Developers cannot easily inspect intermediate layers of failed builds if they were untagged.
* **Network Overhead (Minor)**: If an image is pruned and then immediately needed again (unlikely in this context), it must be re-downloaded/re-built.

## Alternatives Considered

* **Cron jobs on host nodes**: Rejected because it adds host-level configuration requirements outside the Swarm control.
* **External Cleanup Tools**: Rejected to keep the `migasfree-swarm` toolset self-contained.
