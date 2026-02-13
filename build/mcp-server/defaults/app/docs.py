import os
import logging
from settings import CORPUS_PATH_DOCS

_TEXT_EXTENSIONS = (".md", ".rst", ".txt")
_PDF_EXTENSION = ".pdf"
_ALL_EXTENSIONS = _TEXT_EXTENSIONS + (_PDF_EXTENSION,)

logger = logging.getLogger("migasfree-mcp")


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


def convert_all_pdfs_to_markdown():
    """Convert all PDF files in the docs directory to Markdown."""
    if not os.path.exists(CORPUS_PATH_DOCS):
        return

    logger.info("Scanning for PDF files to convert...")
    for filename in os.listdir(CORPUS_PATH_DOCS):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(CORPUS_PATH_DOCS, filename)
            md_filename = os.path.splitext(filename)[0] + ".md"
            md_path = os.path.join(CORPUS_PATH_DOCS, md_filename)

            # Check if conversion is needed
            needs_conversion = False
            if not os.path.exists(md_path):
                needs_conversion = True
            else:
                # If PDF is newer than MD, reconvert
                if os.path.getmtime(pdf_path) > os.path.getmtime(md_path):
                    needs_conversion = True

            if needs_conversion:
                logger.info(f"Converting PDF to Markdown: {filename}")
                try:
                    text = _read_pdf(pdf_path)
                    # Add a header indicating it's an auto-conversion
                    content = f"# {filename} (Auto-converted)\n\n"
                    # Simple text cleanup/formatting could go here
                    content += text

                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    logger.info(f"Saved markdown to {md_filename}")

                    # Delete the PDF only if conversion was successful (no error message returned)
                    if not text.startswith("[PDF file:") and not text.startswith(
                        "[Error reading PDF:"
                    ):
                        try:
                            os.remove(pdf_path)
                            logger.info(f"Deleted original PDF: {filename}")
                        except OSError as e:
                            logger.warning(f"Could not delete PDF {filename}: {e}")
                except Exception as e:
                    logger.error(f"Failed to convert {filename}: {e}")
