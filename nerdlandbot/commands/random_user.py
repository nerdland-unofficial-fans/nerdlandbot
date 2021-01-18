import random
import discord
from discord.ext import commands
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.parser import parse_channel


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


class RandomUser(commands.Cog, name="random_user"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="random_user", aliases=["random"], brief="random_user_brief", usage="random_user_usage",
                      help="random_user_help")
    async def select_random_user(self, ctx: commands.Context, channel_name: str = None):
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
        channel_name = parse_channel(channel_name)

        # Retrieve channel
        channel = discord.utils.get(ctx.channel.guild.channels, name=channel_name)

        # Error if channel does not exist
        if channel is None:
            msg = translate("membercount_channel_nonexistant", await culture(ctx))
            return await ctx.send(msg)

        # Error if channel empty
        if len(channel.members) < 1:
            msg = translate("membercount_empty_channel", await culture(ctx)).format(channel.id)
            return await ctx.send(msg)

        # Pick a random user from channel, and report back to user
        member = random.choice(channel.members)
        msg = translate("random_user_chosen", await culture(ctx)).format(member.id)
        await ctx.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(RandomUser(bot))
