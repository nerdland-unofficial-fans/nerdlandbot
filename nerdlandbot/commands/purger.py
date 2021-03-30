import discord
import os
import requests

from discord.ext import commands, tasks
from nerdlandbot.commands.GuildData import get_all_guilds_data, get_guild_data, GuildData
from nerdlandbot.helpers.log import info, fatal
from nerdlandbot.helpers.channel import get_channel
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.translations.Translations import get_text as translate


class purger(commands.Cog, name="Purger_lists"):
    @commands.command(
        name="add_purger", usage="add_purger_usage", help="add_purger_help",
    )
    @commands.guild_only()
    async def add_purger(self, ctx: commands.Context, text_channel: str, max_age: int):
        """
        Add a channel to be regularly purged.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param text_channel: The text channel that will be purged (str)
        :param max_age: The max age of messages in days (int)
        """
        guild_data = await get_guild_data(ctx.message.guild.id)
        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        text_channel = text_channel.lower()

        # Get channel 
        channel = get_channel(ctx,text_channel)

        # TODO: Give information to the user when the text channel does not exist
        if not channel:
            await ctx.channel.send(translate("membercount_channel_nonexistant", await culture(ctx)))
            raise Exception("Invalid text channel provided")
        
        #Give error if the channel is a voice channel
        if isinstance(channel, discord.VoiceChannel):
            await ctx.channel.send(translate("channel_is_voice", await culture(ctx)))
            return

        # member = ctx.get_member(ctx.user.id)
        channel_permissions = channel.permissions_for(ctx.me)
        if not (channel_permissions.manage_messages and channel_permissions.read_message_history):
            return await ctx.send(translate("purger_permissions", await culture(ctx)))

        add_response = await guild_data.add_purger(channel, max_age)

        msg = ""
        if add_response:
            msg = translate("purger_added", await culture(ctx)).format(str(channel.id), max_age)
        else:
            msg = translate("purger_exists", await culture(ctx)).format(str(channel.id))
        info(msg)
        await ctx.send(msg)

    @commands.command(
        name="remove_purger", usage="remove_purger_usage", help="remove_purger_help",
    )
    @commands.guild_only()
    async def remove_purger(self, ctx: commands.Context, text_channel: str):
        """
        Remove a purger channel that was being notified
        :param ctx: The current context. (discord.ext.commands.Context)
        :param text_channel: The channel where the purger is attached to (str)
        """

        guild_data = await get_guild_data(ctx.message.guild.id)
        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        # Get channel 
        channel = get_channel(ctx,text_channel)

        # TODO: Give information to the user when the text channel does not exist
        if not channel:
            await ctx.channel.send(translate("membercount_channel_nonexistant", await culture(ctx)))
            raise Exception("Invalid text channel provided")
        
        #Give error if the channel is a voice channel
        if isinstance(channel, discord.VoiceChannel):
            await ctx.channel.send(translate("channel_is_voice", await culture(ctx)))
            return

        remove_response = await guild_data.remove_purger(channel)
        msg = ""
        if remove_response:
            msg = translate("purger_removed", await culture(ctx)).format(str(channel.id))
        else:
            msg = translate("purger_no_exists", await culture(ctx)).format(str(channel.id))
        info(msg)
        await ctx.send(msg)

    @commands.command(
        name="list_purger", help="list_purger_help",
    )
    @commands.guild_only()
    async def list_purger_channels(self, ctx: commands.Context):
        """
        List all purger channels that are being monitored
        """

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg = translate("purger_list_title", await culture(ctx))

        for text_channel, max_age in guild_data.purgers.items():
            msg = (
                msg
                + "\n"
                + translate("purger_list_item", await culture(ctx)).format(
                    text_channel, max_age
                )
            )
        await ctx.send(msg)


def setup(bot: commands.bot):
    bot.add_cog(purger(bot))
