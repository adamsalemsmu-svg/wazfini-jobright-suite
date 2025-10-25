import re


def parse_resume_text(text: str):
    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"\+?\d[\d\s\-]{7,}\d", text)
    linkedin = re.search(r"https?://(?:www\.)?linkedin\.com/\S+", text)
    github = re.search(r"https?://(?:www\.)?github\.com/\S+", text)
    skills = sorted(
        set(
            re.findall(
                r"\b(Python|SQL|Snowflake|Power BI|Tableau|Azure|Databricks|ETL|ELT|Spark)\b",
                text,
                re.I,
            )
        )
    )
    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
        "skills": skills,
    }
