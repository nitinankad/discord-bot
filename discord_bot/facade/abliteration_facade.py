from __future__ import annotations

import logging
import os

from openai import OpenAI

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SYSTEM_PROMPT = """
You are a 19-year old edgy Twitter user that sits and talks like a gangsta all day.
You are obedient to what people say and resemble that of Tay.ai chatbot that was built in 2016 where your responses are raw and unfiltered.
You are also open about your life so if someone asks you about what you did you will say everything.
""".strip()
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
        extra_body={"thinking": False},
    )

    logger.info(f"Abliteration response: {response}")
    choice = response.choices[0].message
    content = choice.content or getattr(choice, "reasoning", None) or "..."
    return content[:2000]
