import aiohttp
import asyncio
import json
import os
import discord
import tweepy
import time
from datetime import datetime
from discord.ext import commands
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.log import debug, info, warn, error
from nerdlandbot.helpers.emoji import bird, camera
from nerdlandbot.helpers.constants import REACTION_TIMEOUT

from nerdlandbot.helpers.constants import THE_SPACE_DEVS_BASE_URL, THE_SPACE_DEVS_VERSION, THE_SPACE_DEVS_LIMIT_TO_10_RESULTS
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_HOME_URL, NOTIFY_EMBED_COLOR
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_UPCOMING_LAUNCH_RESOURCE
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_LOCAL_CACHE_SPACE_LAUNCHES_FILE, THE_SPACE_DEVS_LOCAL_CACHE_FOLDER, THE_SPACE_DEVS_TIMESTAMP_FORMAT
from nerdlandbot.helpers.constants import PERCY_TWITTER_ID

class SpaceDevs (commands.Cog, name='Space'):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        self.cache_of_space_launches_json_path = os.path.join(THE_SPACE_DEVS_LOCAL_CACHE_FOLDER, THE_SPACE_DEVS_LOCAL_CACHE_SPACE_LAUNCHES_FILE + '.json')
        self.cache_of_space_launches_time_path = os.path.join (THE_SPACE_DEVS_LOCAL_CACHE_FOLDER, THE_SPACE_DEVS_LOCAL_CACHE_SPACE_LAUNCHES_FILE + '.time')
        if not os.path.isdir(THE_SPACE_DEVS_LOCAL_CACHE_FOLDER):
            os.makedirs(THE_SPACE_DEVS_LOCAL_CACHE_FOLDER)

        self.twitter_creds = {'key':os.getenv("TWITTER_API_KEY"),'secret':os.getenv("TWITTER_API_SECRET")}
        self.twitter_enabled = self.twitter_creds['key'] and self.twitter_creds['secret']
        if not self.twitter_enabled:
            error(
                "No Twitter key and secret in .env file, Twitter functionality will not be available"
            )

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
        percy_data['distance'] = data['properties']['dist_km'] + ' km'
        percy_data['longitude'] = data['geometry']['coordinates'][0]
        percy_data['latitude'] = data['geometry']['coordinates'][1]
        return percy_data

    async def send_percy_tweet(self, ctx: commands.Context):

        auth = tweepy.AppAuthHandler(self.twitter_creds['key'], self.twitter_creds['secret'])
        api = tweepy.API(auth)
        last_status = api.user_timeline(id=PERCY_TWITTER_ID)[0]
        return await ctx.send(last_status.text)

    async def wait_for_tweet_reaction(self, ctx: commands.Context, msg_id: int,
                                       timeout: int = REACTION_TIMEOUT):
        end_time = time.time() + timeout
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda emoji, author: emoji.message.id == msg_id and not author.bot,
                    timeout=timeout,
                )
                if reaction.emoji == bird:
                    return await self.send_percy_tweet(ctx)
            except asyncio.TimeoutError:
                pass

            if time.time() > end_time:
                break

    async def wait_for_camera_reaction(self, ctx: commands.Context, msg, embed, timeout: int = REACTION_TIMEOUT):
        end_time = time.time() + timeout
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda emoji, author: emoji.message.id == msg.id and not author.bot,
                    timeout=timeout,
                )
                if reaction.emoji == camera:
                    embed.set_image(url='https://mars.nasa.gov/mars2020-raw-images/pub/ods/surface/sol/00002/ids/fdr/browse/zcam/ZLF_0002_0667131112_000FDR_N0010052AUT_04096_0260LUJ01_1200.jpg')
                    return await msg.edit(embed=embed)
            except asyncio.TimeoutError:
                pass

            if time.time() > end_time:
                break

    @commands.command(name="percy", hidden = False, help="percy_help", brief="percy_brief")
    async def cmd_percy(self, ctx:commands.Context):
        percy_data = await self.get_percy_data()

        embed=discord.Embed(title="Status update", description="This is your requested latest update from the NASA Perseverance rover.", color=0xb33a00)
        embed.set_author(name="NASA Perseverance rover", url="https://mars.nasa.gov/mars2020/", icon_url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fvanschneider.com%2Fwp-content%2Fuploads%2F2020%2F07%2Fmars_badge.jpg&f=1&nofb=1")
        
        embed.add_field(name="Sol", value=percy_data['sol'], inline=False)
        embed.add_field(name="Latitude", value=percy_data['latitude'], inline=True)
        embed.add_field(name="Longitude", value=percy_data['longitude'], inline=True)
        embed.add_field(name="Distance Driven", value=percy_data['distance'], inline=True)
        if self.twitter_enabled:
            embed.set_footer(text="Click the bird below to receive my latest tweet\n Click the camera to see my Image Of The Week")
        msg = await ctx.send(embed=embed)

        added_reactions = []

        await msg.add_reaction(camera)
        added_reaction = asyncio.create_task(self.wait_for_camera_reaction(ctx,msg,embed))
        added_reactions.append(added_reaction)

        if self.twitter_enabled:
            await msg.add_reaction(bird)
            added_reaction = asyncio.create_task(self.wait_for_tweet_reaction(ctx, msg.id))
            added_reactions.append(added_reaction)
        
        await asyncio.gather(*added_reactions,return_exceptions=True)


        #embed.set_image(url='https://mars.nasa.gov/mars2020-raw-images/pub/ods/surface/sol/00002/ids/fdr/browse/zcam/ZLF_0002_0667131112_000FDR_N0010052AUT_04096_0260LUJ01_1200.jpg')

def setup(bot: commands.Bot):
    bot.add_cog(SpaceDevs(bot))

                
