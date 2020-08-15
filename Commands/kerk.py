import typing
import asyncio
import discord
from discord.ext import commands
from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture
from Helpers.parser import parse_channel

from datetime import datetime

class Kerk(commands.Cog, name="kerk"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="16ukerk", hidden=True)
    async def cmd_kerk16(self, ctx: commands.Context, mention:typing.Optional[str] = None, *, message:typing.Optional[str] = None):
        #check if message in lounge
        if ctx.channel.name == ("testbot"):
            #check if user mentioned  
            if mention:
                #set a task to check if it's 16:00 and posts message
                #while not (datetime.now().hour == 16 and datetime.now().minute == 00):
                #    await asyncio.sleep(59)
                msg = "⛪ Hey {0} het is 4u en <@{1}> wil met u vechten aan de kerk in Hamont! 👊".format(mention,ctx.author.id)
                if message:
                    msg += "\n\t\"{0}\"".format(message)
                return await ctx.send(msg)

def setup(bot: commands.Bot):
    bot.add_cog(Kerk(bot))