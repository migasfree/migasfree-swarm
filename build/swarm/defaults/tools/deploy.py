#!/usr/bin/python3

# https://docker-py.readthedocs.io/en/stable/

import os
import docker
import string
import random
import subprocess
import requests
import time
import socket
import urllib3
import shutil

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


def is_self_signed(certificate_path):
    with open(certificate_path, "rb") as cert_file:
        cert_data = cert_file.read()

    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

    return 'CN=Insecure Certificate Authority' in str(cert.issuer)


def swarm_init():
    info = client.info()

    if 'Swarm' in info and 'Cluster' in info['Swarm']:
        cluster_info = info['Swarm']['Cluster']
        cluster_id = cluster_info['ID']

    if 'cluster_id' not in locals():
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
                    except docker.errors.APIError as e:
                        print("Error: cluster not initiate", e)
                        return None
                else:
                    print("Error: cluster not initiate", e)
                    return None

    return cluster_id


def generate_password(length):
    valid_characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(valid_characters) for _ in range(length))

    return password


def wait_url_available(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code < 400:
            return True
        else:
            return False
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
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Archivo descargado correctamente en {output_path}")
    else:
        print(f"Error al descargar el archivo: {response.status_code}")


def create_labels():
    nodes = client.nodes.list()
    # if only one node
    if len(nodes) == 1:
        node = nodes[0]

        # Add labels to the node
        labels = {
            # "datashare": "true", is only for s3
            "datastore": "true",
            "database": "true"
        }

        node_spec = {
            'Availability': 'active',
            'Name': 'node-1',
            'Role': 'manager',
            'Labels': labels
        }

        node.update(node_spec)


def deploy_infra(context):
    path_template = "/tools/templates/"
    template = "infra.template"
    deploy = os.path.join(_PATH, template)
    with open(deploy, 'w') as file_deploy:
        file_deploy.write(render(path_template, template, context))

    # Secrets swarm-credential
    credentials("swarm-credential", generate_password(8))
    create_secret_file(
        "swarm-credential",
        os.path.join(_PATH_CREDENTIALS, "swarm-credential")
    )

    deploy_stack(deploy, "infra")

    os.remove(deploy)


def config_portainer(context):

    wait_for_dns("portainer")
    wait_url_available("http://portainer:9000/api/status")
    time.sleep(1)

    # credentials configuration
    (user, password) = credentials("swarm-credential")


    response = requests.post(
        "http://portainer:9000/api/users/admin/init",
        json={"Username": user, "Password": password},
        verify=False
    )
    if response and response.status_code != 200:
        print("RESPONSE INIT", response)
        print("RESPONSE INIT", response.text)

    response = requests.get('http://portainer:9000/#!/wizard', verify=False)
    if response and response.status_code != 200:
        print("RESPONSE WIZARD", response)

    if os.path.exists(f"{_PATH_CREDENTIALS}/portainer-token"):
        token = open(f"{_PATH_CREDENTIALS}/portainer-token", "r").read()
    else:
        token = create_token("deploy", user, password)
        open(f"{_PATH_CREDENTIALS}/portainer-token", "w").write(token)

    if token == "":
        os.remove(f"{_PATH_CREDENTIALS}/portainer-token")
        print("Error: The credentials file 'credentials/portainer-token' could not be generated.")
        exit()

    # Customize logo
    api = PortainerAPI("http://portainer:9000/api", token)
    api.settings()

    # Create Environment
    api.set_enpoint_id("primary")

    # Update Public IP
    api.set_public_ip(context['FQDN'])


def credentials(credential_name, user="admin"):
    """
    Save & Read credentials with 'user:password' content
    """
    filename = os.path.join(_PATH_CREDENTIALS, credential_name)
    # if not exist, create it
    if not os.path.exists(filename):
        with open(filename, "w") as credential_file:
            credential_file.write(f"{user}:{generate_password(30)}")

    user, password = open(f"{_PATH_CREDENTIALS}/{credential_name}").read().split(":")
    return (user, password)


def create_secret_file(name, file_path):
    existing_secrets = [secret.name for secret in client.secrets.list()]
    if name not in existing_secrets:
        with open(file_path, 'rb') as f:
            data = f.read()
        create_secret(name=name, data=data)


def create_secret(name, data):
    existing_secrets = [secret.name for secret in client.secrets.list()]
    if name not in existing_secrets:
        client.secrets.create(name=name, data=data)


def deploy_stack(compose_file, stack_name):
    os.system(f'docker stack deploy -c {compose_file} {stack_name} --detach=true --resolve-image=never')


def create_network_overlay(network_name):
    os.system(f'docker network create --attachable --driver overlay --opt encrypted {network_name} --opt com.docker.network.driver.mtu=1200 2>/dev/null')


def create_network_internal(network_name):
    os.system(f'docker network create --internal --driver overlay --opt encrypted {network_name} --opt com.docker.network.driver.mtu=1200 2>/dev/null')


def deploy_migasfree(context):


    create_network_internal(f"{context['STACK']}_network")

    token = open(f"{_PATH_CREDENTIALS}/portainer-token", "r").read()

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
            "AuthorizedTeams": []
        },
        "Variables": [],
        "TLSSkipVerify": False
    }
    api.custom_templates(payload)

    # DEPLOY THE STACK
    payload = {
        "Env": [],
        "Name":	name_template,
        "StackFileContent": content,
        "SwarmID": api.swarm_id
    }

    deploy_stack(file_yml, f"{context['STACK']}")

    os.remove(file_yml)

    print()


