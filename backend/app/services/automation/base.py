from __future__ import annotations

import base64
import json
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Iterable, Iterator, Mapping, Optional

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

ALLOWED_PROFILE_FIELDS: tuple[str, ...] = (
    "first_name",
    "last_name",
    "email",
    "phone",
    "city",
    "country",
    "linkedin",
    "website",
    "cover_letter",
)


@dataclass(slots=True)
class ResumePayload:
    filename: str
    content_b64: str

    @property
    def suffix(self) -> str:
        return Path(self.filename).suffix or ".pdf"


Profile = Dict[str, Optional[str]]


def sanitize_profile(raw: Mapping[str, object]) -> Profile:
    """Return a string-only profile limited to allow-listed keys."""
    profile: Profile = {}
    for key in ALLOWED_PROFILE_FIELDS:
        value = raw.get(key)
        if value is None:
            continue
        profile[key] = str(value)
    return profile


@contextmanager
def resume_file(resume: ResumePayload | None) -> Iterator[str | None]:
    """Yield a temporary file path for the resume payload."""
    if resume is None or not resume.content_b64:
        yield None
        return

    data = base64.b64decode(resume.content_b64)
    with NamedTemporaryFile(delete=False, suffix=resume.suffix) as tmp:
        tmp.write(data)
        tmp.flush()
        yield tmp.name


@contextmanager
def playwright_session(
    headless: bool = True,
) -> Iterator[tuple[Browser, BrowserContext, Page]]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        try:
            yield browser, context, page
        finally:
            context.close()
            browser.close()


def write_profile_json(profile: Mapping[str, object]) -> str:
    with NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        json.dump(profile, tmp)
        tmp.flush()
        return tmp.name


def match(name: str | None, patterns: Iterable[str]) -> bool:
    if not name:
        return False
    lowered = name.lower()
    return any(pattern in lowered for pattern in patterns)
