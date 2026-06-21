from pathlib import Path
from pypdf import PdfReader

DATA_DIR = Path("data")

SUPPORTED_SUFFIXES = [".txt", ".md", ".pdf"]


def list_files():
    if not DATA_DIR.exists():
        return []

    return list(DATA_DIR.iterdir())


def filter_by_suffix(files, suffixes=None):
    suffixes = suffixes or SUPPORTED_SUFFIXES
    return [file for file in files if file.suffix in suffixes]


def read_pdf(file):
    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text


def read_document(file):
    if file.suffix == ".pdf":
        return read_pdf(file)

    elif file.suffix in [".txt", ".md"]:
        return file.read_text(encoding="utf-8")

    else:
        return None
