# Backups & Disaster Recovery (How-to)

Ensuring data safety is critical. This guide explains how Migasfree Swarm handles database dumps and how to perform a full restore.

## Backup Frequency

Both **PostgreSQL** (Database) and **Redis** (Datastore) are automatically backed up as dumps in the shared `migasfree-swarm` volume.

* **Location**: `https://datashare.<FQDN>/files/dump/`
* **Files**: `migasfree.sql` (PostgreSQL) and `dump.rdb` (Redis).
* **Configuration**: The `BACKUP_CRON` variable in `env.py` defines the frequency.

## Performing a Full Backup

To perform a complete backup of your Migasfree instance, you must copy the underlying shared volume data:

* **If NFS**: Copy the exported folder from the NFS server.
* **If Local**: Copy the folder `/var/lib/docker/volumes/migasfree-swarm/_data`.

## Disaster Recovery (Restoring Data)

If you encounter catastrophic data loss, follow these steps to restore from your dump files:

1. **Stop the Stack**:

    ```bash
    ./migasfree-swarm undeploy
    ```

2. **Clean Volumes**: Remove existing (corrupted) database and datastore volumes:

    ```bash
    docker volume rm <STACK>_database <STACK>_datastore
    ```

3. **Redeploy**: Start the stack with empty databases:

    ```bash
    ./migasfree-swarm deploy
    ```

4. **Execute Restore**: Access the shell of the `database` and `datastore` containers via Portainer or `docker exec`, and run:

    ```bash
    restore
    ```

    This command will ingest the dump files from the shared volume into the new containers.
