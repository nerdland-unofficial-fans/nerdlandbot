from os import path
from Translations.Translations import get_text as translate
import discord
import json

_configFolder = "./GuildConfigs/"
_guildConfigCache = dict()


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

    async def sub_user(self, list_name: str, user_id: int) -> str:
        if list_name not in self.notification_lists.keys():
            return translate("list_does_not_exit", self.culture)

        if user_id in self.notification_lists[list_name]["users"]:
            return translate("list_err_already_subscribed", self.culture).format(user_id, list_name)

        self.notification_lists[list_name]["users"].append(user_id)
        await self.save()
        return translate("list_subscribed", self.culture).format(user_id, list_name)

    async def unsub_user(self, list_name: str, user_id: int) -> str:
        if list_name not in self.notification_lists.keys():
            return translate("list_does_not_exit", self.culture)

        if user_id in self.notification_lists[list_name]["users"]:
            self.notification_lists[list_name]["users"].remove(user_id)
            await self.save()
            return translate("list_unsubscribed", self.culture).format(user_id, list_name)

        return translate("list_err_not_subscribed", self.culture).format(user_id, list_name)

    def notify(self, list_name: str) -> str:
        if list_name not in self.notification_lists.keys():
            return translate("list_does_not_exit", self.culture)

        users = self.notification_lists[list_name]["users"]
        if len(users) < 1:
            return translate("list_err_empty", self.culture)

        mentionList = []
        for user_id in users:
            mentionList.append("<@" + str(user_id) + ">")

        mention_string = ", ".join(mentionList)
        return translate("notifying", self.culture).format(mention_string)

    async def add_notification_list(self, list_name: str, emoji: str, is_custom_emoji: bool):
        self.notification_lists[list_name] = {
            "emoji": str(emoji),
            "is_custom_emoji": is_custom_emoji,
            "users": [],
        }
        await self.save()

    async def remove_notification_list(self, list_name: str):
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

    def user_is_admin(self, user: discord.user) -> bool:
        # returns True if the user is a server admin or bot admin
        # returns False if the user is neither a server admin or a bot admin
        return user.guild_permissions.administrator or user.id in self.bot_admins


def get_config_file_path(guild_id: int) -> str:
    return _configFolder + str(guild_id) + ".json"


async def get_guild_data(guild_id: int) -> GuildData:
    # check if memory cache contains server config
    if guild_id in _guildConfigCache.keys():
        return _guildConfigCache[guild_id]

    # check if server config file exists
    fileName = get_config_file_path(guild_id)

    if path.exists(fileName):
        # Load data
        config = await __read_file(guild_id, fileName)
    else:
        # Init new instance of ServerData
        config = GuildData(guild_id)

    _guildConfigCache[guild_id] = config
    return config


async def __read_file(guild_id: int, filename: str) -> GuildData:
    # TODO: Actually make this async
    with open(filename) as config:
        data = json.load(config)

        guildData = GuildData(guild_id)

        guildData.bot_admins = data.get("bot_admins", [])
        guildData.notification_lists = data.get("notification_lists", [])
        guildData.culture = data.get("culture", "en")

        return guildData
