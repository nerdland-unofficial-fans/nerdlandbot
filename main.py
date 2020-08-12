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

# remove default help command
bot.remove_command('help')

# load event handlers
bot.load_extension("EventHandlers.onmemberjoin")
bot.load_extension("EventHandlers.onready")
bot.load_extension("EventHandlers.oncommanderror")

# load commands
bot.load_extension("Commands.notify")
bot.load_extension("Commands.help")
bot.load_extension("Commands.settings")
bot.load_extension("Commands.membercount")
bot.load_extension("Commands.random_user")


bot.run(TOKEN)

