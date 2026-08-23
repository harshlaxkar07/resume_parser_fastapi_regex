import re

SECTION_HEADINGS = {
    "skills",
    "technical skills",
    "education",
    "experience",
    "work experience",
    "professional experience",
    "projects",
    "certifications",
    "certificates",
    "languages",
    "professional summary",
    "summary",
    "profile",
    "objective",
    "professional profile",
    
}


def extract_email(text: str):
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    match = re.search(pattern, text)
    return match.group() if match else None


def extract_phone(text: str):
    pattern = r"\+?\d[\d\s()-]{8,}\d"
    match = re.search(pattern, text)
    return match.group().strip() if match else None


def extract_url(text: str, keyword: str):
    pattern = r"https?://\S+|www\.\S+"
    urls = re.findall(pattern, text)

    for url in urls:
        if keyword.lower() in url.lower():
            return url

    return None


def extract_name(lines):
    for line in lines[:10]:
        value = line.strip()

        if not value:
            continue

        lower = value.lower()

        if "@" in value:
            continue

        if "http" in lower:
            continue

        if "linkedin" in lower:
            continue

        if "github" in lower:
            continue

        if any(char.isdigit() for char in value):
            continue

        words = value.split()

        if 2 <= len(words) <= 4:
            return value

    return None


def extract_section(lines, section_name):
    data = []
    collecting = False

    for line in lines:
        value = line.strip()

        if not value:
            continue

        lower = value.lower()

        if collecting:
            if lower in SECTION_HEADINGS:
                break

            data.append(value)

        elif lower == section_name.lower():
            collecting = True

    return data if data else None


def extract_summary(lines):
    summary = extract_section(lines, "professional summary")
    if summary:
        return " ".join(summary)
    
    summary = extract_section(lines, "professional")
    if summary:
        return " ".join(summary)

    summary = extract_section(lines, "summary")
    if summary:
        return " ".join(summary)

    summary = extract_section(lines, "profile")
    if summary:
        return " ".join(summary)

    summary = extract_section(lines, "objective")
    if summary:
        return " ".join(summary)

    return None


def parse_resume(text: str):
    lines = text.splitlines()

    skills = extract_section(lines, "skills")
    if skills is None:
        skills = extract_section(lines, "technical skills")

    education = extract_section(lines, "education")

    experience = extract_section(lines, "experience")
    if experience is None:
        experience = extract_section(lines, "work experience")
    if experience is None:
        experience = extract_section(lines, "professional experience")

    projects = extract_section(lines, "projects")

    certifications = extract_section(lines, "certifications")
    if certifications is None:
        certifications = extract_section(lines, "certificates")

    languages = extract_section(lines, "languages")

    return {
        "full_name": extract_name(lines),
        "email": extract_email(text),
        "phone_number": extract_phone(text),
        "linkedin": extract_url(text, "linkedin"),
        "github": extract_url(text, "github"),
        "summary": extract_summary(lines),
        "skills": skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "languages": languages,
    }
