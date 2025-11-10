from __future__ import annotations

from typing import Mapping, Optional

from playwright.sync_api import Page

from .base import match, playwright_session, sanitize_profile

COMMON_FIELDS = {
    "first_name": ["first name", "first-name", "firstname", "given name"],
    "last_name": ["last name", "last-name", "lastname", "family name", "surname"],
    "email": ["email", "email address"],
    "phone": ["phone", "mobile"],
    "city": ["city"],
    "country": ["country"],
    "linkedin": ["linkedin", "linkedin url"],
    "website": ["website", "portfolio", "github"],
}


def _fill_inputs(page: Page, profile: Mapping[str, Optional[str]]) -> None:
    inputs = page.locator('input[type="text"], input[type="email"], input[type="tel"]')
    for idx in range(inputs.count()):
        el = inputs.nth(idx)
        name = " ".join(
            part
            for part in (
                el.get_attribute("name"),
                el.get_attribute("id"),
                el.get_attribute("aria-label"),
            )
            if part
        )

        value: Optional[str] = None
        if match(name, COMMON_FIELDS["first_name"]):
            value = profile.get("first_name")
        elif match(name, COMMON_FIELDS["last_name"]):
            value = profile.get("last_name")
        elif match(name, COMMON_FIELDS["email"]):
            value = profile.get("email")
        elif match(name, COMMON_FIELDS["phone"]):
            value = profile.get("phone")
        elif match(name, COMMON_FIELDS["city"]):
            value = profile.get("city")
        elif match(name, COMMON_FIELDS["country"]):
            value = profile.get("country")
        elif match(name, COMMON_FIELDS["linkedin"]):
            value = profile.get("linkedin")
        elif match(name, COMMON_FIELDS["website"]):
            value = profile.get("website")

        if value:
            el.fill(str(value))

    textareas = page.locator("textarea")
    for idx in range(textareas.count()):
        el = textareas.nth(idx)
        label = (el.get_attribute("aria-label") or "").lower()
        if "cover" in label:
            el.fill(profile.get("cover_letter") or "")


def _attach_files(page: Page, resume_path: Optional[str]) -> None:
    if not resume_path:
        return
    files = page.locator('input[type="file"]')
    if files.count():
        files.first.set_input_files(resume_path)


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
        for locator in ("Apply for this job", "Apply Now"):
            try:
                page.get_by_role("link", name=locator, exact=False).first.click()
                break
            except Exception:
                continue
        else:
            try:
                page.locator("a[href*='apply']").first.click()
            except Exception:
                pass
        page.wait_for_load_state("networkidle")
        _fill_inputs(page, profile_data)
        _attach_files(page, resume_path)
        # Leave submission for human confirmation.
