import discord
import os
import requests

from discord.ext import commands, tasks

from nerdlandbot.commands.GuildData import get_all_guilds_data, get_guild_data, GuildData
from nerdlandbot.helpers.channel import get_channel
from nerdlandbot.helpers.log import info, fatal
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.scheduler.YoutubeScheduler import get_latest_video
from nerdlandbot.translations.Translations import get_text as translate


class Youtube(commands.Cog, name="Youtube_lists"):
    @commands.command(
        name="add_youtube", usage="add_youtube_usage", help="add_youtube_help",
    )
    async def add_youtube_channel(
        self, ctx: commands.Context, youtube_channel_id: str, text_channel: str
    ):
        """
        Add a Youtube channel to be notified
        :param ctx: The current context. (discord.ext.commands.Context)
        :param youtube_channel_id: The Youtube channel to be notified of (str)
        :param text_channel: The text channel that will receive the notification (str)
        """
        guild_data = await get_guild_data(ctx.message.guild.id)
        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        # TODO: throw specific error with message when channel ID is wrong
        latest_video = await get_latest_video(youtube_channel_id)

        # Get the channel
        channel = get_channel(ctx, text_channel)

        # TODO: Give information to the user when the text channel does not exist
        if not channel:
            await ctx.channel.send(translate("channel_nonexistant", await culture(ctx)))
            raise Exception("Invalid text channel provided")

        if isinstance(channel, discord.VoiceChannel):
            await ctx.channel.send(translate("channel_is_voice", await culture(ctx)))
            return

        add_response = await guild_data.add_youtube_channel(
            youtube_channel_id, channel, latest_video["video_id"]
        )

        msg = ""
        if add_response:
            msg = translate("youtube_added", await culture(ctx)).format(
                youtube_channel_id, channel
            )
        else:
            msg = translate("youtube_exists", await culture(ctx)).format(
                youtube_channel_id
            )
        info(msg)
        await ctx.send(msg)

    @commands.command(
        name="remove_youtube", usage="remove_youtube_usage", help="remove_youtube_help",
    )
    async def remove_youtube_channel(
        self, ctx: commands.Context, youtube_channel_id: str):
        """
        Remove a Youtube channel that was being notified
        :param ctx: The current context. (discord.ext.commands.Context)
        :param youtube_channel_id: The Youtube channel to be notified of (str)
        """

        guild_data = await get_guild_data(ctx.message.guild.id)
        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        remove_response = await guild_data.remove_youtube_channel(youtube_channel_id)
        msg = ""
        if remove_response:
            msg = translate("youtube_removed", await culture(ctx)).format(
                youtube_channel_id
            )
        else:
            msg = translate("youtube_no_exists", await culture(ctx)).format(
                youtube_channel_id
            )
        info(msg)
        await ctx.send(msg)

    @commands.command(
        name="list_youtube", help="list_youtube_help",
    )
    async def list_youtube_channels(self, ctx: commands.Context):
        """
        List all Youtube channels that are being monitored
        """

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg = translate("youtube_list_title", await culture(ctx))

        for channel_id, channel_data in guild_data.youtube_channels.items():
            msg = (
                msg
                + f"\n - Channel `{channel_id}` posts in <#{channel_data['text_channel_id']}>, last video ID: `{channel_data['latest_video_id']}`"
            )
        await ctx.send(msg)


def setup(bot: commands.bot):
    bot.add_cog(Youtube(bot))
