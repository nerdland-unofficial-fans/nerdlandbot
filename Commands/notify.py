import asyncio
import time
import typing
import discord

from discord.ext import commands
from .GuildData import get_guild_data, GuildData
from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture
from Helpers.emoji import get_custom_emoji


async def wait_for_added_reactions(ctx: commands.Context, msg: discord.Message, guild_data: GuildData, timeout: int):
    while True:
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda new_reaction, author: new_reaction.message.id == msg.id and not author.bot,
                timeout=30.0,
            )

            if reaction.custom_emoji:
                reaction_emoji = str(reaction.emoji.id)
            else:
                reaction_emoji = reaction.emoji

            for list_name, list_data in guild_data.notification_lists.items():

                if reaction_emoji == list_data["emoji"]:
                    msg_string = await guild_data.sub_user(list_name, user.id)
                    await ctx.send(msg_string)

        except asyncio.TimeoutError:
            pass

        if time.time() > timeout:
            break


async def wait_for_removed_reactions(ctx: commands.Context, msg: discord.Message, guild_data: GuildData, timeout: int):
    while True:
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_remove",
                check=lambda new_reaction, author: new_reaction.message.id == msg.id and not author.bot,
                timeout=30.0,
            )

            if reaction.custom_emoji:
                reaction_emoji = str(reaction.emoji.id)
            else:
                reaction_emoji = reaction.emoji

            for list_name, list_data in guild_data.notification_lists.items():
                if reaction_emoji == list_data["emoji"]:
                    msg_string = await guild_data.unsub_user(list_name, user.id)
                    await ctx.send(msg_string)

        except asyncio.TimeoutError:
            pass

        if time.time() > timeout:
            break


