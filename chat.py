import getpass
import logging
import logging.handlers
import os
import random
import sys
import messagecompare

from chatexchange.chatexchange.client import Client
from chatexchange.chatexchange.events import MessageEvent, MessagePosted


logger = logging.getLogger(__name__)
host_name = 'HP Envy'

def main():
    setup_logging()

    #Setup start actions
    host_id = 'stackoverflow.com'
    room_id = '163468' #Debug room
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    client = Client(host_id)
    client.login(email, password)

    room = client.get_room(room_id)
    room.join()
    room.watch(on_message)

    print("(You are now in room #%s on %s.)" % (room_id, host_id))
    while True:
        message = input("<< ")
        room.send_message(message)

    client.logout()


def on_message(message, client):
    if not isinstance(message, MessagePosted):
        # Ignore non-message_posted events.
        logger.debug("event: %r", message)
        return
    message_val = message.content
    print("")
    print(">> (%s) %s" % (message.user.name, message.content))

    #Here are the responses defined
    if message.content.startswith('!!/random'):
        print(message)
        message.message.reply(str(random.random()))
    #region default bot commands
    elif messagecompare.compareMessage(message_val, "alive"):
        print(message)
        message.message.reply("👍 on " + host_name)
    elif messagecompare.compareMessage(message_val, "say"):
        print(message)
        room = client.get_room(163468)
        room.send_message(message.content.split('say', 1)[1])
        #message.message.reply(message.content.split('say', 1)[1])
    elif messagecompare.compareMessage(message_val, "status mine"):
        print(message)
        message.message.reply("You need [69] more helpful flags to get your next rank: **Burn the evil** (666 flags)")
    elif messagecompare.compareMessage(message_val, "status"):
        print(message)
        message.message.reply("Please specify whose status you want to get")
    #region fun answers
    elif messagecompare.compareMessage(message_val, "why"):
        print(message)
        message.message.reply("[Because of you](https://www.youtube.com/watch?v=Ra-Om7UMSJc)")
    elif messagecompare.compareMessage(message_val, "good bot"):
        print(message)
        message.message.reply("Thank you")
    elif messagecompare.compareMessage(message_val, "Thanks") or messagecompare.compareMessage(message_val, "Thank you"):
        print(message)
        message.message.reply("You're welcome.")
    elif messagecompare.compareMessage(message_val, "status Batty") or messagecompare.compareMessage(message_val, "status batty"):
        print(message)
        message.message.reply("Batty [can barely use links](https://chat.stackoverflow.com/rooms/111347/conversation/batty-learns-how-to-use-links). She's not worthy of a flag rank *kappa*")
    elif "shrug" in message.content:
        print(message)
        message.message.reply("🤷")
        # message.message.reply("¯\\ _(ツ)_/¯") This is the more ASCII-/Retro-version. Choose between the emoji and this one as you like
    elif "kappa" in message.content and "gif" in message.content:
        print(message)
        message.message.reply("https://i.imgur.com/8TRbWHM.gif")
    #endregion


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.DEBUG)

    # In addition to the basic stderr logging configured globally
    # above, we'll use a log file for chatexchange.client.
    wrapper_logger = logging.getLogger('chatexchange.client')
    wrapper_handler = logging.handlers.TimedRotatingFileHandler(
        filename='client.log',
        when='midnight', delay=True, utc=True, backupCount=7,
    )
    wrapper_handler.setFormatter(logging.Formatter(
        "%(asctime)s: %(levelname)s: %(threadName)s: %(message)s"
    ))
    wrapper_logger.addHandler(wrapper_handler)


if __name__ == '__main__':
    main(*sys.argv[1:])