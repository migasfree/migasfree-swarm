#!/usr/bin/python3

# https://docker-py.readthedocs.io/en/stable/

import os
from pathlib import Path
import string
import random
import requests
import time
import socket
import subprocess
import urllib3
import shutil
import docker
import http.client

from template import render
from portainer import PortainerAPI, create_token
from context import ContextLoader, get_stacks
from cryptography import x509
from cryptography.hazmat.backends import default_backend

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_PATH = Path("/stack")  # Path in this container
_PATH_SHARE = Path("/mnt/cluster")  # data shared
_PATH_CREDENTIALS = _PATH_SHARE / "credentials"
_PATH_CERTIFICATE = _PATH_SHARE / "certificates"
_FILE_SETTINGS = _PATH / "settings.py"


def generate_password(length=12):
    valid_characters = string.ascii_letters + string.digits
    return "".join(random.choice(valid_characters) for _ in range(length))


def safe_mkdir(path, uid=None, gid=None):
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        if uid is not None and gid is not None:
            os.chown(path, uid, gid)


def wait_url_available(url, timeout=60):
    start_time = time.time()
    while True:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:
                return True
        except (requests.RequestException, http.client.RemoteDisconnected):
            pass

        print("    Waiting for service to be ready...", end="\r")
        if time.time() - start_time > timeout:
            print()
            return False
        time.sleep(2)


def wait_for_dns(hostname, timeout=60, interval=3):
    """
    Waits until hostname can be resolved or until timeout is reached.
    :param hostname: Name to resolve.
    :param timeout: Maximum time in seconds to wait.
    :param interval: Interval in seconds between attempts.
    :return: True if resolved, False if timeout.
    """
    start_time = time.time()
    print(f"Waiting to resolve {hostname} ...")
    while True:
        try:
            socket.getaddrinfo(hostname, None)
            return True
        except socket.gaierror:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"Timeout waiting to resolve {hostname}")
                return False
            print(f"    retrying in {interval}s...")
            time.sleep(interval)


def download_resource(url, output_path):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Archivo descargado correctamente en {output_path}")
    except requests.RequestException as e:
        print(f"Error al descargar el archivo: {e}")


def is_self_signed(certificate_path):
    with open(certificate_path, "rb") as cert_file:
        cert_data = cert_file.read()

    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

    return "CN=Insecure Certificate Authority" in str(cert.issuer)


def get_docker_client():
    return docker.from_env()


def swarm_init(client):
    info = client.info()

    if "Swarm" in info and "Cluster" in info["Swarm"]:
        cluster_info = info["Swarm"]["Cluster"]
        cluster_id = cluster_info["ID"]

    if "cluster_id" not in locals():
        print()
        print("Warning! This system is not a Swarm node.")
        response = "Y"
        response = input("Do you want to create a manager node? (Y/n): ") or response
        if response.upper() == "Y":
            try:
                cluster_id = client.swarm.init()
            except docker.errors.APIError as e:
                print(e)
                if "could not choose an IP address to advertise" in str(e):
                    advertise_addr = input("Please input the IP address to advertise: ")
                    try:
                        cluster_id = client.swarm.init(advertise_addr=advertise_addr)
                    except docker.errors.APIError as exc:
                        print("Error: cluster not initiate", exc)
                        return None
                else:
                    print("Error: cluster not initiate", e)
                    return None

    return cluster_id


def create_labels(client):
    nodes = client.nodes.list()
    # if only one node
    if len(nodes) == 1:
        node = nodes[0]

        # Add labels to the node
        labels = {
            "datastore": "true",
            "database": "true",
        }

        node_spec = {
            "Availability": "active",
            "Name": "node-1",
            "Role": "manager",
            "Labels": labels,
        }

        node.update(node_spec)


def create_secret(client, name, data):
    if name not in [secret.name for secret in client.secrets.list()]:
        client.secrets.create(name=name, data=data)


def create_secret_file(client, name, file_path):
    if name not in [secret.name for secret in client.secrets.list()]:
        with open(file_path, "rb") as f:
            data = f.read()
        create_secret(client, name, data)


