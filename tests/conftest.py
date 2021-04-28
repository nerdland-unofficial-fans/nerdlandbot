from __future__ import annotations

import importlib
import pytest

from collections import defaultdict
from collections.abc import Callable
from unittest.mock import patch, MagicMock, AsyncMock
from discord import Intents, Message, MessageType
from discord.ext import commands

import nerdlandbot as original


class NerdlandBot(commands.bot.BotBase):
    def __init__(self, prefix: str, intents: Intents) -> None:
        super().__init__(command_prefix="!", help_command=None, description="Nerdland testbot")
        self.user = MagicMock(id="0")

    def run(self, token: str) -> None:
        pass

    def event(self, func: Callable[[], None]) -> None:
        pass

    def dispatch(self, type: str, ctx: commands.Context, error=None) -> None:
        pass

    async def command(self, message: str) -> None:
        magic_author = MagicMock(bot=False)

        magic_state = MagicMock()
        magic_state.store_user = lambda a: magic_author

        magic_http = AsyncMock()
        magic_state.http = magic_http

        magic_guild = MagicMock(id="0")

        magic_channel = MagicMock(guild=magic_guild)

        fake_message = Message(state=magic_state, channel=magic_channel, data={
            "content": message,
            "id": "0",
            "attachments": [],
            "embeds": [],
            "edited_timestamp": None,
            "type": MessageType.default,
            "pinned": False,
            "mention_everyone": False,
            "tts": False,
            "author": {"bot": False},
        })
        ctx = await self.get_context(fake_message)
        ctx.guild_id = "0"
        await self.invoke(ctx)

        return ctx, magic_http


@pytest.fixture(autouse=True)
def nerdlandbot() -> NerdlandBot:
    with patch('nerdlandbot.__main__.NerdlandBot', new=NerdlandBot) as mock_nerdlandbot:
        yield original.__main__.main()
