from __future__ import annotations

import boto3
import json
import os
import random

from discord_bot.commands.command_handler import CommandHandler


class T2iCommand(CommandHandler):
    def handle(self, interaction: dict) -> str:
        options = interaction.get("data", {}).get("options") or []
        prompt = next((o.get("value", "") for o in options if o.get("name") == "prompt"), "")

        if not prompt:
            return "Please provide a prompt."

        boto3.client("lambda").invoke(
            FunctionName=os.environ["LAMBDA_FUNCTION_ARN"],
            InvocationType="Event",
            Payload=json.dumps({
                "task": "t2i_followup",
                "prompt": prompt,
                "application_id": interaction.get("application_id"),
                "token": interaction.get("token"),
            }),
        )

        thinking = random.choice([
            "Painting...",
            "Conjuring pixels...",
            "Dreaming up an image...",
            "Summoning the muse...",
            "Rendering...",
            "Mixing colors...",
            "Sketching...",
            "Brushing strokes...",
            "Firing up the canvas...",
            "Imagining...",
        ])
        return f"{thinking} 🎨 (This may take a minute)"
