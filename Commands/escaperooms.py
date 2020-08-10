import discord
import pandas as pd
import re

from datetime import datetime
from discord.ext import commands
from .GuildData import get_guild_data, save_configs
import constants
from common_functions import *


class Escaperooms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def read_tracking_table(self) -> pd.DataFrame:
        """ Reads the Tracking Table from CSV and returns it as Pandas DF"""
        convert_dict = {'Naam': str}
        tracking_table = pd.read_csv(
            'EscaperoomsCSV/tracking_table.csv', dtype=convert_dict)

        tracking_table['Discord ID'] = tracking_table['Discord ID'].astype(
            "Int64").astype(str)
        tracking_table = tracking_table.fillna(0)

        return tracking_table

    def write_tracking_table(self, tracking_table):
        """ Writes the Tracking Table into CSV from Pandas DF"""
        tracking_table.to_csv('EscaperoomsCSV/tracking_table.csv', index=False)

    def transpose_tracking_table(self, tracking_table) -> pd.DataFrame:
        """Returns transposed tracking table with Usernames as columns and Rooms as rows"""
        tracking_table = tracking_table.T
        headers = tracking_table.iloc[0]
        tracking_table = tracking_table[1:]
        tracking_table.columns = headers
        return tracking_table

    def register_room_play(self, ctx, discord_id, escaperoom):
        """ Register that a user has played a room """
        tracking_table = self.read_tracking_table()

        if discord_id in tracking_table.values:
            user_row_index = tracking_table.index[tracking_table['Discord ID'] == discord_id]
        else:
            # user not yet present in table, add empty row
            tracking_table = tracking_table.append(
                pd.Series(), ignore_index=True)
            # populate name and discord ID
            tracking_table.iloc[-1,
                                tracking_table.columns.get_loc('Discord ID')] = discord_id
            tracking_table.iloc[-1, tracking_table.columns.get_loc(
                'Naam')] = ctx.guild.get_member(int(user_id)).display_name
            # fill room columns with 0
            tracking_table = tracking_table.fillna(0.0)
            user_row_index = tracking_table.index[tracking_table['Discord ID'] == discord_id]

        tracking_table.loc[user_row_index, escaperoom] = 1

        self.write_tracking_table(tracking_table)

    def list_users_escaperoom(self, escaperoom) -> list:
        """ Returns list of users who have played the room"""
        tracking_table = self.read_tracking_table()

        users_list = tracking_table.loc[tracking_table[escaperoom] > 0]
        users_list = users_list['Discord ID'].tolist()

        return users_list

    def list_escaperooms_user(self, discord_id) -> list:
        """ Returns list of room that the user has played"""
        tracking_table = self.read_tracking_table()
        tracking_table = tracking_table.drop(
            columns=['Naam', 'Heeft tabletop'])

        # Transpose table
        tracking_table = self.transpose_tracking_table(tracking_table)

        rooms_list = tracking_table.loc[tracking_table[str(discord_id)] > 0]
        rooms_list = rooms_list.index.values

        return rooms_list

    def list_escaperooms(self) -> list:
        """Returns a list of the escaperooms in the tracking table"""
        tracking_table = self.read_tracking_table()
        tracking_table = tracking_table.drop(
            columns=['Naam', 'Heeft tabletop', 'Discord ID'])
        escaperooms = list(tracking_table.columns.values)
        return escaperooms

    # def usernames_from_ids(self,ctx,list_users) -> list:
    #     usernames = []
    #     for user_id in list_users:
    #         try:
    #             # get user displayname based on ID in tracking table
    #             user = ctx.guild.get_member(int(user_id))
    #             usernames.append(user.display_name)
    #         except AttributeError:
    #             # if user not known on server, handle here
    #             print("could not find user with ID: " + user_id)
    #             pass
    #     return sorted(usernames)

    @commands.command(name="i_escaped", brief="Register that you played an escaperoom", usage="<escaperoom>", help="Register that you played escaperoom <escaperoom>")
    async def cmd_iescaped(self, ctx, *, escaperoom_name=None):
        if escaperoom_name:
            if escaperoom_name in self.list_escaperooms():
                self.register_room_play(
                    ctx, str(ctx.author.id), escaperoom_name)
                message = "Congratulation you escaped " + \
                    escaperoom_name + " and we have noted this"
            else:
                message = "but Foemp, that room does not exist!"
        else:
            escaperooms = sorted(self.list_escaperooms())
            message = "Foemp, you didn't tell me which escaperoom, here's a list:\n - " + \
                "\n- ".join(escaperooms)
        await ctx.send(message)

    @commands.command(name="where_escaped", brief="Check which escaperooms a user has played", usage="[mentioned user]", help="Without @-mention: list the escaperooms you have played.\nWith @-mention: list the escaperooms the mentioned user has played. This has to be a mention, not just a name or ID")
    async def cmd_userescaped(self, ctx, user_id=None):
        if not user_id:
            # No user mentioned, therefor set user_id to the command sender
            user_id = str(ctx.author.id)
        elif user_id[:2] == "<@":
            # Valid user id, strip special characters and only retain uder_id numbers
            user_id = re.sub("[^0-9]", "", user_id)
        else:
            # No valid user mentioned, report foemp
            await ctx.send("Please @-mention a user, Foemp.")
            return

        try:
            # collect and sort escaperooms for user and send message
            escaperooms = sorted(self.list_escaperooms_user(user_id))
            if len(escaperooms) != 0:
                message = ctx.guild.get_member(
                    int(user_id)).display_name + " has played:\n- "
                await ctx.send(message + "\n- ".join(escaperooms))
            else:
                await ctx.send("This Foemp has not played any rooms yet.")
        except KeyError:
            # user does not appear in dataframe, therefor hasn't played
            await ctx.send("This Foemp has not played any rooms yet.")

    @commands.command(name="who_escaped", brief="List the people that played the escaperoom", usage="[escaperoom name]", help="With an argument: list the people that played that escaperoom. \nWithout an argument: list all the available escaperooms.")
    async def cmd_escaperoom(self, ctx, *, escaperoom_name=None):
        if escaperoom_name:
            # escaperoom name provided, list users and report back
            try:
                list_users = self.list_users_escaperoom(escaperoom_name)
                if len(list_users) > 0:
                    usernames = usernames_from_ids(ctx, list_users)
                    message = escaperoom_name + " has been played by: " + \
                        ", ".join(usernames[:-1]) + ", and " + usernames[-1]
                else:
                    message = "No-one has played " + escaperoom_name + " yet."
                await ctx.send(message)

            except KeyError:
                # room does not exist in dataframe, send Foemp
                await ctx.send("This escaperoom does not exist, foemp!")
        else:
            # no escaperoom name provided, send back list of available rooms
            escaperooms = sorted(self.list_escaperooms())
            message = "These are the available escaperooms: \n- " + \
                "\n- ".join(escaperooms)
            await ctx.send(message)

    @commands.command(name="lets_escape", brief="set up a new escape session or get the current one", usage="[escaperoom time hh:mm]", help="With an argument: sets up a new escaperoom game at given time. \nWithout an argument: let's you know when the game is taking place.")
    async def cmd_lets_escape(self, ctx, escaperoom_time=None):
        guild_data = await get_guild_data(ctx.message.guild.id)

        # escaperoom_time provided, register new game time for today
        if escaperoom_time:
            pattern = re.compile('^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
            if pattern.match(escaperoom_time):
                now = datetime.today()
                escaperoom_datetime = datetime.strptime(escaperoom_time, '%H:%M').replace(
                    year=now.year, month=now.month, day=now.day)
                is_new_time = await guild_data.new_escaproom_game_time(escaperoom_datetime)
                if is_new_time:
                    await ctx.send("Registering game at: " + escaperoom_time + " today")
                else:
                    await ctx.send("Sorry, There's already a game scheduled today")
            else:
                await ctx.send("That's not a valid time, Foemp!")

        # no escaperoom_time provided, call when_escape
        else:
            await self.cmd_when_escape(ctx)

    @commands.command(name="when_escape", brief="check when there is an escaperoom session today", help="check when there is an escaperoom session today and register using emoji reaction")
    async def cmd_when_escape(self, ctx):
        guild_data = await get_guild_data(ctx.message.guild.id)

        if guild_data.get_datetime_escaperoom_game():
            escape_datetime = guild_data.get_datetime_escaperoom_game()
            str_escapetime = str(escape_datetime.hour) + \
                ":" + str(escape_datetime.minute)
            escapeusers = guild_data.get_users_escaperoom_game()
            message = "Escaperoom today at: **" + str_escapetime + "**"
            if len(escapeusers) > 0:
                escapeusernames = usernames_from_ids(ctx, escapeusers)
                message += "\n\nThe following players are taking part: " + \
                    ", ".join(escapeusernames)
                message += "\n\nRegister by clicking the ✅ below"
            else:
                message += ", no players registered yet.\n\nRegister by clicking the ✅ below"

            msg = await ctx.send(message)
            await msg.add_reaction("✅")
            reaction, register_user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: reaction.message.id == msg.id
                and user == ctx.message.author,
                timeout=60.0
            )
            if reaction.emoji == "✅":
                is_new_register = await guild_data.register_user_escape(register_user.id)
                if is_new_register:
                    await ctx.send("You've registered for the session")
                else:
                    await ctx.send("Already registered, dear Foemp")
        else:
            await ctx.send('No escaperoom session has been scheduled today. Schedule one with `lets_escape HH:MM`')

    def calculate_room(self, user_list) -> str:
        """ Calculates the best room available for the users in list"""
        tracking_table = self.read_tracking_table()

        # calculate sum of each room for full userbase
        room_sums = pd.DataFrame(tracking_table.drop(
            columns=['Naam', 'Discord ID', 'Heeft tabletop']).sum(axis=0, skipna=True))
        room_sums.columns = ['sum_total']

        # Filter table on current users
        subset = tracking_table.loc[tracking_table['Discord ID'].isin(
            user_list)]

        # calculate sum of each room for current users
        sub_room_sums = pd.DataFrame(subset.drop(
            columns=['Naam', 'Discord ID', 'Heeft tabletop']).sum(axis=0, skipna=True))
        sub_room_sums.columns = ['sum']

        # keep only rooms not yet played by current users
        sub_room_sums = sub_room_sums[sub_room_sums['sum'] < 1]

        # join in the number of plays by the full userbase
        sub_room_sums = sub_room_sums.join(room_sums)

        # sort descending
        sub_room_sums.sort_values(
            by=['sum_total'], ascending=False, inplace=True)
        sub_room_sums.reset_index(level=0, inplace=True)

        # pick first room
        return sub_room_sums.loc[0][0]

    def split_group(self, user_list, is_balanced=False) -> list:
        tracking_table = self.read_tracking_table()
        user_list = list(map(str, user_list))

        # Clean table and transpose
        subset = tracking_table.loc[tracking_table['Discord ID'].isin(
            user_list)]
        print(user_list)
        print(subset)
        subset = pd.DataFrame(subset.drop(columns=['Naam', 'Heeft tabletop']))
        subset = self.transpose_tracking_table(subset)

        # Calculate sum of games per user and sort
        sums = pd.DataFrame(subset.sum(axis=0, skipna=True))
        sums.columns = ['sum']
        sums.sort_values(by=['sum'], ascending=False, inplace=True)

        # split groups unbalanced (in order of experience)
        groupsize = int(len(user_list) / 2)
        group1 = sums[:groupsize]
        group2 = sums[groupsize:]

        if is_balanced:
            # split groups balanced by rebuildig dataframe with alternating selection
            alternated_groups = pd.concat(
                [group1, group2]).sort_index(kind='merge')
            group1 = alternated_groups[:groupsize]
            group2 = alternated_groups[groupsize:]

        return [group1.index.values, group2.index.values]

    @commands.command(name="start_escape", brief="Start the escaperoom group and room selection", help="let the bot figure out which room to play with the registered players")
    async def cmd_start_escape(self, ctx):
        guild_data = await get_guild_data(ctx.message.guild.id)
        escape_time = guild_data.get_datetime_escaperoom_game()
        escape_users = guild_data.get_users_escaperoom_game()

        if escape_time and escape_users:
            number_of_users = len(escape_users)
            if number_of_users > constants.ESCAPE_MIN_GROUPSIZE:
                # we have enough information to start
                embed = discord.Embed(
                    title="Escaperoom Start", description="the bot recommends the following rooms", color=0x004080)
                embed.set_thumbnail(
                    url="https://previews.123rf.com/images/arcady31/arcady311810/arcady31181000064/109268325-escape-room-vector-icon.jpg")

                await ctx.send("OK, let's see how what we can do with this group: " + ", ".join(usernames_from_ids(ctx, escape_users)))
                groups = []
                if number_of_users > constants.ESCAPE_MAX_GROUPZIZE:
                    # too many users for one game, split groups
                    msg = await ctx.send('The group is too large and needs to be split, would you like a balanced split (⚖️) or one based on experience (🏆)?')
                    await msg.add_reaction("⚖️")
                    await msg.add_reaction("🏆")
                    reaction, reaction_user = await ctx.bot.wait_for(
                        "reaction_add",
                        check=lambda reaction, user: reaction.message.id == msg.id
                        and user == ctx.message.author,
                        timeout=60.0
                    )
                    balanced = reaction.emoji == '⚖️'
                    groups = self.split_group(escape_users, balanced)
                else:
                    groups = [escape_users]

                for group in groups:
                    room = self.calculate_room(group)
                    mentions = list()
                    for user_id in group:
                        mentions.append('<@!' + str(user_id) + '>')
                    embed.add_field(name=room, value=" ".join(
                        mentions), inline=False)

                embed.set_footer(
                    text="Please register your play with the i_escaped command afterwards")
                await ctx.channel.send(embed=embed)
            else:
                # group is too small
                await ctx.send('Sorry, the group is too small. Please get more players.')
                await self.cmd_when_escape(ctx)
        elif not escape_users:
            # no users registered for the game
            await ctx.send('Sorry no players registered at the moment')
        else:
            # no time is set for the game
            await ctx.send('Sorry no game planned yet')


def setup(bot):
    bot.add_cog(Escaperooms(bot))
