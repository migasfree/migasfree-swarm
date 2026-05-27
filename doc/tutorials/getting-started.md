# Getting Started (Tutorial)

This tutorial guides you through the process of deploying Migasfree Swarm for the first time on a single Swarm manager node.

## Prerequisites

* A Linux machine with [Docker Engine](https://docs.docker.com/engine/install/) installed (we highly recommend installing it via the official Docker repository to ensure compatibility and updates).
* DNS or `/etc/hosts` configured (see [Requirements](../reference/requirements.md)).
* **Root privileges** (make sure to switch to the root shell by running `sudo -i` or `su -` before starting, as all commands in this tutorial must be executed as root).

## Step 1: Install CLI Tool

Extract the unified CLI tool from the Docker container to install it system-wide:

```bash
docker run --rm --entrypoint cat migasfree/swarm:master /tools/migasfree-swarm > /usr/bin/migasfree-swarm && chmod +x /usr/bin/migasfree-swarm
```

Now the `migasfree-swarm` command is globally available!

## Step 2: Initialize Configuration

Run the configuration tool. This will automatically create `/etc/migasfree-swarm/` and configure your cluster:

```bash
migasfree-swarm config
```

During configuration, select `local` if you are testing on a single node:

```txt
DATASHARE_FS (local | nfs): local
```

## Step 3: Download Images

Pull the necessary container images for the stack:

```bash
migasfree-swarm pull
```

## Step 4: Deploy the Stack

Deploy the Migasfree microservices:

```bash
migasfree-swarm deploy
```


Follow the prompts to initialize the Swarm manager if your system isn't already part of a cluster:

```txt
STACK (): acm
FQDN (migasfree.acme.com): 

Warning! This system is not a Swarm node.
Do you want to create a manager node? (Y/n): y
```
## Step 5: Verify Deployment

Monitor the status of your services by visiting:
`https://<YOUR_FQDN>/status`

## Step 6: Secure Your Credentials

Retrieve the automatically generated administrative passwords:

```bash
migasfree-swarm secret
```

> [!TIP]
> Use these credentials to access the administrative consoles shown at the bottom of the status page.
