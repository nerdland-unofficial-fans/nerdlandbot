import discord

from discord.ext import commands

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture


def count_online_members(ctx) -> int:
    """
    Count the amount of online members.
    :param ctx: The current context. (discord.ext.commands.Context)
    :return: The amount of online members. (int)
    """

    def is_online(user):
        if user.status == discord.Status.online:
            return True
        elif user.status == discord.Status.idle:
            return True
        elif user.status == discord.Status.do_not_disturb:
            return True
        else:
            return False

    onlineMembers = filter(is_online, ctx.guild.members)
    return len(list(onlineMembers))


class MemberCount(commands.Cog, name="member_count"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="member_count", aliases=["count", "membercount"], brief="membercount_brief",
                      usage="membercount_usage", help="membercount_help")
    async def count(self, ctx, *, channel_name=None):
        """
        Count the members in a given channel, the members in the current server, or the online members in the current server.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param channel_name: The name of the channel to count, 'online' to count online members, or nothing to count the entire server. (optional - str - default = None)
        """
        if channel_name == "online":
            online_member_count = count_online_members(ctx)
            msg = translate("membercount_online_result", await culture(ctx)).format(online_member_count)
            return await ctx.send(msg)

        if not channel_name:
            msg = translate("membercount_server_result", await culture(ctx)).format(len(ctx.guild.members),
                                                                                    ctx.guild.name)
            return await ctx.send(msg)

        # Retrieve channel
        channel = discord.utils.get(ctx.channel.guild.channels, name=channel_name)

        if channel is None:
            msg = translate("membercount_channel_nonexistant", await culture(ctx))
            return await ctx.send(msg)

        if len(channel.members) < 1:
            msg = translate("membercount_empty_channel", await culture(ctx)).format(channel.id)
            return await ctx.send(msg)

        if len(channel.members) == 1:
            msg = translate("membercount_single_person", await culture(ctx)).format(channel.id)
            return await ctx.send(msg)

        msg = translate("membercount_channel_result", await culture(ctx)).format(len(channel.members), channel.id)
        await ctx.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(MemberCount(bot))
