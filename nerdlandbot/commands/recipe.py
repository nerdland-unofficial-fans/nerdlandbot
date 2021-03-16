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
    

    @commands.command(name="add_recipe")
    async def add_recipe(self, ctx: commands.Context):
        # Getting everything ready to acces 
        gc = gspread.service_account(SHEETS_TOKEN)
        sh = gc.open(SPREADSHEET)
        ws = sh.sheet1
        next_row = next_available_row(ws)

        # TODO: Add this and other text in translations.csv
        questions = ["the name of the dish", "the link to the recipe", "a rating", "comments", "your name"]
        answers = []

        # Fetching date and formatting it
        d_obj = datetime.now()
        date_string = "{}/{}/{} {}:{}:{}".format(d_obj.month, d_obj.day, d_obj.year, d_obj.hour, d_obj.minute, d_obj.second)

        def check(author):
            def inner_check(message):
                return message.author == author
            return inner_check
        
        # Asking the user questions and capturing the answer
        for i in range(len(questions)):
            await ctx.send("Please enter {}".format(questions[i]))
            await asyncio.sleep(1)
            try:
                reaction = await ctx.bot.wait_for("message", timeout=20, check=check(ctx.author))
                answers.append(reaction)
            except asyncio.TimeoutError:
                return await ctx.send("Go to bed, sleepy!")

        # Updating the worksheet(ws) with all the data asked of the user
        ws.update("A{}".format(next_row), date_string)
        ws.format("A{}".format(next_row), {"horizontalAlignment": "RIGHT"})
        ws.update("B{}".format(next_row), answers[0].content)
        ws.format("B{}".format(next_row), {"textFormat": {"bold": True}})
        ws.update("C{}".format(next_row), answers[1].content)
        ws.update("D{}".format(next_row), int(answers[2].content))
        ws.update("E{}".format(next_row), answers[3].content)
        ws.update("F{}".format(next_row), answers[4].content)


def next_available_row(worksheet) -> str:
    """
    Returning the next available row
    worksheet: the sheet you're working on
    """
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

     
def setup(bot: commands.Bot):
    bot.add_cog(Recipe(bot))
