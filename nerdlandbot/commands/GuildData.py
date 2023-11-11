import json
import os

from os import path, listdir, makedirs
from typing import List, Optional
from discord import Member
from datetime import datetime

from nerdlandbot.helpers.constants import DEFAULT_MEMBER_NOTIFICATION_NUMBER

_configFolder = "GuildConfigs"
_guildConfigCache = dict()

if not path.exists(_configFolder):
    makedirs(_configFolder)


class GuildData:
    bot_admins: list
    guild_id: int
    notification_lists: dict
    youtube_channels: dict
    purgers: dict
    culture: str
    pets: dict
    pets_last_id: Optional[int]
    pets_categories: List[str]
    mod_channel: str
    church_channel: int
    church_event: list
    member_notification_number: int
    prefix: str

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.notification_lists = dict()
        self.youtube_channels = dict()
        self.purgers = dict()
        self.bot_admins = []
        self.culture = "en"
        self.pets = {}
        self.pets_last_id = None
        self.pets_categories = []
        self.mod_channel = None
        self.church_channel = None
        self.church_event = []
        self.member_notification_number = DEFAULT_MEMBER_NOTIFICATION_NUMBER
        self.prefix = os.getenv("PREFIX")

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

    def get_emoji(self, list_name: str) -> (str, bool):
        """
        Return the emoji for the given list
        :param list_name: The list to fetch. (str)
        :return: the emoji to use (str), if the emoji is a custom emoji(bool)
        """
        return self.notification_lists[list_name]["emoji"], self.notification_lists[list_name]["is_custom_emoji"]

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
            "created_on": datetime.now().isoformat(),
            "notified_on": []
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

    def user_is_admin_moderator(self, user_to_check: Member):
        """
        Checks whether or not a user is a bot admin or a moderator.
        :param user_to_check: The user to check (discord.Member)
        :return: True if the user is either a bot admin or a server moderator, False if the user is neither (bool)
        """
        # Checks whether the user is moderator by checking the 'Ban Members permission'
        return (
            user_to_check.guild_permissions.administrator
            or user_to_check.guild_permissions.ban_members
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
        latest_video_id: Optional[str] = None,
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

    async def add_purger(self, text_channel, max_age: int) -> bool:
        """
            Adds a purger channel if not already there.
            :param text_channel: The text channel that will be purged (Discord Channel)
            :param max_age: The max age of messages in minutes (int)
            :return: True if added successfully, False if already in list. (bool)
            """

        if str(text_channel.id) not in self.purgers.keys():
            # purger text channel not in list, add to list and return True
            self.purgers[str(text_channel.id)] = max_age
            await self.save()
            return True

        else:
            # purger text channel already in list, return false
            return False

    async def remove_purger(self, text_channel) -> bool:
        """
        Remove a purger channel
        :param text_channel: The text channel with attached purger to be removed (Discord Channel)
        :return: True if added successfully, False if already in list. (bool)
        """

        if str(text_channel.id) in self.purgers.keys():
            # purger text channel exists in list, remove and return True
            self.purgers.pop(str(text_channel.id), None)
            await self.save()
            return True
        else:
            # purger text channel does not exist in list, return False
            return False

    async def update_notification_audit(self, list_name: str) -> bool:
        """
        Updates the notified_on field for the notified list
        :param list_name: The list that needs to be updated (str)
        :return: True if updated successfully, False if something went wrong. (bool)
        """
        if not list_name in self.notification_lists.keys():
            return False

        notification_list = self.notification_lists[list_name]

        if not "notified_on" in notification_list.keys():
            notification_list["notified_on"] = []

        notification_list["notified_on"].append(datetime.now().isoformat())
        await self.save()

        return True

    async def add_pet(self, pet_name: str, user_id: str, category: str) -> None:
        pet_id = await self.get_new_pet_id()
        pet_id_str = str(pet_id)
        self.pets[pet_id_str] = {}
        self.pets[pet_id_str]['owner'] = user_id
        self.pets[pet_id_str]['pet_name'] = pet_name.lower()
        self.pets[pet_id_str]['category'] = category.lower()
        await self.save()

    async def delete_pet(self, pet_id: str) -> None:
        pets = self.pets

        del pets[pet_id]

        await self.save()

    async def get_new_pet_id(self) -> int:
        if self.pets_last_id is None:
            self.pets_last_id = 0

        self.pets_last_id += 1

        await self.save()
        return self.pets_last_id

    async def add_new_pet_category(self, category_name: str) -> bool:
        categories = self.pets_categories

        if category_name in categories:
            return False

        categories.append(category_name)

        await self.save()
        return True

    async def remove_pet_category(self, category_name: str) -> bool:
        categories = self.pets_categories
        category_name = category_name.lower()
        
        if category_name not in categories:
            return False

        categories.remove(category_name)
        await self.save()
        return True
      
    async def update_church_channel(self, church: str) -> bool:
        """
        Updates the kerk_channel
        :param kerk: the channel that's been set
        :return: True if updated and saved, False if it's the same
        """
        church = church.strip("<#")
        church = int(church.strip(">"))
        if church != self.church_channel:
            self.church_channel = church
            await self.save()
            return True
        else:
            return False
    
    async def set_church_event(self, sender: str, receiver: str, day: int, culture: str, message:Optional[str] = None):
        """
        Adds a kerk_event
        :param sender: The person who sent a challenge
        :param receiver: The person who's being challenged
        :param day: The day the challenge will be sent out
        :param culture: The language being used in the bot
        :param message: In case the sender wants to add a message to his challenge
        """
        info = {}
        info["sender"] = sender
        info["receiver"] = receiver
        info["day"] = day
        info["culture"] = culture
        info["message"] = message
        
        self.church_event.append(info)
        await self.save()

    async def remove_church_event(self):
        self.church_event.pop(0)
        await self.save()

    async def update_mod_channel(self, mod_channel: str) -> bool:
        self.mod_channel = mod_channel
        await self.save()

        return True


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
        guild_data.youtube_channels[youtube_channel_id][
            "latest_video_id"
        ] = latest_video_id
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
        guildData.purgers = data.get("purgers", {})
        guildData.pets = data.get("pets", {})
        guildData.pets_last_id = data.get("pets_last_id", None)
        guildData.pets_categories = data.get("pets_categories", [])
        guildData.mod_channel = data.get("mod_channel",None)
        guildData.church_channel = data.get("church_channel", "")
        guildData.church_event = data.get("church_event", [])
        guildData.member_notification_number = data.get("member_notification_number", DEFAULT_MEMBER_NOTIFICATION_NUMBER)
        guildData.prefix = data.get("prefix", os.getenv("PREFIX"))

        return guildData


def get_config_file_path(guild_id: int) -> str:
    """
    Get the path for the save file for the given guild id
    :param guild_id: Guild Id (int)
    :return: filepath (str)
    """
    return path.join(_configFolder, str(guild_id) + ".json")
