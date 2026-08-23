def clean_text(text: str) -> str:
    """
    Cleans raw text extracted from a PDF.

    - Removes leading and trailing whitespace
    - Removes empty lines
    - Removes extra spaces inside each line
    """

    cleaned_lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line = " ".join(line.split())

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)