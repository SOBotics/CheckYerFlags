import os
import sys
import threading
import traceback

import chatoverflow
from flagbot.logger import main_logger
from flagbot.utils import utils
from markdownify import markdownify as md
from chatoverflow.chatexchange.client import Client
from chatoverflow.chatexchange.events import MessagePosted, MessageEdited
import flagbot.flags as check_flags
import flagbot.redunda as redunda
import flagbot.se_api as stackexchange_api
import flagbot.flags_auto_check as fac

#Import config file with custom error message
try:
    import config as config
except ModuleNotFoundError:
    raise Exception("The config module couldn't be imported. Have you renamed config.example.py to config.py?")

utils = utils()

def main():
    """
    Main thread of the bot
    """
    debug_mode = False

    #Get config for the mode (debug/prod)
    try:
        if sys.argv[1] == "--debug":
            print("Loading debug config...")
            utils.config = config.debug_config
            debug_mode = True
        else:
            raise IndexError
    except IndexError:
        print("Loading productive config... \nIf you wanted to load the debug config, use the '--debug' command line option")
        utils.config = config.prod_config

    try:
        #Login and connection to chat
        print("Logging in and joining chat room...")
        utils.room_number = utils.config["room"]
        client = Client(utils.config["chatHost"])
        client.login(utils.config["email"], utils.config["password"])
        utils.client = client
        room = client.get_room(utils.config["room"])
        try:
            room.join()
        except ValueError as e:
            if str(e).startswith("invalid literal for int() with base 10: 'login?returnurl=http%3a%2f%2fchat.stackoverflow.com%2fchats%2fjoin%2ffavorite"):
                raise chatoverflow.chatexchange.browser.LoginError("To many recent logins. Please wait a bit and try again.")

        room.watch_socket(on_message)
        print(room.get_current_user_names())
        utils.room_owners = room.owners

        #Store current quota as variable
        se_api = stackexchange_api.se_api(utils.config["stackExchangeApiKey"])
        quota_obj = se_api.get_user(1)
        if quota_obj['quota_remaining'] is not None:
            utils.quota = quota_obj['quota_remaining']

        main_logger.info(f"Joined room '{room.name}' on {utils.config['chatHost']}")

        #Automated flag checking
        """thread_list = []

        stop_auto_checking_lp = threading.Event()
        auto_check_lp_thread = fac.AutoFlagThread(stop_auto_checking_lp, utils, utils.config, 0, room, thread_list)
        auto_check_lp_thread.start()
        thread_list.append(auto_check_lp_thread)

        stop_auto_checking_hp = threading.Event()
        auto_check_hp_thread = fac.AutoFlagThread(stop_auto_checking_hp, utils, utils.config, 1, None, thread_list)
        auto_check_hp_thread.start()
        thread_list.append(auto_check_hp_thread)"""

        #Redunda pining
        stop_redunda = threading.Event()
        redunda_thread = redunda.RedundaThread(stop_redunda, utils.config, main_logger)
        redunda_thread.start()

        if debug_mode:
            room.send_message(f"[ [CheckYerFlags](https://stackapps.com/q/7792) ] {utils.config['botVersion']} started in debug mode on {utils.config['botParent']}/{utils.config['botMachine']}.")
        else:
            room.send_message(f"[ [CheckYerFlags](https://stackapps.com/q/7792) ] {utils.config['botVersion']} started on {utils.config['botParent']}/{utils.config['botMachine']}.")


        while True:
            message = input()

            if message in ["restart", "reboot"]:
                os._exit(1)
            else:
                room.send_message(message)

    except KeyboardInterrupt:
        os._exit(0)
    except BaseException as e:
        print(e)
        os._exit(1)

