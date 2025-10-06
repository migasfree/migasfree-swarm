import os
import re
import yaml
import json

from collections import defaultdict

from resources import download_url, read_file

from settings import FQDN, CORPUS_PATH_API, RESUME_FILE_API


def create_api_schema_old():
    file_openapi = f'{CORPUS_PATH_API}/migasfree.yaml'

    os.makedirs(CORPUS_PATH_API, exist_ok=True)

    if not os.path.exists(file_openapi):

        download_url(f"https://{FQDN}/api/schema", file_openapi)

        with open(file_openapi, 'r') as file:
            yaml_content = yaml.safe_load(file)

        # Prepare the resume data
        resume_data = []

        # Process each path in the YAML
        for path, path_data in yaml_content.get('paths', {}).items():
            for method, method_data in path_data.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    operation_id = method_data.get('operationId')
                    description = method_data.get('description', '')

                    # Add to resume data
                    element = {"filename": f'{operation_id}.yaml'}
                    if description:
                        element["description"] = description
                    resume_data.append(element)

                    # Create a file for each operationId with the path content
                    if operation_id:
                        with open(os.path.join(CORPUS_PATH_API, f'{operation_id}.yaml'), 'w') as op_file:
                            yaml.dump({path: {method: method_data}}, op_file, default_flow_style=False)

        # Write the resume.json file
        with open(RESUME_FILE_API, 'w') as resume_file:
            json.dump(resume_data, resume_file)


def get_api_schema_old(filename):
    return read_file(f"{CORPUS_PATH_API}/{filename}")


def extract_used_schemas(data):
    """Recursivamente extrae todos los nombres de esquemas referenciados en una estructura de datos"""
    schemas = set()

    if isinstance(data, dict):
        for key, value in data.items():
            if key == '$ref':
                # Extraer el nombre del esquema de la referencia
                match = re.search(r'#/components/schemas/(\w+)', value)
                if match:
                    schemas.add(match.group(1))
            else:
                schemas |= extract_used_schemas(value)
    elif isinstance(data, list):
        for item in data:
            schemas |= extract_used_schemas(item)

    return schemas


def create_api_categories():
    file_openapi = f'{CORPUS_PATH_API}/migasfree.yaml'

    os.makedirs(CORPUS_PATH_API, exist_ok=True)

    if not os.path.exists(RESUME_FILE_API):

        resume = json.loads(read_file("resources/api/resume.json"))
        with open(RESUME_FILE_API, "w") as file:
            file.write(json.dumps(resume))

        download_url("http://core:8080/api/schema/", file_openapi)

        with open(file_openapi, 'r') as file:
            full_yaml = yaml.safe_load(file)

        # Extraer todos los paths y componentes
        paths = full_yaml.get('paths', {})
        components = full_yaml.get('components', {}).get('schemas', {})

        # Crear un diccionario para agrupar por categoría
        categories = defaultdict(lambda: {
            'openapi': full_yaml['openapi'],
            'info': full_yaml['info'],
            'paths': {},
            'components': {'schemas': {}}
        })

        # Crear un mapeo de esquemas usados por categoría
        category_schemas = defaultdict(set)

        # Recorrer todos los endpoints
        for path, methods in paths.items():
            for method, details in methods.items():
                # Obtener los tags del endpoint
                tags = details.get('tags', [])

                # Extraer esquemas usados en este endpoint
                endpoint_schemas = extract_used_schemas(details)

                # Procesar cada tag
                for tag in tags:
                    # Agregar el endpoint a la categoría
                    if path not in categories[tag]['paths']:
                        categories[tag]['paths'][path] = {}
                    categories[tag]['paths'][path][method] = details

                    # Registrar esquemas usados
                    category_schemas[tag] |= endpoint_schemas

        # Agregar esquemas necesarios a cada categoría
        for category, data in categories.items():
            # Obtener todos los esquemas necesarios para esta categoría
            required_schemas = category_schemas[category]

            # Agregar los esquemas y sus dependencias
            added_schemas = set()
            new_schemas = required_schemas.copy()

            while new_schemas:
                current_schema = new_schemas.pop()
                if current_schema in components and current_schema not in added_schemas:
                    # Agregar el esquema actual
                    data['components']['schemas'][current_schema] = components[current_schema]
                    added_schemas.add(current_schema)

                    # Buscar dependencias en este esquema
                    dependencies = extract_used_schemas(components[current_schema])
                    new_schemas |= dependencies - added_schemas

        # Guardar cada categoría en un archivo YAML separado
        for category, data in categories.items():
            # Sanitizar el nombre del archivo
            filename = f"{CORPUS_PATH_API}/{category.replace('/', '_')}.yaml"
            with open(filename, 'w') as f:
                yaml.dump(data, f, sort_keys=False, allow_unicode=True)


def get_api_category(filename):
    content = read_file(f"{CORPUS_PATH_API}/{filename}")

    return yaml.safe_load(content)
