import os

from resources import read_file
from settings import AI_PATH

PROMPTS = {}


def load_prompt(name):
    global PROMPTS
    if os.path.exists(f"{AI_PATH}/prompts/{name}.txt"):
        PROMPTS[name] = read_file(f"{AI_PATH}/prompts/{name}.txt")
    else:
        PROMPTS[name] = read_file(f"prompts/{name}.txt")


load_prompt("classifier")
load_prompt("docs_selector")
load_prompt("docs")
load_prompt("database_selector")
load_prompt("database_schema")
load_prompt("database_sql")
load_prompt("api_selector")
load_prompt("api_schema")
load_prompt("api")
