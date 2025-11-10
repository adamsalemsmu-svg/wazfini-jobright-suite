from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.services.automation.runner import AutomationPlatform, run_automation


def _load_profile(path: str) -> dict:
    return json.loads(Path(path).read_text())


def _load_resume(path: str | None) -> dict | None:
    if not path:
        return None
    payload = Path(path)
    return {
        "filename": payload.name,
        "content_b64": base64.b64encode(payload.read_bytes()).decode("utf-8"),
    }


def run(
    job_url: str, profile_json: str, resume: str | None = None, *, headless: bool = True
) -> None:
    profile = _load_profile(profile_json)
    resume_payload = _load_resume(resume)
    run_automation(
        platform=AutomationPlatform.greenhouse,
        job_url=job_url,
        profile=profile,
        resume=resume_payload,
        headless=headless,
    )
    print("Autofill completed. Review the form and submit manually.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Greenhouse job autofill helper")
    parser.add_argument("--job-url", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--headless", action="store_true", default=False)
    args = parser.parse_args()
    run(args.job_url, args.profile, args.resume, headless=args.headless)
