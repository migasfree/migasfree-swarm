from pathlib import Path
import os

ROOT = '/v1'

PATH_CERTIFICATES = Path('/mnt/cluster/certificates')
PATH_DATASHARES = Path('/mnt/cluster/datashares')

MAX_TOKEN_AGE_HOURS = 72

STACK = os.environ["STACK"]