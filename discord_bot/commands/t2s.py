from __future__ import annotations

import boto3
import json
import os
import random

from discord_bot.commands.command_handler import CommandHandler


class T2sCommand(CommandHandler):
    def handle(self, interaction: dict) -> str:
        options = interaction.get("data", {}).get("options") or []
        opts = {o["name"]: o.get("value", "") for o in options}

        text = opts.get("text", "")
        if not text:
            return "Please provide text to speak."

        boto3.client("lambda").invoke(
            FunctionName=os.environ["LAMBDA_FUNCTION_ARN"],
            InvocationType="Event",
            Payload=json.dumps({
                "task": "t2s_followup",
                "text": text,
                "speaker": opts.get("speaker", "Ryan"),
                "language": opts.get("language", "English"),
                "instruct": opts.get("instruct", ""),
                "application_id": interaction.get("application_id"),
                "token": interaction.get("token"),
            }),
        )

        thinking = random.choice([
            "Speaking...",
            "Finding my voice...",
            "Warming up the mic...",
            "Synthesizing speech...",
            "Reading aloud...",
            "Lending a voice...",
        ])
        return f"{thinking} 🎙️ (This may take a moment)"
