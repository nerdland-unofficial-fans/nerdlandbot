import discord
from discord.ext import commands
from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture

notification_channel_name = 'botplayground'
member_notification_trigger = 100


class OnMemberJoin(commands.Cog, name="on_member_join"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name="on_member_join")
    async def on_member_join(self, ctx: commands.Context, member: discord.Member):
        """
        This function is executed on every member_join event, and logs a message if a certain threshold is passed.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param member: The member that just joined. (discord.Member)
        """
        # Fetch server
        guild = member.guild

        # Get member count
        member_count = len(guild.members)

        # Return if count is no multiple of threshold
        if member_count % member_notification_trigger != 0:
            return

        # Send message to dedicated channel
        channel = self.bot.get_channel(discord.utils.get(guild.channels, name=notification_channel_name).id)
        msg = translate("member_join_count", await culture(ctx)).format(member.guild, member_count)
        await channel.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(OnMemberJoin(bot))
