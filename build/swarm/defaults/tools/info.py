#!/usr/bin/python3

import docker
import os
import sys
from context import ContextLoader, get_stacks


def get_swarm_info(client):
    info = client.info()
    swarm = info.get("Swarm", {})
    return {
        "Status": swarm.get("LocalNodeState", "inactive"),
        "NodeID": swarm.get("NodeID", ""),
        "IsManager": swarm.get("ControlAvailable", False),
        "Nodes": info.get("Swarm", {}).get("Nodes", 0),
        "Managers": info.get("Swarm", {}).get("Managers", 0),
    }


def print_section(title):
    print(f"\n\033[1m{title}\033[0m")
    print("=" * len(title))


def main():
    try:
        client = docker.from_env()
    except Exception as e:
        print(f"Error: Could not connect to Docker: {e}")
        sys.exit(1)

    swarm = get_swarm_info(client)

    print_section("Swarm Cluster Status")
    print(f"  Status:     {swarm['Status']}")
    if swarm["Status"] == "active":
        print(f"  Node Role:  {'Manager' if swarm['IsManager'] else 'Worker'}")
        print(f"  Nodes:      {swarm['Nodes']} ({swarm['Managers']} managers)")

        # Nodes Detail
        print("\n  Nodes Detail:")
        print(
            f"    {'ID':<26} {'Hostname':<20} {'Role':<10} {'Status':<10} {'Availability':<12}"
        )
        for node in client.nodes.list():
            attrs = node.attrs
            spec = attrs.get("Spec", {})
            status = attrs.get("Status", {})
            desc = attrs.get("Description", {})

            print(
                f"    {node.id:<26} {desc.get('Hostname', ''):<20} {spec.get('Role', ''):<10} {status.get('State', ''):<10} {spec.get('Availability', ''):<12}"
            )

    # Stacks Info
    print_section("Deployed Stacks")
    stacks = get_stacks()
    if not stacks:
        print("  No stacks found.")
    else:
        cl = ContextLoader()
        for stack in stacks:
            os.environ["STACK"] = stack  # Required for load_stack
            try:
                cl.load_stack(stack)
                ctx = cl.context
                print(f"  • {stack:<15} -> https://{ctx.get('FQDN')}")

                # Check health
                services = client.services.list(
                    filters={"label": f"com.docker.stack.namespace={stack}"}
                )
                running = 0
                total = len(services)
                for svc in services:
                    # Very basic check: any running tasks?
                    tasks = svc.tasks(filters={"desired-state": "running"})
                    if any(t["Status"]["State"] == "running" for t in tasks):
                        running += 1

                print(f"    Services: {running}/{total} running")
            except Exception as e:
                print(f"  • {stack:<15} (Error loading config: {e})")

    print()


if __name__ == "__main__":
    main()
