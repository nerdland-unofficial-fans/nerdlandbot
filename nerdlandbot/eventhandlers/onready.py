from discord.ext import commands

from nerdlandbot.helpers.log import info


class OnReady(commands.Cog, name="on_ready"):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        """
        This gets executed when the bot connects to discord.
        """
        info(f'{self.bot.user.name} has connected to Discord!')


def setup(bot: commands.Bot):
    bot.add_cog(OnReady(bot))
