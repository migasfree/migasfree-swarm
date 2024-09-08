import sys
import os
import docker

from context import ContextLoader, get_stacks

_PATH = "/stack"  # Path in this container
_PATH_CREDENTIALS = os.path.join(_PATH, "credentials") 
_PATH_CERTIFICATE = os.path.join(_PATH, "certificates") 

def scale_services(service_names,replicas):

    for service_name in service_names:
        try:
            service = client.services.get(service_name)
            
            current_spec = service.attrs['Spec']
            
            service.update(
                mode={'Replicated': {'Replicas': replicas}}
            )
            
            print(f'Scaled "{service_name}" to {replicas}')
        except:
            pass

# PROGRAM
# =======

if sys.argv[1] == "pro":
    replicas = 0
else:
    replicas = 1

cl = ContextLoader()
cl.load_stack(" |".join(get_stacks()))
CONTEXT = cl.context

client = docker.from_env()

# Ejemplo de uso
consoles = [
    f"{CONTEXT['STACK']}_database_console",
    f"{CONTEXT['STACK']}_datastore_console",
    f"{CONTEXT['STACK']}_worker_console"
    ]

scale_services(consoles, replicas)

