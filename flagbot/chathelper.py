"""
Helper class to post messages either as reply or as independent message
"""

class chatHelper:


    def __init__(self, roomNumber, client):
        self.roomNumber = roomNumber
        self.client = client

    def postMessage(self, message):
        print(message)
        self.client.get_room(self.roomNumber).send_message(message)

    @staticmethod
    def replyWith(self,message, reply):
        print(message)
        message.message.reply(reply)