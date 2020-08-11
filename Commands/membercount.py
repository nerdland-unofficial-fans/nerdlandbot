import discord
from discord.ext import commands
import typing

from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture


async def count_online_members(ctx: commands.Context) -> int:
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
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(name="member_count", aliases=["count", "membercount"], brief="membercount_brief",
                      usage="membercount_usage", help="membercount_help")
    async def count(self, ctx: commands.Context, channel_name: typing.Optional[str] = None):
        if channel_name == "online":
            online_member_count = await count_online_members(ctx)
            msg = translate("membercount_online_result", await culture(ctx)).format(online_member_count)
            return await ctx.send(msg)

        if channel_name is None:
            msg = translate("membercount_server_result", await culture(ctx)) \
                .format(len(ctx.guild.members), ctx.guild.name)
            return await ctx.send(msg)

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
