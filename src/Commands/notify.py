from discord.ext import commands
from .serverData import load_guild_config, save_configs
import discord


class Notify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sub", aliases=["subscribe"])
    async def sub(self, ctx, list_name):
        list_name = list_name.lower()

        config = await load_guild_config(ctx)

        if list_name not in config.notification_lists.keys():
            await ctx.send("This list does not exist")
            # TODO: print lists with reactions to sub
        elif ctx.author.id in config.notification_lists[list_name]:
            await ctx.send("You are already subscribed to this list")
        else:
            config.notification_lists[list_name].append(ctx.author.id)
            config.guild_changed = True

            await ctx.send("Subscribed " + ctx.author.nick + " to " + list_name)

    @commands.command(name="unsub", aliases=["unsubscribe"])
    async def unsubscribe(self, ctx, list_name):
        list_name = list_name.lower()

        config = await load_guild_config(ctx)

        if list_name not in config.notification_lists.keys():
            await ctx.Send("That list does not seem to exist, cannot unsubscribe")
        else:
            if ctx.author.id in config.notification_lists[list_name]:
                config.notification_lists[list_name].remove(ctx.author.id)
                config.guild_changed = True

                await ctx.send("Unsubscribed " + ctx.author.nick + " from " + list_name)
            else:
                await ctx.Send("You dont seem to be subscribed to this list")

    @commands.command(name="notify")
    async def notify(self, ctx, list_name):
        list_name = list_name.lower()

        config = await load_guild_config(ctx)

        if list_name not in config.notification_lists.keys():
            await ctx.send("That list does not seem to exist")
        else:
            if config.notification_lists[list_name]:
                mentionList = [
                    "<@" + str(id) + ">" for id in config.notification_lists[list_name]
                ]
                await ctx.send("Notifying " + ", ".join(mentionList))
            else:
                await ctx.send("Nobody to notify")

    @commands.command(name="show_lists")
    async def show_lists(self, ctx):
        config = await load_guild_config(ctx)

        if config.notification_lists:
            msg = await ctx.send(
                ", ".join(
                    [
                        v["icon"] + " - " + k
                        for k, v in config.notification_lists.items()
                    ]
                )
            )
            for v in config.notification_lists.values():
                await msg.add_reaction(v["icon"])

            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: reaction.message.id == msg.id
                and not user.bot,
            )

            # Todo: Sub the user to the list
            # Todo: When making a list, ask the user for an emoticon
            # Todo: listen to all reactions within a certain timeframe (in a while True loop with a time.time() timer)
        else:
            await ctx.send("No lists exist yet")

    @commands.command(name="my_lists")
    async def my_lists(self, ctx):
        config = await load_guild_config(ctx)
        subbed_lists = []

        if config.notification_lists:
            for key, users_list in config.notification_lists.items():
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
