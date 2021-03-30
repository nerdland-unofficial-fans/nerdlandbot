import discord
import asyncio

from discord.ext import commands

from nerdlandbot.commands.GuildData import get_guild_data, GuildData
from nerdlandbot.helpers.channel import get_channel
from nerdlandbot.helpers.constants import NERDLAND_SERVER_ID, MODERATOR_NAME, NOTIFY_EMBED_COLOR, INTERACT_TIMEOUT
from nerdlandbot.helpers.emoji import thumbs_up,thumbs_down
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_id as culture_id
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture_ctx

class AlertModerator(commands.Cog, name="Alert_Moderator"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="moderator", aliases=['mod'], 
                        brief="mod_message_brief",
                        usage="mod_message_usage",
                        help="mod_message_help")
    async def moderator(self, ctx: commands.Context,*,input_message:str = None):

        if not input_message:
            msg = translate("mod_no_message", await culture_id(int(NERDLAND_SERVER_ID)))
            return await ctx.send(msg)
        
        guild_data = await get_guild_data(int(NERDLAND_SERVER_ID))
        mod_channel = guild_data.mod_channel

        recipients = []
        if mod_channel == 'DM':
            nerdland_guild = ctx.bot.get_guild(int(NERDLAND_SERVER_ID))
            moderator_role = discord.utils.find(lambda role: role.name == MODERATOR_NAME,nerdland_guild.roles)
            ##TODO: Not sure how long this will take for the nerdland server with 6000 members. Maybe disable the DM option?
            for member in nerdland_guild.members:
                if moderator_role in member.roles:
                    recipients.append(member)

        elif mod_channel.isnumeric():
            channel = ctx.bot.get_channel(int(mod_channel))
            if channel:
                recipients.append(channel)
            else:
                msg = translate("mod_channel_not_exist", await culture_ctx(ctx))
                return await ctx.send(msg)

        else: 
            msg = translate("mod_no_channel_set", await culture_id(int(NERDLAND_SERVER_ID)))
            return await ctx.send(msg)


        mod_message = translate("mod_message",await culture_id(int(NERDLAND_SERVER_ID))).format(ctx.author,input_message)

        # Ask user confirmation
        msg = translate("mod_confirmation_question", await culture_id(int(NERDLAND_SERVER_ID)))\
                    .format(input_message, thumbs_up,thumbs_down)
        embed = discord.Embed(
            description=msg,
            color=NOTIFY_EMBED_COLOR,
        )
        confirmation_ref = await ctx.send(embed = embed)
        await confirmation_ref.add_reaction(thumbs_up)
        await confirmation_ref.add_reaction(thumbs_down)

        # Handle user reaction
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda emoji, author: emoji.message.id == confirmation_ref.id and author == ctx.message.author,
                timeout=INTERACT_TIMEOUT,
            )

            # Process emoji
            if reaction.emoji == thumbs_up:
                for recipient in recipients:
                    await recipient.send(mod_message)
                msg = translate("mod_message_sent",await culture_id(int(NERDLAND_SERVER_ID)))
                await ctx.send(msg)

            elif reaction.emoji == thumbs_down:
                msg = translate("remove_list_cancel", await culture_id(int(NERDLAND_SERVER_ID))).format(list_name)
                await ctx.send(msg)

            # Delete message
            await confirmation_ref.delete()
        # Handle Timeout
        except asyncio.TimeoutError:
            await confirmation_ref.delete()
            msg = translate("snooze_lose", await culture_id(int(NERDLAND_SERVER_ID)))
            return await ctx.send(msg)

    @commands.command(name="set_mod_channel",usage="add_mod_channel_usage",brief="add_mod_channel_brief", help="add_mod_channel_help")
    @commands.guild_only()
    async def set_mod_channel(self, ctx: commands.Context, mod_channel=None):
        if not ctx.guild.id == int(NERDLAND_SERVER_ID):
            msg = translate("mod_channel_only_nerdland", await culture_ctx(ctx))
            return await ctx.send('This is only for the nerdland server') ##TODO: fix translation

        guild_data = await get_guild_data(ctx)
        if not guild_data.user_is_botslet:
            gif = translate("not_admin_gif", await culture_ctx(ctx))
            return await ctx.send(gif)
        if not mod_channel:
            msg = translate("no_mod_channel", await culture_ctx(ctx))
            return await ctx.send(msg)


        channel = get_channel(ctx,mod_channel)
        if channel:
            if isinstance(channel, discord.VoiceChannel):
                msg = translate("channel_is_voice", await culture_ctx(ctx))
                return await ctx.channel.send(msg)
                
            channel_permissions = channel.permissions_for(ctx.me)
            if not (channel_permissions.send_messages):
                msg = translate("mod_channel_permisions", await culture_ctx(ctx))
                return await ctx.send(msg)
        
            await guild_data.update_mod_channel(str(channel.id))
            msg = translate("mod_channel_set", await culture_ctx(ctx)).format(channel)
            return await ctx.send(msg)
        elif mod_channel == 'DM':
            msg = translate("mod_channel_set", await culture_ctx(ctx)).format(mod_channel)
            return await ctx.send(msg)
        else: 
            msg = translate("mod_channel_not_exist", await culture_ctx(ctx))
            return await ctx.send(msg)

def setup(bot: commands.Bot):
    bot.add_cog(AlertModerator(bot))
