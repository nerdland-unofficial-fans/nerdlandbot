from discord.ext import commands

class OnCommandError(commands.Cog, name="on_command_error"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx, error):
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

def setup(bot):
    bot.add_cog(OnCommandError(bot))
