# Data Persistence (Explanation)

In Docker, volumes provide data persistence by allowing data generated and used by containers to be stored outside the container's lifecycle. Even if a container is deleted or recreated, volumes persist on the host’s filesystem.

## Volume Types in Migasfree Swarm

Migasfree Swarm utilizes three primary volumes:

### 1. Database & Datastore (Local)

These volumes are restricted to specific Swarm nodes for performance reasons:

* **`database` volume**: Stores the PostgreSQL database.
* **`datastore` volume**: Stores the Redis database.

**Node Labels**: You can control the placement of these volumes using Docker labels:

* `database=true`: Label for the PostgreSQL node.
* `datastore=true`: Label for the Redis node.

> [!NOTE]
> Only **one instance** of each of these volumes can exist in the cluster at a time.

### 2. Migasfree-Swarm (Shared)

The `migasfree-swarm` volume stores certificates, Portainer data, credentials, and software repositories. It can be configured in two ways:

* **Local Backend**: Used for testing or single-node clusters (`DATASHARE_FS=local`).
* **NFS Backend**: Used for multi-node production setups (`DATASHARE_FS=nfs`).

## Volume Identification

When listing volumes with `docker volume ls`, identify them by the stack prefix (default is `inv`):

```text
DRIVER    VOLUME NAME
local     inv_database
local     inv_datastore
local     migasfree-swarm
```
