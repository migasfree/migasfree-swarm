# 📚 Documentation Index

Welcome to the Migasfree documentation center. Below is a list of all available resources that help you navigate and understand the system:

| Resource | Type | URI | Description |
| --- | --- | --- | --- |
| **migasfree-ai-cheatsheet.md** | 🤖 AI Reference | `{MCP_SERVER_URI}docs/migasfree-ai-cheatsheet.md` | **Semantic Technical Reference for AI Agents**: Dense, zero-redundancy technical specification of Migasfree v5 (Architecture, Swarm, Configuration, REST API, CLI, Troubleshooting). **Recommended primary reading for AI models** before the full user manual due to token efficiency. |
| **api_core.md** | 🌐 API Reference | `{MCP_SERVER_URI}docs/api_core.md` | **Core API Reference**: Comprehensive documentation of the backend API endpoints used for client communication, synchronization, and system management. Essential for understanding how the Migasfree agent interacts with the server. |
| **api_manager.md** | 🌐 API Reference | `{MCP_SERVER_URI}docs/api_manager.md` | **Manager API Reference**: Detailed guide to the administrative API used by the web interface. Useful for automating management tasks and understanding the backend logic of the dashboard. |
| **db_schema.md** | 🗄️ Database Schema | `{MCP_SERVER_URI}docs/db_schema.md` | **Database Schema (Full)**: The complete PostgreSQL database structure, including table definitions, column types, and relationships. **Crucial for writing accurate SQL queries** with the `db_query` tool. |
| **migasfree-user-manual.md** | 📖 User Manual | `{MCP_SERVER_URI}docs/migasfree-user-manual.md` | **Official User Manual ("Fun with Migasfree")**: The complete, unabridged reference guide in Markdown. Contains detailed conceptual explanations, step-by-step walkthroughs, and end-to-end administration workflows. Use when deep background or narrative tutorials are required. |
| **migasfree_architecture.md** | 🏗️ Architecture | `{MCP_SERVER_URI}docs/migasfree_architecture.md` | **Architecture Guide**: Detailed overview of the Migasfree ecosystem, components (Server, Clients, Tools), and data flow diagrams. |
| **github_repositories.md** | 🐙 Ecosystem | `{MCP_SERVER_URI}docs/github_repositories.md` | **GitHub Repositories**: A complete catalog of all official Migasfree repositories (Backend, Frontend, Clients, Agents, Tools) with descriptions and links. |
| **faq.md** | ❓ FAQ | `{MCP_SERVER_URI}docs/faq.md` | **Frequently Asked Questions**: Quick solutions to common issues, such as SSL/TLS connection errors and client configuration. |

---

## 💡 How to use these resources

* **For AI Agents & Fast Technical Queries**: Start with **`migasfree-ai-cheatsheet.md`** for concise, high-density architecture, config parameters, and operational specs.
* **For Database Queries**: Always consult **`db_schema.md`** first to identify the correct table names and relationships.
* **For API Integrations**: Use **`api_core.md`** and **`api_manager.md`** to find the correct endpoints and parameters.
* **For In-Depth Reading & User Guides**: Consult **`migasfree-user-manual.md`** when deep narrative context, complete background, or end-user step-by-step guides are needed.

*Note: Use the tool `read_resource(uri="...")` to access the full content of any of these documents.*
