import os
import discord
import random

from discord.ext import commands
from Helpers.constants import WOMBATS_DIR_NAME

class Wombat(commands.Cog, name="Wombat"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wombat_pic", brief="Post a random wombat picture", help="The bot will search for a random picture of a wombat in its database, and post it in the chat")
    async def cmd_wombat_pic(self, ctx):

        parent_dir = os.path.join(os.path.dirname(__file__), os.pardir)
        wombats_dir = os.path.join(parent_dir, WOMBATS_DIR_NAME)

        wombat_list = [os.path.join(wombats_dir, w) for w in os.listdir(wombats_dir)]

        await ctx.send(file=discord.File(random.choice(wombat_list)))


def setup(bot):
    bot.add_cog(Wombat(bot))
