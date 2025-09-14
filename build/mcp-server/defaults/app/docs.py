import json
import os

from resources import read_file, download_url



url_chapter = "https://raw.githubusercontent.com/migasfree/fun-with-migasfree/refs/heads/master/{}"

from settings import CORPUS_PATH_DOCS, RESUME_FILE_DOCS


def create_docs():
    if not os.path.exists(CORPUS_PATH_DOCS):
        os.makedirs(CORPUS_PATH_DOCS, exist_ok=True)
        CHAPTERS =  json.loads(read_file("resources/docs/resume.json"))
        for chapter in CHAPTERS:
            filename = chapter['filename']
            download_url(url_chapter.format(filename), f"{CORPUS_PATH_DOCS}/{filename}")

        with open(RESUME_FILE_DOCS,"w") as file:
            file.write(json.dumps(CHAPTERS))


def get_chapter_content(filename):
    return read_file(f"{CORPUS_PATH_DOCS}/{filename}")


def read_docs():
    create_docs()
    content = ""
    with open("resources/docs/resume.json", "r") as f:
        CHAPTERS = json.load(f)
    for chapter in CHAPTERS:
        filename = chapter['filename']
        with open(f"{CORPUS_PATH_DOCS}/{filename}", "r") as file:
            content += file.read()
    return content

CONTENT_MANUAL = read_docs().replace('\n', '').replace('\r', '')