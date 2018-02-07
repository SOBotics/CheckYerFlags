"""
Helper class to post messages either as reply or as independent message
"""
import logging

class chat_helper:
    def __init__(self, roomNumber, client = None, quota = None):
        self.roomNumber = roomNumber

        if client is not None:
            self.client = client

        if quota is not None:
            self.quota = quota


    def setClient(self, client):
        self.client = client

    def setQuota(self, quota):
        self.quota = quota

    def getQuota(self):
        if self.quota is not None:
            return self.quota
        else:
            return -1;

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