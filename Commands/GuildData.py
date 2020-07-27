from os import path

import json

_configFolder = "./GuildConfigs/"
_guildConfigCache = dict()


async def save_configs(guild_id: int):
    for key in _guildConfigCache:
        config = _guildConfigCache[key]

        if config.guild_changed:
            await config.save(guild_id)


async def get_guild_data(guild_id: int):
    # check if memory cache contains server config
    if guild_id in _guildConfigCache.keys():
        return _guildConfigCache[guild_id]

    # check if server config file exists
    config = None
    fileName = get_file_path(guild_id)

    if path.exists(fileName):
        # Load data
        config = await __read_file(guild_id, fileName)
        config.guild_changed = False
    else:
        # Init new instance of ServerData
        config = GuildData(guild_id)

    _guildConfigCache[guild_id] = config
    return config


async def __read_file(guild_id: int, filename: str):
    # TODO: Actually make this async
    with open(filename) as config:
        data = json.load(config)

        guildData = GuildData(guild_id)
        guildData.notification_lists = data["notification_lists"]

        return guildData


def get_file_path(guild_id: int):
    return _configFolder + str(guild_id) + ".json"


class GuildData:
    guild_id: int
    guild_changed: bool
    notification_lists: dict()

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.guild_changed = False
        self.notification_lists = dict()

    async def sub_user(self, list_name: str, user_id: int):
        if list_name not in self.notification_lists.keys():
            return "This list does not exist"
            # TODO: print lists with reactions to sub
        elif user_id in self.notification_lists[list_name]["users"]:
            return "<@" + str(user_id) + ">, you are already subscribed to " + list_name
        else:
            self.notification_lists[list_name]["users"].append(user_id)
            self.guild_changed = True
            await self.save()
            return "Subscribed <@" + str(user_id) + "> to " + list_name

    async def unsub_user(self, list_name: str, user_id: int):
        if list_name not in self.notification_lists.keys():
            return "That list does not seem to exist, cannot unsubscribe"
        else:
            if user_id in self.notification_lists[list_name]["users"]:
                self.notification_lists[list_name]["users"].remove(user_id)
                self.guild_changed = True
                await self.save()
                return "Unsubscribed <@" + str(user_id) + "> from " + list_name
            else:
                return "You dont seem to be subscribed to this list"

    def notify(self, list_name: str):
        if list_name not in self.notification_lists.keys():
            return "That list does not seem to exist"
        else:
            users = self.notification_lists[list_name]["users"]
            if len(users) > 0:
                mentionList = []
                for user_id in users:
                    mentionList.append("<@" + str(user_id) + ">")
                return "Notifying " + ", ".join(mentionList)
            else:
                return "Nobody to notify"

    async def add_notification_list(self, list_name, emoji, custom_emoji):
        # TODO add boolean custom_icon
        self.notification_lists[list_name] = {
            "icon": str(emoji),
            "users": [],
            "custom": custom_emoji,
        }
        await self.save()

    async def save(self):
        await self.__write_file()
        self.guild_changed = False

    async def __write_file(self):
        # TODO: Actually make this async
        with open(get_file_path(self.guild_id), "w+") as config:
            json.dump(self.__dict__, config, indent=4, sort_keys=True)

