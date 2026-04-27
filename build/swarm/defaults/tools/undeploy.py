import subprocess
import sys
import docker

from context import ContextLoader, get_stacks


def remove_stacks(stack_names):
    for stack_name in stack_names:
        try:
            subprocess.run(['docker', 'stack', 'rm', stack_name], check=True)
            print(f"Stack '{stack_name}' removed successfully.")
        except Exception as e:
            print(f"Unexpected error when attempting to remove the stack '{stack_name}': {e}")


def remove_services(stack_name, services):
    client = docker.from_env()
    for service in services:
        service_name = f"{stack_name}_{service}"
        try:
            client.services.get(service_name).remove()
            print(f"Service '{service_name}' removed successfully.")
        except docker.errors.NotFound:
            print(f"Service '{service_name}' not found. Skipping.")
        except Exception as e:
            print(f"Error removing service '{service_name}': {e}")


# PROGRAM
# =======

cl = ContextLoader()
cl.save()

cl.load_stack(" |".join(get_stacks()))
CONTEXT = cl.context

services = sys.argv[1:]
if services:
    remove_services(CONTEXT['STACK'], services)
else:
    remove_stacks([CONTEXT['STACK']])
