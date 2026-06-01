from typing import TYPE_CHECKING

from discord_bot.commands.command_handler import CommandHandler
from discord_bot.commands.ping import PingCommand
from discord_bot.commands.ask import AskCommand


COMMAND_REGISTRY: dict[str, CommandHandler] = {
    "ping": PingCommand(),
    "ask": AskCommand(),
}

def resolve_command(name: str) -> CommandHandler | None:
    return COMMAND_REGISTRY.get(name)
