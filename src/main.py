import os
from Bot.nerdlandbot import NerdlandBot
from dotenv import load_dotenv
from discord.ext import commands

# Set working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

os.chdir(dname)
os.chdir("..")

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

bot = NerdlandBot("?")
for cog in ["games", "notify"]:
    bot.load_extension("Commands." + cog)


# @bot.event
# async def on_reaction_add(reaction, user):
#     if reaction.custom_emoji:
#         print(reaction.emoji.id)
#     else:
#         print(reaction.emoji)
#     if reaction.emoji == "😄":
#         print("LOL 😄")
# print(user)


bot.run(TOKEN)
