from discord.ext import commands
from datetime import datetime

from nerdlandbot.commands.GuildData import get_guild_data
from nerdlandbot.helpers.constants import SATURDAY, SUNDAY


async def get_culture_from_context(ctx: commands.Context) -> str:
    """
    Fetches the current culture for a given context.
    :param ctx: The current context. (discord.ext.commands.Context)
    :return: The culture for the given context. (str)
    """
    guild_id = ctx.guild.id
    guild = await get_guild_data(guild_id)
    return guild.culture

def foemp_or_schat():
    # if it's weekend (5 or 6) the bot will say schatje instead of foemp.
    adjective = "foemp"
    if datetime.now().weekday() == SATURDAY or datetime.now().weekday() == SUNDAY:
        adjective = "schatje"
    return adjective    

def dummy_or_darling():
    # if it's weekend (5 or 6) the bot will say darling instead of dummy.
    adjective = "dummy"
    if datetime.now().weekday() == SATURDAY or datetime.now().weekday() == SUNDAY:
        adjective = "darling"
    return adjective  

def translate_adjective(language):
    if language == "nl":
        return foemp_or_schat()
    else:
        return dummy_or_darling()