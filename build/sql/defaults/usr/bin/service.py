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


DATABASE = {
    'dbname': os.environ['POSTGRES_DB'],
    'user': os.environ['POSTGRES_USER'],
    'password': get_secret_pass(),
    'host': os.environ['POSTGRES_HOST'],
    'port': os.environ['POSTGRES_PORT']
    }

chat = Chat()

urls = (
    '/', 'Index',
    '/send', 'Send',
    '/health', 'Health'
)

render = web.template.render('/www/templates/')
path_querys = "/data"
path_database_console ="/database_console"



class Index:
    def GET(self):
        return render.index()

class Health:
    def GET(self):
        return "OK"

class Send:
    def POST(self):
        data = web.input()
        query = data.query
        return self.process_as_csv(query)


    def process_as_csv(self, query):

        print(f"User: {query}", flush=True )
        data = chat.send(query)
        """
        data={"sql": "","justification": "", "filename": ""}
        """

        # Save
        with open(f"{path_querys}/{data['filename']}.json", 'w') as file:
            json.dump(data, file, indent=4)

        # Save to datashare_console
        with open(f"{path_database_console}/{data['filename']}", 'w') as file:
            file.write("/*\n\n")
            file.write(f"{data['filename']}\n(Powered by Gemini & migasfree)\n\n")
            file.write(f"User: {query}\n\n")
            file.write(f"Gemini: {data['justification']}\n\n")
            file.write("*/\n\n")
            file.write(data['sql'])


        print(f"Gemini: {data['sql']}", flush=True)

        try:

            conn = psycopg2.connect(**DATABASE)
            cursor = conn.cursor()

            # Run the SQL query.
            cursor.execute(data["sql"])
            rows = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]

            # Use StringIO to generate the CSV in memory
            csv_output = io.StringIO()
            csvwriter = csv.writer(csv_output)
            csvwriter.writerow(colnames)
            csvwriter.writerows(rows)

            # Close the connection to the database.
            cursor.close()
            conn.close()

            # Get the content of the CSV from memory.
            csv_content = csv_output.getvalue()
            csv_output.close()

            # Set the headers for the HTTP response.
            web.header('Content-Type', 'text/csv')
            web.header('Content-Disposition', f'attachment; filename="{data["filename"]}.csv"')

            # Return the content of the CSV.
            return csv_content

        except psycopg2.Error as e:
            return f"Database error: {str(e)}"


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()