class Notify(commands.Cog, name="Notification_lists"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="sub", aliases=["subscribe"], brief="notify_sub_brief", usage="notify_sub_usage",
                      help="notify_sub_help")
    async def sub(self, ctx: commands.Context, list_name: typing.Optional[str] = None):
        if list_name:
            list_name = list_name.lower()

            guild_data = await get_guild_data(ctx.message.guild.id)
            msg_string = await guild_data.sub_user(list_name, ctx.author.id)

            await ctx.send(msg_string)
        else:
            await self.show_lists(ctx)

    @commands.command(name="unsub", aliases=["unsubscribe"], brief="notify_unsub_brief", usage="notify_unsub_usage",
                      help="notify_unsub_help")
    async def unsubscribe(self, ctx: commands.Context, list_name:str):
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg_string = await guild_data.unsub_user(list_name, ctx.author.id)

        await ctx.send(msg_string)

    @commands.command(name="notify", brief="notify_notify_brief", usage="notify_notify_usage",
                      help="notify_notify_help")
    async def notify(self, ctx: commands.Context, list_name:str):
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg_string = guild_data.notify(list_name)

        await ctx.send(msg_string)

    @commands.command(name="show_lists", brief="notify_show_lists_brief", help="notify_show_lists_help")
    async def show_lists(self, ctx: commands.Context):
        guild_data = await get_guild_data(ctx.message.guild.id)

        if guild_data.notification_lists:
            text = translate("lists", await culture(ctx)) + ":\n"

            for list_name, list_data in guild_data.notification_lists.items():
                if list_data["is_custom_emoji"]:
                    emoji = get_custom_emoji(ctx, list_data["emoji"])
                else:
                    emoji = list_data["emoji"]

                text += f'\n{emoji}-{list_name}'

            msg = await ctx.send(text)

            for v in guild_data.notification_lists.values():
                await msg.add_reaction(v["emoji"] if not v["is_custom_emoji"] else ctx.bot.get_emoji(int(v["emoji"])))

            # TODO make reaction time configurable
            timeout = time.time() + 60 * 5  # 5 minutes from now
            reaction_added_task = asyncio.create_task(
                wait_for_added_reactions(ctx, msg, guild_data, timeout)
            )
            reaction_removed_task = asyncio.create_task(
                wait_for_removed_reactions(ctx, msg, guild_data, timeout)
            )

            await reaction_added_task
            await reaction_removed_task
            await msg.delete()
            # TODO give option to send a message after delete, or just stay silent?

        else:
            msg = translate("no_existing_lists", await culture(ctx))
            await ctx.send(msg)

    @commands.command(name="my_lists", help="notify_my_lists_help")
    async def my_lists(self, ctx: commands.Context):
        guild_data = await get_guild_data(ctx.message.guild.id)
        subbed_lists = []

        if guild_data.notification_lists:
            for key, notification_list in guild_data.notification_lists.items():
                if ctx.author.id in notification_list["users"]:
                    subbed_lists.append(key)

            if len(subbed_lists) > 0:
                text = translate("your_lists_title", await culture(ctx)) + ":\n - "
                text += "\n - ".join(subbed_lists)
                await ctx.send(text)
            else:
                msg = translate("no_subscriptions_error", await culture(ctx))
                await ctx.send(msg)
        else:
            msg = translate("no_existing_lists", await culture(ctx))
            await ctx.send(msg)

    @commands.command(name="add_list", brief="notify_add_list_brief", usage="notify_add_list_usage",
                      help="notify_add_list_help")
    async def add_list(self, ctx: commands.command(), list_name: str):
        guild_data = await get_guild_data(ctx.message.guild.id)

        # if not admin --> show gif
        if not guild_data.user_is_admin(ctx.author):
            msg = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(msg)

        list_name = list_name.lower()
        guild_data = await get_guild_data(ctx.message.guild.id)

        if list_name in guild_data.notification_lists.keys():
            msg = translate("list_already_exists", await culture(ctx)).format(list_name)
            return await ctx.send(msg)

        msg = translate("list_emoji_request", await culture(ctx)).format(list_name)
        emoji = await ctx.send(msg)
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda new_reaction, author: new_reaction.message.id == emoji.id and author == ctx.message.author,
                timeout=30.0,
            )

            if reaction.custom_emoji:
                try:
                    reaction_emoji = reaction.emoji.id
                    emoji_to_print = get_custom_emoji(ctx, reaction_emoji)
                    is_custom_emoji = True
                except AttributeError:
                    msg = translate("unknown_emoji", await culture(ctx))
                    return await ctx.send(msg)

            else:
                reaction_emoji = reaction.emoji
                emoji_to_print = str(reaction_emoji)
                is_custom_emoji = False

            emoji_exists = False
            for list_name, list_data in guild_data.notification_lists.items():
                if reaction_emoji == list_data["emoji"]:
                    emoji_exists = True
                    break

            if emoji_exists:
                msg = translate("emoji_already_in_use", await culture(ctx))
                await ctx.send(msg)
            else:
                await guild_data.add_notification_list(list_name, reaction_emoji, is_custom_emoji)
                msg = translate("add_list_success", await culture(ctx)).format(list_name, emoji_to_print)
                await ctx.send(msg)

        except asyncio.TimeoutError:
            pass

    @commands.command(name="remove_list", brief="notify_remove_list_brief", usage='notify_remove_list_usage',
                      help="notify_remove_list_help")
    async def remove_list(self, ctx: commands.Context, list_name: str):
        guild_data = await get_guild_data(ctx.message.guild.id)

        if not guild_data.user_is_admin(ctx.author):
            msg = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(msg)

        list_name = list_name.lower()

        if list_name not in guild_data.notification_lists.keys():
            msg = translate("list_err_does_not_exit", await culture(ctx))
            return await ctx.send(msg)

        msg_text = translate("confirmation_question", await culture(ctx))
        msg = await ctx.send(msg_text)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda new_reaction, author: new_reaction.message.id == msg.id and author == ctx.message.author,
                timeout=30.0,
            )

            if reaction.emoji == "👍":
                await guild_data.remove_notification_list(list_name)
                msg = translate("remove_list_success", await culture(ctx)).format(list_name)
            elif reaction.emoji == "👎":
                msg = translate("remove_list_cancel", await culture(ctx)).format(list_name)

            await ctx.send(msg)
            await msg.delete()

        except asyncio.TimeoutError:
            # TODO add option to delete message or not
            await msg.delete()
            msg = translate("snooze_lose", await culture(ctx))
            await ctx.send(msg)
            pass


def setup(bot: commands.Bot):
    bot.add_cog(Notify(bot))
