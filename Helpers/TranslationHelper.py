from discord.ext import commands
from Commands.GuildData import get_guild_data


async def get_culture_from_context(ctx: commands.Context) -> str:
    guild_id = ctx.guild.id
    guild = await get_guild_data(guild_id)
    return guild.culture
