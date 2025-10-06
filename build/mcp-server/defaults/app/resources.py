import requests


def read_file(name):
    try:
        with open(name, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f'ERROR reading {name}: {str(e)}'


def download_url(url, archive):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    with open(archive, 'wb') as f:
        f.write(response.content)
