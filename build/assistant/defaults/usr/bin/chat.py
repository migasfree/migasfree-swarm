import os
import google.generativeai as genai
import json
import requests
import time
import random

from google.ai.generativelanguage_v1beta.types import content
from google.api_core.exceptions import ResourceExhausted
from datetime import datetime, timezone

# https://github.com/google-gemini/generative-ai-python/blob/main/docs/api/google/generativeai.md
# https://ai.google.dev/gemini-api?hl=es-419
# https://ai.google.dev/api?hl=es-419&lang=python
# https://github.com/google-gemini/generative-ai-python
# https://ai.google.dev/api/files?hl=es-419

MODEL="gemini-1.5-flash"

config = {
        "instruction": """You are a migasfree assistant.
Respond with the provided **INSTRUCTIONS FOR ASSISTANT**.
Respond in a funny way, using light humor and jokes to make the answers entertaining, but always remain respectful.
Always respond in the same language as the user's prompt.
Si el prompt empieza por **RESPONSE ASSISTANT** no respondas nada.
Asegura que el response_schema es un JSON válido antes de responder. Debe empezar por "{" y acabar con "}"
""",
        "generation_config": {
            "temperature": 1,
            "max_output_tokens": 8192*4,
            "response_schema": content.Schema(
                type = content.Type.OBJECT,
                required = ['message', 'task', 'justification'],
                properties = {
                    "task": content.Schema(
                        type = content.Type.STRING,
                    ),
                    "message": content.Schema(
                        type = content.Type.STRING,
                    ),
                    "justification": content.Schema(
                        type = content.Type.STRING,
                    ),
                    "filename": content.Schema(
                        type = content.Type.STRING,
                    ),
                },
            ),
            "response_mime_type": "application/json",
        }
    }

resources = {
    "sql": ["migasfree-schema.txt"],
    "api": ["migasfree-api.txt"],
    "doc": ["migasfree-schema.txt", "migasfree-api.txt", "fun-with-migasfree.pdf"],
    "chat": [],
    "general":[]
}


FINISH_REASON = {
    "0": "FINISH_REASON_UNSPECIFIED: The finish reason is unspecified.",
    "1": "STOP: Token generation reached a natural stopping point or a configured stop sequence. ",
    "2": "MAX_TOKEN: Token generation reached the configured maximum output tokens.",
    "3": "SAFETY: Token generation stopped because the content potentially contains safety violations. NOTE: When streaming, content is empty if content filters blocks the output.",
    "4": "RECITATION: Token generation stopped because the content potentially contains copyright violations.",
    "5": "OTHER: All other reasons that stopped the token generation.",
    }


# Samples:
# dame de los ordenadores el nombre e ip de cada uno de ellos
# dame el nombre y fecha de actualizacion de los ordenadores sincronizados con el usuario "pepe"
# cuanta ram tiene el ordenador con id=1
# cuantas syncronizaciones se han hecho en 2023
# muestra el numero de sincronizaciones totales realizadas agrupadas por año
# de los ordenadores dame el nombre, ip y forward_ip
# cuantos paquetes hay en cada proyecto
# dame todos los atributos incluidos por un lado y los excluidos por otro, del conjunto de atributos llamado ALBERTO
# como se llama la tabla de atributos
# dame el nombre de cada ordenador con su ip, y su numero de errores ordenados por numero de errores
# que tablas están relacionadas con los ordenadores
# Donne-moi tous les ordinateurs et leurs erreurs.


def get_timestamp():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    return timestamp

def has_expired(expiration_time):
    return datetime.now(timezone.utc) > expiration_time


def download_file(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)


def load_instructions():
    tasks=["classification","sql","api","doc"]
    instructions={}
    for task in tasks:
        with open(f'/etc/assistant/instructions/{task}', 'r') as _file:
            instructions[task] = _file.read()
    return instructions







def exponential_backoff(attempt):
    """Calcula el tiempo de espera antes de reintentar la solicitud."""
    return min(60, (2 ** attempt) + random.uniform(0, 1))

def generate_content_with_retry(model, input_data, safety_settings=None, max_retries=5):
    """
    Función para manejar la generación de contenido y controlar errores 429 (exceso de cuotas).

    Parámetros:
    - model: El modelo de IA que se está utilizando.
    - input_data: Datos de entrada para generar el contenido.
    - safety_settings: Configuración opcional de seguridad para el modelo.
    - max_retries: Número máximo de intentos en caso de error 429.

    Retorna:
    - response: La respuesta generada por el modelo.
    - None: Si falla después de múltiples intentos.
    """

    response = None

    for attempt in range(max_retries):
        try:
            # Intenta generar el contenido usando el modelo
            response = model.generate_content(input_data, stream=False, safety_settings=safety_settings)
            return response  # Si tiene éxito, retorna la respuesta y termina la función.

        except ResourceExhausted as e:
            # Manejo del error 429 de exceso de cuotas
            wait_time = exponential_backoff(attempt)
            print(f"Error 429: Cuota excedida. Esperando {wait_time:.2f} segundos antes de reintentar... (Intento {attempt + 1}/{max_retries})")
            time.sleep(wait_time)  # Espera antes de volver a intentar.

        except Exception as e:
            # Otros errores (fuera del 429)
            print(f"Ocurrió un error inesperado: {str(e)}")
            return None  # Salir y devolver None en caso de error inesperado.

    # Si se alcanzó el número máximo de reintentos y no se obtuvo una respuesta
    print("No se pudo completar la solicitud después de varios intentos.")
    return None


