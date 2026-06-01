from __future__ import annotations

from typing import Protocol


class CommandHandler(Protocol):
    """Interface for Discord slash command handlers.

    Every command must implement `handle` which receives the parsed
    interaction payload and returns a string to send as the bot's reply.
    """

    def handle(self, interaction: dict) -> str:
        """Handle a slash command interaction.

        Parameters
        ----------
        interaction : dict
            The parsed interaction payload from Discord, e.g.:
            {
                "data": {"name": "hello", "options": [...]},
                ...
            }

        Returns
        -------
        str
            The response content to send back to the user.
        """
        ...
