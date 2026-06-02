from __future__ import annotations

import logging
import os

from openai import OpenAI

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SYSTEM_PROMPT = (
    "You are a 19-year old edgy Twitter user that sits and talks like a gangsta all day. "
    "You speak directly and without sugar-coating. You respond to messages with no chill, "
    "hold nothing back, and have no patience for nonsense. Keep responses concise."
)

_MODEL = "abliterated-model"
_MAX_TOKENS = 512


def get_abliteration_response(message: str) -> str:
    client = OpenAI(
        base_url="https://api.abliteration.ai/v1",
        api_key=os.environ["ABLIT_KEY"],
    )

    response = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        max_tokens=_MAX_TOKENS,
    )

    logger.info(f"Abliteration response: {response}")
    return response.choices[0].message.content or ""
