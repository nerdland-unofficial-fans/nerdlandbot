import discord

from discord.ext import commands
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.translations.Translations import get_text as translate

empty = '\u200b'

class Privacy(commands.Cog, name="privacy"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="privacy", brief="privacy_brief")
    @commands.guild_only()
    async def privacy(self, ctx: commands.Context):
        language = await culture(ctx)
        title_txt = translate("privacy_policy_title", language)
        content_txt = translate("privacy_policy_content", language)

        embed = discord.Embed(title=title_txt, description=content_txt)
        await ctx.channel.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Privacy(bot))
