import json
from os import path
from datetime import datetime

from discord import Member
from typing import List

_configFolder = "./GuildConfigs/"
_guildConfigCache = dict()


class GuildData:
    bot_admins: list
    guild_id: int
    notification_lists: dict
    escaperoom_game: dict
    culture: str

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.notification_lists = dict()
        self.escaperoom_game = dict()
        self.bot_admins = []
        self.culture = "en"

    async def sub_user(self, list_name: str, user_id: int) -> bool:
        """
        Adds a user to the list if not already there.
        :param list_name: The list to add the user to. (str)
        :param user_id: The user to add to the list. (int)
        :return: True if added successfully, False if already in list. (bool)
        """
        user_list = self.notification_lists[list_name]["users"]

        if user_id not in user_list:
            # user not in list, add to list and return True
            user_list.append(user_id)
            await self.save()
            return True

        else:
            # user already in list, return false
            return False

    async def unsub_user(self, list_name: str, user_id: int) -> bool:
        """
        Removes a user from the list
        :param list_name: The list to remove the user from. (str)
        :param user_id: The user to remove from the list. (str)
        :returns: True if the user is successfully removed, False if the user is not on the list. (bool)
        """
        user_list = self.notification_lists[list_name]["users"]

        if user_id in user_list:
            # user exists in list, remove and return True
            user_list.remove(user_id)
            await self.save()
            return True
        else:
            # user does not exist in list, return False
            return False

    def get_users_list(self, list_name: str) -> List[str]:
        """
        Return all users who subscribed to the given list
        :param list_name: The list to fetch. (str)
        :return: A list with the id of all users who subscribed to the given list. (list[str])
        """
        return self.notification_lists[list_name]["users"]

    def does_list_exist(self, list_name: str) -> bool:
        """
        Checks whether or not a list exists.
        :param list_name: The name of the list to check. (str)
        :return: True if the list exists, False if it doesn't. (bool)
        """
        return list_name in self.notification_lists.keys()

    async def add_notification_list(self, list_name: str, emoji, custom_emoji: bool):
        """
        Adds a new notification list.
        :param list_name: The name of the list to add. (str)
        :param emoji: The emoji to be used for the list. (any)
        :param custom_emoji: Whether or not we're using a custom emoji. (bool)
        """
        self.notification_lists[list_name] = {
            "emoji": emoji,
            "is_custom_emoji": custom_emoji,
            "users": [],
        }
        await self.save()

    async def remove_notification_list(self, list_name: str):
        """
        Removes a notification list.
        :param list_name: The list to be removed. (str)
        """
        if list_name in self.notification_lists.keys():
            del self.notification_lists[list_name]
            await self.save()

    async def save(self):
        """
        Saves the current data to storage
        """
        await self.__write_file()

    async def __write_file(self):
        """
        Write data to file
        """
        # TODO: Actually make this async
        with open(get_config_file_path(self.guild_id), "w+") as config:
            json.dump(self.__dict__, config, indent=4, sort_keys=True)

    async def add_admin(self, user_id: int):
        """
        Add a new bot admin
        :param user_id: The id of the user to promote to admin (int)
        """
        if user_id not in self.bot_admins:
            self.bot_admins.append(user_id)
            await self.save()

    async def remove_admin(self, user_id: int):
        """
        Removes a bot admin
        :param user_id: The id of the user to revoke bot admin rights from. (int)
        """
        if user_id in self.bot_admins:
            self.bot_admins.remove(user_id)
            await self.save()

    def user_is_admin(self, user_to_check: Member):
        """
        Checks whether or not a user is a bot admin.
        :param user_to_check: The user to check (discord.Member)
        :return: True if the user is either a bot admin or a server admin, False if the user is neither (bool)
        """
        # returns True if the user is a server admin or bot admin
        # returns False if the user is neither a server admin or a bot admin
        return user_to_check.guild_permissions.administrator or user_to_check.id in self.bot_admins

    async def update_language(self, language: str):
        """
        Updates the language and saves the guild
        :param language: The new language. (str)
        """
        if language != self.culture:
            self.culture = language
            await self.save()

    async def register_user_escape(self, user_id: int) -> bool:
        if 'users' not in self.escaperoom_game.keys():
            self.escaperoom_game['users'] = []

        if user_id not in self.escaperoom_game['users']:
            self.escaperoom_game['users'].append(user_id)
            await self.save()
            return True
        else:
            return False
    
    async def deregister_user_escape(self,user_id: int) -> bool:
        if 'users' in self.escaperoom_game.keys():
            if user_id in self.escaperoom_game['users']:
                self.escaperoom_game['users'].remove(user_id)
                await self.save()
                return True
            else:
                return False
        else:
            return False

    async def new_escaproom_game_time(self, escape_time: datetime, overwrite=False) -> bool:
        if not 'datetime' in self.escaperoom_game.keys():
            # not time has been set yet, set time and clear userlist
            print(escape_time.timestamp())
            self.escaperoom_game['datetime'] = escape_time.timestamp()
            self.escaperoom_game['users'] = []
            await self.save()
            return True
        elif self.escaperoom_game['datetime'] < datetime.now().timestamp() or overwrite:
            # set time has passed or is to be overwritten, set new time and clear userlist
            self.escaperoom_game['datetime'] = escape_time.timestamp()
            self.escaperoom_game['users'] = []
            await self.save()
            return True
        else:
            # time has already been set, don't overwrite
            return False

    async def clear_escaperoom_users(self):
        self.escaperoom_game['users'] = []
        await self.save()

    def get_users_escaperoom_game(self) -> list:
        if 'users' in self.escaperoom_game.keys():
            return self.escaperoom_game['users']
        else:
            return []

    def get_datetime_escaperoom_game(self) -> datetime:
        if 'datetime' in self.escaperoom_game.keys():
            escaperoom_datetime = datetime.fromtimestamp(self.escaperoom_game['datetime'])
            return escaperoom_datetime
        else:
            return None   


async def get_guild_data(guild_id: int) -> GuildData:
    """
    Retrieves the guild data for the given guild id.
    If possible it will be fetched from the cache, otherwise it will be loaded from the json file
    :param guild_id: Guild id (int)
    :returns:GuildData object (GuildData)
    """

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
    """
    Read the given json file and parse it to a GuildData object
    :param guild_id: Guild Id (int)
    :param filename: The name of the file to open (str)
    :returns: GuildData object (GuildData)
    """
    # TODO: Actually make this async
    with open(filename) as config:
        data = json.load(config)

        guildData = GuildData(guild_id)

        guildData.bot_admins = data.get("bot_admins", [])
        guildData.notification_lists = data.get("notification_lists", [])
        guildData.escaperoom_game = data.get("escaperoom_game", [])
        guildData.culture = data.get("culture", "en")

        return guildData


def get_config_file_path(guild_id: int) -> str:
    """
    Get the path for the save file for the given guild id
    :param guild_id: Guild Id (int)
    :return: filepath (str)
    """
    return _configFolder + str(guild_id) + ".json"
