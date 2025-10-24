import json
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

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


def _match(name: str, patterns) -> bool:
    n = (name or "").lower()
    return any(p in n for p in patterns)


def fill_inputs(page, profile: dict) -> None:
    """Fill common input and textarea fields using profile data."""
    # ---- Inputs (text/email/tel) ---------------------------------------------
    inputs = page.locator('input[type="text"], input[type="email"], input[type="tel"]')

    for i in range(inputs.count()):
        el = inputs.nth(i)

        # Build a searchable "name" string from common attributes
        raw_parts = [
            el.get_attribute("name"),
            el.get_attribute("id"),
            el.get_attribute("aria-label"),
        ]
        name = " ".join(part for part in raw_parts if part)

        value = None

        # Person basics
        if _match(name, COMMON_FIELDS["first_name"]):
            value = profile.get("first_name")
        elif _match(name, COMMON_FIELDS["last_name"]):
            value = profile.get("last_name")
        elif _match(name, COMMON_FIELDS["email"]):
            value = profile.get("email")

        # Contact / location / social
        elif _match(name, COMMON_FIELDS["phone"]):
            value = profile.get("phone")
        elif _match(name, COMMON_FIELDS["city"]):
            value = profile.get("city")
        elif _match(name, COMMON_FIELDS["country"]):
            value = profile.get("country")
        elif _match(name, COMMON_FIELDS["linkedin"]):
            value = profile.get("linkedin")
        elif _match(name, COMMON_FIELDS["website"]):
            value = profile.get("website")

        if value:
            el.fill(str(value))

    # ---- Textareas ------------------------------------------------------------
    textareas = page.locator("textarea")

    for i in range(textareas.count()):
        el = textareas.nth(i)
        label = (el.get_attribute("aria-label") or "").lower()

        if "cover" in label:
            el.fill(profile.get("cover_letter", ""))


def attach_files(page, resume_path: str) -> None:
    files = page.locator('input[type="file"]')
    if files.count() and resume_path:
        files.first.set_input_files(resume_path)


def run(job_url: str, profile_json: str, resume: str | None = None, headless: bool = True) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        page.goto(job_url, wait_until="domcontentloaded")

        # Try common “apply” links
        try:
            page.get_by_role("link", name="Apply for this job").first.click()
        except Exception:
            try:
                page.locator("a[href*='apply']").first.click()
            except Exception:
                pass

        page.wait_for_load_state("networkidle")

        profile = json.loads(Path(profile_json).read_text())
        fill_inputs(page, profile)
        if resume:
            attach_files(page, resume)

        print("Autofill completed. Review the form and submit manually.")
        context.close()
        browser.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-url", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--resume", default=None)
    ap.add_argument("--headless", action="store_true", default=False)
    args = ap.parse_args()
    run(args.job_url, args.profile, args.resume, headless=args.headless)
