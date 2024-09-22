import google.generativeai as genai
import json
from datetime import datetime, timezone

# https://ai.google.dev/gemini-api?hl=es-419
# https://ai.google.dev/api?hl=es-419&lang=python
# https://github.com/google-gemini/generative-ai-python
# https://ai.google.dev/api/files?hl=es-419

Instruction="""
You are an expert database analyst specialized in writing SQL statements.
Answer the questions with the requested SQL SELECT statement.
Always respond in plain text with a JSON containing these three elements:
{"sql":"","justification":"","filename":""}.
Propose a short and descriptive filename for the query.
Avoid using extensions in the filename.
The data model you are accessing contains the client_computer table with the ip_address field and it is safe to perform the SELECT using this field name.
When asked for "formulas," it refers to the "core_property" table.
"""


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


resource = "migasfree-schema.txt"

def get_timestamp():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    return timestamp

def has_expired(expiration_time):
    return datetime.now(timezone.utc) > expiration_time

class Chat():

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash",  system_instruction=Instruction)
        self.chat = self.model.start_chat(
            history=[]
        )
        self.file_schema = None

    def set_file_schema(self):
        if self.file_schema == None or has_expired(self.file_schema.expiration_time):
            # Search for the schema file, and if the status is ACTIVE, assign it to 'self.file_schema'
            for file in genai.list_files():
                if file.display_name == resource and file.state==2:
                    self.file_schema = genai.get_file(name=file.name)
                    return
            # upload schema
            print("uplading eschema to gemini")
            self.file_schema = genai.upload_file(f"/data/{resource}")

    def send(self, query):

        if query.lower() == "reset":
            exit(0)

        self.set_file_schema()


        response = self.model.generate_content([self.file_schema,  query], stream=True)
        response.resolve()
        try:

            #print("REASON",response.candidates[0].finish_reason)
            if response.candidates[0].finish_reason == 3:
                return {"query": query, "sql": f"SELECT 'Blocked' as type, 'For security reasons' AS mensaje", "justification": "", "filename": "safety"}

            text=""
            for chunk in response:
                text += chunk.text.replace("\n", "")

            data=json.loads(text[7:-3])
            data["query"] = query
            data["filename"] = f"{get_timestamp()}_{data['filename']}"
        except Exception as e:
            data = {"query": query, "sql": f"SELECT 'error' as type, '{str(e)}' AS mensaje", "justification": str(e), "filename": "error"}

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