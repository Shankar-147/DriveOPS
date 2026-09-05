import os

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def call_llm(messages, tools):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set in the environment (.env).")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": os.getenv("OPENROUTER_MODEL"),
                "messages": messages,
                "tools": tools,
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
