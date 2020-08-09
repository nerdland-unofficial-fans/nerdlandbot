import discord
import asyncio

from discord.ext import commands
from .GuildData import get_guild_data, save_configs


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add_admin", brief="**admin-only** \n\u2003 Add a bot admin", usage="<mentioned user>", help="*admin-only* \u2003 Add a bot admin. The user will be given access to the bot commands that are labelled **admin-only**. The user will not be given the role of server admin. \n\n<mention user> \u2003 Mention the user that you want to make a bot admin.")
    async def add_admin(self, ctx, mention):
        guild_data = await get_guild_data(ctx.message.guild.id)

        if not (ctx.message.author.guild_permissions.administrator or ctx.author.id in guild_data.bot_admins):
            # if the user is not a bot admin or server admin
            await ctx.send("https://gph.is/g/4w8PDNj")
        elif not ctx.message.mentions:
            # if the message has no mentions
            await ctx.send("You should mention a user, foemp.")
            return

        user_id_to_add = ctx.message.mentions[0].id
        user_name_to_add = ctx.message.guild.get_member(
            int(user_id_to_add)).display_name
        elif ctx.message.guild.get_member(int(user_id_to_add)).guild_permissions.administrator:
            # if the requested user is already a server admin
            await ctx.send(f"{user_name_to_add} is a server admin, so no need to make them a bot admin.")
        elif ctx.message.mentions[0].id in guild_data.bot_admins:
            # if the requested user is already an admin
            await ctx.send(f"{user_name_to_add} is already a bot boss, foemp.")
        else:
            await guild_data.add_admin(user_id_to_add)
            await ctx.send(f"{user_name_to_add} is now a bot boss.")

    @commands.command(name="remove_admin", brief="**admin-only** \n\u2003 Remove a bot admin", usage="<mentioned user>", help="*admin-only* \u2003 Remove a bot admin. If the user also has the role of server admin, this role will not be revoked. \n\n<mention user> \u2003 Mention the user that you want to remove from the bot admins.")
    async def remove_admin(self, ctx, mention):
        guild_data = await get_guild_data(ctx.message.guild.id)

        if not (ctx.message.author.guild_permissions.administrator or ctx.author.id in guild_data.bot_admins):
            # if the person to give the command is not a server or bot admin, send gif
            await ctx.send("https://gph.is/g/4w8PDNj")
        elif not ctx.message.mentions:
            # if the message has no mentions
            await ctx.send("You should mention a user, foemp.")
            return

        user_id_to_remove = ctx.message.mentions[0].id
        user_name_to_remove = ctx.message.guild.get_member(
            int(user_id_to_remove)).display_name
        if user_id_to_remove not in guild_data.bot_admins:
            # if the user to remove is not a bot admin
            await ctx.send(f"{user_name_to_remove} is not a bot admin, foemp.")
        elif ctx.author.id == user_id_to_remove:
            # if the user wants to remove themselves as a bot admin
            msg = await ctx.send("Are you sure you want to remove yourself as a bot admin?")
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", check=lambda reaction, user: reaction.message.id == msg.id and user == ctx.message.author, timeout=30.0,)
                if reaction.emoji == "👍":
                    await guild_data.remove_admin(user_id_to_remove)
                    await ctx.send(f"{user_name_to_remove} is no longer a bot admin.")
                elif reaction.emoji == "👎":
                    await ctx.send(f"{user_name_to_remove} won't be removed as a bot admin.")
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.send("You snooze, you lose!")
                pass
        else:
            # if an authorized user wants to remove another bot admin
            msg = await ctx.send(f"Are you sure you want to remove {user_name_to_remove} as a bot admin?")
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", check=lambda reaction, user: reaction.message.id == msg.id and user == ctx.message.author, timeout=30.0,)
                if reaction.emoji == "👍":
                    await guild_data.remove_admin(user_id_to_remove)
                    await ctx.send(f"{user_name_to_remove} is no longer a bot admin.")
                elif reaction.emoji == "👎":
                    await ctx.send(f"{user_name_to_remove} won't be removed as a bot admin.")
            except asyncio.TimeoutError:
                # TODO add option to delete message or not
                await msg.delete()
                await ctx.send("You snooze, you lose!")
                pass

    @commands.command(name="bot_admins", aliases=["who_da_boss"], brief="List the bot admins", help="List the current bot admins. Bot admins can use the **admin-only** commands, but do not have the role of server admin.")
    async def bosses(self, ctx):
        guild_data = await get_guild_data(ctx.message.guild.id)
        message = "The bot admins are:"
        for user_id in guild_data.bot_admins:
            message += f"\n- {ctx.message.guild.get_member(int(user_id)).display_name}"
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Settings(bot))
