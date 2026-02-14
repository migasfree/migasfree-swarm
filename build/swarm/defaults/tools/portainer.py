import requests
import time
import base64

from requests.packages.urllib3.filepost import encode_multipart_formdata


def token_exists(data, token_name):
    for element in data:
        if element.get("description") == token_name:
            return True
    return False


def create_token(name, username, password):
    # https://docs.portainer.io/api/access
    # https://app.swaggerhub.com/apis/portainer/portainer-ce/2.33.1#/users/UserGenerateAPIKey

    server_portainer = "http://portainer:9000"
    while True:
        session = None
        session = requests.Session()
        session.headers = {"Content-Type": "application/json"}
        session.verify = False

        payload = {"username": username, "password": password}
        try:
            response = session.post(
                f"{server_portainer}/api/auth", json=payload, timeout=10
            )
            if response and response.status_code == requests.codes.ok:
                break
        except requests.RequestException as e:
            print("Error creating token:", e)
            print(
                "****** Consider restarting the Docker service: systemctl restart docker"
            )
        time.sleep(2)

    if response and "jwt" in response.json():
        headers = session.headers
        headers["Authorization"] = f"Bearer {response.json()['jwt']}"
        session.headers = headers

        response = session.get(f"{server_portainer}/api/users/me", timeout=10)
        headers = session.headers
        headers["x-csrf-token"] = response.headers["x-csrf-token"]
        session.headers = headers
        if response and response.status_code == requests.codes.ok:
            userid = response.json()["Id"]
            response = session.get(
                f"{server_portainer}/api/users/{userid}/tokens", timeout=10
            )
            if response and response.status_code == requests.codes.ok:
                if not token_exists(response.json(), name):
                    # create token
                    payload = {"description": name, "password": password}
                    response = session.post(
                        f"{server_portainer}/api/users/{userid}/tokens",
                        json=payload,
                        timeout=10,
                    )
                    if response and response.status_code == requests.codes.ok:
                        return response.json()["rawAPIKey"]

    # remove token
    response = session.get(f"{server_portainer}/api/users/{userid}/tokens", timeout=10)
    tokens = response.json()
    token_id = None
    for token in tokens:
        if "description" in token:
            if token["description"] == name:
                token_id = token.get("id")
                response = session.delete(
                    f"{server_portainer}/api/users/{userid}/tokens/{token_id}",
                    timeout=10,
                )

    return ""


class PortainerAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers = {"Content-Type": "application/json", "X-API-Key": token}

    def request(self, method, endpoint, data=None):
        url = self.base_url + endpoint
        try:
            if method == "GET":
                response = self.session.get(url, json=data, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=10)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=10)
                return response
            else:
                raise ValueError("Error: {}".format(method))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code not in [502, 503, 504]:
                print("HTTP Error:", e)
            return None
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
                "Data": base64.b64encode(password.encode("utf-8")).decode("utf-8"),
            }
            response = self.post(endpoint, payload)
            if response:
                resource_id = response["Portainer"]["ResourceControl"]["Id"]
                payload = {
                    "AdministratorsOnly": True,
                    "Public": False,
                    "Teams": [],
                    "Users": [],
                }
                response = self.put(f"/resource_controls/{resource_id}", payload)

    def exists_secret(self, name):
        endpoint = f"/endpoints/{self.endpoint_id}/docker/secrets"
        secrets = self.get(endpoint)
        return any(secret["Spec"]["Name"] == name for secret in secrets)

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
                        # Try to get it from Snapshot first
                        try:
                            self.swarm_id = endpoint["Snapshots"][0][
                                "DockerSnapshotRaw"
                            ]["Info"]["Swarm"]["Cluster"]["ID"]
                            return
                        except (KeyError, IndexError, TypeError):
                            # Fallback to direct Docker info call (live data)
                            info = self.get(
                                f"/endpoints/{self.endpoint_id}/docker/info"
                            )
                            if info and "Swarm" in info and "Cluster" in info["Swarm"]:
                                self.swarm_id = info["Swarm"]["Cluster"]["ID"]
                                return
            time.sleep(2)

    def create_environment(self, name):
        (files, content_type) = encode_multipart_formdata(
            {
                "Name": f"{name}",
                "EndpointCreationType": "2",
                "URL": "tcp://tasks.agent:9001",
                "GroupID": "1",
                "TagIds": "[]",
                "TLS": "true",
                "TLSSkipVerify": "true",
                "TLSSkipClientVerify": "true",
            }
        )

        headers = {
            "Authorization": self.session.headers["Authorization"],
            "Content-Type": content_type,
            "Accept": "application/json, text/plain, */*",
        }

        response = None
        while response is None:
            try:
                response = self.session.post(
                    f"{self.base_url}/endpoints",
                    headers=headers,
                    data=files,
                    verify=False,
                    timeout=10,
                )
            except requests.RequestException:
                time.sleep(1)

        self.set_enpoint_id(name)

        # self.set_swarm_id(self.endpoint_id)

    def set_public_ip(self, ip):
        payload = {"PublicURL": ip}
        self.put(f"/endpoints/{self.endpoint_id}", payload)

    def custom_templates(self, payload):
        self.post("/custom_templates/create/string", payload)

    def delete_custom_templates(self, name):
        response = self.get("/custom_templates")
        if response:
            for template in response:
                if (
                    template["Title"] == name
                    and template["Description"] == "migasfree stack"
                ):
                    self.delete(f"/custom_templates/{template['Id']}")
                    return

    def deploy(self, payload):
        self.post(
            f"/stacks?endpointId={self.endpoint_id}&method=string&type=1", payload
        )

    def settings(self):
        payload = {
            "EdgeAgentCheckinInterval": 5,
            "EnableTelemetry": False,
            "LogoURL": "https://raw.githubusercontent.com/migasfree/migasfree-frontend/master/public/favicon.svg",
            "SnapshotInterval": "5m",
            "TemplatesURL": "https://raw.githubusercontent.com/portainer/templates/v3/templates.json",
        }
        self.put("/settings", payload)

    def get_service_containers(self, service_name):
        url = f"/endpoints/{self.endpoint_id}/docker/containers/json"
        response = self.get(url)
        containers = []
        for container in response:
            if "com.docker.swarm.service.name" in container["Labels"]:
                if container["Labels"]["com.docker.swarm.service.name"] == service_name:
                    containers.append(container["Id"])

        return containers

    def execute_command_in_container(self, container_id, command):
        url = f"/endpoints/{self.endpoint_id}/docker/containers/{container_id}/exec"
        payload = {
            "Cmd": command,
            "AttachStdin": False,
            "AttachStdout": True,
            "AttachStderr": True,
            "Tty": False,
        }
        response = self.post(url, payload)
        exec_id = response["Id"]

        # Start the command execution
        url = f"/endpoints/{self.endpoint_id}/docker/exec/{exec_id}/start"
        payload = {"Detach": False, "Tty": False}
        response = self.session.post(
            f"{self.base_url}{url}", json=payload, verify=False, timeout=10
        )
        return response

    def execute_in_service(self, service_name, command):
        for container_id in self.get_service_containers(service_name):
            self.execute_command_in_container(container_id, command)
