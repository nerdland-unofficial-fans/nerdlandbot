import random
import discord
from discord.ext import commands


def pick_random_online_member(ctx):
    def is_online(user):
        if user.status == discord.Status.online:
            return True
        elif user.status == discord.Status.idle:
            return True
        elif user.status == discord.Status.do_not_disturb:
            return True
        else:
            return False

    online_members = filter(is_online, ctx.guild.members)
    return random.choice(list(online_members))


class RandomUser(commands.Cog, name="random_user"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="random_user", aliases=["random"], brief="select a random user", usage="<channel name>", help="this will select a random user.\n\nWith a channel name: Select a random user from the given channel.\n\n With parameter 'online': Select a random online user from the server.")
    async def select_random_user(self, ctx, channel_name=None):
        if channel_name == "online":
            member = pick_random_online_member(ctx)
            return await ctx.send(f'<@{member.id}> was chosen!')

        if channel_name is None:
            return await ctx.send("Please provide a channel name, foemp!")


        channel = discord.utils.get(ctx.channel.guild.channels, name=channel_name)

        if channel is None:
            return await ctx.send("That channel does not exist, foemp!")

        if len(channel.members) < 1:
            return await ctx.send("That channel is empty, foemp!")

        user = random.choice(channel.members)
        await ctx.send(f'<@{user.id}> was chosen!')

def setup(bot):
    bot.add_cog(RandomUser(bot))
