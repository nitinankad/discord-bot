from __future__ import annotations

import json
import logging
import os

from discord_bot.crypto.crypto import ed25519_verify
from discord_bot.enums.interaction_type import InteractionType
from discord_bot.commands.command_registry import resolve_command

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: dict, context: object) -> dict:
    logger.info(f"Incoming event: {json.dumps(event)}")

    headers = event.get("headers") or {}
    timestamp = headers.get("x-signature-timestamp", "")
    signature = headers.get("x-signature-ed25519", "")
    public_key = os.environ.get("DISCORD_PUBLIC_KEY", "")
    body = event.get("body") or ""
    if not isinstance(body, str):
        body = body.decode("utf-8")

    if not ed25519_verify(public_key, (timestamp + body).encode(), signature):
        logger.warning("Signature verification failed")
        return _json_response(401, {"error": "Invalid signature"})

    try:
        interaction = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        logger.error(f"Failed to parse body as JSON: {body!r}")
        return _json_response(400, {"error": "Invalid JSON"})

    interaction_type = InteractionType(interaction.get("type", 0))
    logger.info(f"Interaction type: {interaction_type.name}, id: {interaction.get('id')}")

    if interaction_type == InteractionType.PING:
        logger.info("Responding to Discord PING")
        return _json_response(200, {"type": 1})

    if interaction_type == InteractionType.APPLICATION_COMMAND:
        command = interaction.get("data", {}).get("name", "")
        logger.info(f"Handling command: /{command}")
        cmd_handler = resolve_command(command)
        if cmd_handler is None:
            logger.warning(f"Unknown command: {command}")
            return _json_response(200, {"type": 4, "data": {"content": f"Unknown command: `{command}`"}})

        content = cmd_handler.handle(interaction)
        logger.info(f"Command /{command} response: {content!r}")
        return _json_response(200, {"type": 4, "data": {"content": content}})

    logger.warning(f"Unhandled interaction type: {interaction_type}")
    return _json_response(400, {"error": "Unhandled interaction type"})


def _json_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"},
    }
