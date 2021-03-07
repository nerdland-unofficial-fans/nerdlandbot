import os
import sys
import discord

from dotenv import load_dotenv

from nerdlandbot.bot import NerdlandBot
from nerdlandbot.helpers.log import info, fatal
from nerdlandbot.translations.Translations import get_text as _
from nerdlandbot.scheduler.YoutubeScheduler import check_and_post_latest_videos
from nerdlandbot.scheduler.PurgeScheduler import purge_messages
from nerdlandbot.commands.GuildData import get_all_guilds_data, GuildData


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
bot.load_extension("nerdlandbot.eventhandlers.onmemberjoin")
bot.load_extension("nerdlandbot.eventhandlers.onready")
bot.load_extension("nerdlandbot.eventhandlers.oncommanderror")

# load commands
bot.load_extension("nerdlandbot.commands.notify")
bot.load_extension("nerdlandbot.commands.help")
bot.load_extension("nerdlandbot.commands.settings")
bot.load_extension("nerdlandbot.commands.membercount")
bot.load_extension("nerdlandbot.commands.random")
bot.load_extension("nerdlandbot.commands.youtube")
bot.load_extension("nerdlandbot.commands.poll")
bot.load_extension("nerdlandbot.commands.purger")
bot.load_extension("nerdlandbot.commands.kerk")

bot.load_extension("nerdlandbot.commands.dad_joke")
bot.load_extension("nerdlandbot.commands.open_source")
bot.load_extension("nerdlandbot.commands.privacy")

bot.load_extension("nerdlandbot.commands.space_launches")

# Initialize and start YouTube scheduler
YOUTUBE_TOKEN = os.getenv("YOUTUBE_TOKEN")


@bot.event
async def on_ready():
    if YOUTUBE_TOKEN:
        info("Starting YouTube scheduler")
        check_and_post_latest_videos.start(bot)
    else:
        fatal(
            "Not starting YouTube scheduler. Please provide a YOUTUBE_TOKEN in your .env file"
        )

    bot.is_purging = {}
    purge_messages.start(bot)
bot.run(TOKEN)
