"""
Helper class to post messages either as reply or as independent message
"""

class chat_helper:


    def __init__(self, roomNumber, client = None):
        self.roomNumber = roomNumber

        if client is not None:
            self.client = client

    def setClient(self, client):
        self.client = client

    def postMessage(self, message):
        print(message)
        self.client.get_room(self.roomNumber).send_message(message)

    def checkAliases(self, message, command):
        if "@cyf " + command in message or "@cf " + command in message or "@CheckYerFlags " + command in message or "cyf " + command in message or "cf " + command in message:
            return True
        else:
            return False

    @staticmethod
    def replyWith(self, message, reply):
        print(message)
        message.message.reply(reply)