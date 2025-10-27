import time
import docker
import urllib3
import subprocess

from context import get_stacks

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def remove_stacks(stack_names):
    for stack_name in stack_names:
        try:
            subprocess.run(['docker', 'stack', 'rm', stack_name], check=True)
            print(f"Stack '{stack_name}' removed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error removing stack '{stack_name}': {e}")
        except Exception as e:
            print(f"Unexpected error when attempting to remove the stack '{stack_name}': {e}")


def remove_volumes(client, volume_names, wait_time=5, max_retries=10):
    for volume_name in volume_names:
        retries = 0
        while retries < max_retries:
            try:
                volume = client.volumes.get(volume_name)
                volume.remove()
                print(f"Volume '{volume_name}' removed successfully.")
                break
            except docker.errors.APIError as e:
                if 'in use' in str(e):
                    print(f"The volume '{volume_name}' is in use. Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    print(f"Error when attempting to remove the volume '{volume_name}': {e}")
                    break
            except docker.errors.NotFound:
                print(f"The volume '{volume_name}' was not found.")
                break
            except Exception as e:
                print(f"Unexpected error when attempting to remove the volume '{volume_name}': {e}")
                break

        if retries == max_retries:
            print(f"Failed to remove the volume '{volume_name}' after {max_retries} attempts.")


def leave_swarm_force(client):
    try:
        client.api.leave_swarm(force=True)
        print("Node has forcefully left the swarm.")
    except docker.errors.APIError as e:
        print(f"Error when attempting to leave the swarm: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def system_prune():
    try:
        subprocess.run(['docker', 'system', 'prune', '-f'], check=True)
        print("Docker system cleaned successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error when attempting to clean the Docker system: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main():
    print("Warning!")
    response = input("Do you want to leave the Swarm cluster? (y/N): ").strip().lower()
    if response != "y":
        print('Aborted by user.')
        return

    client = docker.from_env()
    remove_stacks(client, get_stacks() + ['portainer', 'proxy'])
    leave_swarm_force(client)
    system_prune()


if __name__ == '__main__':
    main()
