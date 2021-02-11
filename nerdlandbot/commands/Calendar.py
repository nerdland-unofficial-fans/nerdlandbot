import discord
import os
import requests
import datetime

from discord.ext import commands, tasks
from nerdlandbot.commands.GuildData import (
    get_all_guilds_data,
    get_guild_data,
    GuildData,
)
from nerdlandbot.helpers.log import info, fatal
from nerdlandbot.helpers.channel import get_channel
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.translations.Translations import get_text as translate


class calendar(commands.Cog, name="Event Calendar"):
    @commands.command(
        name="add_event", usage="add_event_usage", help="add_event_help",
    )
    async def add_event(self, ctx: commands.Context, input_text: str):
        """
        Add an event to the event calendar.
        :param ctx: The current context. (discord.ext.commands.Context)
        Syntax:  "   Title      ;Description;StartDate;Duration(optional)"
        Example: "Title of Event;Description;10/12/2021 13:45;60"
        :param input_text: input to be parsed according to above syntax (str)
        """

        input_text_split = input_text.split(";")

        if len(input_text_split) is not 3 or len(input_text_split) is not 4:
            await ctx.send(translate("add_event_parameters", await culture(ctx)))
            return

        title = input_text_split[0]
        description = input_text[1]
        try:
            startDate = datetime.datetime.strptime(input_text[2], "%d/%m/%Y %H:%M")
        except ValueError:
            await ctx.send(translate("add_event_invalid_date", await culture(ctx)))
            return


def setup(bot: commands.bot):
    bot.add_cog(calendar(bot))
