from __future__ import annotations

from typing import Mapping, Optional

from playwright.sync_api import Page

from .base import match, playwright_session, sanitize_profile

BAYT_FIELDS = {
    "first_name": ["first name", "firstname", "given name"],
    "last_name": ["last name", "lastname", "family name", "surname"],
    "email": ["email"],
    "phone": ["mobile", "phone"],
    "city": ["city"],
    "country": ["country"],
    "linkedin": ["linkedin"],
    "website": ["website", "portfolio", "github"],
}


def _fill_inputs(page: Page, profile: Mapping[str, Optional[str]]) -> None:
    inputs = page.locator("input, select")
    for idx in range(inputs.count()):
        el = inputs.nth(idx)
        attributes = (
            el.get_attribute("name"),
            el.get_attribute("id"),
            el.get_attribute("aria-label"),
            el.get_attribute("placeholder"),
            el.get_attribute("data-qa"),
        )
        descriptor = " ".join(filter(None, attributes))
        value: Optional[str] = None
        for field, patterns in BAYT_FIELDS.items():
            if match(descriptor, patterns):
                value = profile.get(field)
                break
        if value:
            try:
                el.fill(str(value))
            except Exception:
                try:
                    el.select_option(label=str(value))
                except Exception:
                    pass

    textareas = page.locator("textarea")
    for idx in range(textareas.count()):
        el = textareas.nth(idx)
        label = " ".join(
            filter(
                None,
                (
                    el.get_attribute("aria-label"),
                    el.get_attribute("name"),
                    el.get_attribute("placeholder"),
                ),
            )
        ).lower()
        if "cover" in label or "summary" in label:
            el.fill(profile.get("cover_letter") or "")


def _attach_files(page: Page, resume_path: Optional[str]) -> None:
    if not resume_path:
        return
    file_inputs = page.locator('input[type="file"]')
    if file_inputs.count():
        file_inputs.first.set_input_files(resume_path)


def run(job_url: str, profile: Mapping[str, object], resume_path: Optional[str] = None, *, headless: bool = True) -> None:
    profile_data = sanitize_profile(profile)
    with playwright_session(headless=headless) as (_, _, page):
        page.goto(job_url, wait_until="domcontentloaded")
        try:
            page.get_by_role("button", name="Apply", exact=False).first.click()
        except Exception:
            try:
                page.locator("button[data-qa='apply-btn']").first.click()
            except Exception:
                pass
        page.wait_for_load_state("networkidle")
        _fill_inputs(page, profile_data)
        _attach_files(page, resume_path)
