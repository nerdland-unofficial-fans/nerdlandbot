import typing
import asyncio
import discord
from discord.ext import commands
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture


from datetime import datetime

class Kerk(commands.Cog, name="kerk"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="16ukerk", hidden=True)
    async def cmd_kerk16(self, ctx: commands.Context, mention:typing.Optional[str] = None, *, message:typing.Optional[str] = None):
        #check if message in lounge
        if ctx.channel.name == ("lounge"):
            #check if user mentioned  
            if mention and mention[:2] == "<@":
                #set a task to check if it's 16:00 and posts message
                while not (datetime.now().hour == 16 and datetime.now().minute == 00):
                    await asyncio.sleep(59)
                msg = "⛪ Hey {0} het is 4u en <@{1}> wil u zien aan de kerk! 👊".format(mention,ctx.author.id)
                if message:
                    msg += "\n\t\"{0}\"".format(message)
                return await ctx.send(msg)
    @commands.command(name="kerk_channel", hidden=True)
    async def cmd_set_kerk(self, ctx: commands.Context, *, channel_id:typing.Optional[str] = None):
        guild_data = await get_guild_data(ctx.message.guild.id)

        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        await guild_data.update_kerk_channel(channel_id)

def setup(bot: commands.Bot):
    bot.add_cog(Kerk(bot))