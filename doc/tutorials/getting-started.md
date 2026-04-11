# Getting Started (Tutorial)

This tutorial guides you through the process of deploying Migasfree Swarm for the first time on a single Swarm manager node.

## Prerequisites

* A Linux machine with Docker installed.
* DNS or `/etc/hosts` configured (see [Requirements](../reference/requirements.md)).

## Step 1: Initialize Configuration

Create a dedicated directory for your stack and run the configuration tool:

```bash
mkdir migasfree-cluster && cd migasfree-cluster

docker run --detach=false --rm -ti \
  -v $(pwd):/stack \
  -v /var/run/docker.sock:/var/run/docker.sock \
  migasfree/swarm:5.0-beta15 config
```

During configuration, select `local` if you are testing on a single node:

```txt
DATASHARE_FS (local | nfs): local
```

## Step 2: Download Images

Pull the necessary container images for the stack:

```bash
./migasfree-swarm pull
```

## Step 3: Deploy the Stack

Deploy the Migasfree microservices:

```bash
./migasfree-swarm deploy
```

Follow the prompts to initialize the Swarm manager if your system isn't already part of a cluster.

## Step 4: Verify Deployment

Monitor the status of your services by visiting:
`https://<YOUR_FQDN>/services/status`

## Step 5: Secure Your Credentials

Retrieve the automatically generated administrative passwords:

```bash
./migasfree-swarm secret
```

> [!TIP]
> Use these credentials to access the administrative consoles shown at the bottom of the status page.
