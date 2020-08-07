import asyncio
import time
import typing

from discord.ext import commands
from .GuildData import get_guild_data



class Notify(commands.Cog, name="Notification_lists"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sub", aliases=["subscribe"], brief="Subscribe to one or more list(s)", usage="[list name]", help="Subscribe to list(s)\n\nWithout a list name: you get an overview of all the lists with the corresponding emoji's. \nClick the emoji to subscribe to the corresponding list. \nClick the emoji again to unsubscribe from the corresponding list.\n\n With a list name: you will be subscribed to that list.")
    async def sub(self, ctx, list_name: typing.Optional[str] = None):
        if list_name:
            list_name = list_name.lower()

            guild_data = await get_guild_data(ctx.message.guild.id)
            msg_string = await guild_data.sub_user(list_name, ctx.author.id)

            await ctx.send(msg_string)
        else:
            await self.show_lists(ctx)

    @commands.command(name="unsub", aliases=["unsubscribe"], brief="Unsubscribe from a list", usage="<list name>", help="Unsubscribe from a list \n\n<list name> \u2003 The name of the list to unsubscribe from.")
    async def unsubscribe(self, ctx, list_name):
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg_string = await guild_data.unsub_user(list_name, ctx.author.id)

        await ctx.send(msg_string)

    @commands.command(name="notify")
    async def notify(self, ctx, *, message):
        list_name = message.split(" ")[0].lower()

        guild_data = await get_guild_data(ctx.message.guild.id)

        # check if list exists
        if guild_data.does_list_exist(list_name):
            # list exists, pull users from guild_data and check if there are users in the list
            users = guild_data.get_users_list(list_name)
            if len(users) > 0:
                # build users mentioning string
                users_str = ""
                for user_id in users:
                    users_str += " <@" + str(user_id) + ">"

                # send list name and the person that gave the command
                firstline = f"**{list_name.capitalize()}** notified by <@{ctx.message.author.id}>"
                # check if a message was given with the command
                if len(message.split()) > 1:
                    # message given, send message and mention users
                    message_text = firstline + " with message:\n\n" + " ".join(message.split(" ")[1:]) + "\n\n"
                else:
                    # no message given, just mention users
                    message_text = firstline + "\n\n"

                await ctx.send(message_text + users_str)

            # no users in the list
            else:
                await ctx.send(f"{list_name.capitalize()} has no members yet.")
        # list does not exist
        else:
            await ctx.send("That list does not exist, foemp.")

    async def wait_for_added_reactions(self, ctx, msg, guild_data, timeout):
        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", check=lambda reaction, user: reaction.message.id == msg.id and not user.bot, timeout=30.0,)

                if reaction.custom_emoji:
                    reaction_emoji = str(reaction.emoji.id)
                else:
                    reaction_emoji = reaction.emoji

                for key, v in guild_data.notification_lists.items():

                    if reaction_emoji == v["emoji"]:

                        msg_string = await guild_data.sub_user(key, user.id)
                        await ctx.send(msg_string)

            except asyncio.TimeoutError:
                pass

            if time.time() > timeout:
                break

    async def wait_for_removed_reactions(self, ctx, msg, guild_data, timeout):
        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_remove", check=lambda reaction, user: reaction.message.id == msg.id and not user.bot, timeout=30.0,)
                if reaction.custom_emoji:
                    reaction_emoji = str(reaction.emoji.id)
                else:
                    reaction_emoji = reaction.emoji
                for key, v in guild_data.notification_lists.items():

                    if reaction_emoji == v["emoji"]:

                        msg_string = await guild_data.unsub_user(key, user.id)
                        await ctx.send(msg_string)

            except asyncio.TimeoutError:
                pass

            if time.time() > timeout:
                break

    @commands.command(name="show_lists", brief="Show all the existing lists", help="Show all the lists with the corresponding emoji's. \nClick the emoji to subscribe to the specific list. \nClick the emoji again to unsubscribe from the specific list.")
    async def show_lists(self, ctx):
        guild_data = await get_guild_data(ctx.message.guild.id)

        if guild_data.notification_lists:
            text = "Lists:\n"
            for k, v in guild_data.notification_lists.items():
                if v["is_custom_emoji"]:
                    # TODO: Extract to 'get_custom_emoji' method for reusability
                    text += "\n<:" + ctx.bot.get_emoji(int(v["emoji"])).name + ":" + v["emoji"] + "> - " + k
                else:
                    text += "\n" + v["emoji"] + " - " + k

            msg = await ctx.send(text)
            for v in guild_data.notification_lists.values():
                await msg.add_reaction(v["emoji"] if not v["is_custom_emoji"] else ctx.bot.get_emoji(int(v["emoji"])))

            # TODO make reaction time configurable
            timeout = time.time() + 60 * 5  # 5 minutes from now
            reaction_added_task = asyncio.create_task(self.wait_for_added_reactions(ctx, msg, guild_data, timeout))
            reaction_removed_task = asyncio.create_task(self.wait_for_removed_reactions(ctx, msg, guild_data, timeout))

            await reaction_added_task
            await reaction_removed_task
            await msg.delete()
            # TODO give option to send a message after delete, or just stay silent?

        else:
            await ctx.send("No lists exist yet")

    @commands.command(name="my_lists", help="Get an overview of the lists you are subscribed to")
    async def my_lists(self, ctx):
        guild_data = await get_guild_data(ctx.message.guild.id)
        subbed_lists = []

        if guild_data.notification_lists:
            for key, notification_list in guild_data.notification_lists.items():
                if ctx.author.id in notification_list["users"]:
                    subbed_lists.append(key)

            if len(subbed_lists) > 0:

                text = "Your lists are:\n - "
                text += "\n - ".join(subbed_lists)
                await ctx.send(text)
            else:
                await ctx.send("You are not subscribed to any lists.")
        else:
            await ctx.send("No lists exist yet")

    @commands.command(name="add_list", brief="**admin-only** \n\u2003 Add a new list", usage='<list name>', help="*admin-only* \u2003 Add a new list. \n You will be asked what emoji to use for this list. React to the question of the bot with an emoji that is not yet used for another list. \n\n <list name> \u2003 The name of the list to add.")
    async def add_list(self, ctx, list_name):
        guild_data = await get_guild_data(ctx.message.guild.id)
        if not guild_data.user_is_admin(ctx.author):
            await ctx.send("https://gph.is/g/4w8PDNj")
            return
        list_name = list_name.lower()
        guild_data = await get_guild_data(ctx.message.guild.id)

        if list_name in guild_data.notification_lists.keys():
            await ctx.send(list_name + " already exists, foemp")
            # TODO: foemp mode
        else:
            msg = await ctx.send("What emoji do you want to use for " + list_name + " ?")
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", check=lambda reaction, user: reaction.message.id == msg.id and user == ctx.message.author, timeout=30.0,)
                if reaction.custom_emoji:
                    try:
                        reaction_emoji = reaction.emoji.id
                        emoji_to_print = (
                            "<:"
                            + ctx.bot.get_emoji(reaction_emoji).name
                            + ":"
                            + str(reaction_emoji)
                            + ">"
                        )
                        custom_emoji = True
                    except AttributeError:
                        await ctx.send("Emoji not recognized, try again with a standard emoji or a custom emoji from this server")
                        return
                else:
                    reaction_emoji = reaction.emoji
                    emoji_to_print = str(reaction_emoji)
                    custom_emoji = False

                emoji_exists = False
                for key, v in guild_data.notification_lists.items():
                    if reaction_emoji == v["emoji"]:
                        emoji_exists = True

                if emoji_exists:
                    await ctx.send("This emoji is already used for a list, foemp")
                else:
                    await guild_data.add_notification_list(list_name, reaction_emoji, custom_emoji)
                    await ctx.send("The list `" + list_name + "` is saved with the emoji " + emoji_to_print)

            except asyncio.TimeoutError:
                pass

    @commands.command(name="remove_list", brief="**admin-only** \n\u2003 Remove a list", usage='<list name>', help="*admin-only* \u2003 Remove a list. \n\n <list name> \u2003 The name of the list to remove.")
    async def remove_list(self, ctx, list_name):
        guild_data = await get_guild_data(ctx.message.guild.id)
        if not guild_data.user_is_admin(ctx.author):
            await ctx.send("https://gph.is/g/4w8PDNj")
            return
        list_name = list_name.lower()
        guild_data = await get_guild_data(ctx.message.guild.id)

        if list_name not in guild_data.notification_lists.keys():
            await ctx.send("No such list, foemp.")
        else:
            msg = await ctx.send("Are you sure?")
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", check=lambda reaction, user: reaction.message.id == msg.id and user == ctx.message.author, timeout=30.0,)
                if reaction.emoji == "👍":
                    await guild_data.remove_notification_list(list_name)
                    await ctx.send("The list `" + list_name + "` is removed")
                elif reaction.emoji == "👎":
                    await ctx.send(list_name + " won't be removed.")
                await msg.delete()

            except asyncio.TimeoutError:
                # TODO add option to delete message or not
                await msg.delete()
                await ctx.send("You snooze, you lose!")
                pass


def setup(bot):
    bot.add_cog(Notify(bot))
