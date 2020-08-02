import os
from Bot.nerdlandbot import NerdlandBot
from dotenv import load_dotenv
from discord.ext import commands

# Set working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

os.chdir(dname)

load_dotenv()

PREFIX = os.getenv("PREFIX")
TOKEN = os.getenv("DISCORD_TOKEN")

bot = NerdlandBot(PREFIX)
bot.load_extension("Commands.notify")

bot.run(TOKEN)
