from discord.ext import tasks
import discord
import requests
from Commands.GuildData import get_all_guilds_data, GuildData
from Helpers.log import info, fatal
import os
from datetime import datetime, timedelta

# TODO make interval configurable
@tasks.loop(minutes=1.0)
async def purge_messages(bot):
    info("Purging messages")
    guilds_data = await get_all_guilds_data()
    for guild_data in guilds_data:
        for text_channel, max_age in guild_data.purgers.items():
            before = datetime.today() - timedelta(minutes=max_age)
            channel = bot.get_channel(int(text_channel))
            try:
                if channel:
                    await channel.purge(check=check, before=before)
            except:
                fatal(
                    f"Failed to purge messages for channel {channel.name} in guild {guild_data.guild_id}. Does the bot have appropriate permissions on that channel?"
                )


def check(message):
    return not message.pinned
