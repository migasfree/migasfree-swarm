# ❓ Frequently Asked Questions (FAQ)

Welcome to the FAQ. Here you will find answers to the most common questions and solutions to frequent issues.

## � Table of Contents

- [🔌 Connection Issues](#connection-issues)
  - [TLS Certificate Verification Error](#tls-certificate-verification-error)
  - [MCP Client Error: Method Not Allowed](#mcp-client-error-method-not-allowed)
- [⚙️ Configuration](#configuration)
- [🗄️ Database](#database)

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
