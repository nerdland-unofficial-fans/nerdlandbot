import typing
import time
import asyncio
import discord

from discord.ext import commands
from .GuildData import get_guild_data, save_configs


async def main():
    task1 = asyncio.create_task(say_after(1, "hello"))

    task2 = asyncio.create_task(say_after(2, "world"))

    print(f"started at {time.strftime('%X')}")

    # Wait until both tasks are completed (should take
    # around 2 seconds.)
    await task1
    await task2

    print(f"finished at {time.strftime('%X')}")


class Notify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sub", aliases=["subscribe"], help="To subscribe")
    async def sub(self, ctx, list_name: typing.Optional[str] = None):
        if list_name:
            list_name = list_name.lower()

            guild_data = await get_guild_data(ctx.message.guild.id)
            msg_string = await guild_data.sub_user(list_name, ctx.author.id)

            await ctx.send(msg_string)
        else:
            await self.show_lists(ctx)

    @commands.command(name="unsub", aliases=["unsubscribe"])
    async def unsubscribe(self, ctx, list_name):
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg_string = guild_data.unsub_user(list_name, ctx.author.id)

        await ctx.send(msg_string)

    @commands.command(name="notify")
    async def notify(self, ctx, list_name):
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg_string = guild_data.notify(list_name)

        await ctx.send(msg_string)

    async def wait_for_added_reactions(self, ctx, msg, guild_data, timeout):
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: reaction.message.id == msg.id
                    and not user.bot,
                    timeout=30.0,
                )
                if reaction.custom_emoji:
                    reaction_emoji = reaction.emoji.id
                else:
                    reaction_emoji = reaction.emoji
                for key, v in guild_data.notification_lists.items():

                    if reaction_emoji == v["icon"]:

                        msg_string = await guild_data.sub_user(key, user.id)
                        await ctx.send(msg_string)

            except asyncio.TimeoutError:
                pass

            if time.time() > timeout:
                break

    async def wait_for_removed_reactions(self, ctx, msg, guild_data, timeout):
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_remove",
                    check=lambda reaction, user: reaction.message.id == msg.id
                    and not user.bot,
                    timeout=30.0,
                )
                if reaction.custom_emoji:
                    reaction_emoji = reaction.emoji.id
                else:
                    reaction_emoji = reaction.emoji
                for key, v in guild_data.notification_lists.items():

                    if reaction_emoji == v["icon"]:

                        msg_string = await guild_data.unsub_user(key, user.id)
                        await ctx.send(msg_string)

            except asyncio.TimeoutError:
                pass

            if time.time() > timeout:
                break

    @commands.command(name="show_lists")
    async def show_lists(self, ctx):
        guild_data = await get_guild_data(ctx.message.guild.id)

        if guild_data.notification_lists:
            text = "Lists:\n"
            text += "\n".join(
                [
                    v["icon"] + " - " + k
                    for k, v in guild_data.notification_lists.items()
                ]
            )

            msg = await ctx.send(text)
            for v in guild_data.notification_lists.values():
                await msg.add_reaction(v["icon"])

            timeout = time.time() + 60 * 5  # 5 minutes from now
            reaction_added_task = asyncio.create_task(
                self.wait_for_added_reactions(ctx, msg, guild_data, timeout)
            )
            reaction_removed_task = asyncio.create_task(
                self.wait_for_removed_reactions(ctx, msg, guild_data, timeout)
            )

            await reaction_added_task
            await reaction_removed_task
            await msg.delete()
            await ctx.channel.send("You snooze, you lose!")

            # TODO: Sub the user to the list
            # TODO: When making a list, ask the user for an emoticon
            # TODO: listen to all reactions within a certain timeframe (in a while True loop with a time.time() timer)
        else:
            await ctx.send("No lists exist yet")

    @commands.command(name="my_lists")
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

    @commands.command(name="save_config")
    async def save_config(self, ctx):
        await save_configs(ctx)
        await ctx.send("Configurations saved")


def setup(bot):
    bot.add_cog(Notify(bot))
