# Migasfree v4 to v5 Migration Guide

This guide provides precise, step-by-step instructions to safely migrate an existing migasfree Server version 4 installation (including databases, packages, and synchronization statistics) directly to the new migasfree-swarm cluster (version 5).

## Prerequisites

* Have the migasfree-swarm (v5) cluster deployed and running.
* Have network access and open ports from the Swarm *manager* node to the source database server (v4).
* **PostgreSQL port conflict:** If your migasfree v4 installation and the new v5 cluster (*migasfree-swarm*) will temporarily coexist on the same host machine, **you must change the published port of the v4 database container** (e.g., to `5433`), since version 5 needs to bind to port `5432`. If you use *migasfree-docker* for your v4 server, use these exact instructions to reassign the port and free up `5432`:

  ```bash
  # 1. Access the v4 deployment directory
  cd migasfree-docker/mf
  
  # 2. Modify your variables file to reflect the new port (5433 instead of 5432)
  sed -i 's/export POSTGRES_PORT=5432/export POSTGRES_PORT=5433/g' variables
  
  # 3. Reload variables and recreate the db container (data will persist)
  source variables
  docker-compose stop db
  docker-compose rm -f db
  docker-compose up -d db
  ```

* Know the origin server's PostgreSQL credentials (host, modified port, database name, user, and password).
* **Django Configuration file (`settings.py`):** If you had customized your production environment on v4, you will typically find this file at the host path `/var/lib/migasfree/conf/settings.py`. It is crucial that you review its manual variables. Many legacy configurations will break the container startup if you blindly clone them to the new environment. We recommend letting v5 automatically generate the base file (which it will place in the `conf/settings.py` directory inside your volume or *datashare* NFS) and only transcribing the strictly necessary extra adjustments (like LDAP, SMTP configurations, or `MIGASFREE_PACKAGER`).
* The v4 repositories (physical files under the v4 storage path, typically `/var/lib/migasfree/data/`) **must** be synchronized or mounted in the version 5 `migasfree-swarm` volume (so they are accessible in the `MEDIA_ROOT` of the `core` container) **before** launching the file migration.
* The `keys` directory from the v4 installation (typically located at `/var/lib/migasfree/keys/`) **must also be copied exactly as it is** to the corresponding `keys` directory in the version 5 shared volume. This preserves the cryptographic identity necessary for package signatures and client communications.

## Step 1: Database Migration (Relational)

The database migration imports PostgreSQL data (schemas, users, projects, devices, history, etc.) to the new version 5.

1. Open an OS terminal on the Swarm *manager* server where you cloned the `migasfree-swarm` repository.
2. Navigate to the migration scripts directory:

   ```bash
   cd migasfree-swarm/migration
   ```

3. Execute the `migrate-db.sh` script, passing the connection parameters for the v4 server's PostgreSQL database:

   ```bash
   bash migrate-db.sh <OLD_HOST> <OLD_PORT> [OLD_DB] [OLD_USER] [OLD_PWD]
   ```

   *Working Example:*

   ```bash
   bash migrate-db.sh 192.168.1.100 5433 migasfree migasfree mipassw0rd
   ```

4. The script will request security confirmation showing: `This process import the database from the v4 instance... Are you sure [yes/N]?`. Reply by typing `yes` and press Enter.

**What happens internally during this flow?**

* It will scale the `core` and `console` containers of your current cluster down to zero (0) replicas, temporarily disabling them to protect data import.
* Inside the `database` container (PostgreSQL) it will call the automated restore script from v4, creating and dumping everything natively.
* The stopped services (`core`, `console`) will scale back up to their original amount.
* As the final step in this block, the script accesses the new `core` container and uses the Django management-command `refresh_redis_syncs`. It will extract all historical dates from 2010 to present to internally repopulate crucial metrics and caches into the Redis ecosystem (prominently used for client stats in v5).
* Finally, as an automated extra step, the script will prompt: `Do you want to migrate packages and projects now? [yes/N]`. If the STORES directory was configured beforehand and you answer `yes`, the system will perform the entirety of **Step 2** fully automatically.

## Step 2: Repositories, Packages, and Package Sets Migration

Once the native metadata has been successfully stored in the database, we need to organize, reconfigure, and ensure the cryptographic integrity of the hard packages (.deb, .rpm) according to the v5 layout.

*(Note: if the `migrate-db.sh` script detected your `yes` response to the last question in the previous step, you can skip executing this step manually and jump directly to **Step 3**, as the system has completed it for you).*

1. Using Portainer or the local console on your Swarm manager, find the container ID of the v5 *Backend / Core* server and enter it using an interactive shell:

   ```bash
   docker exec -it <core_container_ID> bash
   ```

2. Once you have *root* access inside `core`, run the pre-installed global migration command:

   ```bash
   migrate-packages
   ```

   *(Technically, this binary activates Django's production environment variables and executes the file `/usr/bin/migrate_packages.py`).*

**What happens during the execution of this script?**

* **`update_projects()`:** Adjusts compatibilities for deprecated *PMS (Package Management System)* conventions favoring the current v5 core (e.g., standardizing `apt` subversions).
* **`migrate_structure()`:** Recursively finds the original directories formerly categorized under the hardcoded `STORES` directory and physically adapts them by modifying and moving their paths to match the strict v5 layout (`MIGASFREE_STORE_TRAILING_PATH`).
* **`migrate_packages()`:** This is the heaviest task in the loop. The explorer will identify each orphaned legacy deb/rpm, internally generate secure packaged signatures (JWE and JWS cipher using the current system packager key), and transparently simulate POST uploads towards the API itself (`/api/v1/safe/packages/`), thus restoring the package object.
* **`migrate_package_sets()`:** Rebuilds any packages of a project that were hermetically organized and encapsulated as part of fixed repositories (*Package Sets*). It will dispatch the REST API validation call updating these constraints.
* **`regenerate_metadata()`:** Asynchronously obligates the updated repositories (`Internal Sources`) to export their updated indexes and metadata in plain format, consistent with Linux standards. These indexes will subsequently allow client computers to discover these repositories over the network.

## Step 3: Cryptographic Refinement and Validation

Once both commands satisfactorily complete their processes, it is advisable to ensure consistency across the final ecosystem.

1. Exit your shell session inside the Backend container.
2. Graphically verify the administration consoles (`https://<FQDN>/services/status` and login to the base portal).
3. Log in as an Administrator and ensure your computers and repositories are listed without anomalies, including all their packages.
4. **User and Group Permissions Regeneration:** Even though user names and physical administrator groups have migrated perfectly in the database, **you must** visit the *Authentication and Authorization* menu (in the v5 Django central admin panel) and "re-save" (reassign/regenerate) the permissions granted to each group. This is imperative because the internal semantic structure of permissions used by Django has completely changed since the old v4 scheme, invalidating previous assignments.
5. Finally, it is a great time to ensure a client in the migasfree ecosystem can pair correctly (running a `migasfree --update`). If the client fails consulting the repository index, validate it by manually entering the *Worker* container to the *datashare* directory, where Linux indexes are built.
