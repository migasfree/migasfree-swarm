import requests

from resources import read_file
from settings import ASSISTANT_API_URL, STACK, EMAIL


def get_api_key():
    auth_url = f"{ASSISTANT_API_URL}/api/v1/auths/signin"
    password = read_file(f'/run/secrets/{STACK}_superadmin_pass')
    auth_data = {"email": EMAIL, "password": password}
    headers = {"Content-Type": "application/json"}

    auth_response = requests.post(auth_url, json=auth_data, headers=headers)
    if auth_response.status_code != requests.codes.ok:
        raise Exception("No se pudo autenticar")

    jwt_token = auth_response.json().get("token")
    api_key_url = f"{ASSISTANT_API_URL}/api/v1/auths/api_key"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    api_key_response = requests.get(api_key_url, headers=headers)
    if api_key_response.status_code == requests.codes.ok:
        api_key = api_key_response.json().get("api_key")
    else:
        # Create api_key
        api_key_response = requests.post(api_key_url, headers=headers)
        api_key = api_key_response.json().get("api_key")

    return api_key


def get_base_model_id(id="gas"):
    headers = {
        "Authorization": f"Bearer {ASSISTANT_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{ASSISTANT_API_URL}/api/models", headers=headers)
    if response.status_code == requests.codes.ok:
        result = response.json()
        model = next((m for m in result["data"] if m["id"] == id), None)
        return model["info"]["base_model_id"]
    else:
        raise Exception("ERROR in model {id}: base_model_id not found")
        return ""


ASSISTANT_API_KEY = get_api_key()
