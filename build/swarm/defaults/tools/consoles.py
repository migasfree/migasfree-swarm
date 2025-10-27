import sys
import docker

from context import ContextLoader, get_stacks


def scale_services(client, service_names, replicas):
    for service_name in service_names:
        try:
            service = client.services.get(service_name)
            service.update(
                mode={'Replicated': {'Replicas': replicas}}
            )
            print(f'Scaled "{service_name}" to {replicas}')
        except docker.errors.NotFound:
            print(f'Warning: Service "{service_name}" not found.')
        except docker.errors.APIError as e:
            print(f'Error scaling "{service_name}": {e}')
        except Exception as e:
            print(f'Unexpected error with "{service_name}": {e}')


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [pro|dev]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    replicas = 0 if mode == 'pro' else 1

    cl = ContextLoader()
    cl.load_stack(" | ".join(get_stacks()))
    context = cl.context

    client = docker.from_env()

    consoles = [
        f"{context['STACK']}_database_console",
        f"{context['STACK']}_datastore_console",
        f"{context['STACK']}_worker_console"
    ]
    scale_services(client, consoles, replicas)


if __name__ == '__main__':
    main()
