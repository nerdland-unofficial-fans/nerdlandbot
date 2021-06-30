from typing import Any
import os
from discord.ext import commands


from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.TranslationHelper import get_culture_from_id as culture_id
from nerdlandbot.helpers.log import warn as log_warn


class OnCommandError(commands.Cog, name="on_command_error"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.discord_server_id = os.getenv("DISCORD_SERVER_ID")


    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx: commands.Context, error: Any):
        """
        Handles any errors thrown by the commands.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param error: The current error. (Any)
        """
        #Notify user when using a command in DM that is not meant for DM
        if isinstance(error, commands.NoPrivateMessage):
            msg = translate("err_command_no_DM", await culture_id(int(self.discord_server_id)))
            return await ctx.send(msg)
        # Notify user for MissingRequiredArgument errors
        elif isinstance(error, commands.MissingRequiredArgument):
            command_name = ctx.message.content.split(" ")[0]
            msg = translate("err_missing_parameter", await culture(ctx)).format(command_name, error.param.name)
            return await ctx.send(msg)

        else:
            # Log the warning
            log_warn(error)

        # Notify user with general error
        if ctx.guild:
            msg = translate("err_unrecognized_command", await culture(ctx))
        else:
            msg = translate("err_unrecognized_command", await culture_id(int(self.discord_server_id)))
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(OnCommandError(bot))
