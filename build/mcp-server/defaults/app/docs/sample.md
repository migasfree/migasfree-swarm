# Migasfree System Overview

Migasfree is a centralized software management system designed to manage large fleets of computers.

## Key Components

1. **Manager**: The web-based administrative interface.
2. **Core**: The backend API handling client communications.
3. **Database**: PostgreSQL storing all system state and inventory.
4. **Client**: The agent installed on managed computers.

## Data Flow

Clients synchronize with the Core API periodically. The Core API queries the Database to determine which software packages or configurations should be applied based on the client's attributes (tags).

---
*Created as a sample for the refactored MCP server.*
