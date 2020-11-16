import os
import sys

from Bot.nerdlandbot import NerdlandBot
from dotenv import load_dotenv
import discord

from Helpers.log import info, fatal
from Translations.Translations import get_text as _

from Scheduler.Scheduler import  check_and_post_latest_videos

# Set working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

os.chdir(dname)

load_dotenv()

PREFIX = os.getenv("PREFIX")
TOKEN = os.getenv("DISCORD_TOKEN")

if PREFIX:
    info("Start bot with prefix '" + PREFIX + "'")
else:
    fatal("Please provide a PREFIX in your .env file")
    sys.exit()

# load up intents
intents = discord.Intents.all()

bot = NerdlandBot(PREFIX, intents)

# remove default help command
bot.remove_command("help")

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
bot.load_extension("Commands.youtube")

# Initialize and start YouTube scheduler
YOUTUBE_TOKEN = os.getenv("YOUTUBE_TOKEN")

@bot.event
async  def on_ready():
    if YOUTUBE_TOKEN:
        info("Starting YouTube scheduler")
        check_and_post_latest_videos.start(bot)
    else:
        fatal("Not starting YouTube scheduler. Please provide a YOUTUBE_TOKEN in your .env file")

bot.run(TOKEN)
