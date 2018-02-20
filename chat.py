import getpass
import logging
import sys
import json
import io
import gzip
import threading

import flagbot.check_flags as check_flags
import flagbot.redunda as redunda

from flagbot.chat_helper import chat_helper

from urllib.request import urlopen
from chatexchange.chatexchange.client import Client
from chatexchange.chatexchange.events import MessagePosted, MessageEdited

bot_parent = 'chade_'
bot_machine = 'HP Envy (dev machine)'
bot_version = 'v0.6.1'
rooms = {
    "Debug": 163468,
    "SOBotics": 111347,
    "SOCVR": 41570
}
room_id = rooms["Debug"]
chat_helper = chat_helper(room_id)


def main():
    #Setup start actions
    host_id = 'stackoverflow.com'
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    client = Client(host_id)
    client.login(email, password)
    chat_helper.setClient(client)

    room = client.get_room(room_id)
    room.join()
    room.watch(on_message)
    print(room.get_current_user_names())

    quota_obj = json.loads(gzip.GzipFile(fileobj=io.BytesIO(urlopen("https://api.stackexchange.com/2.2/users/1?order=desc&sort=reputation&site=stackoverflow&key=K8pani4F)SeUn0QlbHQsbA((").read())).read().decode("utf-8"))


    if quota_obj['quota_remaining'] is not None:
        chat_helper.setQuota(quota_obj['quota_remaining'])

    logging.basicConfig(filename="CheckYerFlags.log", level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info("Joined room '{}' on {}".format(room.name, host_id))

    #Run Redunda reporting on a seperate thread/in the background
    stop_redunda = threading.Event()
    redunda_thread = redunda.RedundaThread(stop_redunda, bot_version, logging)
    redunda_thread.start()

    while True:
        message = input("<< ")
        room.send_message(message)

    client.logout()
    stop_redunda.set()

def on_message(message, client):
    if not isinstance(message, MessagePosted) and not isinstance(message, MessageEdited):
        # We ignore non-MessagePosted events.
        return
    message_val = message.content

    #Here are the responses defined
    #region Default bot commands
    if chat_helper.checkAliases(message_val, "alive"):
        chat_helper.replyWith(message, "instance of {} is running on **{}/{}**".format(bot_version, bot_parent, bot_machine))
    elif chat_helper.checkAliases(message_val, "say"):
        chat_helper.postMessage(message.content.split('say', 1)[1])
    elif chat_helper.checkAliases(message_val, "welcome"):
        chat_helper.postMessage("Welcome to SOBotics! You can learn more about SOBotics and what we and [all the bots](https://sobotics.org/all-bots/) are doing here at our website, https://sobotics.org/. If you'd like to help out with flagging, reporting, or anything else, let us know! We have tons of [userscripts](https://sobotics.org/userscripts/) to make things easier, and you'll always find someone around who will help you to install them and explain how they work.")
    elif chat_helper.checkAliases(message_val, "quota"):
        chat_helper.postMessage("The remaining API quota is {}.".format(chat_helper.getQuota()))
    elif chat_helper.checkAliases(message_val, "command") or chat_helper.checkAliases(message_val, "commands"):
        chat_helper.replyWith(message, "You can find a list of my commands [here](https://github.com/SOBotics/FlaggersHall/wiki#commands)")
    #endregion
    elif chat_helper.checkAliases(message_val, "status mine"):
        check_flags.checkOwnFlags(message, chat_helper)
    elif chat_helper.checkAliases(message_val, "status"):
        check_flags.checkFlags(message, chat_helper)
    #region Fun commands
    elif message.content.startswith("🚂"):
        chat_helper.postMessage("🚃")
    elif chat_helper.checkAliases(message_val, "why"):
        chat_helper.replyWith(message, "[Because of you](https://www.youtube.com/watch?v=Ra-Om7UMSJc)")
    elif chat_helper.checkAliases(message_val, "good bot"):
        chat_helper.replyWith(message, "Thank you")
    elif chat_helper.checkAliases(message_val.lower(), "thanks") or chat_helper.checkAliases(message_val.lower(), "thank you") or  chat_helper.checkAliases(message_val.lower(), "thx"):
        chat_helper.replyWith(message, "You're welcome.")
    elif chat_helper.checkAliases(message_val, "status Batty") or chat_helper.checkAliases(message_val, "status batty"):
        chat_helper.replyWith(message, "Batty [can barely use links](https://chat.stackoverflow.com/rooms/111347/conversation/batty-learns-how-to-use-links). She's not worthy of a flag rank *kappa*")
    elif "shrug" in message.content:
        chat_helper.replyWith(message, "🤷")
        # message.message.reply("¯\\ _(ツ)_/¯") This is the more ASCII-/Retro-version. Choose between the emoji and this one as you like
    elif "kappa" in message.content and "gif" in message.content:
        chat_helper.replyWith(message, "https://i.imgur.com/8TRbWHM.gif")
    #endregion



if __name__ == '__main__':
    main()