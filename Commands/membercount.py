import discord
from discord.ext import commands


async def count_online_members(ctx):
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
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="member_count", aliases=["count", "membercount"], brief="performs a member count", usage="[channel name]", help="Perform a member count.\n\nWithout parameter: returns the server member count.\n\nWith a channel name: returns a count of all members currently in the given channel.\n\n With parameter 'online': Return all members curenlty online. ")
    async def count(self, ctx, channel_name=None):
        if channel_name == "online":
            online_member_count = count_online_members(ctx)
            return await ctx.send(f'There are {online_member_count} people online in this server!')

        if channel_name is None:
            return await ctx.send(f'There are {len(ctx.guild.members)} people in `{ctx.guild.name}`!')

        channel = discord.utils.get(ctx.channel.guild.channels, name=channel_name)

        if channel is None:
            return await ctx.send("Please add a channel name to your command, foemp!")

        if len(channel.members) < 1:
            return await ctx.send("That channel is empty, foemp!")

        if len(channel.members) == 1:
            return await ctx.send(f'There is one person in channel <#{channel.id}>!')

        await ctx.send(f'There are {len(channel.members)} people in channel <#{channel.id}>!')


def setup(bot):
    bot.add_cog(MemberCount(bot))
