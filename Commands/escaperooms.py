import discord
import pandas as pd

from discord.ext import commands

class Escaperooms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def read_tracking_table(self) -> pd.DataFrame:
        """ Reads the Tracking Table from CSV and returns it as Pandas DF"""
        convert_dict = {'Naam': str}
        tracking_table = pd.read_csv('tracking_table.csv',dtype=convert_dict)

        tracking_table['Discord ID'] = tracking_table['Discord ID'].astype("Int64").astype(str)
        tracking_table = tracking_table.fillna(0)
        
        return tracking_table

    def write_tracking_table(self,tracking_table):
        """ Writes the Tracking Table into CSV from Pandas DF"""
        tracking_table.to_csv('tracking_table.csv',index=False)

    def register_room_play(self,discord_id,escaperoom):
        """ Register that a user has played a room """
        # TODO: add new record in case user does not yet exists in table
        tracking_table = self.read_tracking_table()

        user_row_index = tracking_table.index[tracking_table['Discord ID'] == discord_id]
        tracking_table.loc[user_row_index,escaperoom] = 1

        self.write_tracking_table(tracking_table)

    def list_users_escaperoom(self,escaperoom) -> list:
        """ Returns list of users who have played the room"""
        tracking_table = self.read_tracking_table()

        users_list = tracking_table.loc[tracking_table[escaperoom] > 0]
        users_list = users_list['Discord ID'].tolist()

        return users_list

    def list_escaperooms_user(self,discord_id) -> list:
        """ Returns list of users who have played the room"""
        tracking_table = self.read_tracking_table()
        tracking_table = tracking_table.drop(columns=['Naam','Heeft tabletop'])
        
        # Transpose table
        tracking_table = tracking_table.T
        headers = tracking_table.iloc[0]
        tracking_table = tracking_table[1:]
        tracking_table.columns = headers

        rooms_list = tracking_table.loc[tracking_table[str(discord_id)] > 0]
        rooms_list = rooms_list.index.values

        return rooms_list

    def calculate_room(self,user_list) -> str:
        """ Calculates the best room available for the users in list"""
        tracking_table = self.read_tracking_table()

        # calculate sum of each room for full userbase
        room_sums = pd.DataFrame(tracking_table.drop(columns=['Naam','Discord ID','Heeft tabletop']).sum(axis = 0, skipna = True))
        room_sums.columns = ['sum_total']

        # Filter table on current users
        subset = tracking_table.loc[tracking_table['Discord ID'].isin(user_list)]
        
        # calculate sum of each room for current users
        sub_room_sums = pd.DataFrame(subset.drop(columns=['Naam','Discord ID','Heeft tabletop']).sum(axis = 0, skipna = True))
        sub_room_sums.columns = ['sum']

        # keep only rooms not yet played by current users
        sub_room_sums = sub_room_sums[sub_room_sums['sum'] < 1]

        # join in the number of plays by the full userbase
        sub_room_sums = sub_room_sums.join(room_sums)

        # sort descending
        sub_room_sums.sort_values(by=['sum_total'],ascending=False,inplace=True)
        sub_room_sums.reset_index(level=0, inplace=True)

        # pick first room
        return sub_room_sums.loc[0][0]

    def split_group(self,user_list,is_balanced=False):
        tracking_table = self.read_tracking_table()
        
        # Clean table and transpose
        subset = tracking_table.loc[tracking_table['Discord ID'].isin(user_list)]
        subset = pd.DataFrame(subset.drop(columns=['Naam','Heeft tabletop']))
        subset = transpose_tracking_table(subset)
        
        # Calculate sum of games per user and sort
        sums = pd.DataFrame(subset.sum(axis = 0, skipna = True))
        sums.columns = ['sum']
        sums.sort_values(by=['sum'],ascending=False,inplace=True)
        
        # split groups unbalanced (in order of experience)
        groupsize = int(len(user_list) / 2)
        group1 = sums[:groupsize]
        group2 = sums[groupsize:]

        if is_balanced:
            #split groups balanced by rebuildig dataframe with alternating selection
            alternated_groups = pd.concat([group1,group2]).sort_index(kind='merge')
            group1 = alternated_groups[:groupsize]
            group2 = alternated_groups[groupsize:]
        
        return group1, group2