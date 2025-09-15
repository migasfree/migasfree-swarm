import requests
from settings import ASSISTANT_API_URL, STACK, EMAIL

import threading
import time
import sys

def get_api_key():
    auth_url = f"{ASSISTANT_API_URL}/api/v1/auths/signin"
    with open(f'/run/secrets/{STACK}_superadmin_pass', 'r', encoding='utf-8') as f:
        PASSWORD = f.read()
    auth_data = {"email": EMAIL, "password": PASSWORD}
    headers={"Content-Type":"application/json"}
    auth_response = requests.post(auth_url, json=auth_data, headers=headers)
    if auth_response.status_code != 200:
        raise Exception("No se pudo autenticar")
    jwt_token = auth_response.json().get("token")
    api_key_url = f"{ASSISTANT_API_URL}/api/v1/auths/api_key"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    api_key_response = requests.post(api_key_url, headers=headers)
    if api_key_response.status_code == 200:
        api_key = api_key_response.json().get("api_key")
        return api_key
    else:
        raise Exception("No se pudo obtener la api_key")

def get_base_model_id(id="gas"):
    headers = {
        "Authorization": f"Bearer {ASSISTANT_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{ASSISTANT_API_URL}/api/models", headers=headers)
    if response.status_code == 200:
        result = response.json()
        model = next((m for m in result["data"] if m["id"] == id), None)
        return model["info"]["base_model_id"]
    else:
        raise Exception("ERROR in model {id}: base_model_id not found")
        return ""

def wait_for_url(url, timeout=10, check_interval=0.5):
    """
    Wait until the URL responds with status 200 or until timeout is reached.

    :param url: URL to check
    :param timeout: Maximum time in seconds to wait before giving up
    :param check_interval: Interval in seconds between retries
    :return: True if URL responded with 200, False if timeout expired
    """
    start_time = time.time()
    while True:
        try:
            response = requests.head(url, timeout=1)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass  # Ignorar errores y continuar intentando

        if time.time() - start_time > timeout:
            return False

        time.sleep(check_interval)


def wait_mcp_server():
    url = "http://localhost:8080/openapi.json"
    wait_for_url(url, timeout=60)

def verify_connection():
    wait_mcp_server()
    headers = {
        "Authorization": f"Bearer {ASSISTANT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "url":"http://mcp-server:8080",
        "path":"openapi.json",
        "auth_type":"bearer",
        "key":"",
        "config":{ "enable":True,
            "access_control": {
                "read": {
                    "group_ids":[],
                    "user_ids":[]
                },
                "write": {
                    "group_ids":[],
                    "user_ids":[]
                }
            }
        },
        "info": {
            "id":"",
            "name":"migasfree-mcp",
            "description":"migasfree-mcp"
        }
    }
    response = requests.post(f"{ASSISTANT_API_URL}/api/v1/configs/tool_servers/verify", json=data, headers=headers)


ASSISTANT_API_KEY = get_api_key()
MODEL_BASE = get_base_model_id("gas")


t = threading.Timer(5.0, verify_connection)
t.start()