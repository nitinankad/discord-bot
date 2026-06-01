from __future__ import annotations

import json
import os

import boto3

from discord_bot.utils.constants import DEFAULT_BEDROCK_MODEL


def _get_bedrock_client():
    return boto3.client("bedrock-runtime")


def get_bedrock_response(question: str) -> str:
    model_id = os.environ.get(
        "BEDROCK_MODEL_ID", DEFAULT_BEDROCK_MODEL
    )
    client = _get_bedrock_client()

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": question}],
        }
    )

    response = client.invoke_model(modelId=model_id, body=body)
    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]
