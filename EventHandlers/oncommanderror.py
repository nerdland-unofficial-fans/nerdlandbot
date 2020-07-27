from discord.ext import commands


async def on_command_error(bot, ctx, error):
    print(error)
    await ctx.send('Unrecognized command')
