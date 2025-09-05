import requests
import logging
import time
import os
import json
import re

from database import get_tables_catalog, get_table_schema, validate_sql, run_sql_select_query
from docs import get_chapter_content
from api import get_api_category
from semantic import SemanticChapterSearch
from resources import read_file
from settings import CORPUS_PATH_DOCS, RESUME_FILE_DOCS, RESUME_FILE_API


from prompts import PROMPTS



logging.basicConfig(
    filename='/app/mcp.log',   # Ruta del archivo donde se guardarán los logs
    level=logging.INFO,            # Nivel mínimo de log (INFO, DEBUG, WARNING, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s'
)


ASSISTANT_API_URL = "http://assistant:8080"
ASSISTANT_API_KEY = "sk-2541056f37804b6b82aeee21415a5e2d"


MODEL_BASE = None


def clean_code(text):
    """
    Removes lines that start with triple backticks (```) from a given text.
    Also removes any empty lines that may result after cleaning.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned text without lines starting with ```.
    """
    # Step 1: Remove lines that match the pattern ^\s*```.*
    text = re.sub(r'^\s*```.*$', '', text, flags=re.MULTILINE)
    # Step 2: Remove any remaining empty or whitespace-only lines
    text = '\n'.join([line for line in text.splitlines() if line.strip()])
    return text


def get_base_model_id(id="gas"):
    headers = {
        "Authorization": f"Bearer {ASSISTANT_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{ASSISTANT_API_URL}/api/models", headers=headers)
    if response.status_code == 200:
        result = response.json()
        model = next((m for m in result["data"] if m["id"] == id), None)
        return model["info"]["base_model_id"]
    else:
        raise Exception("ERROR in model {id}: base_model_id not found")
        return ""


