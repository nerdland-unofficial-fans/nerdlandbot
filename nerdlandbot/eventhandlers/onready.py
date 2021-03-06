from discord.ext import commands
import discord 

from nerdlandbot.helpers.log import info
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.translations.Translations import get_text as translate

class OnReady(commands.Cog, name="on_ready"):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        """
        This gets executed when the bot connects to discord.
        """
        info(f'{self.bot.user.name} has connected to Discord!')

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, 
                name=f"{self.bot.command_prefix}poncho")
            )

def setup(bot: commands.Bot):
    bot.add_cog(OnReady(bot))
