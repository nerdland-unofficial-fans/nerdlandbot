from discord.ext import commands

from nerdlandbot.commands.GuildData import get_guild_data


async def get_culture_from_context(ctx: commands.Context) -> str:
    """
    Fetches the current culture for a given context.
    :param ctx: The current context. (discord.ext.commands.Context)
    :return: The culture for the given context. (str)
    """
    guild_id = ctx.guild.id
    culture = await get_culture_from_id(guild_id)
    return culture


async def get_culture_from_id(guild_id: int) -> str:
    """
    Fetches the current culture for a given context.
    :param guild_id: The id of the guild to get the context from. (int)
    :return: The culture for the given context. (str)
    """
    guild = await get_guild_data(guild_id)
    return guild.culture
