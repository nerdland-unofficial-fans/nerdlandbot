import typing
import discord
from discord.ext import commands
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture


class OpenSource(commands.Cog, name="open_source"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="open_source", aliases=["opensource", "os"], brief="open_source_brief", usage="open_source_usage", help="open_source_help")
    async def open_source(self, ctx: commands.Context, mention:typing.Optional[str] = None):
        #check if user mentioned  
        if mention and mention[:2] == "<@":
            msg = translate("open_source_message_tag", await culture(ctx)).format(mention)
        else:
            msg = translate("open_source_message", await culture(ctx))
        #send message
        await ctx.send(msg)

def setup(bot: commands.Bot):
    bot.add_cog(OpenSource(bot))
