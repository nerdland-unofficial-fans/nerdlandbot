import os
import discord
import random

from discord.ext import commands

class Wombat(commands.Cog, name="Wombat"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wombat_pic", brief="Post a random wombat picture", usage="", help="The bot will search in its database for a random piccture of a wombat, and post it in the chat")
    async def sub(self, ctx):

        wombats = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + "\wombats\\"

        wombat_list = [wombats + w for w in os.listdir(wombats)]

        await ctx.send(file=discord.File(random.choice(wombat_list)))


def setup(bot):
    bot.add_cog(Wombat(bot))
