# Certificate Management (Reference)

Migasfree Swarm supports three methods for securing communication via TLS.

## 1. Self-Signed (Development Only)

Automatically generated on first startup.

* **Path**: `/var/lib/docker/volumes/migasfree-swarm/_data/certificates/<STACK>.pem`
* **Limitation**: Triggers browser security warnings.

## 2. Automatic (Let's Encrypt) - Recommended

Requires port 80 accessibility to handle ACME challenges.

**To Enable**:

1. Open the **Datashare Console**.
2. Set `HTTPSMODE = 'auto'` in `env.py`.
3. Redeploy: `./migasfree-swarm redeploy`

## 3. Manual Replacement

For organizations providing their own trusted CA certificates.

**File Structure**: A combined PEM file containing the full certificate chain and private key.
**Path**: `/var/lib/docker/volumes/migasfree-swarm/_data/certificates/${STACK}/server/${FQDN}.pem`

**Sample Command**:

```bash
# Combine chain and key
cat cert.pem intermediate.pem key.key > /path/to/shared/volume/server/${FQDN}.pem
chmod 600 /path/to/shared/volume/server/${FQDN}.pem
./migasfree-swarm redeploy_all
```

---

## Mutual TLS (mTLS) for Identity

mTLS adds a layer of identity verification for administrative consoles and secure agent communication.

**To Enable**:

1. Set `MTLS = 'True'` in `env.py`.
2. Redeploy: `./migasfree-swarm redeploy`

### Generating Certificates

#### 1. Via One-Time URL (Recommended for Admins)

Generating a one-time URL allows an administrator to create their own certificate securely from their browser.

```bash
./migasfree-swarm url-admin-certificate
```

#### 2. Manual Generation (Advanced/Computers)

The project uses a unified script `create_cert_mtls.sh` (located in the `manager` service) to generate client certificates manually.

**For Administrators**:

```bash
docker exec -it $(docker ps -q -f name=manager) \
  /usr/bin/create_cert_mtls.sh admin <FQDN> <HOST> <STACK> <NAME> <PASSWORD>
```

**For Computers (Agents)**:

```bash
docker exec -it $(docker ps -q -f name=manager) \
  /usr/bin/create_cert_mtls.sh computer <FQDN> <HOST> <STACK> <NAME> <PASSWORD>
```

The resulting `.tar` bundle will be available in `/mnt/cluster/certificates/<STACK>/<TYPE>/certs/`.

---

## Corporate Proxy Inspection

If your network uses a proxy that inspects HTTPS traffic via a private Root CA:

1. Copy your corporate Root CA to the `ca-certificates` folder in the **Datashare Console**.
2. Redeploy: `./migasfree-swarm redeploy`
