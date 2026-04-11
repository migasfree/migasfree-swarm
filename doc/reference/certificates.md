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

## Mutual TLS (mTLS) for Admins

mTLS adds a layer of identity verification for administrative consoles.

**To Enable**:

1. Set `MTLS = 'True'` in `env.py`.
2. Redeploy: `./migasfree-swarm redeploy`

**Client Access**:
Generate a certificate URL for admins:

```bash
./migasfree-swarm url-admin-certificate
```

---

## Corporate Proxy Inspection

If your network uses a proxy that inspects HTTPS traffic via a private Root CA:

1. Copy your corporate Root CA to the `ca-certificates` folder in the **Datashare Console**.
2. Redeploy: `./migasfree-swarm redeploy`
