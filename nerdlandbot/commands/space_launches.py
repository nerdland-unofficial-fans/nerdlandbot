import aiohttp
import asyncio
import json
import discord
from datetime import datetime
from discord.ext import commands
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture

from nerdlandbot.helpers.constants import THE_SPACE_DEVS_BASE_URL
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_VERSION
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_UPCOMING_LAUNCH_RESOURCE
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_LIMIT_TO_10_RESULTS
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_LOCAL_TEST_SERVER_URL
from nerdlandbot.helpers.constants import THE_SPACE_DEVS_HOME_URL
from nerdlandbot.helpers.constants import 


class SpaceDevs (commands.Cog, name='The space devs'):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        self.ctx = None

    @commands.command(name="space_launches", hidden = False, help="space_launches_help", brief="space_launches_brief", usage="space_launches_usage")
    async def cmd_space_launches(self, ctx:commands.Context):
        self.ctx = ctx
        full_url = THE_SPACE_DEVS_LOCAL_TEST_SERVER_URL
#        full_url = '/'.join ([THE_SPACE_DEVS_BASE_URL, THE_SPACE_DEVS_VERSION, THE_SPACE_DEVS_UPCOMING_LAUNCH_RESOURCE])

        async with aiohttp.ClientSession() as session:
            async with session.get(full_url, headers = {"accept":"application/json"}) as resp: 
                if resp.status == 200:
                    msg = await resp.text()
                    await self.parse_and_send_results(msg)
                elif resp.status == 429:
                    await ctx.send('Too many requests. Wait a couple of minutes and try again.')
                else:
                    await ctx.send('Call to the space devs failed. Response status: '+ str(resp.status))
                return

    async def parse_and_send_results(self, json_string):    # extracted for testing purposes
        try:
            dom = json.loads(json_string)
        except json.JSONDecodeError:
            await self.ctx.send('Could not parse the response from space devs.')
            return
        embed = self.main_info_embed()
        for index, result in enumerate (dom['results']):
            await self.get_embed_field_for_upcominglaunch(index, result, embed)
        await self.ctx.send(embed = embed)
        return

    def main_info_embed (self):
        result = discord.Embed(
                                title="Upcoming launches", 
                                url=THE_SPACE_DEVS_HOME_URL, 
                                description="Provided by the space devs api.",
                                color=discord.Color.blue()
                            )
        return result

    async def get_embed_field_for_upcominglaunch(self, index, result_json, embed):
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
            return ' '.join ([index+1, 'Could not parse launch data.'])


        name = str(index+1) + '. ' +service_provider+' : '+ mission+ '  ('+ windows_start +') '
        value =  '; '.join([pad_location, rocket_configuration])
        embed.add_field(name = name, value = value, inline = False)

def setup(bot: commands.Bot):
    bot.add_cog(SpaceDevs(bot))

                
