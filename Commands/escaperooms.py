import discord
import pandas as pd
import re
import time
import asyncio
import os
import math

from datetime import datetime
from discord.ext import commands
from .GuildData import get_guild_data
from Helpers.constants import *
from Helpers.common_functions import usernames_from_ids
from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture
from Helpers.emoji import white_check_mark, scales, trophy, thumbs_down, thumbs_up
from Helpers.log import *


class Escaperooms(commands.Cog, name="Escaperooms"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def read_tracking_table(self) -> pd.DataFrame:
        """ Reads the Tracking Table from CSV and returns it as Pandas DF"""
        #Naam,Discord ID,Heeft tabletop,DummyRoom
        convert_dict = {'Naam': str}
        if os.path.exists(ESCAPE_PATH):
            tracking_table = pd.read_csv(
                ESCAPE_PATH, dtype=convert_dict)
            tracking_table['Discord ID'] = tracking_table['Discord ID'].astype(
                "Int64").astype(str)
            tracking_table = tracking_table.fillna(0)
        else:
            tracking_table = pd.DataFrame(columns=['Naam','Discord ID','Heeft tabletop','DummyRoom'])
            self.write_tracking_table(tracking_table)
        return tracking_table

    def write_tracking_table(self, tracking_table):
        """ Writes the Tracking Table into CSV from Pandas DF"""
        tracking_table.to_csv(ESCAPE_PATH, index=False)

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
                'Naam')] = ctx.guild.get_member(int(discord_id)).display_name
            # fill room columns with 0
            tracking_table = tracking_table.fillna(0.0)
            user_row_index = tracking_table.index[tracking_table['Discord ID'] == discord_id]

        tracking_table.loc[user_row_index, escaperoom] = 1

        self.write_tracking_table(tracking_table)

    def list_users_for_escaperoom(self, escaperoom) -> list:
        """ Returns list of users who have played the room"""
        tracking_table = self.read_tracking_table()

        users_list = tracking_table.loc[tracking_table[escaperoom] > 0]
        users_list = users_list['Discord ID'].tolist()

        return users_list

    def list_escaperooms_for_user(self, discord_id) -> list:
        """ Returns list of rooms that the user has played"""
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

    def add_escaperoom(self, escaperoom_name: str) -> bool:
        """ adds escaperoom with to the tracking table and writes it """
        if escaperoom_name not in self.list_escaperooms():
            tracking_table = self.read_tracking_table()
            tracking_table[escaperoom_name] = 0.0
            self.write_tracking_table(tracking_table)
            return True
        else:
            return False

    def rm_escaperoom(self, escaperoom_name: str) -> bool:
        """ removes an escaperoom from the tracking table and writes it """
        if escaperoom_name in self.list_escaperooms():
            tracking_table = self.read_tracking_table()
            tracking_table = tracking_table.drop(columns=[escaperoom_name])
            self.write_tracking_table(tracking_table)
            return True
        else:
            return False

    async def wait_for_added_reactions(self, ctx, msg, guild_data, timeout):
        """ waits for reactions on message then adds a new registration for escaperoom to guild data """
        cult = await culture(ctx)
        while True:
            try:
                reaction, register_user = await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: reaction.message.id == msg.id
                    and not user.bot,
                    timeout=30.0,
                )

                if reaction.emoji == white_check_mark:
                    is_new_register = await guild_data.register_user_escape(register_user.id)
                    if is_new_register:
                        await ctx.send(
                            translate("esc_registered", cult)
                            .format(ctx.guild.get_member(register_user.id).display_name)
                        )
                    else:
                        await ctx.send(
                            translate("esc_already_registered", cult)
                            .format(ctx.guild.get_member(register_user.id).display_name)
                        )

            except asyncio.TimeoutError:
                pass

            if time.time() > timeout:
                break

    async def wait_for_removed_reactions(self, ctx, msg, guild_data, timeout):
        """ waits for removal of reaction to message then unregisters user from escaperoom in guild date """
        cult = await culture(ctx)
        while True:
            try:
                reaction, deregister_user = await ctx.bot.wait_for(
                    "reaction_remove",
                    check=lambda reaction, user: reaction.message.id == msg.id
                    and not user.bot,
                    timeout=30.0,
                )
                if reaction.emoji == white_check_mark:
                    is_deregister = await guild_data.deregister_user_escape(
                        deregister_user.id
                    )
                    if is_deregister:
                        await ctx.send(
                            translate("esc_confirm_deregister", cult)
                            .format(ctx.guild.get_member(deregister_user.id).display_name)
                        )

            except asyncio.TimeoutError:
                pass

            if time.time() > timeout:
                break

    @commands.command(name="i_escaped", brief="esc_i_escaped_brief", usage="esc_i_escaped_usage",
                      help="esc_i_escaped_help")
    async def cmd_iescaped(self, ctx, *, escaperoom_name=None):
        cult = await culture(ctx)
        if escaperoom_name:
            if escaperoom_name in self.list_escaperooms():
                self.register_room_play(
                    ctx, str(ctx.author.id), escaperoom_name)
                message = translate("esc_congratulations",
                                    cult).format(escaperoom_name)
            else:
                message = translate("esc_no_such_room", cult)
        else:
            escaperooms = sorted(self.list_escaperooms())
            message = translate("esc_noroom_give_list", cult).format(
                "\n - ".join(escaperooms))
        await ctx.send(message)

    @commands.command(name="where_escaped", brief="esc_where_escaped_brief", usage="esc_where_escaped_usage",
                      help="esc_where_escaped_help")
    async def cmd_where_escaped(self, ctx, user_id=None):
        cult = await culture(ctx)
        if not user_id:
            # No user mentioned, therefor set user_id to the command sender
            user_id = str(ctx.author.id)
        elif user_id[:2] == "<@":
            # Valid user id, strip special characters and only retain uder_id numbers
            user_id = re.sub("[^0-9]", "", user_id)
        else:
            # No valid user mentioned, report foemp
            await ctx.send(translate("mention_required", cult))
            return

        try:
            # collect and sort escaperooms for user and send message
            escaperooms = sorted(self.list_escaperooms_for_user(user_id))
            if len(escaperooms) != 0:
                message = translate("esc_user_has_played", cult).format(
                    ctx.guild.get_member(int(user_id)).display_name,
                    "\n - ".join(escaperooms)
                )
                await ctx.send(message)
            else:
                await ctx.send(translate("esc_no_rooms_played", cult))
        except KeyError:
            # user does not appear in dataframe, therefor hasn't played
            await ctx.send(translate("esc_no_rooms_played", cult))

    @commands.command(name="who_escaped", brief="esc_who_escaped_brief", usage="esc_who_escaped_usage",
                      help="esc_where_escaped_help")
    async def cmd_who_escaped(self, ctx, *, escaperoom_name=None):
        cult = await culture(ctx)
        if escaperoom_name:
            # escaperoom name provided, list users and report back
            try:
                list_users = self.list_users_for_escaperoom(escaperoom_name)
                if len(list_users) > 0:
                    usernames = usernames_from_ids(ctx, list_users)
                    message = translate("esc_room_played", cult).format(
                        escaperoom_name,
                        ", ".join(usernames)
                    )
                else:
                    message = translate(
                        "esc_room_not_played", cult
                    ).format(escaperoom_name)
                await ctx.send(message)

            except KeyError:
                # room does not exist in dataframe, send Foemp
                await ctx.send(translate("esc_no_such_room", cult))
        else:
            # no escaperoom name provided, send back list of available rooms
            escaperooms = sorted(self.list_escaperooms())
            message = translate("esc_list_escaperooms", cult).format(
                "\n - ".join(escaperooms))
            await ctx.send(message)

    @commands.command(name="lets_escape", brief="esc_lets_escape_brief", usage="esc_lets_escape_usage",
                      help="esc_lets_escape_help")
    async def cmd_lets_escape(self, ctx, escaperoom_time=None):
        guild_data = await get_guild_data(ctx.message.guild.id)
        cult = await culture(ctx)

        # escaperoom_time provided, register new game time for today
        if escaperoom_time:
            pattern = re.compile('^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
            if pattern.match(escaperoom_time):
                now = datetime.today()
                escaperoom_datetime = datetime.strptime(escaperoom_time, '%H:%M').replace(
                    year=now.year, month=now.month, day=now.day)
                is_new_time = await guild_data.new_escaproom_game_time(escaperoom_datetime)
                if is_new_time:
                    await ctx.send(translate("esc_confirm_newtime", cult).format(escaperoom_time))
                else:
                    await ctx.send(translate("esc_already_scheduled", cult))
            else:
                await ctx.send(translate("invalid_time", cult))

        # no escaperoom_time provided, call when_escape
        else:
            await self.cmd_when_escape(ctx)

    @commands.command(name="when_escape", brief="esc_when_escape_brief", help="esc_when_escape_help")
    async def cmd_when_escape(self, ctx):
        guild_data = await get_guild_data(ctx.message.guild.id)
        cult = await culture(ctx)

        escape_datetime = guild_data.get_datetime_escaperoom_game()

        if escape_datetime:
            if escape_datetime > datetime.now():
                str_escapetime = escape_datetime.strftime('%H:%M')
                escapeusers = guild_data.get_users_escaperoom_game()
                message = translate("esc_room_today_at",
                                    cult).format(str_escapetime)
                if len(escapeusers) > 0:
                    escapeusernames = usernames_from_ids(ctx, escapeusers)
                    message += translate("esc_room_today_players", cult).format(
                        ", ".join(escapeusernames),
                        white_check_mark
                    )
                else:
                    message += translate("esc_room_today_noplayers",
                                         cult).format(white_check_mark)

                timeout = time.time() + TIMEOUT
                msg = await ctx.send(message)
                await msg.add_reaction(white_check_mark)
                reaction_added_task = asyncio.create_task(
                    self.wait_for_added_reactions(
                        ctx, msg, guild_data, timeout)
                )
                reaction_removed_task = asyncio.create_task(
                    self.wait_for_removed_reactions(
                        ctx, msg, guild_data, timeout)
                )

                await reaction_added_task
                await reaction_removed_task
                await msg.delete()

            else:
                await guild_data.clear_escaperoom_users()
                await ctx.send(translate("esc_not_scheduled", cult))
        else:
            await ctx.send(translate("esc_not_scheduled", cult))

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
        subset = pd.DataFrame(subset.drop(columns=['Naam', 'Heeft tabletop']))
        subset = self.transpose_tracking_table(subset)

        # Calculate sum of games per user and sort by number of games played
        sorted_users = pd.DataFrame(subset.sum(axis=0, skipna=True))
        sorted_users.columns = ['sum']
        sorted_users.sort_values(by=['sum'], ascending=False, inplace=True)

        no_groups = math.ceil(len(user_list)/ESCAPE_MAX_GROUPSIZE)
        groupsize = int(len(user_list) / no_groups)
        groups = []
        if not is_balanced:
            for group in range(0,no_groups-1):
                groups.append(sorted_users[group*groupsize:(group+1)*groupsize].index.values)
            groups.append(sorted_users[(no_groups-1)*groupsize:].index.values)

        elif is_balanced:
            groups = [[] for i in range(no_groups)]
            groupnumber = 0
            for user in sorted_users.index.values:
                groups[groupnumber].append(user)
                if groupnumber < no_groups-1:
                    groupnumber += 1
                else:
                    groupnumber = 0

        return groups

    @commands.command(name="start_escape", brief="esc_start_brief", help="esc_start_help")
    async def cmd_start_escape(self, ctx):
        guild_data = await get_guild_data(ctx.message.guild.id)
        cult = await culture(ctx)
        escape_time = guild_data.get_datetime_escaperoom_game()
        escape_users = guild_data.get_users_escaperoom_game()

        if escape_time and escape_users:
            number_of_users = len(escape_users)
            if number_of_users > ESCAPE_MIN_GROUPSIZE:
                # we have enough information to start
                embed = discord.Embed(
                    title=translate("esc_start_title", cult),
                    description=translate("esc_start_desc", cult),
                    color=ESCAPE_COLOUR
                )
                embed.set_thumbnail(url=ESCAPE_THUMB)

                await ctx.send(translate("esc_start_announce", cult).format(
                    ", ".join(usernames_from_ids(ctx, escape_users))))
                groups = []
                if number_of_users > ESCAPE_MAX_GROUPSIZE:
                    # too many users for one game, split groups
                    msg = await ctx.send(translate("esc_start_toolarge", cult).format(
                        scales,
                        trophy
                    ))
                    await msg.add_reaction(scales)
                    await msg.add_reaction(trophy)
                    reaction, reaction_user = await ctx.bot.wait_for(
                        "reaction_add",
                        check=lambda reaction, user: reaction.message.id == msg.id
                        and user == ctx.message.author,
                        timeout=60.0
                    )
                    balanced = reaction.emoji == scales
                    groups = self.split_group(escape_users, balanced)
                else:
                    groups = [escape_users]

                for group in groups:
                    room = self.calculate_room(group)
                    mentions = list()
                    for user_id in group:
                        mentions.append('<@!' + str(user_id) + '>')

                    embed.add_field(
                        name=room,
                        value=" ".join(mentions),
                        inline=False
                    )

                embed.set_footer(text=translate("esc_start_footer", cult))
                await ctx.channel.send(embed=embed)
            else:
                # group is too small
                await ctx.send(translate("esc_start_smallgroup", cult))
                await self.cmd_when_escape(ctx)
        elif not escape_users:
            # no users registered for the game
            await ctx.send(translate("esc_start_noplayers", cult))
        else:
            # no time is set for the game
            await ctx.send(translate("esc_start_nogame", cult))

    @commands.command(name="add_escaperoom", brief="esc_add_room_brief", usage="esc_add_room_usage", 
                      help="esc_add_room_help")
    async def cmd_add_escaperoom(self, ctx, *, escaperoom_name=None):
        guild_data = await get_guild_data(ctx.message.guild.id)
        cult = await culture(ctx)

        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        # make room lower case and strip any special characters
        escaperoom_name = escaperoom_name.lower()
        escaperoom_name = re.sub('[^A-Za-z0-9 ]+', '', escaperoom_name)

        # check if room already exists
        if escaperoom_name in self.list_escaperooms():
            message = translate("esc_err_room_exists",
                                cult).format(escaperoom_name)
            return await ctx.send(message)

        # aks user confirmation
        message = translate("esc_confirm_add_room",
                            cult).format(escaperoom_name)
        confirmation_ref = await ctx.send(message)
        await confirmation_ref.add_reaction(thumbs_up)
        await confirmation_ref.add_reaction(thumbs_down)

        # handle user reaction
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda emoji, author: emoji.message.id == confirmation_ref.id
                and author == ctx.message.author,
                timeout=30.0,
            )

            if reaction.emoji == thumbs_up:
                self.add_escaperoom(escaperoom_name)
                message = translate(
                    "esc_room_added", cult).format(escaperoom_name)
                await ctx.send(message)
            elif reaction.emoji == thumbs_down:
                message = translate("esc_room_not_added", cult)
                await ctx.send(message)

            await confirmation_ref.delete()

        except asyncio.TimeoutError:
            await confirmation_ref.delete()
            msg = translate("snooze_lose", await culture(ctx))
            return await ctx.send(msg)

    @commands.command(name="remove_escaperoom", brief="esc_rm_room_brief", usage="esc_rm_room_usage", 
                      help="esc_rm_room_help")
    async def cmd_rm_escaperoom(self, ctx, *, escaperoom_name=None):
        guild_data = await get_guild_data(ctx.message.guild.id)
        cult = await culture(ctx)

        if not guild_data.user_is_admin(ctx.author):
            gif = translate("not_admin_gif", await culture(ctx))
            return await ctx.send(gif)

        # check if room already exists
        if escaperoom_name not in self.list_escaperooms():
            message = translate("esc_no_such_room",cult)
            return await ctx.send(message)
        
        # aks user confirmation
        message = translate("esc_confirm_rm_room",
                            cult).format(escaperoom_name)
        confirmation_ref = await ctx.send(message)
        await confirmation_ref.add_reaction(thumbs_up)
        await confirmation_ref.add_reaction(thumbs_down)

        # handle user reaction
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda emoji, author: emoji.message.id == confirmation_ref.id
                and author == ctx.message.author,
                timeout=30.0,
            )

            if reaction.emoji == thumbs_up:
                self.rm_escaperoom(escaperoom_name)
                message = translate(
                    "esc_room_rmed", cult).format(escaperoom_name)
                await ctx.send(message)
            elif reaction.emoji == thumbs_down:
                message = translate("esc_room_not_rmed", cult)
                await ctx.send(message)

            await confirmation_ref.delete()

        except asyncio.TimeoutError:
            await confirmation_ref.delete()
            msg = translate("snooze_lose", await culture(ctx))
            return await ctx.send(msg)

def setup(bot):
    bot.add_cog(Escaperooms(bot))
