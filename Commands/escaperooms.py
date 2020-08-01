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

    def increment_user(self,discord_id,escaperoom):
        """ Increments the numer of times a player has played
        an escapreoom with 1 """
        # TODO: add new record in case user does not yet exists in table
        tracking_table = self.read_tracking_table()

        user_row_index = tracking_table.index[tracking_table['Discord ID'] == discord_id]
        tracking_table.loc[user_row_index,escaperoom] += 1

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