def send_message_with_retry(chat, input_data, safety_settings=None, max_retries=5):

    response = None

    for attempt in range(max_retries):
        try:
            # Intenta generar el contenido usando el modelo
            response = chat.send_message(input_data, stream=False, safety_settings=safety_settings)
            return response  # Si tiene éxito, retorna la respuesta y termina la función.

        except ResourceExhausted as e:
            # Manejo del error 429 de exceso de cuotas
            wait_time = exponential_backoff(attempt)
            print(f"Error 429: Cuota excedida. Esperando {wait_time:.2f} segundos antes de reintentar... (Intento {attempt + 1}/{max_retries})")
            time.sleep(wait_time)  # Espera antes de volver a intentar.

        except Exception as e:
            # Otros errores (fuera del 429)
            print(f"Ocurrió un error inesperado: {str(e)}")
            return None  # Salir y devolver None en caso de error inesperado.

    # Si se alcanzó el número máximo de reintentos y no se obtuvo una respuesta
    print("No se pudo completar la solicitud después de varios intentos.")
    return None








class Chat():

    def __init__(self):
        self.config = config
        self.model = genai.GenerativeModel(
            MODEL,
            generation_config=self.config["generation_config"],
            system_instruction=self.config["instruction"]
        )
        self.chat = self.model.start_chat(history=[])
        self.files = []

        self.instructions = load_instructions()

        self.safety_settings = {
            'HATE': 'BLOCK_NONE',
            'HARASSMENT': 'BLOCK_NONE',
            'SEXUAL' : 'BLOCK_NONE',
            'DANGEROUS' : 'BLOCK_NONE'
        }
        """
        try:
            download_file("http://core:8080/docs/?format=openapi", "/data/migasfree-api.txt")
            if not os.path.exists("/data/fun-with-migasfree.pdf"):
                download_file("https://fun-with-migasfree.readthedocs.io/_/downloads/es/4.19/pdf/", "/data/fun-with-migasfree.pdf")
        except:
            pass
        """

    def set_files(self, task):
        for resource in resources[task]:
            print("RESOURCE", resource,flush=True)
            found = False
            for file in genai.list_files():
                #print("FILE", file,flush=True)
                if file.display_name == resource and file.state==2 and (not has_expired(file.expiration_time)):
                    self.files.append(genai.get_file(name=file.name))
                    found = True
                    break
            if not found:
                if os.path.exists(f"/data/{resource}"):
                    self.files.append(genai.upload_file(f"/data/{resource}"))
                else:
                    raise FileNotFoundError(f"/data/{resource} not found.")


    def classification(self, prompt):
        input=[]
        input.append(self.instructions["classification"])
        input.append(f"**USER PROMPT**\n{prompt}")
        print("INPUT CLASSIFICATION", input)
        #response = self.chat.send_message(input, stream=False, safety_settings=self.safety_settings)
        response = send_message_with_retry(self.chat, input, safety_settings=self.safety_settings, max_retries=5)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            data = {"message": response.text, "justification": f"error", "task": "chat" }




        """
        response.resolve()

        text=""
        for chunk in response:
            text += chunk.text.replace("\n", "")
        try:
            data=json.loads(text)
        except:
            pass

        print("RESPONSE DIR:", dir(response), flush=True)
        print("RESPONSE CLASS:", response.text, flush=True)
        try:
            data=json.loads(response.text)
        except Exception as e:
            print(str(e), flush=True)

            data={"response":f"{str(e)}","justification":f"{str(e)}", "task":"general"}

        """

        return data


    def send(self, prompt):
        if prompt.lower() == "exit":
            exit(0)
        classification = self.classification(prompt)
        print("CLASSIFICATION", classification, flush=True)

        if classification["task"] == "chat" or classification["task"] == "general" :
            return classification
        else:
            return self.task(prompt, classification["task"])


    def task(self, prompt, task_type):
        time.sleep(1)
        self.set_files(task_type)
        input = self.files
        input.append(self.instructions[task_type])
        input.append(f"**USER PROMPT**\n{prompt}")
        print("INPUT", input, flush=True)

        #response = self.model.generate_content(input, stream=False, safety_settings=self.safety_settings)

        response = generate_content_with_retry(self.model, input, safety_settings=self.safety_settings, max_retries=5)

        #response.resolve()

        finish_reason = response.candidates[0].finish_reason

        if finish_reason > 1:
            return {
                "prompt": prompt,
                "message": f"{FINISH_REASON[str(finish_reason)]}",
                "task": task_type,
                "finish_reason": finish_reason
            }

        """
        text=""
        for chunk in response:
            text += chunk.text.replace("\n", "")

        print("RESPONSE TASK:", response.text, flush=True)
        data=json.loads(response.text)
        """
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            data = {"message": response.text, "justification": f"error", "task": "chat" }



        data["prompt"] = prompt
        if 'filename' in data:
            data["filename"] = f"{get_timestamp()}_{data['filename']}"
        else:
            data["filename"] = f"{get_timestamp()}"
        data["task"] = task_type
        data["finish_reason"] = finish_reason

        # For history
        #response = self.chat.send_message(f"**RESPONSE ASSISTANT**\n{data['response']}", stream=False, safety_settings=self.safety_settings)
        response = send_message_with_retry(self.chat, f"**RESPONSE ASSISTANT**\n{data['message']}", safety_settings=self.safety_settings, max_retries=5)

        return data








"""
if __name__ == "__main__":
    chat = Chat()
    while True:
        user_input = input("> ")
        data = chat.send(user_input)
        print(data["sql"])
        print(data["justification"])
"""