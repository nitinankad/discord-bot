from __future__ import annotations

import os

import boto3
import logging

from discord_bot.utils.constants import DEFAULT_BEDROCK_MODEL

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_bedrock_client():
    return boto3.client("bedrock-runtime")


def get_bedrock_response(question: str) -> str:
    model_id = os.environ.get(
        "BEDROCK_MODEL_ID", DEFAULT_BEDROCK_MODEL
    )
    client = _get_bedrock_client()

    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": question}]}],
    )
    logger.info(f"Bedrock response: {response}")
    return response["output"]["message"]["content"][0]["text"]
