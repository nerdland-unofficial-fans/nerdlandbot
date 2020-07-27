from discord.ext import commands


async def on_command_error(bot, ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        command_name = ctx.message.content.split(" ")[0]
        msg = (
            "My command `"
            + command_name
            + "` requires more arguments. `"
            + error.param.name
            + "` is missing."
        )
    else:
        msg = "Unrecognized command"
    await ctx.send(msg)
