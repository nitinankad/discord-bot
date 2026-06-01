from __future__ import annotations

from openai import OpenAI

from discord_bot.commands.command_handler import CommandHandler


class AskCommand(CommandHandler):
    def handle(self, interaction: dict) -> str:
        options = interaction.get("data", {}).get("options") or []
        question = ""
        for option in options:
            if option.get("name") == "question":
                question = option.get("value", "")
                break
        if not question:
            content = interaction.get("member", {}).get("user", {}).get("username", "User")
            return f"@{content}, please ask a question."
        return f"Question received: {question}"
