from discord.ext.commands import Bot
from EventHandlers import onready, oncommanderror, onmemberjoin


class NerdlandBot(Bot):
    def __init__(self, prefix):
        self.prefix = prefix

        super().__init__(command_prefix=self.prefix)