def deploy_stack(compose_file, stack_name):
    subprocess.run(
        [
            "docker",
            "stack",
            "deploy",
            "-c",
            compose_file,
            stack_name,
            "--detach=true",
            "--resolve-image=never",
        ],
        check=True,
    )


def create_network_overlay(network_name):
    subprocess.run(
        [
            "docker",
            "network",
            "create",
            "--attachable",
            "--driver",
            "overlay",
            "--opt",
            "encrypted",
            network_name,
            "--opt",
            "com.docker.network.driver.mtu=1200",
        ],
        stderr=subprocess.DEVNULL,
    )


def create_network_internal(network_name):
    subprocess.run(
        [
            "docker",
            "network",
            "create",
            "--internal",
            "--driver",
            "overlay",
            "--opt",
            "encrypted",
            network_name,
            "--opt",
            "com.docker.network.driver.mtu=1200",
        ],
        stderr=subprocess.DEVNULL,
    )


def connect_network(client, network, hostname):
    try:
        client.networks.get(network).connect(hostname)
    except Exception as e:
        print(f"Could not connect to network {network}: {e}")


def create_paths(context):
    safe_mkdir(_PATH_CREDENTIALS)
    safe_mkdir(_PATH_CERTIFICATE)
    shares_path = _PATH_SHARE / "datashares"
    safe_mkdir(shares_path, 890, 890)
    stack_share = shares_path / context["STACK"]
    safe_mkdir(stack_share, 890, 890)


def credentials(credential_name, user="admin", password=None):
    """
    Save & Read credentials with 'user:password' content
    """
    filename = _PATH_CREDENTIALS / credential_name
    # if not exist, create it
    if not filename.exists():
        if password is None:
            password = generate_password(30)
        filename.write_text(f"{user}:{password}")

    user, password = filename.read_text().strip().split(":")

    return user, password


def deploy_infra(client, context):
    path_template = "/tools/templates/"
    template = "infra.template"
    deploy = _PATH / template
    deploy.write_text(render(path_template, template, context))

    # Secrets swarm-credential
    cred_name = "swarm-credential"
    credentials(cred_name, generate_password(12))
    create_secret_file(client, cred_name, _PATH_CREDENTIALS / cred_name)

    deploy_stack(str(deploy), "infra")
    deploy.unlink(missing_ok=True)


def config_portainer(client, context):
    wait_for_dns("portainer")
    wait_url_available("http://portainer:9000/api/system/status")

    # credentials configuration
    user, password = credentials("swarm-credential")
    print("Initializing Portainer admin...")
    while True:
        try:
            response = requests.post(
                "http://portainer:9000/api/users/admin/init",
                json={"Username": user, "Password": password},
                timeout=10,
            )
            if response.status_code == 200 or response.status_code == 409:
                break
            print(
                f"    Waiting for Portainer to be ready... (Status: {response.status_code})"
            )
        except requests.RequestException as e:
            print(f"    Waiting for Portainer network... ({e})", end="\r")
        time.sleep(2)

    print("Verifying Portainer (post-init check)...")
    wait_url_available("http://portainer:9000/api/system/status")

    try:
        response = requests.get("http://portainer:9000/#!/wizard", timeout=10)
        if response.status_code != 200:
            print("RESPONSE WIZARD", response)
    except requests.RequestException as e:
        print(f"Error accessing Portainer wizard: {e}")

    token_file = _PATH_CREDENTIALS / "portainer-token"
    if token_file.exists():
        token = token_file.read_text().strip()
    else:
        token = create_token("deploy", user, password)
        token_file.write_text(token)

    if not token:
        token_file.unlink(missing_ok=True)
        print(
            "Error: The credentials file 'credentials/portainer-token' could not be generated."
        )
        exit()

    # Customize logo
    api = PortainerAPI("http://portainer:9000/api", token)
    api.settings()

    # Create Environment
    api.create_environment("primary")
    api.set_enpoint_id("primary")

    # Update Public IP
    api.set_public_ip(context["FQDN"])


