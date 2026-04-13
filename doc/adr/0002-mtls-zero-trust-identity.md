# ADR 0002: Enforcement of Mutual TLS (mTLS) for Zero-Trust Identity

## Status

Accepted

## Context

Migasfree Swarm manages critical infrastructure and computer fleets. Standard authentication methods (passwords, tokens) are vulnerable to credential theft, brute-force, and lack of strong identity verification for automated agents. In a cloud or distributed environment, the network can no longer be trusted as a security boundary (Zero-Trust).

We need a scalable and highly secure mechanism to:

1. Authenticate administrative users accessing internal consoles.
2. Authenticate managed computers (agents) during synchronization and tunnel establishment.
3. Ensure that only trusted clients can initiate requests to the Migasfree core.

## Decision

We enforce Mutual TLS (mTLS) as the primary security layer for all sensitive communications.

1. **Integrated CA**: The `manager` service is designated as the internal Certificate Authority (CA), responsible for the entire lifecycle (generation, signing, and revocation) of client certificates.
2. **Mandatory Verification**: The `proxy` (HAProxy) is configured to require and verify valid client certificates for endpoints under the `/manager/v1/private/` path and other administrative consoles.
3. **Identity Scoping**: Certificates are issued with specific roles encoded in the Common Name (CN) or SAN, differentiating between `admin` and `computer` (agent) identities.
4. **Decoupled Key Management**: We prioritize methods (like the one-time URL generator) that allow clients to generate their own private keys, ensuring that the private key never traverses the network or the server.

## Consequences

### Positive

* **Zero-Trust Security**: Strong identity verification for every connection. Even with network access, an attacker cannot interact with the management layer without a valid certificate.
* **Revocation Support**: Compromised clients can be immediately neutralized by revoking their certificate at the CA level.
* **Non-Repudiation**: Every action in the system is linked to a cryptographic identity verified at the protocol level.

### Negative

* **Operational Overhead**: Requires managing a PKI, handling rotations, and ensuring the root CA key is adequately protected.
* **Bootstrapping Complexity**: Initial deployment requires a multi-step process to issue the first administrative certificate.
* **Client Dependencies**: Clients must support mTLS and have the local ability to store and present certificates securely.

## References

* [Certificate Management Reference](../reference/certificates.md)
* [ADR 0001: Root-Init, User-Run Pattern](0001-root-init-user-run-pattern.md)
