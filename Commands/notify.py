from discord.ext import commands
from .serverData import get_guild_data, save_configs
import discord


class Notify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sub", aliases=["subscribe"])
    async def sub(self, ctx, list_name):
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg_string = guild_data.sub(list_name, ctx.author.id)

        await ctx.send(msg_string)

    @commands.command(name="unsub", aliases=["unsubscribe"])
    async def unsubscribe(self, ctx, list_name):
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg_string = guild_data.unsub(list_name, ctx.author.id)

        await ctx.send(msg_string)

    @commands.command(name="notify")
    async def notify(self, ctx, list_name):
        list_name = list_name.lower()

        guild_data = await get_guild_data(ctx.message.guild.id)
        msg_string = guild_data.notify(list_name)

        await ctx.send(msg_string)

    @commands.command(name="show_lists")
    async def show_lists(self, ctx):
        guild_data = await get_guild_data(ctx.message.guild.id)

        if guild_data.notification_lists:
            msg = await ctx.send(
                ", ".join(
                    [
                        v["icon"] + " - " + k
                        for k, v in guild_data.notification_lists.items()
                    ]
                )
            )
            for v in guild_data.notification_lists.values():
                await msg.add_reaction(v["icon"])

            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: reaction.message.id == msg.id
                and not user.bot,
            )

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
            for key, users_list in guild_data.notification_lists.items():
                if ctx.author.id in users_list:
                    subbed_lists.append(key)

            if len(subbed_lists) > 0:
                await ctx.send("Your lists are: " + ", ".join(subbed_lists))
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
