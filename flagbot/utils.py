"""
Helper class to post messages either as reply or as independent message
"""
import logging

class utils:
    def __init__(self, roomNumber = None, client = None, quota = None, config = None):
        if roomNumber is not None:
            self.roomNumber = roomNumber

        if client is not None:
            self.client = client

        if quota is not None:
            self.quota = quota
        else:
            self.quota = -1

        if config is not None:
            self.config = config

    def setConfig(self, config):
        self.config = config

    def postMessage(self, message):
        logging.info(message)
        self.client.get_room(self.roomNumber).send_message(message)

    def checkAliases(self, message, command):
        if "@cyf " + command in message or "@cf " + command in message or "@CheckYerFlags " + command in message or "cyf " + command in message or "cf " + command in message:
            return True
        else:
            return False

    @staticmethod
    def replyWith(message, reply):
        logging.info(message)
        message.message.reply(reply)

    @staticmethod
    def blockedMessages(message):
        if not message.content.split('say', 1)[1].startswith(" cf say") and not message.content.split('say', 1)[1].startswith(" cyf say") and not message.content.split('say', 1)[1].startswith(" CheckYerFlags say") and not message.content.split('say', 1)[1].startswith(" @cf say") and not message.content.split('say', 1)[1].startswith(" @cyf say") and not message.content.split('say', 1)[1].startswith(" @CheckYerFlags say") and not message.content.split('say', 1)[1].startswith(" cf status mine") and not message.content.split('say', 1)[1].startswith(" cyf status mine") and not message.content.split('say', 1)[1].startswith(" CheckYerFlags status mine") and not message.content.split('say', 1)[1].startswith(" @cf status mine") and not message.content.split('say', 1)[1].startswith(" @cyf status mine") and not message.content.split('say', 1)[1].startswith(" @CheckYerFlags status mine"):
            logging.warning("Blocked message value detected: {}".format(message.content))
            return False
        else:
            logging.info("Blocked message check passed.")
            return True