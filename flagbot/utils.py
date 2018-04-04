"""
Helper class to post messages either as reply or as independent message
"""
import logging

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
            logging.info(message)
        self.client.get_room(self.room_number).send_message(message)

    def check_aliases(self, message, command):
        if message is None or command is None:
            return False

        if "@cyf " + command in message or "@cf " + command in message or "@CheckYerFlags " + command in message or "cyf " + command in message or "cf " + command in message:
            return True
        else:
            return False

    @staticmethod
    def reply_with(message, reply):
        logging.info(message)
        message.message.reply(reply)

    @staticmethod
    def id_list_without_bots(user_list):
        normal_user_list = []
        bot_id_list = [6373379, 9220325, 7240793, 7481043, 8149646, 6294609, 3735529, 7829893, 7418352, 5675570, 3671802, 5519396, 5675570, 8292957]
        for u in user_list:
            if u.id not in bot_id_list:
                normal_user_list.append(u)
        return  normal_user_list