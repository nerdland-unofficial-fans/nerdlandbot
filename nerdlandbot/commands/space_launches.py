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
                        await ctx.send(embed = self.parse_and_compose_embed(msg))
                    elif resp.status == 429:
                        await ctx.send(embed = self.compose_error_embed('Too many requests. Wait a couple of minutes and try again.'))
                    else:
                        await ctx.send(embed = self.compose_error_embed('Call to the space devs failed. Response status: ' + str(resp.status)))
                    return
        else:
            with open(self.cache_of_space_launches_json_path,"r") as file:
                msg = file.read()
            await ctx.send(embed = self.parse_and_compose_embed(msg))

    def should_call_the_api (self):
        if os.path.isfile(self.cache_of_space_launches_json_path) and os.path.isfile(self.cache_of_space_launches_time_path):
            with open(self.cache_of_space_launches_time_path,"r") as file:
                call_timestamp = datetime.strptime(file.readline(),THE_SPACE_DEVS_TIMESTAMP_FORMAT)
            now_timestamp = datetime.now()
            return (now_timestamp - call_timestamp).total_seconds() > 3600
        else:
            return True
          
    def parse_and_compose_embed(self, json_string):    # extracted for testing purposes      
        try:
            dom = json.loads(json_string)
        except json.JSONDecodeError:
            return self.compose_error_embed('Could not parse the response from space devs.')
        embed = self.main_info_embed()
        for index, result in enumerate (dom['results']):
            self.get_embed_field_for_upcominglaunch(index, result, embed)
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

    def get_embed_field_for_upcominglaunch(self, index, result_json, embed):
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

    async def get_percy_data(self):
        """
        Returns simplified data for percy pulled from the NASA Mars map API
        :return: dict containing sol, distance, longitude and latitude
        """
        url = 'https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints_current.json'
        full_json = ''
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers = {"accept":"application/json"}) as resp:
                full_json = await resp.text()

        data = json.loads(full_json)['features'][0]

        percy_data = dict()
        percy_data['sol'] = data['properties']['sol']
        percy_data['distance'] = data['properties']['dist_km']
        percy_data['longitude'] = data['geometry']['coordinates'][0]
        percy_data['latitude'] = data['geometry']['coordinates'][1]
        return percy_data


    @commands.command(name="percy", hidden = False, help="percy_help", brief="percy_brief")
    async def cmd_percy(self, ctx:commands.Context):
        percy_data = await self.get_percy_data()

        embed=discord.Embed(title="Status update", description="This is your requested latest update from the NASA Perseverance rover.", color=0xb33a00)
        embed.set_author(name="NASA Perseverance rover", url="https://mars.nasa.gov/mars2020/", icon_url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fvanschneider.com%2Fwp-content%2Fuploads%2F2020%2F07%2Fmars_badge.jpg&f=1&nofb=1")
        
        embed.add_field(name="Sol", value=percy_data['sol'], inline=False)
        embed.add_field(name="Latitude", value=percy_data['latitude'], inline=True)
        embed.add_field(name="Longitude", value=percy_data['longitude'], inline=True)
        embed.add_field(name="Distance Driven", value=percy_data['distance'], inline=True)
        embed.set_footer(text="Click the bird below to receive my latest tweet")
        
        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(SpaceDevs(bot))

                