def create_paths():
    if not os.path.exists(_PATH_CREDENTIALS):
        os.mkdir(_PATH_CREDENTIALS)
    if not os.path.exists(_PATH_CERTIFICATE):
        os.mkdir(_PATH_CERTIFICATE)
    if not os.path.exists(f"{_PATH_SHARE}/datashares/"):
        os.mkdir(f"{_PATH_SHARE}/datashares/")
        os.chown(f"{_PATH_SHARE}/datashares/", 890, 890)
    if not os.path.exists(f"{_PATH_SHARE}/datashares/{CONTEXT['STACK']}"):
        os.mkdir(f"{_PATH_SHARE}/datashares/{CONTEXT['STACK']}")
        os.chown(f"{_PATH_SHARE}/datashares/{CONTEXT['STACK']}", 890, 890)


# PROGRAM
# =======

cl = ContextLoader()
CONTEXT = cl.context
cl.save()

cl.load_stack(" | ".join(get_stacks()))
CONTEXT = cl.context
cl.save_stack()

create_paths()

client = docker.from_env()
swarm_init()

(user, password) = credentials(f"{CONTEXT['STACK']}", generate_password(8))

# Stack secrets
create_secret(f"{CONTEXT['STACK']}_superadmin_name", user)
create_secret(f"{CONTEXT['STACK']}_superadmin_pass", password)
create_secret(f"{CONTEXT['STACK']}_pms_pass", generate_password(12))

create_labels()
create_network_overlay("infra_network")


# Connect network portainer to this container (is Necessary in credential configuration)
client.networks.get("infra_network").connect(socket.gethostname())

deploy_infra(CONTEXT)

config_portainer(CONTEXT)

deploy_migasfree(CONTEXT)

if CONTEXT["HTTPSMODE"] == 'auto' and is_self_signed(f"{_PATH_CERTIFICATE}/{CONTEXT['STACK']}.pem"):
    print("Changing to HTTPSMODE auto")
    token = open(f"{_PATH_CREDENTIALS}/portainer-token", "r").read()
    api = PortainerAPI("http://portainer:9000/api", token)
    api.set_enpoint_id("primary")
    api.execute_in_service(f"{CONTEXT['STACK']}_certbot", ["/usr/bin/send_message", "HTTPSMODE='auto'"])
    api.execute_in_service(f"{CONTEXT['STACK']}_certbot", ["/usr/bin/renew-certificates.sh"])
    api.execute_in_service(f"{CONTEXT['STACK']}_certbot", ["/usr/bin/send_message", ""])

try:
    shutil.rmtree(f"/mnt/cluster/datashares/{CONTEXT['STACK']}/__pycache__")
except Exception:
    pass


wait_for_dns("proxy")
wait_url_available(f"https://{CONTEXT['FQDN']}/status")

logo = f"""

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
if CONTEXT['PORT_HTTPS'] == '443':
    print(f"       👍 https://{CONTEXT['FQDN']}/status")
else:
    print(f"       👍 https://{CONTEXT['FQDN']}:{CONTEXT['PORT_HTTPS']}/status")
print()
