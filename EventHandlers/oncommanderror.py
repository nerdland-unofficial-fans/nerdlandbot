from discord.ext import commands
from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture


class OnCommandError(commands.Cog, name="on_command_error"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx, error):
        print(error)

        if isinstance(error, commands.MissingRequiredArgument):
            command_name = ctx.message.content.split(" ")[0]
            msg = translate("err_missing_parameter", await culture(ctx)).format(command_name, error.param.name)
        else:
            msg = translate("err_unrecognized_command", await culture(ctx))

        await ctx.send(msg)


def setup(bot):
    bot.add_cog(OnCommandError(bot))
