from discord.ext import commands


async def on_command_error(bot, ctx, error):
    await ctx.send('Unrecognized command')
