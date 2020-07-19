import os

from Bot.nerdlandbot import NerdlandBot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = NerdlandBot('?')
bot.load_extension('Commands.games')

bot.run(TOKEN)
