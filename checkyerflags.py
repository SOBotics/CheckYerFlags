import logging
import sys
import json
import io
import gzip
import threading

import flagbot.check_flags as check_flags
import flagbot.redunda as redunda
import config as config

from flagbot.utils import utils
from urllib.request import urlopen
from markdownify import markdownify as md
from chatexchange.chatexchange.client import Client
from chatexchange.chatexchange.events import MessagePosted, MessageEdited

utils = utils()

def main():

    #Get config for the mode (debug/prod)
    if input("Mode (use d for debug, leave blank for productive): ") is "d":
        print("Loading debug config...")
        utils.config = config.debugConfig
    else:
        print("Loading productive config...")
        utils.config = config.prodConfig

    utils.roomNumber = utils.config["room"]

    client = Client(utils.config["chatHost"])
    client.login(utils.config["email"], utils.config["password"])
    utils.client = client

    room = client.get_room(utils.config["room"])
    room.join()
    room.watch(on_message)
    print(room.get_current_user_names())

    quota_obj = json.loads(gzip.GzipFile(fileobj=io.BytesIO(urlopen("https://api.stackexchange.com/2.2/users/1?order=desc&sort=reputation&site=stackoverflow&key={}".format(utils.config["stackExchangeApiKey"])).read())).read().decode("utf-8"))


    if quota_obj['quota_remaining'] is not None:
        utils.quota = quota_obj['quota_remaining']

    logging.basicConfig(filename="CheckYerFlags.log", level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info("Joined room '{}' on {}".format(room.name, utils.config["chatHost"]))

    #Run Redunda reporting on a seperate thread/in the background
    stop_redunda = threading.Event()
    redunda_thread = redunda.RedundaThread(stop_redunda, utils.config, logging)
    redunda_thread.start()
    room.send_message("[ [CheckYerFlags](https://stackapps.com/q/7792) ] started.")

    while True:
        message = input("<< ")
        room.send_message(message)

    #client.logout()
    #stop_redunda.set()

def on_message(message, client):
    if not isinstance(message, MessagePosted) and not isinstance(message, MessageEdited):
        # We ignore non-MessagePosted events.
        return
    message_val = message.content

    try:
        #Here are the responses defined
        #region Default bot commands
        if utils.checkAliases(message_val, "alive"):
            utils.replyWith(message, "instance of {} is running on **{}/{}**".format(utils.config["botVersion"], utils.config["botParent"], utils.config["botMachine"]))
        elif utils.checkAliases(message_val, "v") or utils.checkAliases(message_val, "version"):
            utils.replyWith(message, "Current version is {}".format(utils.config["botVersion"]))
        elif utils.checkAliases(message_val, "say"):
            if message.user.id != 9220325: # Don't process commands by the bot account itself
                say_message = md(message.content.split('say', 1)[1])
                utils.postMessage(say_message)
        elif utils.checkAliases(message_val, "welcome"):
            utils.postMessage("Welcome to SOBotics! You can learn more about SOBotics and what we and [all the bots](https://sobotics.org/all-bots/) are doing here at our website, https://sobotics.org/. If you'd like to help out with flagging, reporting, or anything else, let us know! We have tons of [userscripts](https://sobotics.org/userscripts/) to make things easier, and you'll always find someone around who will help you to install them and explain how they work.")
        elif utils.checkAliases(message_val, "quota"):
            utils.postMessage("The remaining API quota is {}.".format(utils.quota))
        elif utils.checkAliases(message_val, "command") or utils.checkAliases(message_val, "commands"):
            utils.replyWith(message, "You can find a list of my commands [here](https://github.com/SOBotics/FlaggersHall/wiki#commands)")
        #endregion
        elif utils.checkAliases(message_val, "status mine") or utils.checkAliases(message_val, "s mine"):
            check_flags.checkOwnFlags(message, utils)
        elif utils.checkAliases(message_val, "status") or utils.checkAliases(message_val, "s"):
            check_flags.checkFlags(message, utils)
        elif utils.checkAliases(message_val, "ranks"):
            utils.replyWith(message, "A list of all ranks is available [here](https://github.com/SOBotics/FlaggersHall/issues/11). Feel free to leave a suggestion there!")
        elif utils.checkAliases(message_val, "ranks next"):
            utils.replyWith(message, "I'm sorry, but this command is not functional yet. Please [check this issue on GitHub](https://github.com/SOBotics/FlaggersHall/issues/17) for updates.")
        #region Fun commands
        elif message.content.startswith("🚂"):
            utils.postMessage("🚃")
        elif utils.checkAliases(message_val, "why"):
            utils.replyWith(message, "[Because of you](https://www.youtube.com/watch?v=Ra-Om7UMSJc)")
        elif utils.checkAliases(message_val, "good bot"):
            utils.replyWith(message, "Thank you")
        elif utils.checkAliases(message_val.lower(), "thanks") or utils.checkAliases(message_val.lower(), "thank you") or  utils.checkAliases(message_val.lower(), "thx"):
            utils.replyWith(message, "You're welcome.")
        elif "shrug" in message.content:
            utils.replyWith(message, "🤷")
        elif "kappa.gif" in message.content:
            utils.replyWith(message, "https://i.imgur.com/8TRbWHM.gif")
        #endregion
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as e:
        logging.error("CRITICAL ERROR: {}".format(e))
        try:
            utils.postMessage("Error on processing the last command ({}); restarted. (cc @chade_)".format(e))
        except AttributeError:
            pass


if __name__ == '__main__':
    main()