from discord.ext import commands


class OnReady(commands.Cog, name="on_ready"):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        print(f'{self.bot.user.name} has connected to Discord!')


def setup(bot):
    bot.add_cog(OnReady(bot))
