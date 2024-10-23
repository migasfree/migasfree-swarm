import web
import csv
import psycopg2
import json
import io
import os
import sys

from chat import Chat


def get_secret_pass():
    stack=os.environ['STACK']
    password = ''
    with open(f'/run/secrets/{stack}_superadmin_pass', 'r') as f:
        password = f.read()
    return password

FQDN = os.environ['FQDN']

DATABASE = {
    'dbname': os.environ['POSTGRES_DB'],
    'user': os.environ['POSTGRES_USER'],
    'password': get_secret_pass(),
    'host': os.environ['POSTGRES_HOST'],
    'port': os.environ['POSTGRES_PORT']
    }


urls = (
    '/', 'Index',
    '/health', 'Health',
    '/send', 'Send',
    '/files/(.*)', 'File'
)

render = web.template.render('/www/templates/')
path_prompts = "/data/prompts"
path_resources = "/data/resources"
path_files = "/data/files"
path_database_console ="/database_console"

mychat = Chat()

class Index:
    def GET(self):
        return render.index()

class Health:
    def GET(self):
        return "OK"

class File:
    def GET(self, file):

        full_file_path = os.path.join(path_files, file)
        if not os.path.isfile(full_file_path) or not full_file_path.startswith(path_files):
            return web.notfound("Not found")

        with open(full_file_path, 'rb') as f:
            content = f.read()

        web.header('Content-Type', 'application/octet-stream')
        web.header(f'Content-Disposition', f'attachment; filename="{os.path.basename(full_file_path)}"')
        return content

class Send:
    def POST(self):
        data = web.input()
        prompt = str(data.prompt)
        print("DATA", data, flush=True)
        response = mychat.send(prompt)
        output={"message": ""}

        if response["task"] == "sql":

            max_retries = 3
            for attempt in range(max_retries):
                output["message"] += f"{response['justification']}<br><br><small>{response['message']}</small><br>"
                try:
                    output["link"] =  file_csv(response)
                    break
                except Exception as e:
                    output["message"] += f'<br><span style="color: red;">!!! {str(e)}</span><br><br>'
                    response = mychat.task(f"{prompt}\n{response['message']}\n**ERROR:** {str(e)}", "sql")
                    if attempt == max_retries - 1:
                        break

        if response["task"] == "api":
            output["link"] =  file_code(response)
            output["message"] = f"{response['justification']}<br>"

        if response["task"] == "doc":
            output["message"] = response["message"]

        if response["task"] == "chat" or response["task"] == "general":
            if "message" in response:
                output["message"] = response["message"]
            else:
                output["message"] = "???"

        web.header('Content-Type', 'application/json')

        return json.dumps(output)


def file_code(data):

    download_file = f"https://{FQDN}/services/assistant/files/{data['filename']}"

    content = f"""
'''
{data['filename']}
(Powered by Gemini & migasfree)

User: {data['prompt']}

Gemini: {data['justification']}

'''
{data['message']}
"""

    # Save data
    with open(f"{path_prompts}/{data['filename']}.json", 'w') as file:
        json.dump(data, file, indent=4)

    # Save code
    with open(f"{path_files}/{data['filename']}", 'w') as file:
        file.write(content)

    return download_file


def file_csv(data):

    download_file = f"https://{FQDN}/services/assistant/files/{data['filename']}.csv"

    # Save data
    with open(f"{path_prompts}/{data['filename']}.json", 'w') as file:
        json.dump(data, file, indent=4)

    # Save to datashare_console file with SELECT SQL
    with open(f"{path_database_console}/{data['filename']}", 'w') as file:
        file.write("/*\n\n")
        file.write(f"{data['filename']}\n(Powered by Gemini & migasfree)\n\n")
        file.write(f"User: {data['prompt']}\n\n")
        file.write(f"Gemini: {data['justification']}\n\n")
        file.write("*/\n\n")
        file.write(data['message'])

    # Establecer conexión con la base de datos
    conn = psycopg2.connect(**DATABASE)
    cursor = conn.cursor()

    # Ejecutar la consulta SQL
    cursor.execute(data["message"])
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]

    # Abrir un archivo en modo escritura (w) para grabar el CSV en disco
    with open(f"{path_files}/{data['filename']}.csv", mode='w', newline='') as csv_file:
        csvwriter = csv.writer(csv_file)

        # Escribir los nombres de las columnas en la primera fila
        csvwriter.writerow(colnames)

        # Escribir las filas de resultados
        csvwriter.writerows(rows)

    # Cerrar la conexión con la base de datos
    cursor.close()
    conn.close()

    # Devolver el link del archivo
    return download_file




if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()