def deploy_migasfree(client, context):
    create_network_internal(f"{context['STACK']}_network")

    token_file = os.path.join(_PATH_CREDENTIALS, "portainer-token")
    with open(token_file) as f:
        token = f.read().strip()

    api = PortainerAPI("http://portainer:9000/api", token)
    file_yml = _PATH / f"{context['STACK']}.yml"
    api.set_enpoint_id("primary")

    # CUSTOM TEMPLATE
    name_template = f"{context['STACK']}"

    api.delete_custom_templates(name_template)

    content = render("/tools/templates", "stack.template", context)
    file_yml.write_text(content)

    payload = {
        "Title": name_template,
        "FileContent": content,
        "File": None,
        "RepositoryURL": "",
        "RepositoryReferenceName": "",
        "RepositoryAuthentication": False,
        "RepositoryUsername": "",
        "RepositoryPassword": "",
        "ComposeFilePathInRepository": f"{context['STACK']}.yml",
        "Description": "migasfree stack",
        "Note": "http://migasfree.org",
        "Logo": "https://raw.githubusercontent.com/migasfree/migasfree-frontend/master/public/favicon.svg",
        "Platform": 1,
        "Type": 1,
        "AccessControlData": {
            "AccessControlEnabled": True,
            "Ownership": "administrators",
            "AuthorizedUsers": [],
            "AuthorizedTeams": [],
        },
        "Variables": [],
        "TLSSkipVerify": False,
    }
    api.custom_templates(payload)

    # DEPLOY THE STACK
    payload = {
        "Env": [],
        "Name": name_template,
        "StackFileContent": content,
        "SwarmID": api.swarm_id,
    }

    deploy_stack(str(file_yml), f"{context['STACK']}")

    file_yml.unlink(missing_ok=True)
    print()


def main():
    cl = ContextLoader()
    cl.save()

    cl.load_stack(" | ".join(get_stacks()))
    context = cl.context
    cl.save_stack()

    create_paths(context)
    client = docker.from_env()
    swarm_init(client)

    user, password = credentials(
        f"{context['STACK']}",
        user=generate_password(12),
        password=generate_password(32),
    )

    # Stack secrets
    create_secret(client, f"{context['STACK']}_superadmin_name", user.encode())
    create_secret(client, f"{context['STACK']}_superadmin_pass", password.encode())

    create_labels(client)
    create_network_overlay("infra_network")
    connect_network(client, "infra_network", socket.gethostname())

    deploy_infra(client, context)
    config_portainer(client, context)
    deploy_migasfree(client, context)

    cert_path = _PATH_CERTIFICATE / f"{context['STACK']}.pem"
    if context.get("HTTPSMODE") == "auto" and is_self_signed(cert_path):
        print("Changing to HTTPSMODE auto")
        token_file = _PATH_CREDENTIALS / "portainer-token"
        token = token_file.read_text().strip()
        api = PortainerAPI("http://portainer:9000/api", token)
        api.set_enpoint_id("primary")
        api.execute_in_service(
            f"{context['STACK']}_certbot", ["/usr/bin/send_message", "HTTPSMODE='auto'"]
        )
        api.execute_in_service(
            f"{context['STACK']}_certbot", ["/usr/bin/renew-certificates.sh"]
        )
        api.execute_in_service(
            f"{context['STACK']}_certbot", ["/usr/bin/send_message", ""]
        )

    cache_path = _PATH_SHARE / "datashares" / context["STACK"] / "__pycache__"
    try:
        shutil.rmtree(cache_path)
    except Exception:
        pass

    wait_for_dns("proxy")
    wait_url_available(f"https://{context['FQDN']}/status")

    logo = """

                   █                          ██
                                             █
         ███ ██    █    ██     ███     ███  ████  ███  ███    ███
        █   █  █   █   █  █       █   █      █   █    █   █  █   █
        █   █  █   █   █  █    ████    ██    █   █    ████   ████
        █   █  █   █   █  █   █   █      █   █   █    █      █
        █   █  █   █    ███    ███    ███    █   █     ███    ███
                          █
        we love change  ██

"""

    print(logo)
    if context["PORT_HTTPS"] == "443":
        print(f"       👍 https://{context['FQDN']}/status")
    else:
        print(f"       👍 https://{context['FQDN']}:{context['PORT_HTTPS']}/status")

    print()


if __name__ == "__main__":
    main()
