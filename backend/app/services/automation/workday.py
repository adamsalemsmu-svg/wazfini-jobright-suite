from __future__ import annotations

from typing import Mapping, Optional

from playwright.sync_api import Locator, Page

from .base import match, playwright_session, sanitize_profile

WORKDAY_PATTERNS = {
    "first_name": ["legalfirstname", "preferredfirstname", "candidatefirstname"],
    "last_name": ["legallastname", "preferredlastname", "candidatelastname"],
    "email": ["email", "emailaddress"],
    "phone": ["phonenumber", "mobile"],
    "city": ["city"],
    "country": ["country"],
    "linkedin": ["linkedin"],
    "website": ["website", "portfolio"],
}


def _descriptor(el: Locator) -> str:
    attributes = (
        el.get_attribute("data-automation-id"),
        el.get_attribute("aria-label"),
        el.get_attribute("name"),
        el.get_attribute("id"),
        el.get_attribute("placeholder"),
    )
    return " ".join(filter(None, attributes)).lower()


def _fill_inputs(page: Page, profile: Mapping[str, Optional[str]]) -> None:
    inputs = page.locator("input")
    for idx in range(inputs.count()):
        el = inputs.nth(idx)
        desc = _descriptor(el)
        value: Optional[str] = None
        for field, patterns in WORKDAY_PATTERNS.items():
            if match(desc, patterns):
                value = profile.get(field)
                break
        if value:
            el.fill(str(value))

    textareas = page.locator("textarea")
    for idx in range(textareas.count()):
        el = textareas.nth(idx)
        desc = _descriptor(el)
        if "cover" in desc:
            el.fill(profile.get("cover_letter") or "")


def _attach_files(page: Page, resume_path: Optional[str]) -> None:
    if not resume_path:
        return
    upload_triggers = page.locator('input[type="file"]')
    if upload_triggers.count():
        upload_triggers.first.set_input_files(resume_path)


def run(
    job_url: str,
    profile: Mapping[str, object],
    resume_path: Optional[str] = None,
    *,
    headless: bool = True,
) -> None:
    profile_data = sanitize_profile(profile)
    with playwright_session(headless=headless) as (_, _, page):
        page.goto(job_url, wait_until="domcontentloaded")
        try:
            page.get_by_role("button", name="Apply", exact=False).first.click()
        except Exception:
            try:
                page.locator("a[data-automation-id='applyButton']").first.click()
            except Exception:
                pass
        page.wait_for_load_state("networkidle")
        _fill_inputs(page, profile_data)
        _attach_files(page, resume_path)
