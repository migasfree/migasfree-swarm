import requests
import docker
import socket

def crear_token_usuario(base_url, stack, common_name, validity_days=7305):
    url = f"{base_url}/v1/{stack}/admin/token"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "common_name": common_name,
        "validity_days": validity_days
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        token_info = response.json()
        return token_info
    else:
        raise Exception(f"Error creando token: {response.status_code} - {response.text}")

def solicitar_parametros():
    stack = ""
    while not stack:
        stack = input("Stack: ").strip()

    common_name = ""
    while not common_name:
        common_name = input("User: ").strip()

    validez_default = 7305
    dias_str = input(f"Validity ({validez_default}): ").strip()
    if not dias_str:
        validity_days = validez_default
    else:
        try:
            validity_days = int(dias_str)
            if validity_days <= 0:
                validity_days = validez_default
        except ValueError:
            validity_days = validez_default

    return stack, common_name, validity_days

if __name__ == "__main__":
    base_url = "http://ca/ca"
    stack, common_name, validity_days = solicitar_parametros()

    client = docker.from_env()
    client.networks.get("infra_network").connect(socket.gethostname())

    try:
        token_info = crear_token_usuario(base_url, stack, common_name, validity_days)
        print("Token created:", token_info)
    except Exception as e:
        print(str(e))
