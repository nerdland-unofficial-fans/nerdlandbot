import os
import discord
import random
import aiohttp
import asyncio

from discord.ext import commands
from nerdlandbot.helpers.constants import WOMBATS_DIR_NAME, PONCHO_DIR_NAME
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.log import warn
from nerdlandbot.helpers.constants import EIGHT_BALL_URL,DAD_JOKE_URL
from nerdlandbot.helpers.channel import get_channel

def pick_random_online_member(ctx: commands.Context) -> discord.Member:
    """
    Selects a random online member from the server.
    :param ctx: The current context: (discord.ext.commands.Context)
    :return: The chosen member. (discord.Member)
    """

    def is_online(user: discord.Member):
        if user.status == discord.Status.online:
            return True
        elif user.status == discord.Status.idle:
            return True
        else:
            return False

    online_members = filter(is_online, ctx.guild.members)
    return random.choice(list(online_members))


class Random(commands.Cog, name="Random"):
    def __init__(self, bot):
        self.bot = bot

        current_directory = os.getcwd()
        
        if not os.path.exists(WOMBATS_DIR_NAME):
            os.makedirs(WOMBATS_DIR_NAME)
            warn(f"Directory {os.path.join(current_directory,WOMBATS_DIR_NAME)} is created, put some wombat pictures in it!" )

        if not os.path.exists(PONCHO_DIR_NAME):
            os.makedirs(PONCHO_DIR_NAME)
            warn(f"Directory {os.path.join(current_directory,PONCHO_DIR_NAME)} is created, put some Poncho pictures in it!" )

    @commands.command(name="random_user", aliases=["randomuser"], brief="random_user_brief", usage="random_user_usage",
                      help="random_user_help")
    async def select_random_user(self, ctx: commands.Context, *, channel_name: str = None):
        """
        Selects a random user from the server, channel, or online members.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param channel_name: The channel to pick from, 'online' in order to pick an online member from the server. (str)
        """

        # Error for missing parameter
        if channel_name is None:
            msg = translate("random_user_no_channel", await culture(ctx))
            return await ctx.send(msg)

        # Choose from online members if requested
        if channel_name == "online":
            member = pick_random_online_member(ctx)
            msg = translate("random_user_chosen", await culture(ctx)).format(member.id)
            return await ctx.send(msg)

        # Sanitize channel name
        channel = get_channel(ctx,channel_name)

        # Error if channel does not exist
        if channel is None:
            msg = translate("channel_nonexistant", await culture(ctx))
            return await ctx.send(msg)

        # Error if channel empty
        if len(channel.members) < 1:
            msg = translate("membercount_empty_channel", await culture(ctx)).format(channel.id)
            return await ctx.send(msg)

        # Pick a random user from channel, and report back to user
        member = random.choice(channel.members)
        msg = translate("random_user_chosen", await culture(ctx)).format(member.id)
        await ctx.send(msg)

    @commands.command(name="wombat_pic", aliases = ["wombat","wombatpic"], hidden=True, help="wombat_pic_help")
    async def cmd_wombat_pic(self, ctx):
        wombat_list = [os.path.join(WOMBATS_DIR_NAME, w) for w in os.listdir(WOMBATS_DIR_NAME)]

        if not wombat_list:
            msg = translate("empty_wombat_list", await culture(ctx))
            return await ctx.send(msg)

        await ctx.send(file=discord.File(random.choice(wombat_list)))

    @commands.command(name="poncho", aliases=["poncho_pic","ponchopic"],hidden=True, help="poncho_pic_help")
    async def cmd_poncho_pic(self, ctx):
        poncho_list = [os.path.join(PONCHO_DIR_NAME, w) for w in os.listdir(PONCHO_DIR_NAME)]

        if not poncho_list:
            msg = translate("empty_poncho_list", await culture(ctx))
            return await ctx.send(msg)

        msg = translate("poncho_hond", await culture(ctx))
        await ctx.send(msg)
        await ctx.send(file=discord.File(random.choice(poncho_list)))

    @commands.command(name="eight_ball", aliases=["eightball"], help="eight_ball_help")
    async def cmd_eight_ball(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get(EIGHT_BALL_URL) as resp:
                msg = await resp.text(encoding='utf-8')
                msg = msg[1:-2]
                await ctx.reply(msg)

    @commands.command(name="dad_joke", aliases=["dadjoke"], help="dad_joke_help")
    async def cmd_dad_joke(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get(DAD_JOKE_URL,headers = { "Accept": "text/plain" }) as resp:
                msg = await resp.text(encoding='utf-8')

                # msg can contain utf 2028 charactercode which is line-separator, we're just converting it to '\n'
                msg = '\n'.join(msg.splitlines())
                await ctx.send(msg)

def setup(bot):
    bot.add_cog(Random(bot))
