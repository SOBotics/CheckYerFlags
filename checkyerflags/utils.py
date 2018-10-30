"""
Helper class for regularly used functions
"""
import re
from datetime import datetime, timedelta

from chatoverflow.chatexchange.events import MessagePosted, MessageEdited
from checkyerflags.logger import main_logger


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

        self.start_time = datetime.now()
        self.se_api = None

    def post_message(self, message, log_message = True, length_check = True):
        """
        Post a chat message
        """
        if log_message:
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
        Check if a user is allowed to use privileged commands (usually restricted to bot owners, room owners and moderators)
        """

        privileged_users = [4733879] #Replace this value with your SE/SO user id
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

    def get_uptime(self):
        """
        Returns the time since the bot was started
        """
        td = datetime.now() - self.start_time
        sec = timedelta(seconds=td.total_seconds())
        d = datetime(1,1,1) + sec
        return f"{d.day-1:02}d {d.hour:02}h {d.minute:02}m {d.second:02}s"

    def get_current_room(self):
        return self.client.get_room(self.room_number)

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
        Exclude bots from the checkable user list (Except Natty and Smokey) to reduce the amount of requests (as they don't flag, there's no need to check them)
        """
        checkable_users = []
        bot_id_list = [6373379, 9220325, 7240793, 7481043, 8149646, 6294609, 7829893, 7418352, 5675570, 3671802, 5519396, 5675570, 8292957, 5269493, 8300708, 10042414, 10162108]
        for u in user_list:
            if u.id not in bot_id_list:
                checkable_users.append(u)
        return checkable_users

MessagePosted.reply_to = lambda self, reply: self.message.reply(reply)
MessageEdited.reply_to = lambda self, reply: self.message.reply(reply)

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)