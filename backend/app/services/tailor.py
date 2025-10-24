# stdlib
import hashlib
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple  # removed unused Any

# third-party
from dotenv import load_dotenv
from fastapi import HTTPException
from openai import OpenAI

# === Load .env and allow it to override any OS env vars ===
load_dotenv(override=True)
root_env = Path(__file__).resolve().parents[2] / ".env"
if root_env.exists():
    load_dotenv(root_env, override=True)

def _env(name: str, default: str = "") -> str:
    return (os.getenv(name, default) or "").strip()

MOCK_TAILORING = _env("MOCK_TAILORING", "0").lower() in ("1", "true", "yes", "on")
OPENAI_API_KEY = _env("OPENAI_API_KEY")
OPENAI_PROJECT = _env("OPENAI_PROJECT")

# Cache settings
CACHE_TTL_SECONDS = int(_env("TAILOR_CACHE_TTL_SECONDS", "86400"))   # 24h by default
CACHE_MAX_ITEMS   = int(_env("TAILOR_CACHE_MAX_ITEMS", "200"))

print("TAILOR: MOCK_TAILORING =", MOCK_TAILORING)
print("TAILOR: OPENAI_API_KEY set =", bool(OPENAI_API_KEY))
print("TAILOR: OPENAI_PROJECT =", OPENAI_PROJECT or "(none)")
print("TAILOR: CACHE_TTL_SECONDS =", CACHE_TTL_SECONDS, "CACHE_MAX_ITEMS =", CACHE_MAX_ITEMS)

SYSTEM_PROMPT = (
    "You are an expert resume tailor and ATS optimizer. "
    "Return concise, impact-focused bullet points that end with a period. "
    "Prioritize exact keywords and tools from the job description. Keep claims truthful."
)

# --------------------------------------------------------------------------------------
#                                  Simple in-process cache
# --------------------------------------------------------------------------------------
# key -> (stored_at_ts, (tailored_text, ats_hint, keywords))
_CACHE: Dict[str, Tuple[float, Tuple[str, str, List[str]]]] = {}

def _prune_cache() -> None:
    """Remove expired entries and shrink if above max size."""
    if not _CACHE:
        return
    now = time.time()
    # Expire old
    expired_keys = [k for k, (t, _) in _CACHE.items() if now - t > CACHE_TTL_SECONDS]
    for k in expired_keys:
        _CACHE.pop(k, None)
    # Shrink if too big (drop oldest)
    if len(_CACHE) > CACHE_MAX_ITEMS:
        # sort by timestamp (oldest first)
        items = sorted(_CACHE.items(), key=lambda kv: kv[1][0])
        for k, _ in items[: len(_CACHE) - CACHE_MAX_ITEMS]:
            _CACHE.pop(k, None)

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _cache_key(resume_text: str, job_text: str, language: str, style: str, model: str) -> str:
    return "|".join([
        _sha256(resume_text),
        _sha256(job_text),
        language.lower().strip(),
        style.lower().strip(),
        model.lower().strip(),
    ])

# --------------------------------------------------------------------------------------
#                                     Utilities
# --------------------------------------------------------------------------------------
def extract_keywords(job_text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9+\-#\.]{2,}", job_text)
    seen, out = set(), []
    signals = [
        "sql", "python", "snowflake", "azure", "aws", "gcp", "power", "tableau",
        "dbt", "spark", "bi", "etl", "api", "databricks", "fabric", "airflow", "kafka"
    ]
    for t in tokens:
        k = t.strip(",.;:()[]{}").strip()
        kl = k.lower()
        if kl in seen:
            continue
        if k.isupper() or any(s in kl for s in signals):
            out.append(k)
            seen.add(kl)
        if len(out) >= 40:
            break
    return out

def _mock_tailor(resume_text: str, job_text: str, kws: List[str]) -> str:
    bullets = [
        f"Aligned experience to JD focus areas ({', '.join(kws[:8])})",
        "Built and optimized ETL/ELT workflows; reduced manual effort by 40%.",
        "Developed dashboards for KPI visibility and stakeholder decision-making.",
        "Improved data quality to 99.9% via validations, tests, and monitoring.",
        "Automated recurring analytics using Python and SQL for faster SLAs.",
        "Collaborated with product/ops to prioritize and deliver data initiatives."
    ]
    return (
        "### Tailored Resume (Mock)\n\n"
        + "\n".join(f"- {b}" if b.endswith(".") else f"- {b}." for b in bullets)
        + "\n\n**Core Keywords Mapped:** "
        + ", ".join(kws[:15])
    )

def _openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    proj = os.getenv("OPENAI_PROJECT")
    if not key:
        raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY")
    return OpenAI(api_key=key, project=proj or None)

# Some suggested models you likely have access to
RECOMMENDED_MODELS = [
    "gpt-4-turbo",
    "gpt-4o-mini",
    "gpt-3.5-turbo",
]

def list_recommended_models() -> List[str]:
    """Return a static list of recommended models; you can call the API to enumerate too."""
    return RECOMMENDED_MODELS

# --------------------------------------------------------------------------------------
#                                       Tailor
# --------------------------------------------------------------------------------------
def tailor_resume_for_job(
    resume_text: str,
    job_text: str,
    language: str = "en",
    style: str = "concise-impact",
    model: str = "gpt-4-turbo",
    force_refresh: bool = False,
) -> Tuple[str, str, List[str]]:
    """
    Sync function using the new OpenAI client. Endpoint should run it via
    anyio.to_thread.run_sync(...) to avoid blocking.

    Returns: (tailored_text, ats_hint, keywords)
    """
    # Normalize / validate model
    model = (model or "gpt-4-turbo").strip()
    if model not in RECOMMENDED_MODELS:
        # If the requested model isn't in recommended list, still allow it
        # but keep a sane default if blank.
        if not model:
            model = "gpt-4-turbo"

    kws = extract_keywords(job_text)

    if MOCK_TAILORING:
        tailored = _mock_tailor(resume_text, job_text, kws)
        hint = "MOCK MODE: Mirror JD keywords, quantify impact, and end bullets with periods."
        return tailored, hint, kws

    # --- Cache ---
    _prune_cache()
    key = _cache_key(resume_text, job_text, language, style, model)
    if not force_refresh and key in _CACHE:
        ts, value = _CACHE[key]
        if time.time() - ts <= CACHE_TTL_SECONDS:
            return value

    client = _openai_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Language: {language}\nStyle: {style}\n\n"
            f"JOB DESCRIPTION:\n{job_text}\n\n"
            f"RESUME:\n{resume_text}\n\n"
            "Rewrite the resume content to align with the JD using truthful, measurable bullets "
            "(8–12 per role). Finish with a short 'ATS Optimization Tip' (<60 words)."
        )},
    ]

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )
    except Exception as e:
        print("OpenAI error:", e)
        raise HTTPException(status_code=500, detail=str(e))

    tailored_text = resp.choices[0].message.content
    ats_hint = (
        "Mirror JD keywords, quantify outcomes (%, time saved), and use exact tool names "
        "(SQL, Python, Snowflake). Lead with results and align titles/seniority to the role."
    )
    result = (tailored_text, ats_hint, kws)

    # Save in cache
    _CACHE[key] = (time.time(), result)
    _prune_cache()

    return result
