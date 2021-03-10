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

