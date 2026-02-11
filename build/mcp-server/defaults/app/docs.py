import os
import logging
from resources import read_file
from settings import CORPUS_PATH_DOCS

logger = logging.getLogger("migasfree-mcp")

# Supported file extensions
_TEXT_EXTENSIONS = (".md", ".rst", ".txt")
_PDF_EXTENSION = ".pdf"
_ALL_EXTENSIONS = _TEXT_EXTENSIONS + (_PDF_EXTENSION,)

# Cache for manual content
_manual_cache = None
_manual_mtime = 0


def _read_pdf(path: str) -> str:
    """Extract text content from a PDF file."""
    try:
        import fitz  # pymupdf

        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except ImportError:
        logger.warning("pymupdf not installed, cannot read PDF files")
        return f"[PDF file: {os.path.basename(path)} - pymupdf not installed]"
    except Exception as e:
        logger.error(f"Error reading PDF {path}: {e}")
        return f"[Error reading PDF: {os.path.basename(path)}: {str(e)}]"


def get_manual_content():
    """Returns the concatenated content of all documents in the docs directory.

    Supports .md, .rst, .txt and .pdf files.
    Results are cached and invalidated when any file in the directory changes.
    """
    global _manual_cache, _manual_mtime

    if not os.path.exists(CORPUS_PATH_DOCS):
        return "No documentation found."

    # Check if cache is still valid by comparing latest mtime
    current_mtime = _get_latest_mtime()
    if _manual_cache is not None and current_mtime <= _manual_mtime:
        return _manual_cache

    logger.info("Rebuilding documentation cache...")
    content = ""
    files = sorted(os.listdir(CORPUS_PATH_DOCS))

    for filename in files:
        path = os.path.join(CORPUS_PATH_DOCS, filename)
        if not os.path.isfile(path):
            continue

        if filename.endswith(_TEXT_EXTENSIONS):
            content += f"\n\n# FILE: {filename}\n\n"
            content += read_file(path)
        elif filename.endswith(_PDF_EXTENSION):
            content += f"\n\n# FILE: {filename}\n\n"
            content += _read_pdf(path)

    _manual_cache = (
        content if content else "No documentation files found in the directory."
    )
    _manual_mtime = current_mtime

    return _manual_cache


def _get_latest_mtime():
    """Get the latest modification time of any file in the docs directory."""
    latest = 0
    try:
        for filename in os.listdir(CORPUS_PATH_DOCS):
            path = os.path.join(CORPUS_PATH_DOCS, filename)
            if os.path.isfile(path):
                mtime = os.path.getmtime(path)
                if mtime > latest:
                    latest = mtime
    except OSError:
        pass
    return latest
