import os

from Bot.nerdlandbot import NerdlandBot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = NerdlandBot('?')
for cog in ['games','notify']:
    bot.load_extension('Commands.'+ cog)

bot.run(TOKEN)
