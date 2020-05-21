import os

from Bot.nerdlandbot import NerdlandBot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = NerdlandBot('?')
bot.run(TOKEN)
