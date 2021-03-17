import typing
import asyncio
import discord
from discord.ext import commands
import datetime

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.constants import *


class Reminder(commands.Cog, name="Simple Reminder"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="reminder", aliases=["remind_me"], brief="reminder_brief", usage="reminder_usage", help="reminder_help")
    async def reminder(self, ctx: commands.Context, time: typing.Optional[str] = None, *, message: typing.Optional[str] = None):
        # If the user doesn't enter a time-format, let him know
        msg = translate("reminder_err_no_int", await culture(ctx))
        title = translate("reminder_err_title", await culture(ctx))
        embed = discord.Embed(
            description=msg,
            color=NOTIFY_EMBED_COLOR
        )
        if time != None:
            if time.isnumeric():
                time_int = int(time)
            else:
                return await ctx.send(embed=embed)
        else:
            return await ctx.send(embed=embed)

        # If the time is longer than a day
        if time_int >= MAX_REMINDER_TIME:
            msg = translate("reminder_err_too_long", await culture(ctx))
            title = translate("reminder_err_title", await culture(ctx))
            embed = discord.Embed(
                title=title,
                description=msg,
                color=NOTIFY_EMBED_COLOR
            )
            return await ctx.send(embed=embed)

        # If the time is shorter than 5 minutes
        if time_int <= MIN_REMINDER_TIME:
            msg = translate("reminder_err_too_short", await culture(ctx))
            title = translate("reminder_err_title", await culture(ctx))
            embed = discord.Embed(
                title=title,
                description=msg,
                color=NOTIFY_EMBED_COLOR
            )
            return await ctx.send(embed=embed)
        
        # Logic to determine the time the user wants to be reminded
        current_time = datetime.datetime.now()
        remind_time = current_time + datetime.timedelta(minutes=time_int)
        remind_hour = remind_time.hour
        remind_minute = remind_time.minute

        # Fixing notation for first 10 min of the hour
        remind_minute_string = str(remind_minute).rjust(2,"0")

        # If there is a message, include it
        if message:
            reminder_set = translate("reminder_set_with_message", await culture(ctx)).format(remind_hour, remind_minute_string, message)
            reminder = translate("reminder_with_message", await culture(ctx)).format(ctx.message.author, remind_hour, remind_minute_string, message)
        else:
            reminder_set = translate("reminder_set_no_message", await culture(ctx)).format(remind_hour, remind_minute_string)
            reminder = translate("reminder_no_message", await culture(ctx)).format(ctx.message.author, remind_hour, remind_minute_string)

        reminder_embed_title = translate("reminder_embed_title", await culture(ctx))

        # Setting the embeds up
        embed_reminder_set = discord.Embed(
            title=reminder_embed_title,
            description=reminder_set,
            color=NOTIFY_EMBED_COLOR
        )

        embed_reminder = discord.Embed(
            title=reminder_embed_title,
            description=reminder,
            color=NOTIFY_EMBED_COLOR
        )

        # Sending confirmation that the reminder has been set
        await ctx.send(embed=embed_reminder_set)

        # If it's not the specified time, wait for it.
        while not (datetime.datetime.now().hour == remind_hour and datetime.datetime.now().minute == remind_minute):
            await asyncio.sleep(60)
       
        # Tag the author and send the message!
        author = f"<@{ctx.message.author.id}>"
        await ctx.send(author)
        return await ctx.send(embed=embed_reminder)

def setup(bot: commands.Bot):
    bot.add_cog(Reminder(bot))
