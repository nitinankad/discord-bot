from __future__ import annotations

from openai import OpenAI

from discord_bot.commands.command_handler import CommandHandler


class AskCommand(CommandHandler):
    def handle(self, interaction: dict) -> str:
        return "Ask me anything!"
