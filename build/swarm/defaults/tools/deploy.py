#!/usr/bin/python3

# https://docker-py.readthedocs.io/en/stable/

import os
import string
import random
import requests
import time
import socket
import subprocess
import urllib3
import shutil
import docker

from template import render
from portainer import PortainerAPI, create_token
from context import ContextLoader, get_stacks
from cryptography import x509
from cryptography.hazmat.backends import default_backend

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_PATH = "/stack"  # Path in this container
_PATH_SHARE = "/mnt/cluster"  # data shared
_PATH_CREDENTIALS = os.path.join(_PATH_SHARE, "credentials")
_PATH_CERTIFICATE = os.path.join(_PATH_SHARE, "certificates")
_FILE_SETTINGS = os.path.join(_PATH, "settings.py")


def generate_password(length=12):
    valid_characters = string.ascii_letters + string.digits
    return "".join(random.choice(valid_characters) for _ in range(length))


def safe_mkdir(path, uid=None, gid=None):
    if not os.path.exists(path):
        os.mkdir(path)
        if uid is not None and gid is not None:
            os.chown(path, uid, gid)


def wait_url_available(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code < 400
    except requests.RequestException:
        return False


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
        response = requests.get(url)
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
            # "datashare": "true", is only for s3
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
        create_secret(name=name, data=data)


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
    shares_path = os.path.join(_PATH_SHARE, "datashares")
    safe_mkdir(shares_path, 890, 890)
    stack_share = os.path.join(shares_path, context["STACK"])
    safe_mkdir(stack_share, 890, 890)


def credentials(credential_name, user="admin", password=None):
    """
    Save & Read credentials with 'user:password' content
    """
    filename = os.path.join(_PATH_CREDENTIALS, credential_name)
    # if not exist, create it
    if not os.path.exists(filename):
        if password is None:
            password = generate_password(30)
        with open(filename, "w") as credential_file:
            credential_file.write(f"{user}:{password}")

    with open(filename) as cred_file:
        user, password = cred_file.read().strip().split(":")

    return user, password


def deploy_infra(client, context):
    path_template = "/tools/templates/"
    template = "infra.template"
    deploy = os.path.join(_PATH, template)
    with open(deploy, "w") as file_deploy:
        file_deploy.write(render(path_template, template, context))

    # Secrets swarm-credential
    cred_name = "swarm-credential"
    credentials(cred_name, generate_password(8))
    create_secret_file(client, cred_name, os.path.join(_PATH_CREDENTIALS, cred_name))

    deploy_stack(deploy, "infra")
    os.remove(deploy)


def config_portainer(client, context):
    wait_for_dns("portainer")
    wait_url_available("http://portainer:9000/api/status")
    time.sleep(1)

    # credentials configuration
    user, password = credentials("swarm-credential")
    response = requests.post(
        "http://portainer:9000/api/users/admin/init",
        json={"Username": user, "Password": password},
        verify=False,
    )
    if response and response.status_code != 200:
        print("RESPONSE INIT", response)
        print("RESPONSE INIT", response.text)

    response = requests.get("http://portainer:9000/#!/wizard", verify=False)
    if response and response.status_code != 200:
        print("RESPONSE WIZARD", response)

    token_file = os.path.join(_PATH_CREDENTIALS, "portainer-token")
    if os.path.exists(token_file):
        token = open(token_file, "r").read()
    else:
        token = create_token("deploy", user, password)
        open(token_file, "w").write(token)

    if not token:
        os.remove(token_file)
        print(
            "Error: The credentials file 'credentials/portainer-token' could not be generated."
        )
        exit()

    # Customize logo
    api = PortainerAPI("http://portainer:9000/api", token)
    api.settings()

    # Create Environment
    api.set_enpoint_id("primary")

    # Update Public IP
    api.set_public_ip(context["FQDN"])


def deploy_migasfree(client, context):
    create_network_internal(f"{context['STACK']}_network")

    token_file = os.path.join(_PATH_CREDENTIALS, "portainer-token")
    with open(token_file) as f:
        token = f.read().strip()

    api = PortainerAPI("http://portainer:9000/api", token)
    file_yml = f"/stack/{context['STACK']}.yml"
    api.set_enpoint_id("primary")

    # CUSTOM TEMPLATE
    name_template = f"{context['STACK']}"

    api.delete_custom_templates(name_template)

    content = render("/tools/templates", "stack.template", context)
    with open(file_yml, "w") as f:
        f.write(content)

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

    deploy_stack(file_yml, f"{context['STACK']}")

    os.remove(file_yml)
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

    user, password = credentials(f"{context['STACK']}", password=generate_password(8))

    # Stack secrets
    create_secret(client, f"{context['STACK']}_superadmin_name", user.encode())
    create_secret(client, f"{context['STACK']}_superadmin_pass", password.encode())

    create_labels(client)
    create_network_overlay("infra_network")
    connect_network(client, "infra_network", socket.gethostname())

    deploy_infra(client, context)
    config_portainer(client, context)
    deploy_migasfree(client, context)

    cert_path = os.path.join(_PATH_CERTIFICATE, f"{context['STACK']}.pem")
    if context.get("HTTPSMODE") == "auto" and is_self_signed(cert_path):
        print("Changing to HTTPSMODE auto")
        token_file = os.path.join(_PATH_CREDENTIALS, "portainer-token")
        with open(token_file) as f:
            token = f.read().strip()
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

    cache_path = os.path.join(
        _PATH_SHARE, "datashares", context["STACK"], "__pycache__"
    )
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
