import os
import discord
import requests
import time

from datetime import datetime, timedelta
from discord.ext import tasks

from nerdlandbot.commands.GuildData import get_all_guilds_data, GuildData, get_guild_data
from nerdlandbot.helpers.log import info, fatal

# TODO make interval configurable
@tasks.loop(seconds = 8.0)
async def purge_messages(bot):
    info("Purging messages")
    guild_data = await get_all_guilds_data()

    for guild_data in guilds_data:
        if bot.is_purging.get(str(guild_data.guild_id),False) == False:
            bot.is_purging[str(guild_data.guild_id)] = True
            for text_channel, max_age in guild_data.purgers.items():
                before = datetime.today() - timedelta(days=max_age)
                channel = bot.get_channel(int(text_channel))
                try:
                    if channel:
                        await channel.purge(check=check, before=before)
                except:
                    fatal(
                        f"Failed to purge messages for channel {channel.name} in guild {guild_data.guild_id}. Does the bot have appropriate permissions on that channel?"
                    )
            bot.is_purging[str(guild_data.guild_id)] = False
            
def check(message):
    return not message.pinned
