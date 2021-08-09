import asyncio
import typing

from discord.ext import commands

from nerdlandbot.helpers.constants import INTERACT_TIMEOUT
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.emoji import thumbs_up, thumbs_down, flags
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.commands.GuildData import get_guild_data


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="add_admin", brief="settings_add_admin_brief", usage="settings_add_admin_usage",
                      help="settings_add_admin_help")
    @commands.guild_only()
    async def add_admin(self, ctx: commands.Context):
        """
        Add a new bot admin.
        :param ctx: The current context. (discord.ext.commands.Context)
        """

        guild_data = await get_guild_data(ctx.guild.id)

        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        # Error if the command had no mention
        if not ctx.message.mentions:
            err = translate("mention_required", await culture(ctx))
            return await ctx.send(err)

        # Fetch user data
        user_id_to_add = ctx.message.mentions[0].id
        user_to_add = ctx.guild.get_member(int(user_id_to_add))
        user_name_to_add = user_to_add.display_name

        # Error if the user is a server admin (no point in giving him bot admin rights)
        if ctx.guild.get_member(int(user_id_to_add)).guild_permissions.administrator:
            err = translate("bot_admin_error_discord_admin", await culture(ctx)).format(user_name_to_add)
            return await ctx.send(err)

        # Error if the user already is a bot admin
        if ctx.message.mentions[0].id in guild_data.bot_admins:
            err = translate("bot_admin_error_already_admin", await culture(ctx)).format(user_name_to_add)
            return await ctx.send(err)

        # Actually add the user to the admins
        await guild_data.add_admin(user_id_to_add)

        # Display success
        msg = translate("bot_admin_add_success", await culture(ctx)).format(user_name_to_add)
        await ctx.send(msg)

    @commands.command(name="remove_admin", brief="settings_remove_admin_brief", usage="settings_remove_admin_usage",
                      help="settings_remove_admin_help")
    @commands.guild_only()
    async def remove_admin(self, ctx: commands.Context):
        """
        Remove a bot admin.
        :param ctx: The current context. (discord.ext.commands.Context)
        """

        guild_data = await get_guild_data(ctx.guild.id)

        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        # Error if the command had no mention
        if not ctx.message.mentions:
            err = translate("mention_required", await culture(ctx))
            return await ctx.send(err)

        # Fetch user data
        user_id_to_remove = ctx.message.mentions[0].id
        user_to_remove = ctx.guild.get_member(int(user_id_to_remove))
        user_name_to_remove = user_to_remove.display_name

        # Error if the user is not a bot admin
        if user_id_to_remove not in guild_data.bot_admins:
            err = translate("bot_admin_error_not_admin", await culture(ctx)).format(user_name_to_remove)
            return await ctx.send(err)

        # User is trying to revoke his own rights
        if ctx.author.id == user_id_to_remove:
            # Ask confirmation
            confirmation_text = translate("bot_admin_confirm_remove_self", await culture(ctx))
            confirmation_ref = await ctx.send(confirmation_text)
            await confirmation_ref.add_reaction(thumbs_up)
            await confirmation_ref.add_reaction(thumbs_down)

            # Handle user reaction
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda new_reaction, author: new_reaction.message.id == confirmation_ref.id and author == ctx.message.author,
                    timeout=INTERACT_TIMEOUT,
                )

                # Process thumbs up
                if reaction.emoji == thumbs_up:
                    await guild_data.remove_admin(user_id_to_remove)
                    msg = translate("bot_admin_remove_success", await culture(ctx)).format(user_name_to_remove)
                    return await ctx.send(msg)

                # Process thumbs down
                if reaction.emoji == thumbs_down:
                    msg = translate("bot_admin_remove_cancel", await culture(ctx)).format(user_name_to_remove)
                    return await ctx.send(msg)

                # If we reach here, an invalid emoji was used
                await confirmation_ref.delete()
                return

                # Handle timeout
            except asyncio.TimeoutError:
                await confirmation_ref.delete()
                msg = translate("snooze_lose", await culture(ctx))
                return await ctx.send(msg)

        # Authorized user wants to remove another bot admin
        # Ask confirmation
        confirmation_text = translate("bot_admin_confirm_remove", await culture(ctx)).format(user_name_to_remove)
        confirmation_ref = await ctx.send(confirmation_text)
        await confirmation_ref.add_reaction(thumbs_up)
        await confirmation_ref.add_reaction(thumbs_down)

        # Handle user reaction
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda new_reaction, author: new_reaction.message.id == confirmation_ref.id and author == ctx.message.author,
                timeout=INTERACT_TIMEOUT,
            )

            # Process thumbs up
            if reaction.emoji == thumbs_up:
                await guild_data.remove_admin(user_id_to_remove)
                msg = translate("bot_admin_remove_success", await culture(ctx)).format(user_name_to_remove)
                return await ctx.send(msg)

            # Process thumbs down
            elif reaction.emoji == thumbs_down:
                msg = translate("bot_admin_remove_cancel", await culture(ctx)).format(user_name_to_remove)
                return await ctx.send(msg)

            # If we reach here, an invalid emoji was used
            await confirmation_ref.delete()
            return

        # Handle timeout
        except asyncio.TimeoutError:
            await confirmation_ref.delete()
            msg = translate("snooze_lose", await culture(ctx))
            return await ctx.send(msg)

    @commands.command(name="bot_admins", aliases=["who_da_boss"], brief="settings_bot_admins_brief",
                      help="settings_bot_admins_help")
    @commands.guild_only()
    async def admins_bot(self, ctx: commands.Context):
        """
        Show a list of all bot admins.
        :param ctx: The current context. (discord.ext.commands.Context)
        """

        guild_data = await get_guild_data(ctx.guild.id)

        # Error if no admins found
        if not guild_data.bot_admins:
            msg = translate("bot_admin_err_no_admins", await culture(ctx))
            return await ctx.send(msg)

        # Build list
        message = translate("bot_admin_list_prefix", await culture(ctx))
        for user_id in guild_data.bot_admins:
            message += f"\n- {ctx.guild.get_member(int(user_id)).display_name}"

        # Show list
        await ctx.send(message)

    @commands.command(name="language", aliases=["translate"], brief="settings_language_brief",
                      help="settings_language_help")
    @commands.guild_only()
    async def set_language(self, ctx: commands.Context):
        """
        Show the current language, and allow for updates.
        :param ctx: The current context. (discord.ext.commands.Context)
        """

        # Get guild data
        guild_data = await get_guild_data(ctx.guild.id)

        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        # Get current language
        current_culture = await culture(ctx)

        # Show current language
        msg = translate("current_language", current_culture).format(translate(current_culture, current_culture))
        await ctx.send(msg)

        # Request new language
        confirmation_message = translate("pick_new_language", current_culture)
        confirmation_ref = await ctx.send(confirmation_message)
        for emoji in flags.values():
            await confirmation_ref.add_reaction(emoji)

        # Handle user reaction
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda new_reaction, author: new_reaction.message.id == confirmation_ref.id and author == ctx.message.author,
                timeout=INTERACT_TIMEOUT,
            )

            # Parse reaction
            new_language = None
            for lan in flags.keys():
                if flags[lan] == reaction.emoji:
                    new_language = lan
                    break

            # Update language if found
            if new_language:
                await guild_data.update_language(new_language)
                await confirmation_ref.delete()
                msg = translate("picked_new_language", new_language).format(translate(new_language, new_language))
                return await ctx.send(msg)

        # Handle timeout
        except asyncio.TimeoutError:
            await confirmation_ref.delete()
            msg = translate("snooze_lose", await culture(ctx))
            return await ctx.send(msg)

    @commands.command(name="set_member_notification_number", aliases=["new_members"], brief="settings_member_notification_number_brief",
                      help="settings_member_notification_number_help", usage="settings_member_notification_number_usage")
    @commands.guild_only()
    async def set_member_notification_number(self, ctx: commands.Context, max: typing.Optional[str]=None):
        """
        Show the current max number of users to be notified in a single message, before it is split in multiple posts.
        :param ctx: The current context. (discord.ext.commands.Context)
        """
        # Get guild data
        guild_data = await get_guild_data(ctx.guild.id)

        # Get current culture
        current_culture = await culture(ctx)

        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", current_culture)
            return await ctx.send(gif)

        # Error if no valid argument
        if not max or not max.isnumeric():
            msg = translate("set_member_notification_number_invalid_parameter", current_culture)
            return await ctx.send(msg)

        # Update value
        guild_data.member_notification_number = int(max)
        await guild_data.save()

        # Notify success
        msg = translate("set_member_notification_number_success", current_culture).format(int(max))
        await ctx.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))
