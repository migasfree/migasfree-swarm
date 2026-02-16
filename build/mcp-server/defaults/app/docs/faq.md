# ❓ Frequently Asked Questions (FAQ)

Welcome to the FAQ. Here you will find answers to the most common questions and solutions to frequent issues.

## � Table of Contents

- [🔌 Connection Issues](#connection-issues)
  - [TLS Certificate Verification Error](#tls-certificate-verification-error)
  - [MCP Client Error: Method Not Allowed](#mcp-client-error-method-not-allowed)
- [⚙️ Configuration](#configuration)
- [🗄️ Database](#database)
- [💻 Migasfree Client](#migasfree-client)
  - [Sync Error: 404](#sync-error-404)
  - [TLSV1_ALERT_UNKNOWN_CA](#tlsv1_alert_unknown_ca)
- [🤖 Migasfree Agent](#migasfree-agent)
  - [Manager Error: 403](#manager-error-403)
  - [CERTIFICATE_VERIFY_FAILED](#certificate_verify_failed)

---

## Connection Issues

### TLS Certificate Verification Error

**Problem:**  
You encounter an error similar to:  
`calling "initialize": rejected by transport: sending "initialize": Post "https://<FQDN>/mcp/sse": tls: failed to verify certificate: x509: certificate signed by unknown authority.`

**Solution:**  
This error indicates that the MCP client cannot verify the server's SSL/TLS certificate. This typically happens when the certificate is self-signed or not issued by a trusted Certification Authority (CA).

To resolve this, you must manually install the server's certificate on the system where the client is running:

1. **Extract the certificate from the server:**
    Run the following command (replace `<FQDN>` with your server's address):

    ```bash
    openssl s_client -showcerts -connect <FQDN>:443 < /dev/null | openssl x509 -outform PEM > /usr/local/share/ca-certificates/<FQDN>.crt
    ```

2. **Update the system's CA certificates:**
    Inform the operating system of the new certificate:

    ```bash
    update-ca-certificates
    ```

### MCP Client Error: Method Not Allowed

**Problem:**  
You encounter an error similar to:  
`Error: calling "initialize": sending "initialize": Method Not Allowed.`

**Solution:**  
This error occurs because the client's IP address or network is not authorized to access the MCP server.

To resolve this, you must authorize the specific IP or network by editing the `.env` configuration file in your swarm environment and updating the `NETWORK_MCP` variable:

```bash
# In 'https://datashare-<FQDN>/files/env.py edit the `NETWORK_MCP` variable 

# ------------------------------------------------------------------------------------------------------------------------
# NETWORK_MCP
# Networks or hosts that are permitted to access the MCP server
# Default value: 127.0.0.1 (local access only)
# You can add multiple IPs or networks separated by spaces
# Set to 0.0.0.0/0 to allow access from anywhere (not recommended without other security)
# ------------------------------------------------------------------------------------------------------------------------
NETWORK_MCP='<CLIENTS_IPS>'
```

---

## Configuration

*Placeholder for configuration related questions.*

---

## Database

*Placeholder for database related questions.*

---

## Migasfree Client

### Sync Error: 404

**Problem:**  
The client synchronization fails with an error similar to:

```bash
ERROR - url_request - _error_response - url_request server error response code: 404
```

**Solution:**
This error typically occurs when the server's encryption keys have been reset or changed (for example, if the `migasfree-swarm` volume on the server was deleted or recreated).

To resolve this issue, you must delete the obsolete keys on the client machine. This will allow the client to perform a fresh key exchange during the next synchronization:

```bash
rm -rf /var/migasfree-client/keys
```

### TLSV1_ALERT_UNKNOWN_CA

**Problem:**  
You encounter an error similar to:

```bash
WARNING - connectionpool - urlopen - Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(1, '[SSL: TLSV1_ALERT_UNKNOWN_CA] tlsv1 alert unknown ca (_ssl.c:2649)')': /api/v1/public/server/info/
```

**Solution:**

The mTLS certificate is incorrect or has expired. This can happen if the server certificate has been changed or if the client has not downloaded the certificate correctly.

```bash
rm -rf /var/migasfree-client/mtls
migasfree sync
```

---

## Migasfree Agent

### Manager Error: 403

**Problem:**  
You encounter an error similar to the following when checking the agent logs (e.g., `journalctl -u migasfree-agent.service -f`):

`ERROR - Manager error: 403 Client Error: Forbidden for url: https://<FQDN>/manager/v1/private/tunnel/register`

**Solution:**  
This error is typically caused by an invalid or expired mTLS certificate on the agent side.

To resolve this, delete the existing certificate and force a new download by performing a fresh synchronization:

```bash
rm -rf /var/migasfree-client/mtls
migasfree sync
systemctl restart migasfree-agent
```

### CERTIFICATE_VERIFY_FAILED

**Problem:**  
You encounter an error similar to:

```bash
ERROR - Connection error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1029)```

**Solution:**

The mTLS certificate is incorrect or has expired. This can happen if the server certificate has been changed or if the client has not downloaded the certificate correctly.

```bash
rm -rf /var/migasfree-client/mtls
migasfree sync
systemctl restart migasfree-agent
```
