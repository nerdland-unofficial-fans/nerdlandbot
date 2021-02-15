import discord
import aiohttp
import asyncio

from discord.ext import commands


class DadJoke(commands.Cog, name="dad_joke"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="dad_joke", help="dad_joke_help")
    async def cmd_dad_joke(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://icanhazdadjoke.com',headers = { "Accept": "text/plain" }) as resp:
                msg = await resp.text(encoding='utf-8')

                # msg can contain utf 2028 charactercode which is line-separator, we're just converting it to '\n'
                msg = '\n'.join(msg.splitlines())
                await ctx.send(msg)

def setup(bot: commands.Bot):
    bot.add_cog(DadJoke(bot))
    