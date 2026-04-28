# AGENTS.md

> **Context for AI Agents working on `migasfree-swarm`**
> This file provides the essential context, commands, and conventions for AI agents to work effectively on this project.

## 1. Project Overview

**migasfree-swarm** is the orchestration and deployment framework for the Migasfree Systems Management System using Docker Swarm. It manages the entire lifecycle of Migasfree stacks, including service deployment, scaling, secrets management, and data migration.

- **Orchestration**: Docker Swarm
- **Language**: Bash (Orchestration scripts) / Python 3.x (Deployment logic)
- **Infrastructure**: Proxy (HAProxy), Core (Django), Manager (FastAPI), Database (PostgreSQL), Cache (Redis).
- **Storage**: Local volumes or NFS cluster.
- **Migration**: Specialized scripts for v4 to v5 data transition.

## 2. Setup & Commands

The main entry point for orchestration is the `migasfree-swarm` script. Its location is user-defined (e.g., `~/swarm/migasfree-swarm` or `./migasfree-swarm`). In the examples below, `<SWARM>` represents the path to this script.

- **Deploy Stack**: `<SWARM> deploy`
- **Undeploy Stack**: `<SWARM> undeploy`
- **Redeploy Service**: `<SWARM> redeploy <service_name>`
- **Build Image**: `./build.sh [--no-cache] <service_name>` (Run from the `build/` directory)
- **Check Status**: `<SWARM> info`
- **Configure Cluster**: `<SWARM> config`
- **Enable Dev Consoles**: `<SWARM> consoles-dev`

## 3. Code Style & Conventions

- **Bash Scripts**: Must be robust, idempotent, and follow shellcheck best practices where possible. Use `set -e` carefully.
- **Python Tools**: Follow PEP 8. Use `httpx` for async API calls and `docker` SDK for container management.
- **Dockerfiles**: Use multi-stage builds and minimize image size. Use Alpine as the base image when possible.
- **Service Defaults**: Configuration templates and default files are stored in `build/<service>/defaults/`.

## 4. Architecture Standards

- **`build/`**: Contains the build context for every service in the stack.
  - `defaults/`: Replicated into the container image root.
- **`migration/`**: Logic for database and file migrations.
  - `migrate-v4-to-v5.sh`: Orchestrates the full migration flow.
- **`doc/`**: Technical documentation and migration guides.
- **Secrets**: Managed via Docker Secrets. Never hardcode credentials.

## 5. Available Skills & Specialized Constraints

This project is supported by specialized AI Skills. **ALWAYS** check and use these skills:

- **Docker & Swarm**: `docker-expert` (Orchestration, healthchecks, networking)
- **PostgreSQL**: `postgresql-expert` (Database migrations, optimization)
- **Bash & Scripting**: `bash-expert` (Idempotent deployment scripts)
- **Python Language**: `python-expert` (Deployment tools and logic)
- **Security**: `security-expert` (Secrets management, network hardening)
- **Documentation**: `docs-expert` (Architecture guides, migration docs)

## 6. Critical Rules

1. **Environment Integrity**: Always respect `STACK` and `FQDN` environment variables.
2. **Idempotency**: All deployment and migration scripts MUST be idempotent.
3. **Internal vs Public**: When communicating between services in the swarm, ALWAYS use internal service names (e.g., `http://core:8080`) instead of public FQDNs.
4. **Data Safety**: Never perform destructive operations in `migration/` without explicit backups or confirmation.
5. **Pagination Aware**: Any tool interacting with the Migasfree API must handle pagination correctly (see `core_client.py` implementation).
