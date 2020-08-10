import discord
from discord.ext import commands

notification_channel_name = 'botplayground'
member_notification_trigger = 100


class OnMemberJoin(commands.Cog, name="on_member_join"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_member_join")
    async def on_member_join(self, member):
        guild = member.guild
        member_count = len(guild.members)

        if member_count % member_notification_trigger != 0:
            return

        channel = self.bot.get_channel(discord.utils.get(guild.channels, name=notification_channel_name).id)
        await channel.send('{} now has {} members! Congratulations!'.format(member.guild, member_count))

def setup(bot):
    bot.add_cog(OnMemberJoin(bot))
