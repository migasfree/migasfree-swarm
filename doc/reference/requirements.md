# System Requirements (Reference)

Before deploying Migasfree Swarm, ensure your infrastructure meets the following hardware, software, and networking requirements.

## 1. Hardware Requirements

* **RAM**: >= 16 GB
* **CPU**: >= 4 cores
* **Disk (System)**: >= 80 GB
* **Disk (Data/NFS)**: >= 1 TB recommended for production.

## 2. Software Requirements

* **OS**: Linux (supporting Docker Swarm).
* **Docker Engine**: Latest stable version installed on each node.
* **Kernel Configuration**: `vm.overcommit_memory=1` must be set on the node running Redis.
  * Add `vm.overcommit_memory=1` to `/etc/sysctl.conf` and reboot.

## 3. Networking & DNS

### FQDN Configuration

Choose a Fully Qualified Domain Name (e.g., `migasfree.mydomain.com`). In a production environment, you must register the following subdomains in your organization's DNS server to resolve to the Swarm manager's IP:

* `<FQDN>`
* `portainer-<FQDN>`
* `datastore-<FQDN>`
* `database-<FQDN>`
* `datashare-<FQDN>`
* `worker-<FQDN>`

### Local Name Resolution (/etc/hosts)

If you are testing or developing locally and do not have access to a DNS server, you must manually define resolution for these domains on the client computers by adding them to the `/etc/hosts` file. Remember that this IP address must match the IP of your Swarm manager:

For example, if FQDN = `migasfree.acme.com` and the IP is `172.0.0.30`, then:

```text
172.0.0.30 migasfree.acme.com
172.0.0.30 portainer-migasfree.acme.com
172.0.0.30 database-migasfree.acme.com
172.0.0.30 datashare-migasfree.acme.com
172.0.0.30 datastore-migasfree.acme.com
172.0.0.30 worker-migasfree.acme.com
```

> [!TIP]
> **Windows Clients**: To map these domains on Windows 10/11 client computers, see the [Windows Client Access Guide](../how-to/windows-client-access.md).

## 4. Storage Backend (NFS)

In multi-node production environments, an NFS server is mandatory.

* See [NFS Installation Guide](../nfs.md) for detailed setup.
* The `migasfree-swarm` shared volume will use this NFS backend.
