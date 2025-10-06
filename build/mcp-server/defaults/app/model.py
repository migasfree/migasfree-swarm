import requests
import logging
import time
import json
import re

from database import get_tables_catalog, get_table_schema, validate_sql, run_sql_select_query
from api import get_api_category
from resources import read_file
from settings import RESUME_FILE_API, ASSISTANT_API_URL
from assistant import ASSISTANT_API_KEY, get_base_model_id
from prompts import PROMPTS
from docs import CONTENT_MANUAL


MODEL_BASE = None

logging.basicConfig(
    filename='/app/mcp.log',  # Ruta del archivo donde se guardarán los logs
    level=logging.INFO,  # Nivel mínimo de log (INFO, DEBUG, WARNING, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s'
)


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


def call_model(system_prompt, user_prompt):
    global MODEL_BASE

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

        if response.status_code == requests.codes.ok:
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

            logging.info(f"❗ Limit reached. Waiting {wait_seconds} seconds before attempt {attempt + 1}/{max_retries}...")
            time.sleep(wait_seconds)

        else:
            logging.info(f"❌ Error {response.status_code}: {response.text}")
            raise RuntimeError(f"❌ Error HTTP {response.status_code}: {response.text}")

    logging.info("❌ Error 429. We couldn't complete your request because too many attempts failed. Please try again later.")
    raise RuntimeError("❌ We couldn't complete your request because too many attempts failed. Please try again later.")


def guru(question):
    global MODEL_BASE

    MODEL_BASE = get_base_model_id("gas")

    system_prompt = PROMPTS["classifier"]

    logging.info(f"**************************** Model base: {MODEL_BASE} *****************************************")
    logging.info(f"🤖 QUESTION: {question}")

    try:
        classification = call_model(system_prompt, question)
    except Exception as e:
        return f"❌ {str(e)}"

    classification = classification.strip()

    logging.info(f"🤖 CLASSIFICATION: {classification}")

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
        answer = f"❌ {str(e)}"

    logging.info(answer)

    return json.dumps({
        "model_llm": MODEL_BASE,
        "question": question,
        "classification": classification,
        "response": answer
    })


def retrieve_schema_db(question):
    # logging.info(f"🤖 QUESTION: {question}")

    available_tables = get_tables_catalog()

    system_prompt = PROMPTS["database_selector"]

    user_prompt = f"""
AVAILABLE_TABLES:
{available_tables}

QUESTION: {question}

Return only the JSON array of relevant table names:
"""
    try:
        tables_json = call_model(system_prompt, user_prompt)
    except Exception as e:
        return f"❌ {str(e)}"

    logging.info(f"🤖 TABLES: {tables_json}")
    tables = json.loads(clean_code(tables_json))

    schema = []
    for table in tables:
        schema.append(json.loads(get_table_schema(table)))

    return schema


def retrieve_data(question):
    """
    Given a question, generates a SQL SELECT statement, executes it, and returns the data
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
        time.sleep(1)
        try:
            select = call_model(system_prompt, user_prompt)
        except Exception as e:
            return f"❌ {str(e)}"

        select = clean_code(select)
        check = validate_sql(select)

        logging.info(f"🤖 CHECK: {check}")

        if check["valid"] is True:
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
    # logging.info(f"🤖 DATA: {data}")

    result = f"""
** SQL executed:
{select}

ANSWER:
-------
{data}

"""
    return result


def retrieve_docs(question):
    system_prompt = PROMPTS["docs"]
    user_prompt = f"""
CONTEXT:
{CONTENT_MANUAL}

INSTRUCTIONS:
Please analyze the CONTEXT and answer the QUESTION.

QUESTION:
{question}
"""
    try:
        response = call_model(system_prompt, user_prompt)
    except Exception as e:
        return f"❌ {str(e)}"

    return f"""

** Context lenght: ({len(CONTENT_MANUAL)} bytes)


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
    try:
        filenames_json = call_model(system_prompt, user_prompt)
    except Exception as e:
        return f"❌ {str(e)}"

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
    try:
        response = call_model(system_prompt, user_prompt)
    except Exception as e:
        return f"❌ {str(e)}"

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
    try:
        response = call_model(system_prompt, user_prompt)
    except Exception as e:
        return f"❌ {str(e)}"

    return f"""
** Context lenght: ({len(context)} bytes)

ANSWER:
{response}

"""
