# Setting Up an NFS Server

To configure an NFS (Network File System) server on a machine `outside the Swarm cluster` (i.e., a non-cluster node):

1. First, install the NFS server package and create the directory where the shared data will be stored:

   ```bash
   # Run as root
   apt install nfs-kernel-server

   mkdir -p /exports/migasfree-swarm
   ```

2. Next, you need to configure the directories that will be shared with the cluster nodes. Edit the `/etc/exports` file to include the following line:

   ```txt
   /exports/migasfree-swarm 172.0.0.0/24(rw,sync,no_subtree_check,anonuid=0,anongid=0)
   ```

   This example exports the /exports/migasfree-swarm directory to all hosts in the 172.0.0.0/24 network range, with read/write permissions (rw) and synchronous data transfer (sync).

3. Apply the new export settings and restart the NFS service:

   ```bash
   exportfs -ra

   # check
   exportfs

   # Restart service NFS
   systemctl restart nfs-kernel-server
   ```

4. Now, you need to allow access to the NFS server from the nodes in the Swarm cluster. Use the following commands to update the firewall settings:

   ```bash
   nodes=("172.0.0.10" "172.0.0.11" "172.0.0.12")
   for node in "${nodes[@]}"
   do
      sudo ufw allow from $node to any port nfs
   done

   # Or all network 172.0.0.0/24
   # ufw allow from 172.0.0.0/24 to any port nfs
   ```

  This ensures that all nodes in the specified network range can communicate with the NFS server.

## Setting Up NFS Clients on Swarm Nodes

* To enable Swarm nodes to connect to the NFS server, you need to install the NFS client software on each node:

   ```bash
   apt install nfs-common
   ```

  This will allow the nodes to access the shared NFS directory.

## Migrating from Local to NFS

If you started with a single-node cluster using `DATASHARE_FS='local'` and now want to scale to a multi-node cluster using NFS, the `migasfree-swarm` script provides an automated migration path.

## 1. Prerequisites

1. **Backup your data**: Although the script handles the data copy, it is highly recommended to create a manual backup of your local data before proceeding. You can simply copy the content of the local volume:
    `cp -a /var/lib/docker/volumes/migasfree-swarm/_data /your/backup/path`
2. Set up the **NFS Server** as described in the first section of this document.
3. Install the **NFS Client** on **all** nodes (including the current manager).
4. Ensure the manager node can reach the NFS server. You can verify this with:

    ```bash
    # Check if NFS port is open
    nc -zv <NFS_SERVER_IP> 2049

    # Or check exports from the server
    showmount -e <NFS_SERVER_IP>
    ```

## 2. Migration Procedure

1. **Edit Configuration**: Open your `env.py` file and update the variables to point to your new NFS server:

    ```python
    DATASHARE_FS='nfs'
    DATASHARE_SERVER='<NFS_SERVER_IP>'
    DATASHARE_PATH='/exports/migasfree-swarm'
    DATASHARE_PORT='2049'
    ```

2. **Run Deployment**: Execute the deploy command:

    ```bash
    ./migasfree-swarm deploy
    ```

3. **Automatic Detection**: The script will detect the change in `DATASHARE_FS` and prompt you:
    * `Detected change in DATASHARE_FS mode from local to nfs`
    * `Do you want to keep the data? (y/n)`

4. **Confirm**:
    * Select **`y`** to automatically copy all existing data (certificates, dumps, stacks) from the local disk to the NFS server.
    * The script will stop the stack, create the new NFS-backed volume, copy the data, and restart the services.

## 3. Post-Migration

Once the migration is complete, you can add more worker nodes to the cluster. Every new node will automatically mount the same NFS volume, ensuring data consistency across the entire swarm.

With these steps, your NFS server and clients should be properly set up for communication within the Swarm cluster. If you have more than one node or additional network considerations, adjust the firewall settings and exports as needed.
