"""
Usage:
  python crawler/crawl.py https://boards.greenhouse.io/<company> https://jobs.lever.co/<company>
This script fetches job links and JDs from provided Greenhouse/Lever boards and POSTs them to the backend /jobs/ingest.
"""

# --- stdlib
import asyncio
import os
import sys

# --- third-party
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# load .env if present (optional, but avoids F401 since it's used)
load_dotenv()

API = os.getenv("WAZFINI_API", "http://127.0.0.1:8000")


async def fetch(url, client):
    r = await client.get(
        url,
        timeout=30,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    r.raise_for_status()
    return r.text


async def parse_greenhouse(board_url, client):
    html = await fetch(board_url, client)
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select("a[href*='/jobs/']"):
        href = a.get("href")
        if href and "/jobs/" in href:
            if href.startswith("http"):
                links.append(href)
            else:
                links.append(board_url.rstrip("/") + "/" + href.lstrip("/"))
    return list(dict.fromkeys(links))


async def parse_lever(board_url, client):
    html = await fetch(board_url, client)
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select("a[href*='jobs/']"):
        href = a.get("href")
        if href and "jobs/" in href:
            if href.startswith("http"):
                links.append(href)
            else:
                links.append(board_url.rstrip("/") + "/" + href.lstrip("/"))
    return list(dict.fromkeys(links))


async def fetch_jd(url, client):
    html = await fetch(url, client)
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("h1") or soup.select_one("h2")
    title = title.get_text(strip=True) if title else "Job"
    container = soup.select_one("#content") or soup.select_one("#job") or soup.select_one("section") or soup
    jd_text = container.get_text("\n", strip=True)[:200000]
    return title, jd_text


async def main(urls):
    async with httpx.AsyncClient() as client:
        for board in urls:
            try:
                if "greenhouse.io" in board:
                    job_links = await parse_greenhouse(board, client)
                    source = "greenhouse"
                elif "lever.co" in board:
                    job_links = await parse_lever(board, client)
                    source = "lever"
                else:
                    print(f"Unknown source for board: {board}")
                    continue

                print(f"[{source}] Found {len(job_links)} jobs on {board}")

                for link in job_links[:100]:
                    try:
                        title, jd_text = await fetch_jd(link, client)
                        payload = {
                            "source": source,
                            "title": title,
                            "company": "",
                            "location": "",
                            "remote": False,
                            "canonical_url": link,
                            "raw_jd": jd_text,
                        }
                        r = await client.post(f"{API}/jobs/ingest", json=payload)
                        print(link, r.status_code, r.text[:80])
                    except Exception as e:
                        print("job error:", e)
            except Exception as e:
                print("board error:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crawler/crawl.py <board1> <board2> ...")
        sys.exit(1)
    asyncio.run(main(sys.argv[1:]))
