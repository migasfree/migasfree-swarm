# Deployment & Management (How-to)

Advanced operational guides for managing your Migasfree Swarm stack.

## Service Lifecycle

* **Update Configuration**: Edit `env.py` and run `./migasfree-swarm deploy`.
* **Update Code/Images**: Run `./migasfree-swarm pull` followed by `./migasfree-swarm deploy`.
* **Clean Up Images**: Run `./migasfree-swarm prune` to remove dangling `<none>` images.
* **Check Status**: Run `./migasfree-swarm info` to see the cluster and stacks overview.
* **Stop Infrastructure**: Run `./migasfree-swarm undeploy`.

## Console Management

Migasfree provides several consoles for development and production.

### Development Mode

Enable all consoles (Database, Datastore, Worker, Datashare):

```bash
./migasfree-swarm consoles-dev
```

### Production Mode

Disable sensitive consoles (Database, Datastore, Worker) while keeping the public status and core services:

```bash
./migasfree-swarm consoles-pro
```

### Remote Access Security

By default, all administrative consoles are restricted to `127.0.0.1` for security. To access them from your management network, edit `env.py` and set `NETWORK_MNG`:

```python
# env.py
NETWORK_MNG = '192.168.1.0/24'  # Allow your local network
```

Then redeploy the stack:

```bash
./migasfree-swarm deploy
```

## Scaling the Cluster

### Adding Worker Nodes

Run this on the **Manager** node:

```bash
./migasfree-swarm join-worker
```

Copy and paste the resulting command onto your worker nodes.

### Leaving the Swarm

To gracefully remove a node from the cluster without deleting local volumes:

```bash
./migasfree-swarm leave
```

## Monitoring the Cluster

To get a comprehensive overview of your Swarm cluster status, including nodes and deployed stacks:

```bash
./migasfree-swarm info
```

This command provides:
*   **Swarm Status**: Role of the local node, total nodes, and manager count.
*   **Node details**: Hostname, status (Ready/Down), and availability.
*   **Stacks overview**: List of deployed stacks, their access URLs, and service health (running/total).

## Image Maintenance

To manually build images from source:

```bash
cd build
bash build.sh
```

The build script will provide a **BUILD SUMMARY** at the end, listing successes and failures.

To build specific images:

```bash
bash build.sh core database manager
```

### Cleaning Up Images

Docker builds and pulls can leave "dangling" images (tagged as `<none>`) that consume disk space. To safely remove them:

```bash
./migasfree-swarm prune
```

> [!NOTE]
> This command only removes images that are not tagged and not used by any container.

To list available images:

```bash
bash build.sh --list
```
