#!/usr/bin/python3

import os
import subprocess
import sys
import docker

from context import get_stacks


def print_section(title):
    print(f"\n\033[1m{title}\033[0m")
    print("=" * len(title))


def get_service_container(client, stack, service_name):
    full_service_name = f"{stack}_{service_name}"
    # Try by swarm service label first
    containers = client.containers.list(
        filters={
            "label": f"com.docker.swarm.service.name={full_service_name}",
            "status": "running",
        }
    )
    if containers:
        return containers[0]

    # Fallback: search by name
    containers = client.containers.list(filters={"name": f"{full_service_name}."})
    for c in containers:
        if c.status == "running":
            return c

    return None


def show_usage(stacks):
    print("Error: Missing stack name.")
    print("Usage:\n  migasfree-swarm backup <stack> [filename]\n")
    if stacks:
        print("Available stacks:")
        for s in stacks:
            print(f"  - {s}")
    else:
        print("No deployed stacks found in cluster.")


def main():
    stacks = get_stacks()

    if len(sys.argv) < 2:
        show_usage(stacks)
        sys.exit(1)

    stack = sys.argv[1]
    if stack not in stacks:
        print(f"Error: Stack '{stack}' not found.")
        if stacks:
            print(f"Available stacks: {', '.join(stacks)}")
        sys.exit(1)

    filename = sys.argv[2] if len(sys.argv) > 2 else "migasfree"
    base_name = filename
    if base_name.endswith((".sql", ".rdb")):
        base_name = base_name.rsplit(".", 1)[0]

    sql_file = f"{base_name}.sql"
    rdb_file = f"{base_name}.rdb"

    try:
        client = docker.from_env()
    except Exception as e:
        print(f"Error connecting to Docker: {e}")
        sys.exit(1)

    print_section(f"Backing up stack '{stack}'")
    print(f"Target files: {sql_file}, {rdb_file}")

    # 1. Backup PostgreSQL database
    print("\n--- [1/2] PostgreSQL (database) ---")
    db_container = get_service_container(client, stack, "database")
    if not db_container:
        print(f"Warning: Service '{stack}_database' is not running on this node.")
    else:
        print(f"Running backup on container '{db_container.name}'...")
        res = subprocess.run(["docker", "exec", db_container.id, "/usr/bin/backup", sql_file])
        if res.returncode != 0:
            print(f"Error during PostgreSQL backup (code {res.returncode})")

    # 2. Backup Redis datastore
    print("\n--- [2/2] Redis (datastore) ---")
    ds_container = get_service_container(client, stack, "datastore")
    if not ds_container:
        print(f"Warning: Service '{stack}_datastore' is not running on this node.")
    else:
        print(f"Running backup on container '{ds_container.name}'...")
        res = subprocess.run(["docker", "exec", ds_container.id, "/usr/bin/backup", rdb_file])
        if res.returncode != 0:
            print(f"Error during Redis backup (code {res.returncode})")

    dump_dir = f"/mnt/cluster/datashares/{stack}/dump"
    print_section("Backup Summary")
    print(f"Dump directory: {dump_dir}")
    if os.path.exists(f"{dump_dir}/{sql_file}"):
        size = os.path.getsize(f"{dump_dir}/{sql_file}")
        print(f"  ✓ {sql_file} ({size} bytes)")
    if os.path.exists(f"{dump_dir}/{rdb_file}"):
        size = os.path.getsize(f"{dump_dir}/{rdb_file}")
        print(f"  ✓ {rdb_file} ({size} bytes)")
    print()


if __name__ == "__main__":
    main()
