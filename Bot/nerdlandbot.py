from discord.ext.commands import Bot
from discord import Intents


class NerdlandBot(Bot):
    def __init__(self, prefix: str, intents: Intents):
        self.prefix = prefix
        super().__init__(command_prefix=self.prefix, intents=intents, case_insensitive=True,)
