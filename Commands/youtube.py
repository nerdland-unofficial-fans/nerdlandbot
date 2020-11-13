from discord.ext import commands
from .GuildData import get_guild_data, GuildData
from Helpers.parser import parse_channel
from Helpers.log import info, fatal
from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture
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

        msg = ""
        if add_response:
            msg = f"Added a notifier for `{youtube_channel_id}` to be posted in text channel #{channel}"
        else:
            msg = f"Notifier for `{youtube_channel_id}` already exists"
        info(msg)
        await ctx.send(msg)

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
        msg = ""
        if remove_response:
            msg = f"Removed notifier for `{youtube_channel_id}`"
        else:
            msg = f"There is no notifier for `{youtube_channel_id}`"
        info(msg)
        await ctx.send(msg)

    @commands.command(
        name="youtube_list",
        aliases=[],
        brief="youtube_list_brief",
        usage="youtube_list_usage",
        help="youtube_list_help",
    )
    async def list_youtube_channels(self, ctx: commands.Context):
        """
        List all Youtube channels that are being monitored
        """

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg = translate("youtube_list_title", await culture(ctx)) + "\n - " + "\n - "
        print(
            str(
                guild_data.youtube_channels["UCPjHlmSGP-rMg5PR-PyaJug"][
                    "text_channel_id"
                ]
            )
        )
        # for channel_id, channel_data in guild_data.youtube_channels:
        #     print(str(channel_id))
        #     print(str(channel_data))
        #     print(str(channel["text_channel_id"]))
        #     msg = msg + str(channel["text_channel_id"])
        await ctx.send(msg)

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
