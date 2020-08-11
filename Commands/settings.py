import asyncio

from discord.ext import commands
from Helpers.TranslationHelper import get_culture_from_context as culture
from Translations.Translations import get_text as translate

from .GuildData import get_guild_data


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="add_admin", brief="settings_add_admin_brief", usage="settings_add_admin_usage",
                      help="settings_add_admin_help")
    async def add_admin(self, ctx: commands.Context):
        guild_data = await get_guild_data(ctx.guild.id)

        if not guild_data.user_is_admin(ctx.author):
            # if the user is not a bot admin or server admin
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        if not ctx.message.mentions:
            # if the message has no mentions
            err = translate("mention_required", await culture(ctx))
            return await ctx.send(err)

        user_id_to_add = ctx.message.mentions[0].id
        user_to_add = ctx.guid.get_member(int(user_id_to_add))
        user_name_to_add = user_to_add.display_name

        if ctx.guild.get_member(int(user_id_to_add)).guild_permissions.administrator:
            # if the requested user is already a server admin
            err = translate("bot_admin_error_discord_admin", await culture(ctx)).format(user_name_to_add)
            return await ctx.send(err)

        if ctx.message.mentions[0].id in guild_data.bot_admins:
            # if the requested user is already an admin
            err = translate("bot_admin_error_already_admin", await culture(ctx)).format(user_name_to_add)
            return await ctx.send(err)

        await guild_data.add_admin(user_id_to_add)

        msg = translate("bot_admin_add_success", await culture(ctx)).format(user_name_to_add)
        await ctx.send(msg)

    @commands.command(name="remove_admin", brief="settings_remove_admin_brief", usage="settings_remove_admin_usage",
                      help="settings_remove_admin_help")
    async def remove_admin(self, ctx: commands.Context):
        guild_data = await get_guild_data(ctx.guild.id)

        if not guild_data.user_is_admin(ctx.author):
            # if the person to give the command is not a server or bot admin, send gif
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)
        if not ctx.message.mentions:
            # if the message has no mentions
            err = translate("mention_required", await culture(ctx))
            return await ctx.send(err)

        user_id_to_remove = ctx.message.mentions[0].id
        user_to_remove = ctx.guild.get_member(user_id_to_remove)
        user_name_to_remove = user_to_remove.display_name

        if user_id_to_remove not in guild_data.bot_admins:
            # if the user to remove is not a bot admin
            err = translate("bot_admin_error_not_admin", await culture(ctx)).format(user_name_to_remove)
            return await ctx.send(err)

        if ctx.author.id == user_id_to_remove:
            # if the user wants to remove themselves as a bot admin
            confirmation_text = translate("bot_admin_confirm_remove_self", await culture(ctx))
            msg = await ctx.send(confirmation_text)
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda new_reaction, author:
                        new_reaction.message.id == msg.id and author == ctx.message.author,
                    timeout=30.0, )

                if reaction.emoji == "👍":
                    await guild_data.remove_admin(user_id_to_remove)
                    msg = translate("bot_admin_remove_success", await culture(ctx)).format(user_name_to_remove)
                    return await ctx.send(msg)
                elif reaction.emoji == "👎":
                    msg = translate("bot_admin_remove_cancel", await culture(ctx)).format(user_name_to_remove)
                    return await ctx.send(msg)

            except asyncio.TimeoutError:
                await msg.delete()
                msg = translate("snooze_lose", await culture(ctx))
                return await ctx.send(msg)

        # if an authorized user wants to remove another bot admin
        confirmation_text = translate("bot_admin_confirm_remove", await culture(ctx)).format(user_name_to_remove)
        msg = await ctx.send(confirmation_text)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda new_reaction, author: new_reaction.message.id == msg.id and author == ctx.message.author,
                timeout=30.0,
            )
            if reaction.emoji == "👍":
                await guild_data.remove_admin(user_id_to_remove)
                msg = translate("bot_admin_remove_success", await culture(ctx)).format(user_name_to_remove)
                return await ctx.send(msg)
            elif reaction.emoji == "👎":
                msg = translate("bot_admin_remove_cancel", await culture(ctx)).format(user_name_to_remove)
                return await ctx.send(msg)

        except asyncio.TimeoutError:
            await msg.delete()
            msg = translate("snooze_lose", await culture(ctx))
            return await ctx.send(msg)

    @commands.command(name="bot_admins", aliases=["who_da_boss"], brief="settings_bot_admins_brief",
                      help="settings_bot_admins_help")
    async def admins_bot(self, ctx: commands.Context):
        guild_data = await get_guild_data(ctx.guild.id)
        if len(guild_data.bot_admins) >= 1:
            message = translate("bot_admin_list_prefix", await culture(ctx))
            for user_id in guild_data.bot_admins:
                message += f"\n- {ctx.guild.get_member(int(user_id)).display_name}"
        else:
            message = translate("bot_admin_err_no_admins", await culture(ctx))
        await ctx.send(message)


def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))
