import typing
import discord
from discord.ext import commands
import gspread
import os
from datetime import datetime

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.constants import NOTIFY_EMBED_COLOR

SHEETS_TOKEN = os.getenv("SHEETS_JSON")


class Recipe(commands.Cog, name="recipes"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    

    @commands.command(name="recipe")#, aliases=["opensource", "os"], brief="open_source_brief", usage="open_source_usage", help="open_source_help")
    async def cmd_recipe(self, ctx: commands.Context):
        # TODO: experiment with the position of this and if I can use a command to set this up properly
        gc = gspread.service_account(SHEETS_TOKEN)
        sh = gc.open("#nomnom recepten")
        ws = sh.sheet1
        next_row = next_available_row(ws)

        # Fetching date and formatting it
        d_obj = datetime.now()
        date_string = "{}/{}/{} {}:{}:{}".format(d_obj.month, d_obj.day, d_obj.year, d_obj.hour, d_obj.minute, d_obj.second)
        
        # Asking the users questions
        # TODO: Make this use a loop, it's too repetitive.
        await ctx.send("Please enter the name of the dish")
        msg = await ctx.bot.wait_for('message', timeout=30)

        await ctx.send("Please enter the link to the recipe, either a discord or external link")
        msg2 = await ctx.bot.wait_for('message', timeout=30)

        await ctx.send("Please give a rating out of 5")
        msg3 = await ctx.bot.wait_for("message", timeout=30)

        await ctx.send("Please enter any comments you might have on the recipe")
        msg4 = await ctx.bot.wait_for("message", timeout=60)

        await ctx.send("Please enter your name")
        msg5 = await ctx.bot.wait_for("message", timeout=30)

        # Updating the worksheet(ws) with all the data asked of the user
        ws.update("A{}".format(next_row), date_string)
        ws.format("A{}".format(next_row), {"horizontalAlignment": "RIGHT"})
        ws.update("B{}".format(next_row), msg.content)
        ws.format("B{}".format(next_row), {"textFormat": {"bold": True}})
        ws.update("C{}".format(next_row), msg2.content)
        ws.update("D{}".format(next_row), int(msg3.content))
        ws.update("E{}".format(next_row), msg4.content)
        ws.update("F{}".format(next_row), msg5.content)


def next_available_row(worksheet) -> str:
    """
    Returning the next available row
    worksheet: the sheet you're working on
    """
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)
        
        
def setup(bot: commands.Bot):
    bot.add_cog(Recipe(bot))