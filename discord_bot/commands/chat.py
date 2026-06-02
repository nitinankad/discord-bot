from __future__ import annotations

import boto3
import json
import os
import random

from discord_bot.commands.command_handler import CommandHandler


_THINKING_VERBS = [
    "Dillydallying...",
    "Tinkering...",
    "Pondering...",
    "Ruminating...",
    "Cogitating...",
    "Noodling...",
    "Scheming...",
    "Consulting the void...",
    "Asking the oracle...",
    "Summoning wisdom...",
    "Connecting the dots...",
    "Doing math...",
    "Vibing...",
    "Manifesting an answer...",
    "Thinking really hard...",
]


class ChatCommand(CommandHandler):
    def handle(self, interaction: dict) -> str:
        options = interaction.get("data", {}).get("options") or []
        message = next((o.get("value", "") for o in options if o.get("name") == "message"), "")

        if not message:
            return "Please provide a message."

        boto3.client("lambda").invoke(
            FunctionName=os.environ["LAMBDA_FUNCTION_ARN"],
            InvocationType="Event",
            Payload=json.dumps({
                "task": "chat_followup",
                "message": message,
                "application_id": interaction.get("application_id"),
                "token": interaction.get("token"),
            }),
        )

        return f"{random.choice(_THINKING_VERBS)} 🤔"
