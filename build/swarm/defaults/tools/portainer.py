import requests
import time
import base64

from requests.packages.urllib3.filepost import encode_multipart_formdata


def token_exists(data, token_name):
    for element in data:
        if element.get('description') == token_name:
            return True
    return False


def create_token(name, username, password):
    # https://docs.portainer.io/api/access
    # https://app.swaggerhub.com/apis/portainer/portainer-ce/2.21.0#/users/UserGenerateAPIKey

    while True:
        session = None
        session = requests.Session()
        session.headers = {"Content-Type": "application/json"}
        session.verify = False

        payload = {"username": username, "password": password}
        try:
            response = session.post("http://portainer:9000/api/auth", json=payload)
            if response and response.status_code == 200:
                break
        except Exception as e:
            print("Error creating token:", e)
            print("****** Consider restarting the Docker service: systemctl restart docker")
        time.sleep(2)

    if response and 'jwt' in response.json():
        headers = session.headers
        headers["Authorization"] = f"Bearer {response.json()['jwt']}"
        session.headers = headers

        response = session.get('http://portainer:9000/api/users/me')
        headers = session.headers
        headers["x-csrf-token"] = response.headers["x-csrf-token"]
        session.headers = headers
        if response and response.status_code == 200:
            userid = response.json()["Id"]
            response = session.get(f'http://portainer:9000/api/users/{userid}/tokens')
            if response and response.status_code == 200:
                if not token_exists(response.json(), name):
                    # create token
                    payload = {"description": name, "password": password}
                    response = session.post(f'http://portainer:9000/api/users/{userid}/tokens', json=payload)
                    if response and response.status_code == 201:
                        return response.json()["rawAPIKey"]

    return ""


class PortainerAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers = {
            "Content-Type": "application/json",
            "X-API-Key": token
        }

    def request(self, method, endpoint, data=None):
        url = self.base_url + endpoint
        try:
            if method == "GET":
                response = self.session.get(url, json=data)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError("Error: {}".format(method))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error:", e)
            return None

    def get(self, endpoint, data=None):
        return self.request("GET", endpoint, data)

    def post(self, endpoint, data):
        return self.request("POST", endpoint, data)

    def put(self, endpoint, data):
        return self.request("PUT", endpoint, data)

    def delete(self, endpoint):
        return self.request("DELETE", endpoint)

    def create_secret(self, name, password):
        if not self.exists_secret(name):
            endpoint = f"/endpoints/{self.endpoint_id}/docker/secrets/create"
            payload = {
                "Name": name,
                "Data": base64.b64encode(password.encode("utf-8")).decode("utf-8")
            }
            response = self.post(endpoint, payload)
            if response:
                resource_id = response['Portainer']['ResourceControl']['Id']
                payload = {
                    "AdministratorsOnly": True,
                    "Public": False,
                    "Teams": [],
                    "Users": []
                }
                response = self.put(f"/resource_controls/{resource_id}", payload)

    def exists_secret(self, name):
        endpoint = f"/endpoints/{self.endpoint_id}/docker/secrets"
        secrets = self.get(endpoint)
        return any(secret['Spec']['Name'] == name for secret in secrets)

    """
    def set_swarm_id(self, endpoint_id):
        response = self.get(f"/endpoints")
        for endpoint in response:
            if endpoint["Id"] == endpoint_id:
                self.swarm_id = endpoint["Snapshots"][0]["DockerSnapshotRaw"]["Info"]["Swarm"]["Cluster"]["ID"]
                break
    """

    def set_enpoint_id(self, name):
        while True:
            response = self.get("/endpoints")
            if response:
                for endpoint in response:
                    if endpoint["Name"] == name:
                        self.endpoint_id = endpoint["Id"]
                        self.swarm_id = endpoint["Snapshots"][0]["DockerSnapshotRaw"]["Info"]["Swarm"]["Cluster"]["ID"]
                        return
            time.sleep(2)

    def create_environment(self, name):
        (files, content_type) = encode_multipart_formdata({
            "Name": f"{name}",
            "EndpointCreationType": "2",
            "URL": "tcp://tasks.agent:9001",
            "GroupID": "1",
            "TagIds": "[]",
            "TLS": "true",
            "TLSSkipVerify": "true",
            "TLSSkipClientVerify": "true"
        })

        headers = {
            "Authorization": self.session.headers["Authorization"],
            "Content-Type": content_type,
            "Accept": "application/json, text/plain, */*"
        }

        response = None
        while response is None:
            response = self.session.post(f'{self.base_url}/endpoints', headers=headers, data=files, verify=False)
            time.sleep(1)

        self.set_enpoint_id(name)

        # self.set_swarm_id(self.endpoint_id)

    def set_public_ip(self, ip):
        payload = {"PublicURL": ip}
        self.put(f"/endpoints/{self.endpoint_id}", payload)

    def custom_templates(self, payload):
        self.post("/custom_templates?method=string", payload)

    def delete_custom_templates(self, name):
        response = self.get("/custom_templates")
        if response:
            for template in response:
                if template["Title"] == name and template["Description"] == "migasfree stack":
                    self.delete(f"/custom_templates/{template['Id']}")
                    return

    def deploy(self, payload):
        self.post(f"/stacks?endpointId={self.endpoint_id}&method=string&type=1", payload)

    def settings(self):
        payload = {
            "EdgeAgentCheckinInterval": 5,
            "EnableTelemetry": False,
            "LogoURL": "https://raw.githubusercontent.com/migasfree/migasfree-frontend/master/public/favicon.svg",
            "SnapshotInterval": "5m",
            "TemplatesURL": "https://raw.githubusercontent.com/portainer/templates/v3/templates.json"
        }
        self.put("/settings", payload)
