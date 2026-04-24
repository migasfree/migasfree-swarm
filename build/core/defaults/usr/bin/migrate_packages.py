#!/usr/bin/python3

import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple

import requests
from django.conf import settings
from migasfree.core.pms import get_pms
from migasfree.core.validators import build_magic
from migasfree.secure import unwrap, wrap
from migasfree.utils import get_secret, get_setting
from requests.adapters import HTTPAdapter
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib3.util.retry import Retry

# --- Configuration & Constants ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

_fqdn = os.environ.get("MIGASFREE_FQDN") or get_setting("MIGASFREE_FQDN")
SERVER_URL = f"http://{_fqdn}"
API_URL = f"{SERVER_URL}/api/v1/token"
UPLOAD_PKG_URL = f"{SERVER_URL}/api/v1/safe/packages/"

PRIVATE_KEY = Path(get_setting("MIGASFREE_KEYS_DIR")) / "migasfree-packager.pri"
PUBLIC_KEY = Path(get_setting("MIGASFREE_KEYS_DIR")) / "migasfree-server.pub"
TMP_DIR = Path("/tmp")
OLD_STORE_TRAILING = "STORES"


class Migrator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": self._get_auth_token()})

        # Reliability strategy: Retry on common transient errors
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _get_auth_token(self) -> str:
        import os

        # 1. Try environment variable
        token = os.environ.get("MIGASFREE_TOKEN")
        if token:
            return f"Token {token}"

        # 2. Fallback: Login with superadmin credentials
        try:
            username = get_secret("superadmin_name")
            password = get_secret("superadmin_pass")
            if username and password:
                logger.info(f"Attempting login as {username}...")
                # Use localhost:8080 to reach Gunicorn directly inside the container
                login_url = "http://localhost:8080/api/v1/token/login/"
                resp = requests.post(
                    login_url,
                    json={"username": username, "password": password},
                    timeout=10,
                )
                if resp.status_code == 200:
                    return f"Token {resp.json()['token']}"
        except Exception as e:
            logger.warning(f"Fallback login failed: {e}")

        logger.error("No valid authentication mechanism found.")
        return ""

    def get_locations(self) -> Generator[Path, None, None]:
        """Memory-efficient exploration of media directory using generators."""
        media_root = Path(settings.MEDIA_ROOT)
        store_path = get_setting("MIGASFREE_STORE_TRAILING_PATH")

        for path in media_root.iterdir():
            if path.is_dir():
                for sub in path.rglob(store_path):
                    if sub.is_dir():
                        yield sub

    def migrate_structure(self, projects: List[Dict[str, Any]]) -> None:
        """Translates legacy directory structure to new standard naming."""
        media_root = Path(settings.MEDIA_ROOT)
        store_path = get_setting("MIGASFREE_STORE_TRAILING_PATH")

        for prj in projects:
            source = media_root / prj["name"] / OLD_STORE_TRAILING
            if source.exists():
                target = media_root / prj["slug"] / store_path
                target.parent.mkdir(parents=True, exist_ok=True)
                source.rename(target)
                logger.info(f"{source} migrated to {target}")

                # Cleanup old project base if empty
                old_root = media_root / prj["name"]
                if old_root.exists() and not any(old_root.iterdir()):
                    old_root.rmdir()

    def upload_package(
        self, data: Dict[str, Any], upload_files: List[Path]
    ) -> Dict[str, Any]:
        """Securely prepares and uploads package with JWE/JWS wrapping."""
        payload = json.dumps(
            {
                "msg": wrap(
                    data, sign_key=str(PRIVATE_KEY), encrypt_key=str(PUBLIC_KEY)
                ),
                "project": data["project"],
            }
        )

        my_magic = build_magic()
        file_list: List[Tuple[str, Tuple[str, bytes, str]]] = []

        for _file in upload_files:
            content = _file.read_bytes()
            tmp_header = TMP_DIR / _file.name
            tmp_header.write_bytes(content[:1024])
            mime = my_magic.file(str(tmp_header))
            tmp_header.unlink(missing_ok=True)

            file_list.append(("file", (_file.name, content, mime)))

        fields = json.loads(payload)
        fields.update(dict(file_list))

        encoder = MultipartEncoder(fields=fields)
        headers = {"Content-Type": encoder.content_type}

        try:
            resp = self.session.post(UPLOAD_PKG_URL, data=encoder, headers=headers)
            resp.raise_for_status()
            json_resp = resp.json()

            if "msg" in json_resp:
                return unwrap(
                    json_resp["msg"],
                    decrypt_key=str(PRIVATE_KEY),
                    verify_key=str(PUBLIC_KEY),
                )
            return json_resp
        except requests.RequestException as e:
            logger.error(f"Upload failed for {data.get('fullname')}: {e}")
            return {"error": str(e)}

    def migrate_packages(self) -> None:
        """Finds and migrates individual packages based on Ic-containing match."""
        media_root = Path(settings.MEDIA_ROOT)
        packages: List[Dict[str, Any]] = []

        for location in self.get_locations():
            # Calculate depth relative to media root
            base_parts = location.relative_to(media_root).parts
            for item in location.iterdir():
                if item.is_file():
                    packages.append(
                        {
                            "location": item,
                            "fullname": item.name,
                            "project": base_parts[0],
                            "store": base_parts[-1],
                        }
                    )

        for pkg in packages:
            try:
                resp = self.session.get(
                    f"{API_URL}/packages/",
                    params={
                        "fullname__icontains": pkg["fullname"],
                        "project__name__icontains": pkg["project"],
                        "store__name__icontains": pkg["store"],
                    },
                )
                resp.raise_for_status()
                data = resp.json()

                if data["count"] == 1:
                    target = data["results"][0]
                    logger.info(f"Migrating {target['fullname']}...")
                    self.upload_package(
                        data={
                            "project": target["project"]["name"],
                            "store": target["store"]["name"],
                            "is_package": True,
                        },
                        upload_files=[pkg["location"]],
                    )
            except requests.RequestException as e:
                logger.warning(f"Could not query package {pkg['fullname']}: {e}")

    def migrate_package_sets(self) -> None:
        """Finds and migrates package sets by matching directory structures."""
        media_root = Path(settings.MEDIA_ROOT)
        package_sets: List[Dict[str, Any]] = []

        for location in self.get_locations():
            for entry in location.iterdir():
                if entry.is_dir() and any(entry.iterdir()):
                    parts = entry.relative_to(media_root).parts
                    package_sets.append(
                        {
                            "location": entry,
                            "name": entry.name,
                            "project": parts[0],
                            "store": parts[-2],
                            "packages": [
                                f.name for f in entry.iterdir() if f.is_file()
                            ],
                        }
                    )

        for pset in package_sets:
            try:
                resp = self.session.get(
                    f"{API_URL}/package-sets/",
                    params={
                        "name": pset["name"],
                        "project__name__icontains": pset["project"],
                        "store__name__icontains": pset["store"],
                    },
                )
                resp.raise_for_status()
                data = resp.json()

                if data["count"] == 1:
                    target = data["results"][0]
                    logger.info(f"Migrating package set {target['name']}...")

                    files_to_upload = []
                    for pkg_name in pset["packages"]:
                        pkg_path = pset["location"] / pkg_name
                        files_to_upload.append(
                            (
                                "files",
                                (
                                    pkg_name,
                                    pkg_path.read_bytes(),
                                    get_pms(target["project"]["pms"]).mimetype[0],
                                ),
                            )
                        )

                    encoder = MultipartEncoder(fields=files_to_upload)
                    patch_resp = self.session.patch(
                        f"{API_URL}/package-sets/{target['id']}/",
                        data=encoder,
                        headers={"Content-Type": encoder.content_type},
                    )
                    if patch_resp.status_code == requests.codes.ok:
                        logger.info(
                            f"Package set {target['name']} migrated successfully."
                        )
                    else:
                        logger.error(
                            f"Failed to migrate {target['name']}: {patch_resp.text}"
                        )
            except requests.RequestException as e:
                logger.warning(
                    f"Connectivity issue during package set {pset['name']} migration: {e}"
                )

    def get_projects(self) -> List[Dict[str, Any]]:
        """Retrieves and paginates projects from the API."""
        try:
            resp = self.session.get(f"{API_URL}/projects/")
            if resp.status_code != requests.codes.ok:
                logger.error("Invalid credentials. Review token.")
                sys.exit(1)

            data = resp.json()
            if "detail" in data:
                logger.error(data["detail"])
                sys.exit(1)

            # Paginate to get all results
            resp = self.session.get(
                f"{API_URL}/projects/", params={"page_size": data["count"]}
            )
            return resp.json()["results"]
        except requests.RequestException as e:
            logger.critical(f"Failed to fetch projects: {e}")
            sys.exit(1)

    def update_projects(self, projects: List[Dict[str, Any]]) -> None:
        """Normalizes PMS naming conventions concurrently."""
        def _update(prj):
            if prj["pms"].startswith("apt"):
                prj["pms"] = "apt"

            prj["platform"] = prj["platform"]["id"]
            try:
                resp = self.session.patch(f"{API_URL}/projects/{prj['id']}/", json=prj)
                if resp.status_code == requests.codes.ok:
                    logger.info(f"Project {prj['name']} normalized.")
            except requests.RequestException as e:
                logger.error(f"Failed to update project {prj['name']}: {e}")

        num_workers = (os.cpu_count() or 1) * 5
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            executor.map(_update, projects)

    def regenerate_metadata(self) -> None:
        """Trigger metadata regeneration for all internal-source deployments concurrently."""
        try:
            resp = self.session.get(f"{API_URL}/deployments/internal-sources/")
            data = resp.json()

            resp = self.session.get(
                f"{API_URL}/deployments/internal-sources/",
                params={"page_size": data["count"]},
            )

            results = resp.json()["results"]
            logger.info(f"Regenerating metadata for {len(results)} deployments...")

            def _regenerate(deploy):
                try:
                    m_resp = self.session.get(
                        f"{API_URL}/deployments/internal-sources/{deploy['id']}/metadata/",
                        timeout=300 # High timeout for metadata
                    )
                    if m_resp.status_code == requests.codes.ok:
                        logger.info(f"Metadata for {deploy['name']} regenerated.")
                    else:
                        logger.error(f"Metadata regeneration failed for {deploy['name']}.")
                except requests.RequestException as e:
                    logger.error(f"Metadata task failed for {deploy['name']}: {e}")

            num_workers = (os.cpu_count() or 1) * 4
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                executor.map(_regenerate, results)

        except requests.RequestException as e:
            logger.error(f"Metadata fetch failed: {e}")


if __name__ == "__main__":
    migrator = Migrator()

    # Execution sequence
    all_projects = migrator.get_projects()
    migrator.update_projects(all_projects)
    migrator.migrate_structure(all_projects)
    migrator.migrate_packages()
    migrator.migrate_package_sets()
    migrator.regenerate_metadata()
