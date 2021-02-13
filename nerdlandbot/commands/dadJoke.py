import typing
import asyncio
import discord
import requests

from discord.ext import commands
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture


class DadJoke(commands.Cog, name="dadJoke"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="dadJoke", help="dadjoke_help")
    async def cmd_dadJoke(self, ctx: commands.Context, mention:typing.Optional[str] = None, *, message:typing.Optional[str] = None): 
        r = requests.get('https://icanhazdadjoke.com',headers = { "Accept": "text/plain" })
        r.encoding = 'utf-8' 
        msg = r.text
        if message:
            msg += "\n\t\"{0}\"".format(message)
        return await ctx.send(msg)

def setup(bot: commands.Bot):
    bot.add_cog(DadJoke(bot))