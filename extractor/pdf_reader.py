import fitz


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Opens a PDF file and returns all text as one string.
    """

    document = fitz.open(pdf_path)

    try:
        text = ""

        for page in document:
            text += page.get_text()

        return text

    finally:
        document.close()

        