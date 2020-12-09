import os
import discord
import requests

from discord.ext import tasks

from nerdlandbot.commands.GuildData import get_all_guilds_data, GuildData, update_youtube_channel_video_id
from nerdlandbot.helpers.constants import SCHEDULER_INTERVAL
from nerdlandbot.helpers.log import info, fatal


@tasks.loop(minutes=SCHEDULER_INTERVAL)
async def check_and_post_latest_videos(bot):
    print("check_and_post_latest_videos")
    guilds_data = await get_all_guilds_data()
    for guild_data in guilds_data:
        for channel_id, channel_data in guild_data.youtube_channels.items():
            channel = bot.get_channel(channel_data["text_channel_id"])
            latest_video = await get_latest_video(channel_id)
            if latest_video["video_id"] != channel_data["latest_video_id"]:
                await update_youtube_channel_video_id(guild_data.guild_id, channel_id, latest_video["video_id"])
                msg = latest_video['link']
                await channel.send(msg)

async def get_latest_video(youtube_channel_id: str):
    # TODO don't get the token on each request
    YOUTUBE_TOKEN = os.getenv("YOUTUBE_TOKEN")

    info(f"Get latest videos for channel {youtube_channel_id}")

    r = requests.get(
        f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={youtube_channel_id}&maxResults=10&order=date&type=video&key={YOUTUBE_TOKEN}"
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
