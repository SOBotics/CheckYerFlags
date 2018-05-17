"""
Helper class to post messages either as reply or as independent message
"""
import logging

from chatexchange.chatexchange.events import MessagePosted, MessageEdited


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

    def post_message(self, message, no_logging = False):
        if not no_logging:
            utils.log_message(message)
        self.client.get_room(self.room_number).send_message(message)

    def alias_valid(self, alias):
        """Check if the specified alias is valid"""
        if alias in ["@Check", "@CheckYerFlags", "cf", "cyf"]:
            #Alias valid
            return True
        elif alias in ["@cyf", "@cf"]:
            #Alias deprecated, post message with deprecation message
            self.post_message("This alias is deprecated and subject to be removed. Please use a [supported alias](https://checkyerflags.sobotics.org/#aliases) in the future.")
            return True
        else:
            #Alias invalid
            return False

    def is_privileged(self, message):
        priviledged_users = [4733879]
        for owner in self.room_owners:
            priviledged_users.append(owner.id)

        # Restrict function to (site) moderators, room owners and maintainers
        if  message.user.is_moderator or message.user.id in priviledged_users:
            return True
        else:
            return False

    @staticmethod
    def reply_with(message, reply):
        utils.log_message(message)
        message.message.reply(reply)

    @staticmethod
    def log_command(command_name):
        logging.info("Command call of: {}".format(command_name))

    @staticmethod
    def log_message(message):
        if isinstance(message, MessagePosted) or isinstance(message, MessageEdited):
            logging.info("Message #{} was posted by '{}' in room '{}'".format(message._message_id, message.user.name, message.room.name))


    @staticmethod
    def id_list_without_bots(user_list):
        normal_user_list = []
        bot_id_list = [6373379, 9220325, 7240793, 7481043, 8149646, 6294609, 3735529, 7829893, 7418352, 5675570, 3671802, 5519396, 5675570, 8292957]
        for u in user_list:
            if u.id not in bot_id_list:
                normal_user_list.append(u)
        return  normal_user_list