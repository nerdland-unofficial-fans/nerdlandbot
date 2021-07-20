from discord.ext.commands import Bot
from discord import Intents


class NerdlandBot(Bot):
    def __init__(self, prefix: str, intents: Intents):
        self.prefix = prefix
        super().__init__(command_prefix=self.prefix, intents=intents, case_insensitive=True,)

    async def process_commands(self, message):
        # # Intentionally don't ignore other bots' messages
        # if message.author.bot:
        #     return

        ctx = await self.get_context(message)
        await self.invoke(ctx)
