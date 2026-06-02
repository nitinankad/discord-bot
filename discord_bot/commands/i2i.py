from __future__ import annotations

import boto3
import json
import os
import random

from discord_bot.commands.command_handler import CommandHandler


class I2iCommand(CommandHandler):
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
                "task": "i2i_followup",
                "image_url": attachment.get("url"),
                "prompt": prompt,
                "application_id": interaction.get("application_id"),
                "token": interaction.get("token"),
            }),
        )

        thinking = random.choice([
            "Transforming...",
            "Reimagining...",
            "Applying your vision...",
            "Remixing...",
            "Reshaping the image...",
            "Working the magic...",
            "Repainting...",
            "Morphing...",
            "Rethinking...",
            "Crafting your image...",
        ])
        return f"{thinking} 🖼️ (This may take a minute)"
