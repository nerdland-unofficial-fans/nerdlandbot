import discord
import requests

from discord.ext import commands


class DadJoke(commands.Cog, name="dadJoke"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="dadJoke", help="dadjoke_help")
    async def cmd_dadJoke(self, ctx: commands.Context): 
        r = requests.get('https://icanhazdadjoke.com',headers = { "Accept": "text/plain" })
        r.encoding = 'utf-8' 
        msg = r.text
        await ctx.send(msg)

def setup(bot: commands.Bot):
    bot.add_cog(DadJoke(bot))