from typing import TYPE_CHECKING

from discord_bot.commands.command_handler import CommandHandler
from discord_bot.commands.ping import PingCommand
from discord_bot.commands.ask import AskCommand
from discord_bot.commands.chat import ChatCommand
from discord_bot.commands.t2i import T2iCommand
from discord_bot.commands.t2v import T2vCommand
from discord_bot.commands.i2v import I2vCommand
from discord_bot.commands.i2i import I2iCommand
from discord_bot.commands.t2s import T2sCommand


COMMAND_REGISTRY: dict[str, CommandHandler] = {
    "ping": PingCommand(),
    "ask": AskCommand(),
    "chat": ChatCommand(),
    "t2i": T2iCommand(),
    "t2v": T2vCommand(),
    "i2v": I2vCommand(),
    "i2i": I2iCommand(),
    "t2s": T2sCommand(),
}

def resolve_command(name: str) -> CommandHandler | None:
    return COMMAND_REGISTRY.get(name)