def call_model(system_prompt, user_prompt):

    global MODEL_BASE

    if MODEL_BASE is None:
        MODEL_BASE = get_base_model_id("gas")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


    headers = {
        "Authorization": f"Bearer {ASSISTANT_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_BASE,
        "messages": messages,
        "stream": False
    }


    max_retries = 5

    for attempt in range(max_retries):
        response = requests.post(f"{ASSISTANT_API_URL}/api/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            return reply

        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")

            if retry_after is not None:
                try:
                    wait_seconds = int(retry_after)
                except ValueError:
                    # Si no es número, lo ignoramos y usamos un backoff
                    wait_seconds = 2 ** attempt
            else:
                wait_seconds = 2 ** attempt  # Backoff exponencial por defecto

            logging.info(f"⚠️ Límite alcanzado. Esperando {wait_seconds} segundos antes del intento {attempt + 1}/{max_retries}...")
            time.sleep(wait_seconds)

        else:
            logging.info(f"❌ Error {response.status_code}: {response.text}")
            return f"❌ Error {response.status_code}: {response.text}"

    return "❌ Se agotaron los intentos tras múltiples errores 429."





def guru(question):

    system_prompt = PROMPTS["classifier"]

    logging.info(f"**************************** {MODEL_BASE} *****************************************")
    logging.info(f"🤖 QUESTION: {question}")

    classification = call_model(system_prompt, question)
    classification = classification.strip()

    logging.info(f"🤖 CLASSICATION: {classification}")

    try:
        if classification == "database":
            answer = retrieve_data(question)
        elif classification == "schema_db":
            answer = f"```json\n{json.dumps(retrieve_schema_db(question))}\n```"
        elif classification == "docs":
            answer = retrieve_docs(question)
        elif classification == "api":
            answer = retrieve_api(question)
        elif classification == "code":
            answer = retrieve_code(question)
        else:
            answer = "I’m not sure how to address this matter."
    except Exception as e:
        answer = f"❌ {e}"


    logging.info(answer)

    return json.dumps({
        "model_llm": MODEL_BASE,
        "question": question,
        "classification": classification,
        "response": answer
    })



def retrieve_schema_db(question):
    #logging.info(f"🤖 QUESTION: {question}")

    available_tables = get_tables_catalog()

    system_prompt = PROMPTS["database_selector"]

    user_prompt =f"""
AVAILABLE_TABLES:
{available_tables}

QUESTION: {question}

Return only the JSON array of relevant table names:
"""

    tables_json = call_model(system_prompt, user_prompt)

    logging.info(f"🤖 TABLES: {tables_json}")
    tables = json.loads(clean_code(tables_json))

    schema = []
    for table in tables:
        schema.append(json.loads(get_table_schema(table)))

    return schema

def retrieve_data(question):
    """
    Dada una question, genera una SELECT de SQL, la ejecuta y devuelve los datos
    """

    schema = retrieve_schema_db(question)

    system_prompt = PROMPTS["database_sql"]
    user_prompt = f"""
CONTEXT:
Database Schema: {schema}
User Question: {question}

Generate the SQL SELECT statement following all requirements above.
"""

    # CREATE A SELECT STATEMENT
    # =========================
    check = {"valid": False}
    for i in range(3):
        select = call_model(system_prompt, user_prompt)
        select = clean_code(select)
        check = validate_sql(select)

        logging.info(f"🤖 CHECK: {check}")

        if check["valid"] == True:
            break
        else:
            user_prompt = f"""{user_prompt}

select {i}:
{select}

❌ error {i}:
{check["message"]}

"""

            logging.info(f"❌ {user_prompt}")


    if not check["valid"]:
        return f"""
ANSWER:
-------
❌ SQL:
{select}

{check['message']}
"""

    data = run_sql_select_query(select)
    #logging.info(f"🤖 DATA: {data}")

    result  = f"""
** SQL executed:
{select}

ANSWER:
-------
{data}

"""
    return result


def retrieve_docs(question):

    resume_docs = read_file(RESUME_FILE_DOCS)

    system_prompt = PROMPTS["docs_selector"]
    user_prompt = f"""
DOCUMENT CATALOG:
{resume_docs}

USER QUESTION: {question}

INSTRUCTIONS:
Analyze the user's question and select up to 3 most relevant documents from the catalog. Consider:
- Direct topic matches
- Related concepts and keywords
- Context and user intent
- Information completeness

Return only a JSON array of the selected filenames, ordered by relevance.
"""

    filenames_json = call_model(system_prompt, user_prompt)


    logging.info(f"🤖 CHAPTERS: {filenames_json}")
    filenames = json.loads(clean_code(filenames_json))
    context = ""
    """
    for filename in filenames:
        logging.info(f"🤖 SOURCE DOCUMENT {filename}")
        context += f"SOURCE DOCUMENT {filename}:\n{get_chapter_content(filename)}"
    """

    try:

        searcher = SemanticChapterSearch()
        chunks = searcher.search_chunks_with_context(question)

        for chunk in chunks:
            if not chunk['filename'] in filenames:
                logging.info(f"🤖 SOURCE DOCUMENT (chunk)  {chunk['filename']}")
                context += f"SOURCE DOCUMENT (chunk) {chunk['filename']}:\n{chunk['full_text']}"


    except Exception as e:
        context += f"🤖 CHUNKS: {e}"


    system_prompt = PROMPTS["docs"]

    user_prompt = f"""
CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS: Please analyze the provided context and answer the question using only the
information available in the source documents. Include the name of source documents and indicate if any
part of the question cannot be answered based on the available context.
"""

    response = call_model(system_prompt, user_prompt)

    return f"""
** Context lenght: ({len(context)} bytes)

ANSWER:
{response}

"""


def retrieve_schema_api(question):
    resume_api = read_file(RESUME_FILE_API)

    system_prompt = PROMPTS["api_selector"]
    user_prompt = f"""
API CATALOG:
{resume_api}

USER QUESTION: {question}

INSTRUCTIONS:
Analyze the user's question and select up to 2 most relevant documents from the catalog. Consider:
- Direct topic matches
- Related concepts and keywords
- Context and user intent

Return only a JSON array of the selected filenames, ordered by relevance. No comments. ONLY JSON.
"""

    filenames_json = call_model(system_prompt, user_prompt)

    logging.info(f"🤖 APIS: {filenames_json}")

    filenames = json.loads(clean_code(filenames_json))

    api = []
    for filename in filenames:
        logging.info(f"🤖 API {filename}")
        api.append(get_api_category(filename))
    return api



def retrieve_api(question):

    context = retrieve_schema_api(question)

    system_prompt = PROMPTS["api"]

    user_prompt = f"""
API SCHEMA:
{context}

QUESTION: {question}

Please provide:
A detailed explanation of the relevant API endpoints
Any important considerations or limitations
"""

    response = call_model(system_prompt, user_prompt)

    return f"""
** Context lenght: ({len(context)} bytes)

ANSWER:
{response}

"""

def retrieve_code(question):
    context = retrieve_schema_api(question)

    system_prompt = PROMPTS["api"]

    user_prompt = f"""
API SCHEMA:
{context}

QUESTION: {question}

Please provide:
A script
"""

    response = call_model(system_prompt, user_prompt)

    return f"""
** Context lenght: ({len(context)} bytes)

ANSWER:
{response}

"""
