import typing
import discord
from discord.ext import commands
import gspread
import os
import asyncio
from datetime import datetime

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.constants import NOTIFY_EMBED_COLOR

SHEETS_TOKEN = os.getenv("SHEETS_JSON")
SPREADSHEET = os.getenv("SPREADSHEET")


class Recipe(commands.Cog, name="recipes"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    

    @commands.command(name="add_recipe", brief="recipe_brief", help="recipe_help")
    async def add_recipe(self, ctx: commands.Context):
        # Getting everything ready to acces 
        gc = gspread.service_account(SHEETS_TOKEN)
        sh = gc.open(SPREADSHEET)
        ws = sh.sheet1
        next_row = next_available_row(ws)

        # Fetching date and formatting it
        d_obj = datetime.now()
        date_string = "{}/{}/{} {}:{}:{}".format(d_obj.month, d_obj.day, d_obj.year, d_obj.hour, d_obj.minute, d_obj.second)

        def check(author):
            def inner_check(message):
                return message.author == author
            return inner_check
        
        lang = await culture(ctx)
        questions = []
        answers = []
        
        # Asking the user questions and capturing the answer
        for i in range(5):
            questions.append(translate("recipe_template", lang).format(translate("recipe_{}_question".format(i+1), lang)))
            await ctx.send(questions[i])
            await asyncio.sleep(1)
            try:
                reaction = await ctx.bot.wait_for("message", timeout=30, check=check(ctx.author))
                answers.append(reaction)
                if i == 2:
                    try:
                        int(reaction.content)
                    except:
                        int_error = translate("recipe_int_error", lang)
                        return await ctx.send(int_error)
            except asyncio.TimeoutError:
                timeout = translate("recipe_timeout", lang)
                return await ctx.send(timeout)

        # Updating the worksheet(ws) with all the data asked of the user
        ws.update("A{}".format(next_row), date_string)
        ws.format("A{}".format(next_row), {"horizontalAlignment": "RIGHT"})
        ws.update("B{}".format(next_row), answers[0].content)
        ws.format("B{}".format(next_row), {"textFormat": {"bold": True}})
        ws.update("C{}".format(next_row), answers[1].content)
        ws.update("D{}".format(next_row), int(answers[2].content))
        ws.update("E{}".format(next_row), answers[3].content)
        ws.update("F{}".format(next_row), answers[4].content)

        # On a delay of 5 seconds (google isn't instant) check if the last cell was added
        await asyncio.sleep(5)
        if not ws.acell("F{}".format(next_row)).value:
            error_msg = translate("recipe_error", lang)
            return await ctx.send(error_msg)
        else:
            succes_msg = translate("recipe_succes", lang)
            return await ctx.send(succes_msg)



def next_available_row(worksheet) -> str:
    """
    Returning the next available row
    :param worksheet: The worksheet you're working on
    :return: The index of the next available column
    """
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

     
def setup(bot: commands.Bot):
    bot.add_cog(Recipe(bot))
