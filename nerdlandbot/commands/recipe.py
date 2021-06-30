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



class Recipe(commands.Cog, name="Spreadsheets"):
    def __init__(self, bot: commands.Bot):
        self.sheets_token = os.getenv("SHEETS_JSON")
        self.spreadsheet = os.getenv("SPREADSHEET")
        self.bot = bot
    

    @commands.command(name="add_recipe", aliases=["recipe"], brief="recipe_brief", help="recipe_help")
    @commands.guild_only()
    async def add_recipe(self, ctx: commands.Context):
        # Getting everything ready to acces 
        lang = await culture(ctx)
        try:
            gc = gspread.service_account(self.sheets_token)
            sh = gc.open(self.spreadsheet)
        except:
            msg = translate("recipe_verification_error", lang)
            return await ctx.send(msg)
        ws = sh.sheet1
        next_row = next_available_row(ws)

        # Fetching date and formatting it
        d_obj = datetime.now()
        date_string = "{}/{}/{} {}:{}:{}".format(d_obj.month, d_obj.day, d_obj.year, d_obj.hour, d_obj.minute, d_obj.second)

        # Initializing variables needed
        embed_title = translate("recipe_title", lang)
        questions = []
        answers = []


        
        # Asking the user questions and capturing the answer
        for i in range(5):
            questions.append(translate("recipe_template", lang).format(translate("recipe_{}_question".format(i+1), lang)))
            embed = discord.Embed(
                title = embed_title,
                description = questions[i],
                color = NOTIFY_EMBED_COLOR
            )
            await ctx.send(embed=embed)
            try:
                reaction = await ctx.bot.wait_for("message", timeout=30, check=check(ctx.author))
                await asyncio.sleep(1)
                answers.append(reaction)
                # If the user wants to abort, he can enter '0'
                if reaction.content == "0":
                    abort = translate("recipe_abort", lang)
                    embed = discord.Embed(
                        title = embed_title,
                        description = abort,
                        color = NOTIFY_EMBED_COLOR
                    )
                    return await ctx.send(embed=embed)
                # When the user is asked a rating, check if it's a number between 1 and 5
                if i == 2:
                    if reaction.content.isnumeric():
                        reaction_int = int(reaction.content)
                        if reaction_int > 5 or reaction_int < 1:
                            rating_error = translate("recipe_rating_error", lang)
                            embed = discord.Embed(
                                title = embed_title,
                                description = rating_error,
                                color = NOTIFY_EMBED_COLOR
                            )
                            return await ctx.send(embed=embed)
                    else:
                        int_error = translate("recipe_int_error", lang)
                        embed = discord.Embed(
                            title = embed_title,
                            description = int_error,
                            color = NOTIFY_EMBED_COLOR
                        )
                        return await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                timeout = translate("recipe_timeout", lang)
                embed = discord.Embed(
                    title = embed_title,
                    description = timeout,
                    color = NOTIFY_EMBED_COLOR
                )
                return await ctx.send(embed=embed)
        
        # Let the user know the process has completed and he/she/it just has to wait now
        processing = translate("recipe_processing", lang)
        embed = discord.Embed(
                    title = embed_title,
                    description = processing,
                    color = NOTIFY_EMBED_COLOR
                )
        msg = await ctx.send(embed=embed)


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
            embed = discord.Embed(
                title = embed_title,
                description = error_msg,
                color = NOTIFY_EMBED_COLOR
            )
            await ctx.send(embed=embed)
        else:
            succes_msg = translate("recipe_succes", lang)
            embed = discord.Embed(
                title = embed_title,
                description = succes_msg,
                color = NOTIFY_EMBED_COLOR
            )
            await ctx.send(embed=embed)
        
        # Removing the processing message
        return await msg.delete()



def next_available_row(worksheet) -> str:
    """
    Returning the next available row
    :param worksheet: The worksheet you're working on
    :return: The index of the next available column
    """
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

def check(author):
    def inner_check(message):
        return message.author == author
    return inner_check

     
def setup(bot: commands.Bot):
    bot.add_cog(Recipe(bot))
