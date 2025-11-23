import os
import json
import requests
import socket
import logging
import docker

from deploy import credentials

VALIDITY_DAYS = 7305
BASE_URL = 'http://manager:8080/manager'
NETWORK = 'infra_network'

_PATH_SHARE = "/mnt/cluster"  # data shared
_PATH_CREDENTIALS = os.path.join(_PATH_SHARE, "credentials")

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def login(stack):

    username, password = credentials(stack)

    url = f'{BASE_URL}/v1/private/auth/login'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'scope': '',
        'client_id': '',
        'client_secret': ''
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]  # Token info in response
    except requests.RequestException as exc:
        print(f'Login error: {exc}')
        return None

def create_user_token(stack, common_name, validity_days=VALIDITY_DAYS):

    token = login(stack)
    url = f'{BASE_URL}/v1/private/mtls/admin-tokens'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'common_name': common_name,
        'validity_days': validity_days
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.error('Error creating token: %s', exc)
        return None


def input_parameters():
    stack = ''
    while not stack:
        stack = input('Stack: ').strip()

    common_name = ''
    while not common_name:
        common_name = input('User: ').strip()

    days_str = input(f'Validity ({VALIDITY_DAYS}): ').strip()
    try:
        validity_days = int(days_str) if days_str else VALIDITY_DAYS
        if validity_days <= 0:
            validity_days = VALIDITY_DAYS
    except ValueError:
        validity_days = VALIDITY_DAYS

    return stack, common_name, validity_days


if __name__ == '__main__':
    stack, common_name, validity_days = input_parameters()

    client = docker.from_env()
    try:
        client.networks.get(NETWORK).connect(socket.gethostname())
    except docker.errors.APIError as exc:
        logger.warning('Could not connect to network %s: %s', NETWORK, exc)
    except Exception as err:
        logger.warning(err)

    user_token = create_user_token(stack, common_name, validity_days)
    if user_token:
        print(json.dumps(user_token, indent=2))
    else:
        logger.error('Failed to get user token.')
