import os
import sys

from Bot.nerdlandbot import NerdlandBot
from dotenv import load_dotenv


# Set working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

os.chdir(dname)

load_dotenv()

PREFIX = os.getenv("PREFIX")
TOKEN = os.getenv("DISCORD_TOKEN")

if PREFIX:
    print("Start bot with prefix '" + PREFIX + "'")
else:
    sys.exit("Please provide a PREFIX in your .env file")


bot = NerdlandBot(PREFIX)
bot.remove_command('help')
bot.load_extension("Commands.notify")
bot.load_extension("Commands.help")
bot.load_extension("Commands.settings")


bot.run(TOKEN)

