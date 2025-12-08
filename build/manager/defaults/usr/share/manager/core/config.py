from pathlib import Path
import os
ROOT_PATH = '/manager'
API_VERSION = '/v1'

PATH_CERTIFICATES = Path('/mnt/cluster/certificates')
PATH_DATASHARES = Path('/mnt/cluster/datashares')

MAX_TOKEN_AGE_HOURS = 72

FQDN = os.environ["FQDN"]
STACK = os.environ["STACK"]


CORE_URL = "http://core:8080"
CORE_LOGIN_URL = f"{CORE_URL}/rest-auth/login/"
CORE_USER_URL = f"{CORE_URL}/rest-auth/user/"
CORE_TOKEN_URL = f"{CORE_URL}/api/v1/token"
CORE_AUTH_URL = f"{CORE_URL}/token-auth/"

