import discord
import asyncio
import os
from discord.ext import commands

from nerdlandbot.commands.GuildData import get_guild_data, GuildData
from nerdlandbot.helpers.channel import get_channel
from nerdlandbot.helpers.constants import NOTIFY_EMBED_COLOR, INTERACT_TIMEOUT
from nerdlandbot.helpers.emoji import thumbs_up,thumbs_down
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_id as culture_id
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture

class ModeratorFunctions(commands.Cog, name="Moderator functions"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.discord_server_id = os.getenv("DISCORD_SERVER_ID")
        self.moderator_name = os.getenv("MODERATOR_NAME")

    @commands.command(name="moderator", aliases=['mod'], 
                        brief="mod_message_brief",
                        usage="mod_message_usage",
                        help="mod_message_help")
    async def moderator(self, ctx: commands.Context,*,input_message:str = None):

        if not input_message:
            msg = translate("mod_no_message", await culture_id(int(self.discord_server_id)))
            return await ctx.send(msg)

        # Get the channel ID from the guild data
        guild_data = await get_guild_data(int(self.discord_server_id))
        mod_channel = guild_data.mod_channel
        if not mod_channel:
            msg = translate("mod_no_channel_set", await culture_id(int(self.discord_server_id)))
            return await ctx.send(msg)

        # Get the channel object from the ID
        channel = ctx.bot.get_channel(int(mod_channel))
        if not channel:
            msg = translate("mod_no_channel_set", await culture_id(int(self.discord_server_id)))
            return await ctx.send(msg)

        nerdland_guild = ctx.bot.get_guild(int(self.discord_server_id))
        moderator_role = discord.utils.find(lambda role: role.name == self.moderator_name,nerdland_guild.roles)


        if moderator_role:
            mod_message = moderator_role.mention + "\n"
        else:
            mod_message = ""
        mod_message += translate("mod_message",await culture_id(int(self.discord_server_id)))\
                        .format(ctx.author)

        mod_embed = discord.Embed(
            description=translate("mod_embed_title", await culture_id(int(self.discord_server_id))),
            color=NOTIFY_EMBED_COLOR,
        )
        mod_embed.add_field(name = "\u200b", value = input_message, inline = False)

        # Ask user confirmation
        confirmation_embed = discord.Embed(
            description=translate("mod_confirmation_intro", await culture_id(int(self.discord_server_id))),
            color=NOTIFY_EMBED_COLOR,
        )
        confirmation_embed.add_field(name="\u200b", value = input_message, inline=False)
        confirmation_embed.add_field(name="\u200b", value = translate("mod_confirmation_footer", 
                                                await culture_id(int(self.discord_server_id)))
                                                .format(thumbs_up,thumbs_down), 
                                    inline=False)

        confirmation_ref = await ctx.send(embed = confirmation_embed)
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
                await channel.send(mod_message)
                await channel.send(embed = mod_embed)
                msg = translate("mod_message_sent",await culture_id(int(self.discord_server_id)))
                await ctx.send(msg)

            elif reaction.emoji == thumbs_down:
                msg = translate("mod_message_cancel", await culture_id(int(self.discord_server_id)))
                await ctx.send(msg)

            # Delete message
            await confirmation_ref.delete()
        # Handle Timeout
        except asyncio.TimeoutError:
            await confirmation_ref.delete()
            msg = translate("snooze_lose", await culture_id(int(self.discord_server_id)))
            return await ctx.send(msg)

    @commands.command(name="set_mod_channel",aliases = ['mod_channel'],usage="set_mod_channel_usage",brief="set_mod_channel_brief", help="set_mod_channel_help")
    @commands.guild_only()
    async def set_mod_channel(self, ctx: commands.Context, mod_channel=None):

        if not ctx.guild.id == int(self.discord_server_id):
            msg = translate("mod_channel_only_nerdland", await culture(ctx))
            return await ctx.send(msg)

        guild_data = await get_guild_data(ctx.guild.id)
        if not guild_data.user_is_admin_moderator:
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)
        if not mod_channel:
            msg = translate("no_mod_channel_given", await culture(ctx))
            return await ctx.send(msg)


        channel = get_channel(ctx,mod_channel)
        if channel:
            if isinstance(channel, discord.VoiceChannel):
                msg = translate("channel_is_voice", await culture(ctx))
                return await ctx.channel.send(msg)
                
            channel_permissions = channel.permissions_for(ctx.me)
            if not (channel_permissions.send_messages):
                msg = translate("mod_channel_permisions", await culture(ctx))
                return await ctx.send(msg)
        
            await guild_data.update_mod_channel(str(channel.id))
            msg = translate("mod_channel_set", await culture(ctx)).format(channel)
            return await ctx.send(msg)
        else: 
            msg = translate("mod_channel_not_exist", await culture(ctx))
            return await ctx.send(msg)


    @commands.command(name="boodschap",aliases = ['bvan','algemeen_nut'],usage="boodschap_usage", help="boodschap_help")
    @commands.guild_only()
    async def boodschap(self, ctx: commands.Context,*,input_message:str = None):
        guild_data = await get_guild_data(ctx.guild.id)
        if not guild_data.user_is_admin_moderator:
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)
        if input_message == None:
            msg = translate("boodschap_no_message", await culture(ctx))
            return await ctx.send(msg)

        guild_data = await get_guild_data(ctx.guild.id)
        boodschap_channel = guild_data.boodschap_channel
        if not boodschap_channel:
            msg = translate("boodschap_no_channel_set", await culture(ctx))
            return await ctx.send(msg)

        # Get the channel object from the ID
        channel = ctx.bot.get_channel(int(boodschap_channel))
        if not channel:
            msg = translate("boodschap_no_channel_set", await culture(ctx))
            return await ctx.send(msg)


        # Ask user confirmation
        confirmation_embed = discord.Embed(
            description=translate("boodschap_confirmation_intro", await culture(ctx)).format(channel.id),
            color=NOTIFY_EMBED_COLOR,
        )
        confirmation_embed.add_field(name="\u200b", value = input_message, inline=False)
        confirmation_embed.add_field(name="\u200b", value = translate("boodschap_confirmation_footer", 
                                                await culture(ctx))
                                                .format(thumbs_up,thumbs_down), 
                                    inline=False)

        confirmation_ref = await ctx.send(embed = confirmation_embed)
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
                await channel.send(input_message)
                msg = translate("boodschap_message_sent",await culture(ctx)).format(channel.id)
                await ctx.send(msg)

            elif reaction.emoji == thumbs_down:
                msg = translate("boodschap_message_cancel", await culture(ctx))
                await ctx.send(msg)

            # Delete message
            await confirmation_ref.delete()
        # Handle Timeout
        except asyncio.TimeoutError:
            await confirmation_ref.delete()
            msg = translate("snooze_lose", await culture(ctx))
            return await ctx.send(msg)

    @commands.command(name="set_boodschap_channel",aliases = ['set_bvan_channel','set_algemeen_nut_channel'],usage="set_boodschap_usage",brief="set_boodschap_brief", help="set_boodschap_help")
    @commands.guild_only()
    async def set_boodschap_channel(self, ctx: commands.Context, boodschap_channel=None):
        guild_data = await get_guild_data(ctx.guild.id)
        if not guild_data.user_is_admin_moderator:
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)
        if not boodschap_channel:
            msg = translate("no_boodschap_channel_given", await culture(ctx))
            return await ctx.send(msg)


        channel = get_channel(ctx,boodschap_channel)
        if channel:
            if isinstance(channel, discord.VoiceChannel):
                msg = translate("channel_is_voice", await culture(ctx))
                return await ctx.channel.send(msg)
                
            channel_permissions = channel.permissions_for(ctx.me)
            if not (channel_permissions.send_messages):
                msg = translate("boodschap_channel_permissions", await culture(ctx))
                return await ctx.send(msg)
        
            await guild_data.update_boodschap_channel(str(channel.id))
            msg = translate("boodschap_channel_set", await culture(ctx)).format(channel)
            return await ctx.send(msg)
        else: 
            msg = translate("boodschap_channel_not_exist", await culture(ctx))
            return await ctx.send(msg)

        
def setup(bot: commands.Bot):
    bot.add_cog(ModeratorFunctions(bot))
