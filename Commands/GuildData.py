from os import path

import json

_configFolder = "./GuildConfigs/"
_guildConfigCache = dict()


async def get_guild_data(guild_id: int):
    # check if memory cache contains server config
    if guild_id in _guildConfigCache.keys():
        return _guildConfigCache[guild_id]

    # check if server config file exists
    config = None
    fileName = get_config_file_path(guild_id)

    if path.exists(fileName):
        # Load data
        config = await __read_file(guild_id, fileName)
    else:
        # Init new instance of ServerData
        config = GuildData(guild_id)

    _guildConfigCache[guild_id] = config
    return config

async def get_guild_culture(guild_id: int):
    guild = await get_guild_data(guild_id)
    return guild.culture

async def __read_file(guild_id: int, filename: str):
    # TODO: Actually make this async
    with open(filename) as config:
        data = json.load(config)

        guildData = GuildData(guild_id)

        guildData.bot_admins = data.get("bot_admins", [])
        guildData.notification_lists = data.get("notification_lists", [])
        guildData.culture = data.get("culture", "en")

        return guildData


def get_config_file_path(guild_id: int):
    return _configFolder + str(guild_id) + ".json"


class GuildData:
    bot_admins: list
    guild_id: int
    notification_lists: dict()
    culture: str

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.notification_lists = dict()
        self.bot_admins = []
        self.culture = "en"

    async def sub_user(self, list_name: str, user_id: int):
        if list_name not in self.notification_lists.keys():
            return "This list does not exist"
        elif user_id in self.notification_lists[list_name]["users"]:
            return "<@" + str(user_id) + ">, you are already subscribed to " + list_name + ", foemp."
        else:
            self.notification_lists[list_name]["users"].append(user_id)
            await self.save()
            return "Subscribed <@" + str(user_id) + "> to " + list_name

    async def unsub_user(self, list_name: str, user_id: int):
        if list_name not in self.notification_lists.keys():
            return "That list does not seem to exist, cannot unsubscribe, foemp."
        else:
            if user_id in self.notification_lists[list_name]["users"]:
                self.notification_lists[list_name]["users"].remove(user_id)
                await self.save()
                return "Unsubscribed <@" + str(user_id) + "> from " + list_name
            else:
                return "You dont seem to be subscribed to this list, foemp."

    def notify(self, list_name: str):
        if list_name not in self.notification_lists.keys():
            return "That list does not seem to exist, foemp."
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
        self.notification_lists[list_name] = {
            "emoji": str(emoji),
            "is_custom_emoji": custom_emoji,
            "users": [],
        }
        await self.save()

    async def remove_notification_list(self, list_name):
        del self.notification_lists[list_name]
        await self.save()

    async def save(self):
        await self.__write_file()

    async def __write_file(self):
        # TODO: Actually make this async
        with open(get_config_file_path(self.guild_id), "w+") as config:
            json.dump(self.__dict__, config, indent=4, sort_keys=True)

    async def add_admin(self, user_id: int):
        self.bot_admins.append(user_id)
        await self.save()

    async def remove_admin(self, user_id: int):
        self.bot_admins.remove(user_id)
        await self.save()

    def user_is_admin(self, user_to_check):
        # returns True if the user is a server admin or bot admin
        # returns False if the user is neither a server admin or a bot admin
        return (user_to_check.guild_permissions.administrator or user_to_check.id in self.bot_admins)
