import os

STACK = os.getenv("STACK", "")

EMAIL = os.getenv("EMAIL", "admin@domain.com")

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