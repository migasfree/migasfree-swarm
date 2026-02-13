# Connecting to the Migasfree MCP Server

This document explains how to connect Antigravity (or any other MCP-compatible client) to the Migasfree MCP server.

## 1. Network Access Configuration

For security reasons, MCP server access is restricted to local connections by default. To allow external connections, you must configure the allowed IP ranges in your stack configuration.

### Variable to Configure

In your stack's `env.py` file (or via the `./migasfree-swarm config` command), locate or add the following variable:

```python
NETWORK_MCP='YOUR_IP_OR_RANGE'
```

**Examples:**

- Allow a specific IP: `NETWORK_MCP='192.168.1.50'`
- Allow a network range: `NETWORK_MCP='192.168.1.0/24'`
- Allow multiple origins: `NETWORK_MCP='172.16.0.0/16 80.24.1.2/32'`
- Open to everyone (⚠️ NOT RECOMMENDED): `NETWORK_MCP='0.0.0.0/0'`

After changing this value, you must redeploy to apply the changes to the proxy (HAProxy):

```bash
./migasfree-swarm deploy
```

## 2. Client Connection (Antigravity)

The Migasfree MCP server uses the **SSE (Server-Sent Events)** protocol to allow connections through networks and proxies.

### Connection URL

The URL to configure in your client is:

```
https://<YOUR_FQDN>/mcp/sse
```

### Self-Signed Certificates

If the Migasfree server uses a self-signed certificate, the machine running the MCP client must have the CA certificate installed.

Example:

```bash
# The public certificate from the certification authority is required.
wget --no-check-certificate -O /usr/local/share/ca-certificates/ca-inv.org.crt https://inv.org/pool/install/ca-inv.org.crt
update-ca-certificates --fresh
```

### Configuration in Antigravity

If you are manually configuring Antigravity using a JSON configuration file, the structure would look like this:

```json
{
  "<STACK>": {
    "migasfree": {
      "serverUrl": "https://<YOUR_FQDN>/mcp/sse"
    }
  }
}
```

*Note: The server implementation uses FastAPI to handle POST messages at `/mcp/messages` and the event stream at `/mcp/sse`.*

## 3. Available Tools

Once connected, you will have access to the following tools:

1. **`db_query`**: Execute SQL `SELECT` queries directly on the Migasfree database.

### Resources

In addition to tools, the MCP server exposes valuable **documentation resources** that provide context to the AI:

- **User Manual**: Comprehensive guide on using Migasfree (`docs/migasfree-user-manual.md`).
- **Architecture**: High-level system overview (`docs/migasfree_architecture.md`).
- **Database Schema**: detailed DB structure (`docs/db_schema.md`).
- **API Documentation**: OpenAPI specifications for integration.

---
*For additional support, refer to the technical documentation in the migasfree-swarm repository.*
