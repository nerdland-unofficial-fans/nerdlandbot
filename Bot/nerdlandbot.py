from discord.ext.commands import Bot

class NerdlandBot(Bot):
    def __init__(self, prefix):
        self.prefix = prefix

        super().__init__(command_prefix=self.prefix)
