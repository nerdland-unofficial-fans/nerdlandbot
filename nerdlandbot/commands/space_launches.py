import aiohttp
import asyncio
import json
import os
import discord
from datetime import datetime
from discord.ext import commands
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture

from nerdlandbot.helpers.constants import THE_SPACE_DEVS_BASE_URL, THE_SPACE_DEVS_VERSION, THE_SPACE_DEVS_LIMIT_TO_10_RESULTS
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_HOME_URL, NOTIFY_EMBED_COLOR
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_UPCOMING_LAUNCH_RESOURCE
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_LOCAL_CACHE_SPACE_LAUNCHES_FILE, THE_SPACE_DEVS_LOCAL_CACHE_FOLDER, THE_SPACE_DEVS_TIMESTAMP_FORMAT

class SpaceDevs (commands.Cog, name='Space'):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        self.cache_of_space_launches_json_path = os.path.join(THE_SPACE_DEVS_LOCAL_CACHE_FOLDER, THE_SPACE_DEVS_LOCAL_CACHE_SPACE_LAUNCHES_FILE + '.json')
        self.cache_of_space_launches_time_path = os.path.join (THE_SPACE_DEVS_LOCAL_CACHE_FOLDER, THE_SPACE_DEVS_LOCAL_CACHE_SPACE_LAUNCHES_FILE + '.time')
        if not os.path.isdir(THE_SPACE_DEVS_LOCAL_CACHE_FOLDER):
            os.makedirs(THE_SPACE_DEVS_LOCAL_CACHE_FOLDER)

    @commands.command(name="space_launches", hidden = False, help="space_launches_help", brief="space_launches_brief")
    @commands.guild_only()
    async def cmd_space_launches(self, ctx:commands.Context):
        full_url = '/'.join ([THE_SPACE_DEVS_BASE_URL, THE_SPACE_DEVS_VERSION, '/'.join (THE_SPACE_DEVS_UPCOMING_LAUNCH_RESOURCE),THE_SPACE_DEVS_LIMIT_TO_10_RESULTS])
        if self.should_call_the_api ():
            async with aiohttp.ClientSession() as session:
                async with session.get(full_url, headers = {"accept":"application/json"}) as resp: 
                    if resp.status == 200:
                        msg = await resp.text()
                        with open(self.cache_of_space_launches_json_path,"w") as file:
                            file.write(msg)
                        with open(self.cache_of_space_launches_time_path,"w") as file:
                            timestamp = datetime.now().strftime(THE_SPACE_DEVS_TIMESTAMP_FORMAT)
                            file.write(timestamp)
                        embed = self.parse_from_file_and_compose_embed (self.cache_of_space_launches_json_path)
                        await ctx.send(embed = embed)
                    elif resp.status == 429:
                        await ctx.send(embed = self.compose_error_embed('Too many requests. Wait a couple of minutes and try again.'))
                    else:
                        await ctx.send(embed = self.compose_error_embed('Call to the space devs failed. Response status: ' + str(resp.status)))
                    return
        else:
            embed = self.parse_from_file_and_compose_embed (self.cache_of_space_launches_json_path)
            await ctx.send(embed = embed)

    def should_call_the_api (self):
        if os.path.isfile(self.cache_of_space_launches_json_path) and os.path.isfile(self.cache_of_space_launches_time_path):
            with open(self.cache_of_space_launches_time_path,"r") as file:
                call_timestamp = datetime.strptime(file.readline(),THE_SPACE_DEVS_TIMESTAMP_FORMAT)
            now_timestamp = datetime.now()
            return (now_timestamp - call_timestamp).total_seconds() > 3600
        else:
            return True
          
    def parse_from_file_and_compose_embed(self, json_file):    # extracted for testing purposes      
        ''' This function expects that the json_file is already verified for existence '''
        with open(json_file,'r') as file:
            try:
                dom = json.load(file)
            except json.JSONDecodeError:
                return self.compose_error_embed('Could not parse the response from space devs.')
            embed = self.main_info_embed()
            for index, result in enumerate (dom['results']):
                self.add_embed_field_for_upcominglaunch(index, result, embed)
            return embed

    def compose_error_embed(self, error_msg):
        embed = self.main_info_embed()
        embed.add_field(name = 'ERROR:', value= error_msg, inline=True)
        return embed

    def main_info_embed (self):
        result = discord.Embed(
                                title="Upcoming launches", 
                                url=THE_SPACE_DEVS_HOME_URL, 
                                description="Provided by the space devs api. Timestamps = UTC",
                                color=NOTIFY_EMBED_COLOR
                            )
        return result

    def add_embed_field_for_upcominglaunch(self, index, result_json, embed):
        try:
            try:
                windows_start = datetime.strptime(result_json["window_start"],'%Y-%m-%dT%H:%M:%SZ')
                windows_start = windows_start.strftime('%a, %d %b at %H:%M')
            except TypeError:
                windows_start = "No start time"           
            try:
                service_provider = result_json["launch_service_provider"]["name"]
            except TypeError:
                service_provider = "No provider"
            
            try:                
                mission = result_json["mission"]["name"]
            except TypeError:
                mission = "No mission"            
            try:
                rocket_configuration = result_json["rocket"]["configuration"]["name"]
            except TypeError:
                rocket_configuration = "No configuration"
            try:
                pad_location = result_json["pad"]["location"]["name"]
            except TypeError:
                pad_location = "No location"
        except KeyError:
            embed.add_field(name = 'ERROR:', value= ' '.join ([index+1, 'Could not parse launch data.']),inline = False)
        name = str(index+1) + '. ' +service_provider+' : '+ mission+ '  ('+ windows_start +') '
        value =  '; '.join([pad_location, rocket_configuration])
        embed.add_field(name = name, value = value, inline = False)
        return

def setup(bot: commands.Bot):
    bot.add_cog(SpaceDevs(bot))
