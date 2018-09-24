"""
Helper class for regularly used functions
"""
import re

from chatoverflow.chatexchange.events import MessagePosted, MessageEdited
from flagbot.logger import main_logger


class utils:
    def __init__(self, room_number = None, client = None, quota = None, config = None, room_owners = None):
        if room_number is not None:
            self.room_number = room_number

        if client is not None:
            self.client = client

        if quota is not None:
            self.quota = quota
        else:
            self.quota = -1

        if config is not None:
            self.config = config

        if room_owners is not None:
            self.room_owners = room_owners

    def post_message(self, message, no_main_logger = False, length_check = True):
        """
        Post a chat message
        """
        if not no_main_logger:
            utils.log_message(message)
        self.client.get_room(self.room_number).send_message(message, length_check)

    def alias_valid(self, alias):
        """
        Check if the specified alias is valid
        """
        if re.match(r"@[Cc]he[c]?[k]?[Yy]?[e]?[r]?[Ff]?[l]?[a]?[g]?[s]?", alias):
            #Alias valid
            return True
        else:
            #Alias invalid
            return False

    def is_privileged(self, message, owners_only=False):
        """
        Check if a user is allowed to use privileged commands (usally restricted to bot owners, room owners and moderators)
        """

        privileged_users = [4733879]
        if owners_only:
            if message.user.id in privileged_users:
                return True
            else:
                return False

        for owner in self.room_owners:
            privileged_users.append(owner.id)

        # Restrict function to (site) moderators, room owners and maintainers
        if message.user.is_moderator or message.user.id in privileged_users:
            return True
        else:
            return False

    @staticmethod
    def log_command(command_name):
        """
        Log a command call
        """
        main_logger.info(f"Command call of: {command_name}")

    @staticmethod
    def log_message(message):
        """
        Log a chat message with the message id
        """
        if isinstance(message, MessagePosted) or isinstance(message, MessageEdited):
            main_logger.info(f"Message #{message._message_id} was posted by '{message.user.name}' (in room '{message.room.name}')")

    @staticmethod
    def checkable_user_ids(user_list):
        """
        Exclude moderators and bots from the checkable user list (Except Natty and Smokey) to reduce the amount of requests
        """
        checkable_users = []
        bot_id_list = [6373379, 9220325, 7240793, 7481043, 8149646, 6294609, 7829893, 7418352, 5675570, 3671802, 5519396, 5675570, 8292957, 5269493, 8300708, 10042414]
        for u in user_list:
            if u.id not in bot_id_list:
                checkable_users.append(u)
        return checkable_users

MessagePosted.reply_to = lambda self, reply: self.message.reply(reply)
MessageEdited.reply_to = lambda self, reply: self.message.reply(reply)