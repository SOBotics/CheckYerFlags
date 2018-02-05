import getpass
import logging
import logging.handlers
import sys
import flagbot.html_parser as html_parser
from flagbot.chat_helper import chat_helper

from urllib.request import urlopen
from pyquery import PyQuery as pq

from chatexchange.chatexchange.client import Client
from chatexchange.chatexchange.events import MessagePosted


logger = logging.getLogger(__name__)
bot_parent = 'chade_'
bot_machine = 'HP Envy (dev machine)'
bot_version = 'v0.4 [Name: The fractured but whole]'
room_id = 163468 #Use 163468 for the debug room, and 111347 for SOBotics
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

    print("(You are now in room #%s on %s.)" % (room_id, host_id))
    while True:
        message = input("<< ")
        room.send_message(message)

    client.logout()

def on_message(message, client):
    if not isinstance(message, MessagePosted):
        # We ignore non-message_posted events.
        return
    message_val = message.content

    #Here are the responses defined
    #region default bot commands
    if chat_helper.checkAliases(message_val, "alive"):
        print(message)
        message.message.reply("instance of {} is running on **{}/{}**".format(bot_version, bot_parent, bot_machine))
    elif chat_helper.checkAliases(message_val, "say"):
        print(message)
        room = client.get_room(room_id)
        room.send_message(message.content.split('say', 1)[1])
    elif chat_helper.checkAliases(message_val, "command") or chat_helper.checkAliases(message_val, "commands"):
        print(message)
        message.message.reply("You can find a list of my commands [here](https://github.com/SOBotics/FlaggersHall/wiki#commands)")
    #endregion
    elif chat_helper.checkAliases(message_val, "status mine"):
        print(message)
        page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.user.id))
        html = page.read().decode("utf-8")
        jQuery = pq(html)
        flagCount = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
        message.message.reply("You have {} helpful flags. Ranks are coming soon, you can suggest levels [here](https://github.com/SOBotics/FlaggersHall/issues/11)!".format(flagCount))
        # message.message.reply("**This feature is not working yet!** You need [69] more helpful flags to get your next rank: **Burn the evil** (666 flags)") # original message, currently kept for historical reasons
    elif chat_helper.checkAliases(message_val, "status"):
        print(message)
        page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.content.split('status ', 1)[1]))
        html = page.read().decode("utf-8")
        jQuery = pq(html)
        flagCount = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
        userName = str(pq(jQuery(".name")[0]).html()).replace('\n', ' ').replace('\r', '').strip()
        # Stripping mod markup from the name
        userName = html_parser.strip_tags(userName)
        room = client.get_room(room_id)
        room.send_message("{} has {} helpful flags. [Ranks are coming soon, stay tuned!](https://github.com/SOBotics/FlaggersHall/issues/11)".format(userName, flagCount))

        #message.message.reply("Please specify whose status you want to get (for yourself it's `status mine`)")
    #region fun answers
    elif message.content.startswith("🚂"):
        print(message)
        room = client.get_room(room_id)
        room.send_message("🚃")
    elif chat_helper.checkAliases(message_val, "why"):
        print(message)
        message.message.reply("[Because of you](https://www.youtube.com/watch?v=Ra-Om7UMSJc)")
    elif chat_helper.checkAliases(message_val, "good bot"):
        print(message)
        message.message.reply("Thank you")
    elif chat_helper.checkAliases(message_val.lower(), "thanks") or chat_helper.checkAliases(message_val.lower(), "thank you") or  chat_helper.checkAliases(message_val.lower(), "thx"):
        print(message)
        message.message.reply("You're welcome.")
    elif chat_helper.checkAliases(message_val, "status Batty") or chat_helper.checkAliases(message_val, "status batty"):
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



if __name__ == '__main__':
    main(*sys.argv[1:])