def on_message(message, client):
    """
    Handling the event if a message was posted, edited or deleted
    """
    if not isinstance(message, MessagePosted) and not isinstance(message, MessageEdited):
        # We ignore events that aren't MessagePosted or MessageEdited events.
        return

    #Check that the message object is defined
    if message is None or message.content is None:
        main_logger.warning("ChatExchange message object or content property is None.")
        main_logger.warning(message)
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
    elif message.content.lower().startswith("@bots alive"):
        utils.log_command("@bots alive")
        utils.post_message("You doubt me?")
    elif "/shrug" in message_val:
        utils.log_command("shrug")
        utils.post_message("¯\\ \_(ツ)\_ /¯", True)
    elif "/tableflip" in message_val:
        utils.log_command("tableflip")
        utils.post_message("(╯°□°）╯︵ ┻━┻", True)
    elif "/unflip" in message_val:
        utils.log_command("unflip")
        utils.post_message("┬─┬ ノ( ゜-゜ノ)", True)
    elif "/kappa.gif" in message_val:
        utils.log_command("kappa gif")
        utils.reply_to(message, "https://i.imgur.com/8TRbWHM.gif")

    #Check if alias is valid
    if not utils.alias_valid(words[0]):
        return

    #Check if command is not set
    if len(words) <= 1:
        utils.reply_to(message, "Huh?")
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
                utils.reply_to(message, "You are privileged.")
            else:
                utils.reply_to(message, "You are not privileged. Ping Filnor if you believe that's an error.")
        elif command in ["a", "alive"]:
            utils.log_command("alive")
            utils.reply_to(message, "You doubt me?")
        elif command in ["v", "version"]:
            utils.log_command("version")
            utils.reply_to(message, f"Current version is {utils.config['botVersion']}")
        elif command in ["loc", "location"]:
            utils.log_command("location")
            utils.reply_to(message, f"This instance is running on {utils.config['botParent']}/{utils.config['botMachine']}")
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
                    message_ping = f"@{user_to_ping.replace('@', '')} "
                except IndexError:
                    pass
                utils.post_message(f"{message_ping}Welcome to SOBotics! You can learn more about SOBotics and what we and [all the bots](https://sobotics.org/all-bots/) are doing here at our website, https://sobotics.org/. If you'd like to help out with flagging, reporting, or anything else, let us know! We have tons of [userscripts](https://sobotics.org/userscripts/) to make things easier, and you'll always find someone around who will help you to install them and explain how they work.")
            else:
                utils.post_message("This command is not supported in this room")
        elif command in ["quota"]:
            utils.log_command("quota")
            utils.post_message(f"The remaining API quota is {utils.quota}.")
        elif command in ["kill", "stop"]:
            utils.log_command("kill")
            main_logger.warning(f"Termination or stop requested by {message.user.name}")

            if utils.is_privileged(message):
                try:
                    utils.client.get_room(utils.room_number).leave()
                except BaseException:
                    pass
                raise os._exit(0)
            else:
                utils.reply_to(message, "This command is restricted to moderators, room owners and maintainers.")
        elif command in ["leave", "bye"]:
            utils.log_command("leave")
            main_logger.warning(f"Leave requested by {message.user.name}")

            # Restrict function to (site) moderators, room owners and maintainers
            if utils.is_privileged(message):
                utils.post_message("Bye")
                utils.client.get_room(utils.room_number).leave()
            else:
                utils.reply_to(message, "This command is restricted to moderators, room owners and maintainers.")
        elif command in ["update"]:
            utils.log_command("update")

            # Restrict function to (site) moderators, room owners and maintainers
            if message.user.id is 4733879:
                utils.post_message("Pulling from GitHub...")
                os.system("git config core.fileMode false")
                os.system("git pull")
            else:
                utils.reply_to(message, "This command is restricted to bot maintainers.")
        elif command in ["reboot"]:
            utils.log_command("reboot")
            main_logger.warning(f"Reboot requested by {message.user.name}")

            if utils.is_privileged(message):
                try:
                    utils.post_message("Rebooting now...")
                    utils.client.get_room(utils.room_number).leave()
                except BaseException:
                    pass
                raise os._exit(1)
            else:
                utils.reply_to(message, "This command is restricted to moderators, room owners and maintainers.")
        elif command in ["commands", "help"]:
            utils.log_command("command list")
            utils.post_message("    ### CheckYerFlags commands ###\n" + \
                               "    delete, del, poof            - Deletes the last posted message, if possible. Requires privileges.\n" + \
                               "    amiprivileged                - Checks if you're allowed to run privileged commands\n" + \
                               "    alive, a                     - Replies with a message if the bot.\n" + \
                               "    version, v                   - Returns current version\n" + \
                               "    say [message]                - Sends [message] as chat message\n" + \
                               "    welcome [username]           - Post a chat room introduction message (only in SOBotics). If the username is specified, the user will also will get pinged.\n" + \
                               "    quota                        - Returns the amount of remaining Stack Exchange API quota\n" + \
                               "    kill, stop                   - Stops the bot. Requires privileges.\n" + \
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
        elif command in ["why"]:
            utils.log_command("why")
            utils.reply_to(message, "[42.](https://en.wikipedia.org/wiki/Phrases_from_The_Hitchhiker%27s_Guide_to_the_Galaxy#Answer_to_the_Ultimate_Question_of_Life,_the_Universe,_and_Everything_(42))")
        elif full_command in ["good bot", "good job"]:
            utils.log_command("good bot")
            utils.reply_to(message, "Thank you!")
        elif full_command.lower() in ["ty", "thx", "thanks", "thank you"] :
            utils.log_command("thanks")
            utils.reply_to(message, "You're welcome.")
        elif full_command.lower() in ["code", "github", "source"] :
            utils.log_command("code")
            utils.reply_to(message, "My code is on GitHub [here](https://github.com/SOBotics/FlaggersHall).")
        elif full_command.lower() in ["leaderboard", "scoreboard", "sb"] :
            utils.log_command("code")
            utils.reply_to(message, "The leaderboard will come soon.")
    except BaseException as e:
        main_logger.error(f"CRITICAL ERROR: {e}")
        if message is not None and message.id is not None:
            main_logger.error(f"Caused by message id {message.id}")
            main_logger.error(traceback.format_exc())
        try:
            utils.post_message(f"Error on processing the last command ({e}); rebooting instance... (cc @Filnor)")
            os._exit(1)

        except AttributeError:
            os._exit(1)
            pass


if __name__ == '__main__':
    main()
