import getpass
import logging
import logging.handlers
import sys
import messagecompare
import flagbot.chathelper
from urllib.request import urlopen
from pyquery import PyQuery as pq
from html.parser import HTMLParser
from chatexchange.chatexchange.client import Client
from chatexchange.chatexchange.events import MessagePosted


logger = logging.getLogger(__name__)
bot_parent = 'chade_'
bot_machine = 'HP Envy (dev machine)'
bot_version = 'v0.3.1'
room_id = 163468 #Use 163468 for the debug room, and 111347 for SOBotics

def main():
    #setup_logging()

    #Setup start actions
    host_id = 'stackoverflow.com'
    email = "support@philnet.ch"#input("Email: ")
    password = "Where2see+"#getpass.getpass("Password: ")

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
        # We ignore non-message_posted events.
        return
    message_val = message.content

    #Here are the responses defined
    #region default bot commands
    if messagecompare.compareMessage(message_val, "alive"):
        print(message)
        message.message.reply("instance of {} is running on **{}/{}**".format(bot_version, bot_parent, bot_machine))
    elif messagecompare.compareMessage(message_val, "say"):
        print(message)
        room = client.get_room(room_id)
        room.send_message(message.content.split('say', 1)[1])
    elif messagecompare.compareMessage(message_val, "command") or messagecompare.compareMessage(message_val, "commands"):
        print(message)
        message.message.reply("You can find a list of my commands [here](https://github.com/SOBotics/FlaggersHall/wiki#commands)")
    #endregion
    elif messagecompare.compareMessage(message_val, "status mine"):
        print(message)
        page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.user.id))
        html = page.read().decode("utf-8")
        jQuery = pq(html)
        flagCount = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
        message.message.reply("You have {} helpful flags. [Ranks are coming soon, stay tuned!](https://github.com/SOBotics/FlaggersHall/issues/11)".format(flagCount))
        # message.message.reply("**This feature is not working yet!** You need [69] more helpful flags to get your next rank: **Burn the evil** (666 flags)") # original message, currently kept for historical reasons
    elif messagecompare.compareMessage(message_val, "status"):
        print(message)
        page = urlopen("https://stackoverflow.com/users/{}?tab=topactivity".format(message.content.split('status ', 1)[1]))
        html = page.read().decode("utf-8")
        jQuery = pq(html)
        flagCount = str(pq(jQuery(".g-col.g-row.fl-none").children()[6]).html()).replace('\n', ' ').replace('\r', '').strip().strip(" helpful flags")
        userName = str(pq(jQuery(".name")[0]).html()).replace('\n', ' ').replace('\r', '').strip()
        # Stripping mod markup from the name
        userName = strip_tags(userName)
        room = client.get_room(room_id)
        room.send_message("{} has {} helpful flags. [Ranks are coming soon, stay tuned!](https://github.com/SOBotics/FlaggersHall/issues/11)".format(userName, flagCount))

        #message.message.reply("Please specify whose status you want to get (for yourself it's `status mine`)")
    #region fun answers
    elif message.content.startswith("🚂"):
        print(message)
        room = client.get_room(room_id)
        room.send_message("🚃")
    elif messagecompare.compareMessage(message_val, "why"):
        print(message)
        message.message.reply("[Because of you](https://www.youtube.com/watch?v=Ra-Om7UMSJc)")
    elif messagecompare.compareMessage(message_val, "good bot"):
        print(message)
        message.message.reply("Thank you")
    elif messagecompare.compareMessage(message_val.lower(), "thanks") or messagecompare.compareMessage(message_val.lower(), "thank you") or  messagecompare.compareMessage(message_val.lower(), "thx"):
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


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

if __name__ == '__main__':
    main(*sys.argv[1:])
