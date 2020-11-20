from discord.ext import commands, tasks
from .GuildData import get_all_guilds_data, get_guild_data, GuildData
from Helpers.parser import parse_channel
from Helpers.log import info, fatal
from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture
import discord
import requests
import os


class purger(commands.Cog, name="Purger_lists"):
    @commands.command(
        name="add_purger", usage="add_purger_usage", help="add_purger_help",
    )
    async def add_purger(self, ctx: commands.Context, text_channel: str, max_age: int):
        """
        Add a channel to be regularly purged.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param text_channel: The text channel that will be purged (str)
        :param max_age: The max age of messages in minutes (int)
        """
        guild_data = await get_guild_data(ctx.message.guild.id)
        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        text_channel = text_channel.lower()

        # Sanitize channel name
        text_channel = parse_channel(text_channel)

        # Retrieve channel
        channel = discord.utils.get(ctx.channel.guild.channels, name=text_channel)
        if not channel:
            channel = ctx.bot.get_channel(int(text_channel))

        # TODO: Give information to the user when the text channel does not exist
        if not channel:
            raise Exception("Invalid text channel provided")

        add_response = await guild_data.add_purger(channel, max_age)

        msg = ""
        if add_response:
            msg = translate("purger_added", await culture(ctx)).format(channel, max_age)
        else:
            msg = translate("purger_exists", await culture(ctx)).format(channel)
        info(msg)
        await ctx.send(msg)

    @commands.command(
        name="remove_purger", usage="remove_purger_usage", help="remove_purger_help",
    )
    async def remove_purger(self, ctx: commands.Context, text_channel: str):
        """
        Remove a purger channel that was being notified
        :param ctx: The current context. (discord.ext.commands.Context)
        :param text_channel: The channel where the purger is attached to (str)
        """

        guild_data = await get_guild_data(ctx.message.guild.id)
        # Error if not admin
        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        channel = discord.utils.get(ctx.channel.guild.channels, name=text_channel)
        if not channel:
            channel = ctx.bot.get_channel(int(text_channel))

        # TODO: Give information to the user when the text channel does not exist
        if not channel:
            raise Exception("Invalid text channel provided")

        remove_response = await guild_data.remove_purger(channel)
        msg = ""
        if remove_response:
            msg = translate("purger_removed", await culture(ctx)).format(channel)
        else:
            msg = translate("purger_no_exists", await culture(ctx)).format(channel)
        info(msg)
        await ctx.send(msg)

    @commands.command(
        name="list_purger", help="list_purger_help",
    )
    async def list_purger_channels(self, ctx: commands.Context):
        """
        List all purger channels that are being monitored
        """

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg = translate("purger_list_title", await culture(ctx))

        for text_channel, max_age in guild_data.purgers.items():
            # TODO translate
            msg = (
                msg
                + "\n"
                + translate("purget_list_item", await culture(ctx)).format(
                    text_channel, max_age
                )
            )
        await ctx.send(msg)


def setup(bot: commands.bot):
    bot.add_cog(purger(bot))
