import logging
import os
import sys
import threading
import traceback
from flagbot.utils import utils
from markdownify import markdownify as md
from chatexchange.chatexchange.client import Client
from chatexchange.chatexchange.events import MessagePosted, MessageEdited
import flagbot.flags as check_flags
import flagbot.redunda as redunda
import flagbot.se_api as stackexchange_api
#import flagbot.flags_auto_check as fac

#Import config file with custom error message
try:
    import config as config
except ModuleNotFoundError:
    raise Exception("The config module couldn't be imported. Have you renamed config.example.py to config.py?")

utils = utils()

def main():

    #Get config for the mode (debug/prod)
    try:
        if sys.argv[1] == '--debug':
            print("Loading debug config...")
            utils.config = config.debug_config
        else:
            raise IndexError
    except IndexError:
        print("Loading productive config... \nIf you wanted to load the debug config, use the '--debug' command line option")
        utils.config = config.prod_config

    #region Login and connection to chat
    utils.room_number = utils.config["room"]
    client = Client(utils.config["chatHost"])
    client.login(utils.config["email"], utils.config["password"])
    utils.client = client
    room = client.get_room(utils.config["room"])
    room.join()
    room.watch_socket(on_message)
    print(room.get_current_user_names())
    utils.room_owners = room.owners
    #endregion

    #Store current quota as variabke
    se_api = stackexchange_api.se_api(utils.config["stackExchangeApiKey"])
    quota_obj = se_api.get_user(1)
    if quota_obj['quota_remaining'] is not None:
        utils.quota = quota_obj['quota_remaining']

    logging.basicConfig(filename="CheckYerFlags.log", level=logging.INFO, filemode="a", format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    logging.getLogger("chatexchange").setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info("Joined room '{}' on {}".format(room.name, utils.config["chatHost"]))

    #region Background threads

    #Auto-Checking (currently disabled)
    """cu = room.get_current_users()
    nb = utils.id_list_without_bots(cu)

    thread_list = []

    stop_auto_checking_lp = threading.Event()
    auto_check_lp_thread = fac.AutoFlagThread(stop_auto_checking_lp, utils, utils.config, logging, 0, nb, thread_list)
    auto_check_lp_thread.start()
    thread_list.append(auto_check_lp_thread)

    stop_auto_checking_hp = threading.Event()
    auto_check_hp_thread = fac.AutoFlagThread(stop_auto_checking_hp, utils, utils.config, logging, 1, [], thread_list)
    auto_check_hp_thread.start()
    thread_list.append(auto_check_hp_thread)
    #auto_check_lp_thread.check_flags_lp()"""

    #Redunda pining
    stop_redunda = threading.Event()
    redunda_thread = redunda.RedundaThread(stop_redunda, utils.config, logging)
    redunda_thread.start()
    #endregion

    try:
        if sys.argv[1] == '--debug':
            room.send_message("[ [CheckYerFlags](https://stackapps.com/q/7792) ] started in debug mode.")
        else:
            raise IndexError
    except IndexError:
        room.send_message("[ [CheckYerFlags](https://stackapps.com/q/7792) ] started.")

    while True:
        message = input()

        if message in ["restart", "reboot"]:
            os._exit(1)
        else:
            room.send_message(message)

    #client.logout()
    #stop_redunda.set()

def on_message(message, client):
    if not isinstance(message, MessagePosted) and not isinstance(message, MessageEdited):
        # We ignore events that aren't MessagePosted or MessageEdited events.
        return

    #Check that the message object is defined
    if message is None or message.content is None:
        logging.warning("ChatExchange message object or content property is None.")
        logging.warning(message)
        return

    #Get message as full string and as single words
    message_val = message.content
    words = message.content.split()

    #If the bot account posted a message, store it's id
    if message.user.id == 9220325:
        utils.last_bot_message = message

    #Check for non-alias-command calls
    if message.content.startswith("🚂"):
        utils.log_command("train")
        utils.post_message("🚃")
    elif "shrug" in message_val:
        utils.log_command("shrug")
        utils.post_message("¯\\ \_(ツ)\_ /¯", True)
    elif "tableflip" in message_val or "table flip" in message_val:
        utils.log_command("tableflip")
        utils.post_message("(╯°□°）╯︵ ┻━┻", True)
    elif "unflip" in message_val:
        utils.log_command("unflip")
        utils.post_message("┬─┬ ノ( ゜-゜ノ)", True)
    elif "kappa.gif" in message_val:
        utils.log_command("kappa gif")
        utils.reply_with(message, "https://i.imgur.com/8TRbWHM.gif")

    #Check if alias is valid
    if not utils.alias_valid(words[0]):
        return

    #Store command in it's own variable
    command = words[1]
    full_command = ' '.join(words[1:])

    try:
        #Here are the commands defined
        if command in ["del", "delete", "poof"]:
            msg = client.get_message(utils.last_bot_message._message_id)
            if msg is not None:
                msg.delete()
        elif command in ["amiprivileged"]:
            utils.log_command("amiprivileged")

            if utils.is_privileged(message):
                utils.reply_with(message, "You are privileged.")
            else:
                utils.reply_with(message, "You are not privileged. Ping Filnor if you believe that's an error.")
        elif command in ["a", "alive"]:
            utils.log_command("alive")
            utils.reply_with(message, "Instance of {} is running on **{}/{}**".format(utils.config["botVersion"], utils.config["botParent"], utils.config["botMachine"]))
        elif command in ["v", "version"]:
            utils.log_command("version")
            utils.reply_with(message, "Current version is {}".format(utils.config["botVersion"]))
        elif command in ["say"]:
            utils.log_command("say")
            if message.user.id != 9220325: # Don't process commands by the bot account itself
                say_message = md(' '.join(map(str, words[2:])))
                utils.post_message(say_message)
        elif command in ["welcome"]:
            utils.log_command("welcome")
            #Only run in SOBotics
            if utils.room_number == 111347:
                message_ping = ""
                try:
                    user_to_ping = words[2]
                    message_ping = "@{} ".format(user_to_ping.replace("@", ""))
                except IndexError:
                    pass
                utils.post_message("{}Welcome to SOBotics! You can learn more about SOBotics and what we and [all the bots](https://sobotics.org/all-bots/) are doing here at our website, https://sobotics.org/. If you'd like to help out with flagging, reporting, or anything else, let us know! We have tons of [userscripts](https://sobotics.org/userscripts/) to make things easier, and you'll always find someone around who will help you to install them and explain how they work.".format(message_ping))
            else:
                utils.post_message("This command is not supported in this room")
        elif command in ["quota"]:
            utils.log_command("quota")
            utils.post_message("The remaining API quota is {}.".format(utils.quota))
        elif command in ["kill", "stop"]:
            utils.log_command("kill")
            logging.warning("Termination or stop requested by {}".format(message.user.name))

            if utils.is_privileged(message):
                try:
                    utils.client.get_room(utils.room_number).leave()
                except BaseException:
                    pass
                raise os._exit(0)
            else:
                utils.reply_with(message, "This command is restricted to moderators, room owners and maintainers.")
        elif command in ["leave", "bye"]:
            utils.log_command("leave")
            logging.warning("Leave requested by {}".format(message.user.name))

            # Restrict function to (site) moderators, room owners and maintainers
            if utils.is_privileged(message):
                utils.post_message("Bye")
                utils.client.get_room(utils.room_number).leave()
            else:
                utils.reply_with(message, "This command is restricted to moderators, room owners and maintainers.")
        elif command in ["commands", "help"]:
            utils.log_command("command list")
            utils.post_message("    ### CheckYerFlags commands ###\n" + \
                "    delete, del, poof            - Deletes the last posted message, if possible. Requires privileges.\n" + \
                "    amiprivileged                - Checks if you're allowed to run privileged commands\n" + \
                "    alive, a                     - Returns with the location and the running version of the bot, if it's running. No response likely means the bot is dead/not in this room.\n" + \
                "    version, v                   - Returns current version\n" + \
                "    say [message]                - Sends [message] as chat message\n" + \
                "    welcome [username]           - Post a chat room introduction message (only in SOBotics). If the username is specified, the user will also will get pinged.\n" + \
                "    quota                        - Returns the amount of remaining Stack Exchange API quota\n" + \
                "    kill, stop                   - Terminates the bot instance. Requires privileges.\n" + \
                "    leave, bye                   - Tells the bot to leave the chat room. A restart is required to use it again. Requires privileges.\n" + \
                "    commands, help               - This command. Lists all available commands\n" + \
                "    status mine, s m             - Gets your own flag rank and status to the next rank\n" + \
                "    status, s [user id]          - Gets flag rank and status to the next rank for the specified [user id]\n" + \
                "    ranks, ranks next, r n       - Gets your next flag rank and how much flags you need to get to it\n" + \
                "    why                          - Gives the answer to everything\n" + \
                "    good bot, good job           - Thanks you for being nice\n" + \
                "    ty, thx, thanks, thank you   - Replies \"You're welcome.\"", False, False)
        elif full_command in ["s m", "status mine"]:
            utils.log_command("status mine")
            check_flags.check_own_flags(message, utils)
        elif command in ["s", "status"] and full_command not in ["s m", "status mine"]:
            utils.log_command("status user id")
            check_flags.check_flags(None, utils, None, words[2])
        elif full_command in ["r", "ranks", "r n", "ranks next"]:
            utils.log_command("rank next")
            check_flags.check_own_flags_next_rank(message, utils)
        #region Fun commands
        elif command in ["why"]:
            utils.log_command("why")
            utils.reply_with(message, "[42.](https://en.wikipedia.org/wiki/Phrases_from_The_Hitchhiker%27s_Guide_to_the_Galaxy#Answer_to_the_Ultimate_Question_of_Life,_the_Universe,_and_Everything_(42))")
        elif full_command in ["good bot", "good job"]:
            utils.log_command("good bot")
            utils.reply_with(message, "Thank you!")
        elif full_command.lower() in ["ty", "thx", "thanks", "thank you"] :
            utils.log_command("thanks")
            utils.reply_with(message, "You're welcome.")
        #endregion
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
    except BaseException as e:
        logging.error("CRITICAL ERROR: {}".format(e))
        if message is not None and message.id is not None:
            logging.error("Caused by message id ".format(message.id))
            logging.error(traceback.format_exc())
        try:
            utils.post_message("Error on processing the last command ({}); rebooting instance... (cc @Filnor)".format(e))
            os._exit(1)

        except AttributeError:
            pass


if __name__ == '__main__':
    main()