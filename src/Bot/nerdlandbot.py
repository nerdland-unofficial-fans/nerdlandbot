from discord.ext.commands import Bot
from EventHandlers import onready, oncommanderror, onmemberjoin
from Commands import rolldice


class NerdlandBot(Bot):
    def __init__(self, prefix):
        self.prefix = prefix

        super().__init__(command_prefix=self.prefix)

        self.command(name='roll_dice')(self.roll_dice)

    async def on_ready(self):
        await onready.on_ready(self)

    async def on_command_error(self, context, exception):
        await oncommanderror.on_command_error(self, context, exception)

    async def on_member_join(self,member):
        await onmemberjoin.on_member_join(self,member)

    async def roll_dice(self, ctx, number_of_dice: int, number_of_sides: int):
        await rolldice.roll(ctx, number_of_dice, number_of_sides)
