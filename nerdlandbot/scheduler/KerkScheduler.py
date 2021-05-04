import os
import discord
import requests
import time

from datetime import datetime, timedelta
from discord.ext import tasks

from nerdlandbot.commands.GuildData import get_all_guilds_data, GuildData, get_guild_data
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.emoji import fist, church_emoji
from nerdlandbot.helpers.log import warn

@tasks.loop(minutes = 1.0)
async def church_fights(bot):
    guilds_data = await get_all_guilds_data()
    day = datetime.now().day
    hour = datetime.now().hour
    for guild_data in guilds_data:
        channel_id = guild_data.church_channel
        try:
            channel = bot.get_channel(channel_id)
        except:
            warn("Something went wrong. It's possible the channel is not set.")
        for church in guild_data.church_event:
            # For every church_event scheduled, send it to the kerk channel
            for _ in range(len(guild_data.church_event)):
                if day == church[2] and hour == 16:
                    msg = translate("church", church[3]).format(church_emoji, church[1], church[0], fist)
                    if church[4]:
                        msg += translate("church_message", church[3]).format(church[4])
                    await channel.send(msg)
                    await guild_data.remove_church_event()
