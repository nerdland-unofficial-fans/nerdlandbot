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
from nerdlandbot.helpers.log import error

@tasks.loop(minutes=1.0)
async def church_fights(bot):
    current_time = datetime.now()
    if current_time.hour == 16 and current_time.minute == 0:
        guilds_data = await get_all_guilds_data()
        day = current_time.day
        for guild_data in guilds_data:
            channel_id = guild_data.church_channel
            channel = bot.get_channel(channel_id)
            for church in guild_data.church_event:
                for _ in range(len(guild_data.church_event)):
                    if day == church["day"]:
                        msg = translate("church", church["culture"]).format(
                            church_emoji, church["receiver"], church["sender"], fist)
                        if church["message"]:
                            msg += translate("church_message",
                                            church["culture"]).format(church["message"])
                        if channel is not None:
                            await channel.send(msg)
                            await guild_data.remove_church_event()
                        else:
                            error("There is no channel set. Use the church_channel command to set it!")
