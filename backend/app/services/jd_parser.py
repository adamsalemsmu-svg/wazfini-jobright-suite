import httpx
from bs4 import BeautifulSoup


async def fetch_and_parse_jd(url: str) -> str:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for sel in [
        "div#content",
        "div#job",
        "div.content",
        "div.body",
        "section",
        "article",
    ]:
        node = soup.select_one(sel)
        if node and len(node.get_text(strip=True)) > 200:
            return node.get_text("\n", strip=True)
    return soup.get_text("\n", strip=True)
