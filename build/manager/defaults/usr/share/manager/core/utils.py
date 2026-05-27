import os
import re
import subprocess
import json
from datetime import datetime

from core.config import PATH_DATASHARES

def grep(file, pattern):
    regex = re.compile(pattern)
    try:
        with open(file, "r") as f:
            for line in f:
                if regex.search(line):
                    return line.strip()
    except Exception:
        pass
    return None


def get_variable(file, variable):
    from pathlib import Path
    path = Path(file)
    if not path.exists():
        return ""

    try:
        line = grep(str(path), r"^" + variable + r"\s*=")
        if line:
            _, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            return value
    except Exception:
        pass
    return ""


def get_host(stack) -> str:
    fqdn = get_fqdn(stack)
    port = get_variable(str(PATH_DATASHARES/stack/"stack.conf"), "PORT_HTTPS")
    if port == "443" or not port:
        return fqdn
    return f"{fqdn}:{port}"


def get_fqdn(stack) -> str:
    return get_variable(str(PATH_DATASHARES/stack/"stack.conf"), "FQDN")


async def get_organization(stack) -> str:
    with open(str(PATH_DATASHARES/stack/"conf/settings.py"), 'r', encoding='utf-8') as file:
        content = file.read()
    pattern = r'MIGASFREE_ORGANIZATION\s*=\s*(.+)'
    result = re.search(pattern, content)
    if result:
        return result.group(1)[1:-1]
    return ''


def get_extensions() -> list[str]:
    pms_enabled = os.environ['PMS_ENABLED']
    extensions = []
    result = subprocess.run(
        ['curl', '-X', 'GET', 'core:8080/api/v1/public/pms/'],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    if result.returncode == 0:
        all_pms = json.loads(result.stdout)
        for pms in all_pms:
            if f'pms-{pms}' in pms_enabled:
                for extension in all_pms[pms]['extensions']:
                    extensions.append(extension)
    return list(set(extensions))


def get_timestamp() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
