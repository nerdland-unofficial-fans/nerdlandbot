import os
import discord
import random

from discord.ext import commands
from nerdlandbot.helpers.constants import WOMBATS_DIR_NAME
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.translations.Translations import get_text as translate

if not os.path.exists(WOMBATS_DIR_NAME):
    os.makedirs(WOMBATS_DIR_NAME)

class Wombat(commands.Cog, name="Wombat"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wombat_pic", brief="Post a random wombat picture", help="The bot will search for a random picture of a wombat in its database, and post it in the chat")
    async def cmd_wombat_pic(self, ctx):
        wombat_list = [os.path.join(WOMBATS_DIR_NAME, w) for w in os.listdir(WOMBATS_DIR_NAME)]

        if not wombat_list:
            msg = translate("empty_wombat_list", await culture(ctx))
            return await ctx.send(msg)

        await ctx.send(file=discord.File(random.choice(wombat_list)))


def setup(bot):
    bot.add_cog(Wombat(bot))
