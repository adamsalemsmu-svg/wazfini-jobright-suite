import json
from ..core.config import settings
import openai

openai.api_key = settings.OPENAI_API_KEY

SYSTEM_PROMPT = (
    "You are Penguin, a precise AI assistant for job search in the UAE. "
    "Give clear, practical guidance based on the user's question, "
    "and avoid legal claims. Be concise."
)

async def penguin_reply(message: str, context: dict) -> str:
    try:
        r = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps({"message": message, **(context or {})})},
            ],
            temperature=0.3,
        )
        return r.choices[0].message["content"].strip()
    except Exception as e:
        return f"(Penguin) Error: {e}"
