from os import path

import json

_configFolder = "./GuildConfigs/"
_guildConfigCache = dict()

async def load_guild_config(ctx):
    #check if memory cache contains server config
    if ctx.message.guild.id in _guildConfigCache.keys():
        return _guildConfigCache[ctx.message.guild.id]

    #check if server config file exists
    config = None
    fileName = _configFolder + str(ctx.message.guild.id) + ".txt"

    if path.exists(fileName):
        #Load data
        config = await __read_file(fileName)
        config.guild_changed = False
    else:
        #Init new instance of ServerData
        config = GuildData()

    _guildConfigCache[ctx.message.guild.id] = config
    return config

async def save_configs(ctx):
    for key in _guildConfigCache:
        config = _guildConfigCache[key]

        if config.guild_changed:
            fileName = _configFolder + str(ctx.message.guild.id) + ".txt"
            await __write_file(fileName, config)

async def __read_file(filename:str):
    with open(filename) as config:
        data = json.load(config)

        serverData = GuildData()
        serverData.notification_lists = data["notification_lists"]

        return serverData

async def __write_file(filename:str, guildConfig):
    with open(filename, 'w') as config:
        json.dump(guildConfig.__dict__, config, indent=4, sort_keys=True)    

class GuildData():
    guild_changed: bool
    notification_lists: dict()

    def __init__(self):
        self.guild_changed = False
        self.notification_lists = dict()