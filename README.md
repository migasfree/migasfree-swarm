# Migasfree Swarm

Migasfree Swarm is the containerized infrastructure implementation of the **Migasfree Server Suite 5** designed to run on [Docker Swarm](https://docs.docker.com/engine/swarm/).

> [!IMPORTANT]
> **Security First**: This project implements a Zero Trust model with non-root execution, mTLS identity, and encrypted overlay networks.

## 📚 Documentation (Diátaxis)

Our documentation is structured following the Diátaxis framework to help you find precisely what you need:

### 🚀 Tutorials (Learning-Oriented)

* **[Getting Started](doc/tutorials/getting-started.md)**: Deploy your first Migasfree stack in 5 minutes.

### 🛠️ How-to Guides (Goal-Oriented)

* **[Deployment & Management](doc/how-to/deploy-and-manage.md)**: Manage service lifecycles and scale your nodes.
* **[Backups & Recovery](doc/how-to/backups-and-recovery.md)**: Secure your data and perform disaster recovery.
* **[NFS Installation](doc/nfs.md)**: Setup shared storage for multi-node production clusters.
* **[Windows Client Access](doc/how-to/windows-client-access.md)**: Configure Windows 10/11 machines to use the console.

### 📖 Reference (Information-Oriented)

* **[System Requirements](doc/reference/requirements.md)**: Hardware, software, and networking specs.
* **[Configuration Variables](doc/reference/env-variables.md)**: Detailed reference for `env.py` and customization variables.
* **[Certificate Management](doc/reference/certificates.md)**: Configuring SSL, Let's Encrypt, and mTLS.
* **[Consoles Guide](doc/consoles.md)**: Overview of the administration interfaces.
* **[MCP Connection](doc/mcp_connection.md)**: Connect your development tools to the swarm.
* **[Migration from v4](doc/migration_v4_to_v5.md)**: Detailed steps for legacy upgrade.

### 🧠 Explanation (Understanding-Oriented)

* **[Architecture Overview](doc/explanation/architecture.md)**: Deep dive into the Swarm stack design.
* **[Data Persistence](doc/explanation/data-persistence.md)**: How volumes and shared storage work.

---

## 🏗️ Project Structure

* `build/`: Source code and Dockerfiles for images.
* `doc/`: Full documentation repository.
* `images/`: Utilities for handling pre-built Docker images.
* `migration/`: Scripts for migrating from version 4.
* `test/`: Automated testing environments.

## 🤝 Contributing

Please refer to our **[Todo List](doc/todo.md)** for current development goals and open tasks.

---
**License**: GPLv3
**Version**: 5.0
