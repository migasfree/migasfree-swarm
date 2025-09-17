import os

STACK = os.getenv("STACK", "")

FQDN = os.getenv("FQDN","localhost")

ASSISTANT_API_URL = "http://assistant:8080"

AI_PATH = f"/mnt/datashare/pool/ai"

CORPUS_PATH_DOCS = os.path.join(AI_PATH,"corpus/docs")
RESUME_FILE_DOCS = os.path.join(CORPUS_PATH_DOCS,"resume.json")

CORPUS_PATH_DATABASE = os.path.join(AI_PATH,"corpus/database")
RESUME_FILE_DATABASE = os.path.join(CORPUS_PATH_DATABASE,"resume.json")

CORPUS_PATH_API = os.path.join(AI_PATH,"corpus/api")
RESUME_FILE_API = os.path.join(CORPUS_PATH_API,"resume.json")

CORPUS_PATH_EMBEDDING = os.path.join(AI_PATH,"corpus/embedding")

with open(f'/run/secrets/{STACK}_superadmin_name', 'r', encoding='utf-8') as f:
    SUPERADMIN_NAME = f.read()

EMAIL = f"{SUPERADMIN_NAME}@{FQDN}"
