from discord.ext.commands import Bot
from EventHandlers import onready, oncommanderror, onmemberjoin
from Commands import notify


class NerdlandBot(Bot):
    def __init__(self, prefix):
        self.prefix = prefix

        super().__init__(command_prefix=self.prefix)

        self.command(name='sub')(self.subscribe)
        self.command(name='unsub')(self.unsubscribe)
        # self.command(name='notify')(self.notify)
        self.command(name='show_lists')(self.show_lists)
        self.command(name='save_config')(self.save_config)

    # EVENTS
    async def on_ready(self):
        await onready.on_ready(self)

    async def on_command_error(self, context, exception):
        await oncommanderror.on_command_error(self, context, exception)

    async def on_member_join(self,member):
        await onmemberjoin.on_member_join(self,member)

    # NOTIFICATIONS
    async def subscribe(self, ctx, list_name:str):
        await notify.subscribe(ctx, list_name.lower())

    async def unsubscribe(self, ctx, list_name:str):
        await notify.unsubscribe(ctx, list_name.lower())

    async def notify(self, ctx, list_name:str):
        await notify.notify(ctx, list_name.lower())

    async def show_lists(self, ctx):
        await notify.show_lists(ctx)

    async def save_config(self, ctx):
        #TODO: We should probably add some way to only allow the person that hosts the bot to run this command
        await notify.save_config(ctx)