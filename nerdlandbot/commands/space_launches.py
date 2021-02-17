import aiohttp
import asyncio
import json
import discord
from discord.ext import commands
from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture

THE_SPACE_DEVS_BASE_URL = ' HTTPS://THESPACEDEVS.COM'
THE_SPACE_DEVS_VERSION = '2.0.0'
THE_SPACE_DEVS_UPCOMING_LAUNCH_RESOURCE = 'launch/upcoming'
THE_SPACE_DEVS_LIMIT_TO_10_RESULTS = '?limit=10&offset=0'


class SpaceDevs (commands.Cog, name='The space devs'):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        self.ctx = None

    @commands.command(name="space_launches", hidden = False, help="space_launches_help", brief="space_launches_brief", usage="space_launches_usage")
    async def cmd_space_launches(self, ctx:commands.Context):
        self.ctx = ctx
        full_url = '/'.join ([THE_SPACE_DEVS_BASE_URL, THE_SPACE_DEVS_VERSION,
                             THE_SPACE_DEVS_UPCOMING_LAUNCH_RESOURCE,THE_SPACE_DEVS_LIMIT_TO_10_RESULTS])
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url, HEADERS = {"Accept":"application/json", "Accept-Charset":"UTF-8" }) as resp: 
                if resp.status == '200':
                    msg = await resp.text()
                    self.parse_and_send_results(msg)
                else:
                    await ctx.send('Call to the space devs failed.')

    async def parse_and_send_results(self, json_string):    # extracted for testing purposes
        try:
            dom = json.loads(json_string)
        except json.JSONDecodeError:
            await self.ctx.send('Could not parse the response from space devs.')
        lines = [self.get_line_for_upcoming_launches(index, result) for index, result in enumerate(dom['results'])]
        await self.ctx.send('\n'.join(lines))

    def get_line_for_upcoming_launches(self, index, result_json):
        try:
            windows_start = result_json["window_start"]
            service_provider = result_json["launch_service_provider"]["name"]
            mission = result_json["mission"]["name"]
            rocket_configuration = result_json["rocket"]["configuration"]["name"]
            pad_location = result_json["pad"]["location"]["name"]
        except KeyError:
            return ' '.join ([index+1, 'Could not parse launch data.'])
        return ' '.join ([index+1, windows_start, service_provider, mission, rocket_configuration, pad_location])
    

def setup(bot: commands.Bot):
    bot.add_cog(SpaceDevs(bot))

                
