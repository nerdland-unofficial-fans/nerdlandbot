import json
from os import path, listdir
import typing

from discord import Member
from typing import List

_configFolder = "./GuildConfigs/"
_guildConfigCache = dict()


class GuildData:
    bot_admins: list
    guild_id: int
    notification_lists: dict
    youtube_channels: dict
    culture: str

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.notification_lists = dict()
        self.youtube_channels = dict()
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

    def get_emoji(self, list_name: str) -> (str,bool):
        """
        Return the emoji for the given list
        :param list_name: The list to fetch. (str)
        :return: the emoji to use (str), if the emoji is a custom emoji(bool)
        """
        return self.notification_lists[list_name]["emoji"],self.notification_lists[list_name]["is_custom_emoji"]

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
        return (
            user_to_check.guild_permissions.administrator
            or user_to_check.id in self.bot_admins
        )

    async def update_language(self, language: str):
        """
        Updates the language and saves the guild
        :param language: The new language. (str)
        """
        if language != self.culture:
            self.culture = language
            await self.save()

    async def add_youtube_channel(
        self,
        youtube_channel_id: str,
        text_channel: str,
        latest_video_id: typing.Optional[str] = None,
    ) -> bool:
        """
        Adds a youtube channel if not already there.
        :param youtube_channel_id: The Youtube channel to be notified for (str)
        :param text_channel: The text channel that will receive the notification (str)
        :param latest_video_id: ID of the latest video (optional - str - default = None)
        :return: True if added successfully, False if already in list. (bool)
        """

        if youtube_channel_id not in self.youtube_channels.keys():
            # youtube channel not in list, add to list and return True
            self.youtube_channels[youtube_channel_id] = {
                "latest_video_id": latest_video_id,
                "text_channel_id": text_channel.id,
            }
            await self.save()
            return True

        else:
            # youtube channel already in list, return false
            return False

    async def remove_youtube_channel(self, youtube_channel_id: str) -> bool:
        """
        Remove a youtube channel
        :param youtube_channel_id: The Youtube channel to be removed (str)
        :return: True if added successfully, False if already in list. (bool)
        """

        if youtube_channel_id in self.youtube_channels.keys():
            # youtube channel exists in list, remove and return True
            self.youtube_channels.pop(youtube_channel_id, None)
            await self.save()
            return True
        else:
            # youtube channel does not exist in list, return False
            return False
    
async def update_youtube_channel_video_id(guild_id: int, youtube_channel_id, latest_video_id):
    """
    Sets the video ID of a channel. This is needed so that only a notification is posted
    when a new video is uploaded.
    :param guild_id: The Guild ID of the youtube list (int)
    :param youtube_channel_id: The Youtube channel to be notified for (str)
    :param latest_video_id: ID of the latest video (str)
    :return: True if updated successfully, False if the channel doesn't exist yet. (bool)
    """
    print("update_youtube_channel_video_id")
    guild_data = await get_guild_data(guild_id)
    if youtube_channel_id in guild_data.youtube_channels.keys():
        # youtube channel in list, update video ID and return True
        guild_data.youtube_channels[youtube_channel_id]["latest_video_id"] = latest_video_id
        # TODO: check if file is already being saved?
        await guild_data.save()

    else:
        # youtube channel not in list, return false
        return False

async def get_all_guilds_data() -> [GuildData]:
    """
    Retrieves the guild data for all guilds.
    :returns: List of GuildData objects ([GuildData])
    """
    guilds_data = []
    for file in listdir(_configFolder):
        split_file = path.splitext(file)
        if split_file[1] == ".json":
            guild_data = await get_guild_data(int(split_file[0]))
            guilds_data.append(guild_data)
    return guilds_data


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
        guildData.culture = data.get("culture", "en")
        guildData.youtube_channels = data.get("youtube_channels", {})

        return guildData


def get_config_file_path(guild_id: int) -> str:
    """
    Get the path for the save file for the given guild id
    :param guild_id: Guild Id (int)
    :return: filepath (str)
    """
    return _configFolder + str(guild_id) + ".json"
