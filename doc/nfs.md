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


# Setting Up NFS Clients on Swarm Nodes

* To enable Swarm nodes to connect to the NFS server, you need to install the NFS client software on each node:

   ```bash
   apt install nfs-common
   ```
  This will allow the nodes to access the shared NFS directory.

With these steps, your NFS server and clients should be properly set up for communication within the Swarm cluster. If you have more than one node or additional network considerations, adjust the firewall settings and exports as needed.