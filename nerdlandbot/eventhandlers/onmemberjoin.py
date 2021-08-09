import discord

from discord.ext import commands

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.commands.GuildData import get_guild_data

notification_channel_name = 'botplayground'

class OnMemberJoin(commands.Cog, name="on_member_join"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name="on_member_join")
    async def on_member_join(self, member: discord.Member):
        """
        This function is executed on every member_join event, and logs a message if a certain threshold is passed.
        :param member: The member that just joined. (discord.Member)
        """
        # Fetch server
        guild = member.guild

        # Get member count
        member_count = len(guild.members)

        # Get notification trigger
        guild_data = await get_guild_data(guild.id)
        member_notification_trigger = guild_data.member_notification_number

        # Return if count is no multiple of threshold
        if member_count % member_notification_trigger != 0:
            return

        # Send message to dedicated channel
        channel = discord.utils.get(guild.channels, name=notification_channel_name)
        culture = (await get_guild_data(member.guild.id)).culture
        msg = translate("member_join_count", culture).format(member.guild, member_count)
        await channel.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(OnMemberJoin(bot))
