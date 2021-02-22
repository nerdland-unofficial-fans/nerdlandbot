import discord
import aiohttp
import asyncio

from discord.ext import commands


class EightBall(commands.Cog, name="eight_ball"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="eight_ball", aliases=["eightball"], help="eight_ball_help")
    async def cmd_eight_ball(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://evening-castle-06130.herokuapp.com/eightball') as resp:
                msg = await resp.text(encoding='utf-8')
                msg = msg[1:-2]
                await ctx.send(msg)

def setup(bot: commands.Bot):
    bot.add_cog(EightBall(bot))
