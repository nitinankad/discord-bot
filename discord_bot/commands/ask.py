from __future__ import annotations

import boto3
import json
import os
import random

from discord_bot.commands.command_handler import CommandHandler

class AskCommand(CommandHandler):
    def handle(self, interaction: dict) -> str:
        options = interaction.get("data", {}).get("options") or []
        question = next((o.get("value", "") for o in options if o.get("name") == "question"), "")

        if not question:
            return "Please provide a question."

        boto3.client("lambda").invoke(
            FunctionName=os.environ["LAMBDA_FUNCTION_ARN"],
            InvocationType="Event",
            Payload=json.dumps({
                "task": "ask_followup",
                "question": question,
                "application_id": interaction.get("application_id"),
                "token": interaction.get("token"),
            }),
        )

        thinking = random.choice([
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
        ])
        return f"{thinking} 🤔"
