# Backups & Disaster Recovery (How-to)

Ensuring data safety is critical. This guide explains how Migasfree Swarm handles database dumps and how to perform a full restore.

## Backup Frequency & Dumps

Both **PostgreSQL** (Database) and **Redis** (Datastore) are automatically backed up as dumps in the shared `migasfree-swarm` volume.

* **Location**: `https://datashare.<FQDN>/files/dump/` (or locally at `/mnt/cluster/datashares/<STACK>/dump/`)
* **Files**: `migasfree.sql` (PostgreSQL) and `migasfree.rdb` (Redis).
* **Configuration**: The `BACKUP_CRON` variable in `stack.conf` defines the frequency (default: daily at midnight).

## Performing Manual Dumps with the CLI

You can trigger manual database and datastore dumps at any time using the `migasfree-swarm` CLI:

```bash
# Generate default dumps (migasfree.sql and migasfree.rdb)
migasfree-swarm backup <stack>

# Generate dumps with a custom filename (e.g., 20260814.sql and 20260814.rdb)
migasfree-swarm backup <stack> 20260814
```

## Performing a Full Backup

To perform a complete backup of your Migasfree instance, you must copy the underlying shared volume data:

* **If NFS**: Copy the exported folder from the NFS server.
* **If Local**: Copy the folder `/var/lib/docker/volumes/migasfree-swarm/_data`.

## Disaster Recovery (Restoring Data)

If you encounter catastrophic data loss, follow these steps to restore from your dump files:

1. **Stop the Stack**:

    ```bash
    migasfree-swarm undeploy <stack>
    ```

2. **Clean Volumes**: Remove existing (corrupted) database and datastore volumes:

    ```bash
    docker volume rm <stack>_database <stack>_datastore
    ```

3. **Redeploy**: Start the stack with empty databases:

    ```bash
    migasfree-swarm deploy <stack>
    ```

4. **Execute Restore**: Restore the dumps directly using the CLI:

    ```bash
    # Restore default dumps (migasfree.sql and migasfree.rdb)
    migasfree-swarm restore <stack>

    # Or restore a specific dump (e.g., 20260814.sql and 20260814.rdb)
    migasfree-swarm restore <stack> 20260814
    ```
