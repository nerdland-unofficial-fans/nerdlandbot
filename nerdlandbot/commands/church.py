import typing
import asyncio
from datetime import datetime, timedelta
import discord
from discord.ext import commands

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.channel import get_channel
from nerdlandbot.commands.GuildData import get_all_guilds_data, get_guild_data, GuildData



class Kerk(commands.Cog, name="Church"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="16uchurch", hidden=True)
    async def cmd_kerk16(self, ctx: commands.Context, mention:typing.Optional[str] = None, *, message:typing.Optional[str] = None):
        guild_data = await get_guild_data(ctx.message.guild.id)  
        lang = await culture(ctx)
        temp_date = datetime.now()
        # If it's past 16:00 it will be scheduled for the next day
        if temp_date.hour >= 23:
            church_day = (temp_date + timedelta(days=1)).day
        else:
            church_day = temp_date.day
        
        # Adding a church_event to the guild data.
        await guild_data.set_church_event(ctx.author.id, mention, church_day, lang, message)
        msg = translate("church_event_success", lang)
        
        return await ctx.send(msg)
        
    

    @commands.command(name="church_channel", hidden=True)
    async def cmd_set_kerk(self, ctx: commands.Context, *, channel_id:typing.Optional[str] = None):
        guild_data = await get_guild_data(ctx.message.guild.id)

        lang = await culture(ctx)

        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", lang)
            return await ctx.send(gif)

        # Give error if the channel is a voice channel
        channel = get_channel(ctx,channel_id)
        if isinstance(channel, discord.VoiceChannel):
            return await ctx.send(translate("channel_is_voice", lang))

        if not channel:
            return await ctx.send(translate("membercount_channel_nonexistant", lang))

        if(await guild_data.update_church_channel(channel_id)):
            msg = translate("church_channel_success", lang).format(channel)
        else:
            msg = translate("church_channel_error", lang)

        return await ctx.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(Kerk(bot))
