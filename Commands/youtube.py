from discord.ext import commands
from .GuildData import get_guild_data, GuildData
from Helpers.parser import parse_channel
from Helpers.log import info, fatal
import discord
import requests
import os


class Youtube(commands.Cog, name="Youtube_lists"):
    @commands.command(
        name="youtube_add",
        aliases=[],
        brief="youtube_add_brief",
        usage="youtube_add_usage",
        help="youtube_add_help",
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
        # guild_data = await get_guild_data(ctx.message.guild.id)
        text_channel = text_channel.lower()

        # Sanitize channel name
        text_channel = parse_channel(text_channel)

        # TODO: throw specific error with message when channel ID is wrong
        latest_video = await self.get_latest_video(youtube_channel_id)

        # Retrieve channel
        channel = discord.utils.get(ctx.channel.guild.channels, name=text_channel)
        # TODO: Give information to the user when the text channel does not exist
        if not channel:
            raise Exception("Invalid text channel provided")

        guild_data = await get_guild_data(ctx.message.guild.id)
        add_response = await guild_data.add_youtube_channel(
            youtube_channel_id, channel, latest_video["video_id"]
        )

        if add_response:
            info(
                f"Added a notifier for {youtube_channel_id} to be posted in text channel #{channel}"
            )
        else:
            info(f"Notifier for {youtube_channel_id} already exists")

    @commands.command(
        name="youtube_remove",
        aliases=[],
        brief="youtube_remove_brief",
        usage="youtube_remove_usage",
        help="youtube_remove_help",
    )
    async def remove_youtube_channel(
        self, ctx: commands.Context, youtube_channel_id: str, text_channel: str
    ):
        """
        Add a Youtube channel to be notified
        :param ctx: The current context. (discord.ext.commands.Context)
        :param youtube_channel_id: The Youtube channel to be notified of (str)
        """

        guild_data = await get_guild_data(ctx.message.guild.id)
        remove_response = await guild_data.remove_youtube_channel(youtube_channel_id)
        if remove_response:
            info(f"Removed notifier for {youtube_channel_id}")
        else:
            info(f"There is no notifier for {youtube_channel_id}")

    async def get_latest_video(self, youtube_channel_id: str):
        TOKEN = os.getenv("YOUTUBE_TOKEN")
        if TOKEN:
            info(f"Get latest videos for channel {youtube_channel_id}")
        else:
            fatal("Please provide a YOUTUBE_TOKEN in your .env file")
            raise Exception("YouTube token is not set")

        r = requests.get(
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={youtube_channel_id}&maxResults=10&order=date&type=video&key={TOKEN}"
        )
        response = r.json()["items"][0]

        video_id = response["id"]["videoId"]
        title = response["snippet"]["title"]
        description = response["snippet"]["description"]
        link = f"https://www.youtube.com/watch?v={video_id}"

        return {
            "video_id": video_id,
            "title": title,
            "description": description,
            "link": link,
        }


def setup(bot: commands.bot):
    bot.add_cog(Youtube(bot))
