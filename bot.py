import os
import sys
import threading
import traceback

import git
from markdownify import markdownify as md

import chatoverflow
import checkyerflags.check_flags as check_flags
import checkyerflags.flags_auto_check as fac
import checkyerflags.se_api as stackexchange_api
from chatoverflow.chatexchange.client import Client
from chatoverflow.chatexchange.events import MessagePosted, MessageEdited
from checkyerflags import redunda, custom_goals
from checkyerflags.check_flags import InvalidUserIdError, NoApiKeyError, NonExistentUserIdError, NotEnoughFlagsError
from checkyerflags.logger import main_logger
from checkyerflags.utils import utils, Struct

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
            print("Using debug config.")
            utils.config = Struct(**config.debug_config)
            debug_mode = True
        else:
            raise IndexError
    except IndexError:
        print("Using productive config. \nIf you intended to use the debug config, use the '--debug' command line option")
        utils.config = Struct(**config.prod_config)

    #Set version
    utils.config.botVersion = "v1.6.0"

    #Initialize SE API class instance
    utils.se_api = stackexchange_api.se_api(utils.config.stackExchangeApiKey)

    try:
        #Login and connection to chat
        print("Logging in and joining chat room...")
        utils.room_number = utils.config.room
        client = Client(utils.config.chatHost)
        client.login(utils.config.email, utils.config.password)
        utils.client = client
        room = client.get_room(utils.config.room)
        try:
            room.join()
        except ValueError as e:
            if str(e).startswith("invalid literal for int() with base 10: 'login?returnurl=http%3a%2f%2fchat.stackoverflow.com%2fchats%2fjoin%2ffavorite"):
                raise chatoverflow.chatexchange.browser.LoginError("Too many recent logins. Please wait a bit and try again.")

        room.watch_socket(on_message)
        print(room.get_current_user_names())
        utils.room_owners = room.owners

        main_logger.info(f"Joined room '{room.name}' on {utils.config.chatHost}")

        #Automated flag checking
        thread_list = []

        stop_auto_checking_lp = threading.Event()
        auto_check_lp_thread = fac.AutoFlagThread(stop_auto_checking_lp, utils, 0, room, thread_list)
        auto_check_lp_thread.start()
        thread_list.append(auto_check_lp_thread)

        stop_auto_checking_hp = threading.Event()
        auto_check_hp_thread = fac.AutoFlagThread(stop_auto_checking_hp, utils, 1, None, thread_list)
        auto_check_hp_thread.start()
        thread_list.append(auto_check_hp_thread)

        #Redunda pining
        stop_redunda = threading.Event()
        redunda_thread = redunda.RedundaThread(stop_redunda, utils.config, main_logger)
        redunda_thread.start()

        if debug_mode:
            room.send_message(f"[ [CheckYerFlags](https://stackapps.com/q/7792) ] {utils.config.botVersion} started in debug mode on {utils.config.botOwner}/{utils.config.botMachine}.")
        else:
            room.send_message(f"[ [CheckYerFlags](https://stackapps.com/q/7792) ] {utils.config.botVersion} started on {utils.config.botOwner}/{utils.config.botMachine}.")


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
        try:
            if message.user.id is 6294609:
                return
        except AttributeError:
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
        utils.post_message("[🚃](https://youtu.be/943gMyU5-PQ)")
    elif message.content.lower().startswith("@bots alive"):
        utils.log_command("@bots alive")
        utils.post_message("Yep, I'm fine.")
    elif "shrug" in message_val:
        utils.log_command("shrug")
        utils.post_message("¯\\ \_(ツ)\_ /¯", log_message=False)
    elif "/tableflip" in message_val:
        utils.log_command("tableflip")
        utils.post_message("(╯°□°）╯︵ ┻━┻", log_message=False)
    elif "/unflip" in message_val:
        utils.log_command("unflip")
        utils.post_message("┬─┬ ノ( ゜-゜ノ)", log_message=False)
    elif "/kappa" in message_val:
        utils.log_command("kappa")
        message.reply_to("https://i.imgur.com/8TRbWHM.gif")
    elif "After a happy meal, feeds @PaulStenne now" in message_val:
        utils.log_command("ping war")
        utils.post_message("@BhargavRao, it's your turn to wash the dishes.")
    elif "I think it is better to wait till @Filnor and @PaulStenne finishes their meals." in message_val:
        utils.log_command("ping war")
        utils.post_message("We will be changing plates for dessert, so get @BhargavRao working! Maybe @PetterFriberg wants to help you?")

    #Check if alias is valid
    if not utils.alias_valid(words[0]):
        return

    #Check if command is not set
    if len(words) <= 1:
        message.reply_to("Huh?")
        return

    #Store command in it's own variable
    command = words[1]
    full_command = ' '.join(words[1:])
    utils.log_command(full_command)

    try:
        #Here are the commands defined
        if command in ["del", "delete", "poof"]:
            msg = client.get_message(message.parent_message_id)
            if msg is not None:
                if utils.is_privileged(message):
                    msg.delete()
                else:
                    message.reply_to("This command is restricted to moderators, room owners and maintainers.")
        elif command in ["amiprivileged", "aip", "privs"]:
            if utils.is_privileged(message):
                message.reply_to("You are privileged.")
            else:
                message.reply_to(f"You are not privileged. Ping {utils.config.botOwner} if that doesn't makes sense to you.")
        elif command in ["a", "alive"]:
            message.reply_to("You doubt me?")
        elif command in ["v", "version"]:
            message.reply_to(f"Current version is {utils.config.botVersion}")
        elif command in ["loc", "location"]:
            message.reply_to(f"This instance is running on {utils.config.botOwner}/{utils.config.botMachine}")
        elif command in ["say"]:
            if message.user.id != 9220325: # Don't process commands by the bot account itself to prevent abuse of the say command
                say_message = md(' '.join(map(str, words[2:])))
                utils.post_message(say_message)
        elif command in ["welcome"]:
            #Only run in SOBotics
            if utils.room_number == 111347:
                message_ping = ""
                try:
                    user_to_ping = words[2]
                    message_ping = f"@{user_to_ping.replace('@', '')} "
                except IndexError:
                    pass
                utils.post_message(f"{message_ping}Welcome to SOBotics! You can learn more about SOBotics and what we and [all the bots](https://sobotics.org/all-bots/) are doing here at our website, https://sobotics.org/. If you'd like to help out with flagging, reporting, or anything else, let us know! We have tons of [userscripts](https://sobotics.org/userscripts/) to make things easier, and you'll always find someone around who will help you to install them and explain how they work. Also make sure to check out [our GitHub page](https://github.com/sobotics).")
            else:
                utils.post_message("This command is not supported in this room.")
        elif command in ["quota"]:
            utils.post_message(f"The remaining API quota is {utils.se_api.check_quota()}.")
        elif command in ["kill", "stop"]:
            main_logger.warning(f"Stop requested by {message.user.name}")

            if utils.is_privileged(message):
                try:
                    utils.post_message("I'll be back!")
                    utils.client.get_room(utils.room_number).leave()
                except BaseException:
                    pass
                raise os._exit(0)
            else:
                message.reply_to("This command is restricted to moderators, room owners and maintainers.")
        elif command in ["standby", "sb"]:
            main_logger.warning(f"Leave requested by {message.user.name}")

            # Restrict function to (site) moderators, room owners and maintainers
            if utils.is_privileged(message):
                utils.post_message("I'll be back!")
                utils.client.get_room(utils.room_number).leave()
            else:
                message.reply_to("This command is restricted to moderators, room owners and maintainers.")
        elif command in ["reboot", "restart"]:
            main_logger.warning(f"Reboot requested by {message.user.name}")

            if utils.is_privileged(message):
                try:
                    utils.post_message("Rebooting now...")
                    utils.client.get_room(utils.room_number).leave()
                except BaseException:
                    pass
                raise os._exit(1)
            else:
                message.reply_to("This command is restricted to moderators, room owners and maintainers.")
        elif command in ["commands", "help"]:
            utils.post_message("    ### CheckYerFlags commands ###\n" + \
                               "    del[ete], poof               - Deletes the last posted message, if possible. Requires privileges.\n" + \
                               "    amiprivileged                - Checks if you're allowed to run privileged commands\n" + \
                               "    a[live]                      - Replies with a message if the bot.\n" + \
                               "    v[ersion]                    - Returns current version\n" + \
                               "    loc[ation]                   - Returns current location where the bot is running\n" + \
                               "    say <message>                - Sends [message] as chat message\n" + \
                               "    welcome <username>           - Post a chat room introduction message (only in SOBotics). If the username is specified, the user will also will get pinged.\n" + \
                               "    quota                        - Returns the amount of remaining Stack Exchange API quota\n" + \
                               "    kill, stop                   - Stops the bot. Requires privileges.\n" + \
                               "    standby, sb                  - Tells the bot to go to standby mode. That means it leaves the chat room and a bot maintainer need to issue a restart manually. Requires privileges.\n" + \
                               "    restart, reboot              - Restarts the bot. Requires privileges.\n" + \
                               "    commands, help               - This command. Lists all available commands\n" + \
                               "    s[tatus] m[ine]              - Gets your own flag rank and status to the next rank\n" + \
                               "    s[tatus] <user id>           - Gets flag rank and status to the next rank for the specified <user id>\n" + \
                               "    goal                         - Returns the value for the custom goal you have set\n" + \
                               "    goal <flag count>            - Set your custom goal to <flag count> flags\n" + \
                               "    goal del[ete]                - Deletes our custom goal\n" + \
                               "    ranks, ranks next, r n       - Gets your next flag rank and how much flags you need to get to it\n" + \
                               "    uptime                       - Returns how long the bot is running\n" + \
                               "    update                       - Updates the bot to the latest commit git and restart it. Requires owner privileges.\n" + \
                               "    system                       - Returns uptime, location and api quota\n" + \
                               "    why                          - Gives the answer to everything\n" + \
                               "    good bot, good job           - Thanks you for being nice\n" + \
                               "    ty, thx, thanks, thank you   - Replies \"You're welcome.\"", log_message=False, length_check=False)
        elif full_command in ["s m", "status mine"]:
            flag_count = 0
            try:
                flag_count = check_flags.get_flag_count_for_user(message.user.id, utils)
            except NoApiKeyError:
                main_logger.error("No API Key specified, unable to check flags")
                message.reply_to("No API Key specified, unable to check flags")
                return
            except InvalidUserIdError:
                message.reply_to("The specfied argument for the user id is not correct. Only digits are allowed.")
                return
            except NonExistentUserIdError:
                message.reply_to("The specfied user id does not belong to an existing user.")
                return
            except (IndexError, ValueError) as e:
                utils.post_message(f"Error while parsing flag count. (cc @{utils.config.botOwner})")
                return

            try:
                current_flag_rank = check_flags.get_current_flag_rank(flag_count)
                next_flag_rank = Struct(**check_flags.get_next_flag_rank(current_flag_rank))
                current_flag_rank = Struct(**current_flag_rank)
                flag_count_difference = next_flag_rank.count - flag_count
            except NotEnoughFlagsError:
                message.reply_to(f"You have {flag_count} helpful flags. Appears that you are not flagging that much.")
                return
            current_rank_description = ""
            if current_flag_rank.description is not None:
                current_rank_description = f" ({current_flag_rank.description})"
            message.reply_to(f"You have {flag_count} helpful flags. Your last achieved rank was **{current_flag_rank.title}**{current_rank_description} for {current_flag_rank.count} helpful flags. You need {flag_count_difference} more flags for your next rank, *{next_flag_rank.title}*.")
        elif command in ["s", "status"] and full_command not in ["s m", "status mine"]:
            flag_count = 0
            user_name = ""
            try:
                flag_count = check_flags.get_flag_count_for_user(words[2], utils)
                user_name = check_flags.get_user_name(words[2], utils)
            except NoApiKeyError:
                main_logger.error("No API Key specified, unable to check flags")
                message.reply_to("No API Key specified, unable to check flags")
                return
            except InvalidUserIdError:
                message.reply_to("The specfied argument for the user id is not correct. Only digits are allowed.")
                return
            except NonExistentUserIdError:
                message.reply_to("The specfied user id does not belong to an existing user.")
                return
            except (IndexError, ValueError) as e:
                utils.post_message(f"Error while parsing flag count. (cc @{utils.config.botOwner})")
                return
            except BaseException as e:
                utils.post_message(f"Critical Error: {e}")
                return

            try:
                current_flag_rank = check_flags.get_current_flag_rank(flag_count)
                next_flag_rank = Struct(**check_flags.get_next_flag_rank(current_flag_rank))
                current_flag_rank = Struct(**current_flag_rank)
                flag_count_difference = next_flag_rank.count - flag_count
            except NotEnoughFlagsError:
                utils.post_message(f"{user_name} has {flag_count} helpful flags. Appears that they are not flagging that much.")
                return
            current_rank_description = ""
            if current_flag_rank.description is not None:
                current_rank_description = f" ({current_flag_rank.description})"
            utils.post_message(f"{user_name} has {flag_count} helpful flags. Their last achieved rank was **{current_flag_rank.title}**{current_rank_description} for {current_flag_rank.count} helpful flags. They need {flag_count_difference} more flags for their next rank, *{next_flag_rank.title}*.")
        elif full_command in ["r", "ranks", "r n", "ranks next"]:
            flag_count = 0
            try:
                flag_count = check_flags.get_flag_count_for_user(message.user.id, utils)
            except NoApiKeyError:
                main_logger.error("No API Key specified, unable to check flags")
                message.reply_to("No API Key specified, unable to check flags")
                return
            except InvalidUserIdError:
                message.reply_to("The specfied argument for the user id is not correct. Only digits are allowed.")
                return
            except NonExistentUserIdError:
                message.reply_to("The specfied user id does not belong to an existing user.")
                return
            except (IndexError, ValueError) as e:
                utils.post_message(f"Error while parsing flag count. (cc @{utils.config.botOwner})")
                return

            flag_count_difference = None
            try:
                current_flag_rank = check_flags.get_current_flag_rank(flag_count)
                next_flag_rank = Struct(**check_flags.get_next_flag_rank(current_flag_rank))
                current_flag_rank = Struct(**current_flag_rank)
                flag_count_difference = next_flag_rank.count - flag_count
            except NotEnoughFlagsError:
                first_flag_rank = Struct(**check_flags.get_current_flag_rank(365))
                if flag_count_difference is None:
                    flag_count_difference = first_flag_rank.count

                message.reply_to(f"You need {flag_count_difference} more flags to get your first flag rank, **{first_flag_rank.title}** ({first_flag_rank.count} flags in total).")
                return
            next_rank_description = ""
            if current_flag_rank.description is not None:
                next_rank_description = f" ({next_flag_rank.description})"
            message.reply_to(f"You need {flag_count_difference} more flags to get your next flag rank, **{next_flag_rank.title}**{next_rank_description} ({next_flag_rank.count} flags in total).")
        elif command in ["why"]:
            message.reply_to("[42.](https://en.wikipedia.org/wiki/Phrases_from_The_Hitchhiker%27s_Guide_to_the_Galaxy#Answer_to_the_Ultimate_Question_of_Life,_the_Universe,_and_Everything_(42))")
        elif full_command in ["good bot", "good job"]:
            message.reply_to("Thank you!")
        elif full_command.lower() in ["ty", "thx", "thanks", "thank you"] :
            message.reply_to("You're welcome.")
        elif full_command.lower() in ["code", "github", "source"] :
            message.reply_to("My code is on GitHub [here](https://github.com/SOBotics/CheckYerFlags).")
        elif command in ["leaderboard", "scoreboard", "sb"] :
            message.reply_to("You can find the scoreboard [here](https://rankoverflow.philnet.ch/scoreboard). Note that loading the data takes about 15 seconds.")
        elif command in ["goal"]:
            goal_flag_count = 0
            user_id = message.user.id
            overwrite = False

            try:
                if words[3] in ["--force", "--overwrite"]:
                    overwrite = True
            except IndexError: pass

            try:
                goal_flag_count = words[2]
                custom_message = None
                try:
                    msg = ""
                    for word in words[3:]:
                        msg = f"{msg} {word}"
                    custom_message = msg.lstrip()
                except IndexError:
                    pass

                #Validate if given parameter als
                if goal_flag_count.isdigit() or goal_flag_count in ["del", "delete"]:
                    goal_flag_count = int(goal_flag_count)

                else:
                    message.reply_to("Please pass an integer number as parameter")
                    return

                #Check if the user has not already reached this amount of flags
                current_flag_count = check_flags.get_flag_count_for_user(user_id, utils)
                if goal_flag_count <= current_flag_count:
                    message.reply_to(f"Your custom goal must be higher than your current flag count, which is {current_flag_count}.")
                    return

                #Add or overwrite
                add_result = custom_goals.add_custom_goal(user_id, goal_flag_count, custom_message, overwrite)
                if add_result[0]:
                    message.reply_to(f"Set custom goal to {goal_flag_count} helpful flags.")
                else:
                    message.reply_to(f"You already have a custom rank set to {add_result[1]} helpful flags. Append the `--force` parameter to overwrite the rank")

            except IndexError:
                current_flag_count = check_flags.get_flag_count_for_user(user_id, utils)
                custom_goal = custom_goals.get_custom_goal_for_user(user_id)
                if custom_goal is None:
                    message.reply_to("You haven't set a custom goal currently.")
                    return
                goal_flag_count = custom_goal[0]
                flags_to_goal = goal_flag_count - current_flag_count

                goal_message = ""
                if custom_goal[1] not in ['', 'None']:
                    goal_message = f" You set '{custom_goal[1]}' as your custom message."

                if goal_flag_count is not None:
                    message.reply_to(f"Your custom goal is set to {goal_flag_count} helpful flags. You need {flags_to_goal} more flags to reach it.{goal_message}")
                else:
                    message.reply_to("You haven't set a custom goal currently.")
                return
            except ValueError:
                if words[2] in ["del", "delete"]:
                    if custom_goals.delete_custom_goal(user_id):
                        message.reply_to("Your custom goal was deleted.")
                    else:
                        message.reply_to("Your custom goal couldn't be deleted. Please try again later.")
                    return
                return
        elif command in ["uptime"]:
            message.reply_to(f"Running since {utils.get_uptime()}")
        elif command in ["system"]:
            utils.post_message(f"    uptime         {utils.get_uptime()}\n" + \
                               f"    location       {utils.config.botOwner}/{utils.config.botMachine}\n" + \
                               f"    api quota      {utils.se_api.check_quota()}", log_message=False, length_check=False)
        elif command in ["update"]:
            if utils.is_privileged(message, owners_only=True):
                try:
                    repo = git.Repo(".")
                    repo.git.reset("--hard","origin/master")
                    g = git.cmd.Git(".")
                    g.pull()
                    main_logger.info("Update completed, restarting now.")
                    raise os._exit(1)
                except BaseException as e:
                    main_logger.error(f"Error while updating: {e}")
                    pass
            else:
                message.reply_to("This command is restricted to bot maintainerers.")



    except BaseException as e:
        main_logger.error(f"CRITICAL ERROR: {e}")
        if message is not None:
            try:
                if message.îd is not None:
                    main_logger.error(f"Caused by message id {message.id}")
            except AttributeError:
                pass
            main_logger.error(traceback.format_exc())
        try:
            utils.post_message(f"Error on processing the last command ({e}); rebooting instance... (cc @{utils.config.botOwner})")
            os._exit(1)

        except AttributeError:
            os._exit(1)
            pass


if __name__ == '__main__':
    main()
