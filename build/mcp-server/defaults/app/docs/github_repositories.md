# 🐙 GitHub Repositories

This document lists all the official repositories of the Migasfree project on GitHub, categorized by their function and purpose.

## 🏗️ Core System

These repositories contain the central components of the Migasfree infrastructure (Servers, Backend, Frontend).

| Repository | Description |
| :--- | :--- |
| **[migasfree-backend](https://github.com/migasfree/migasfree-backend)** | **Systems Management System (Backend)**. Core application built with Django that provides the REST API and business logic. |
| **[migasfree-frontend](https://github.com/migasfree/migasfree-frontend)** | **Systems Management System (Frontend)**. Modern web interface built with the Quasar framework for managing the Migasfree server. |
| **[migasfree-swarm](https://github.com/migasfree/migasfree-swarm)** | **Docker Swarm Deployment**. Complete stack for deploying the Migasfree Server Suite 5 on a Docker Swarm cluster. Includes orchestration configurations. |

## 💻 Clients & Agents

These components run on the managed devices to communicate with the server.

| Repository | Description |
| :--- | :--- |
| **[migasfree-client](https://github.com/migasfree/migasfree-client)** | **GNU/Linux Client**. The classic client for Linux systems. Handles package management, hardware inventory, and policy execution. |
| **[migasfree-agent](https://github.com/migasfree/migasfree-agent)** | **Cross-Platform Agent**. New generation agent (likely Go or Rust based depending on recent changes) creating a persistent WebSocket connection for real-time management. Supports Linux and Windows. |
| **[migasfree-connect](https://github.com/migasfree/migasfree-connect)** | **Remote Connection Tool**. Facilitates remote access to managed devices, integrating with the Migasfree ecosystem. |
| **[migasfree-play](https://github.com/migasfree/migasfree-play)** | **Client App Store UI**. User-friendly frontend for the client that allows users to install/uninstall available applications and verify devices. |

## 🧰 Tools & Utilities

Helper tools for specific platforms or tasks.

| Repository | Description |
| :--- | :--- |
| **[migasfree-imports](https://github.com/migasfree/migasfree-imports)** | **Data Import tools**. Scripts and utilities to import external deployments and devices into the Migasfree database. |
| **[windows-package-tool](https://github.com/migasfree/windows-package-tool)** | **Windows Package Manager**. Simplified package management system designed specifically for Windows devices managed by Migasfree. |
| **[lshw-windows-emulator](https://github.com/migasfree/lshw-windows-emulator)** | **Windows Hardware Lister**. A port of the `lshw` project for Windows, based on WMI, to report hardware inventory to the server. |

## 📚 Documentation & Ecosystem

Resources for learning, standards, and community content.

| Repository | Description |
| :--- | :--- |
| **[ai-rules](https://github.com/migasfree/ai-rules)** | **AI Standards & Rules**. Defines the coding standards, workflows, and prompts for AI agents (like Antigravity) working on the Migasfree project. |
| **[fun-with-migasfree](https://github.com/migasfree/fun-with-migasfree)** | **Project Documentation**. A collection of guides, tutorials, and fun documentation resources. |
| **[migasfree.github.io](https://github.com/migasfree/migasfree.github.io)** | **Official Website**. Source code for the Migasfree project website. |
