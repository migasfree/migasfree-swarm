# ADR 0003: Decoupled, Multi-Protocol Package Management (PMS) Architecture

## Status

Accepted

## Context

Migasfree Swarm is designed to manage heterogeneous fleets including various Linux distributions (Debian-based, RHEL-based, Arch-based, etc.) and Windows. Each distribution relies on specific, and often conflicting, package management tools (GPG versions, metadata creators, compression libraries).

A monolithic approach where a single service handles all repository types would result in:

* **Dependency Hell**: Conflicting tool versions.
* **Bloated Images**: Large attack surface and slow deployments.
* **Poor Fault Isolation**: A failure in one repository generator could stall the entire system.

## Decision

We implement a **Decoupled PMS Architecture** where each Package Management System is treated as an independent, containerized microservice.

1. **Service Specialization**: Each repository protocol (APT, YUM, PACMAN, APK, etc.) has its own dedicated directory in `build/pms-<type>/` and its own container image.
2. **Core Logic Sharing**: All PMS containers leverage a multi-stage build to include a standardized Migasfree Python core, ensuring consistent interaction with the central package pool.
3. **Storage Federation**: All PMS services mount a shared `public` volume. While the files are shared, each service is only responsible for the metadata and signing of its own protocol sub-directories.
4. **Independent Orchestration**: Each PMS can be scaled or updated independently via the Swarm stack, allowing for side-by-side versions of the same protocol if necessary.

## Consequences

### Positive

* **High Extensibility**: Adding support for a new operating system or distribution only requires creating a new isolated container.
* **Fault Isolation**: A crash or metadata corruption in the APT service does not affect YUM or WPT clients.
* **Optimization**: Container images are kept minimal, containing only the tools specifically needed for that protocol.

### Negative

* **Resource Usage**: Running multiple containers increases the baseline memory and CPU overhead compared to a single process.
* **Configuration Complexity**: Requires managing multiple service definitions in the Swarm stack and ensuring consistent volume mounts across all nodes.

## References

* [ADR 0001: Root-Init, User-Run Pattern](0001-root-init-user-run-pattern.md)
* [PMS Builder (manager service)](../../build/manager/defaults/usr/bin/pms-builder.py)
