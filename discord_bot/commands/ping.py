from __future__ import annotations

from discord_bot.commands.command_handler import CommandHandler

class PingCommand(CommandHandler):
    def handle(self, interaction: dict) -> str:
        return "Pong!"
