from __future__ import annotations

import boto3
import json
import os
import random

from discord_bot.commands.command_handler import CommandHandler


class I2vCommand(CommandHandler):
    def handle(self, interaction: dict) -> str:
        data = interaction.get("data", {})
        options = data.get("options") or []

        attachment_id = next((o.get("value") for o in options if o.get("name") == "image"), None)
        prompt = next((o.get("value", "") for o in options if o.get("name") == "prompt"), "")

        attachment = data.get("resolved", {}).get("attachments", {}).get(attachment_id, {})
        if not attachment.get("content_type", "").startswith("image/"):
            return "Please provide an image file."

        if not prompt:
            return "Please provide a prompt."

        boto3.client("lambda").invoke(
            FunctionName=os.environ["LAMBDA_FUNCTION_ARN"],
            InvocationType="Event",
            Payload=json.dumps({
                "task": "i2v_followup",
                "image_url": attachment.get("url"),
                "prompt": prompt,
                "application_id": interaction.get("application_id"),
                "token": interaction.get("token"),
            }),
        )

        thinking = random.choice([
            "Animating...",
            "Bringing it to life...",
            "Rolling cameras...",
            "Adding motion...",
            "Setting the scene in motion...",
            "Generating movement...",
            "Warping reality...",
            "Directing...",
            "Filming...",
            "Rendering frames...",
        ])
        return f"{thinking} 🎬 (This may take a few minutes)"
