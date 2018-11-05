"""Background process for checking flag counts"""
import time
from threading import Thread
from checkyerflags import custom_goals, check_flags
from checkyerflags.check_flags import NoApiKeyError, InvalidUserIdError, NonExistentUserIdError, NotEnoughFlagsError
from checkyerflags.logger import auto_logger
from checkyerflags.scoreboard import update_scoreboard
from checkyerflags.utils import Struct


class AutoFlagThread(Thread):
    def __init__(self, event, utils, priority, room, thread_list, next_ranks = []):
        Thread.__init__(self)
        self.stopped = event
        self.utils = utils
        self.priority = priority
        self.users = []
        self.room = room
        self.thread_list = thread_list
        self.next_ranks = next_ranks

    def run(self):
        if self.priority == 1:
            #High priority, check every 5 minutes
            while not self.stopped.wait(300):
                self.check_flags_hp()
        else:
            #Low priority, check every 15 minutes
            self.check_flags_lp()
            while not self.stopped.wait(900):
                self.check_flags_lp()

    def check_flags_lp(self):
        cu = self.utils.get_current_room().get_current_users()
        self.users = self.utils.checkable_user_ids(cu)
        for u in self.users:
            try:
                #Obtain the current flag count and the next flag rank
                flag_count = 0
                next_flag_rank = None

                try:
                    flag_count = check_flags.get_flag_count_for_user(u.id, self.utils)
                    next_flag_rank = Struct(**check_flags.get_next_flag_rank(check_flags.get_current_flag_rank(flag_count)))
                except NoApiKeyError:
                    auto_logger.error("No API Key specified, unable to check flags.")
                    return
                except InvalidUserIdError:
                    auto_logger.error(f"The user id was invalid while checking user {u.name}.")
                    return
                except NonExistentUserIdError:
                    auto_logger.error(f"The user id for {u.name} appears to not belong to an actual user.")
                    return
                except NotEnoughFlagsError:
                    next_flag_rank = Struct(**check_flags.get_next_flag_rank())
                except (IndexError, ValueError) as e:
                    auto_logger.error(f"Error while parsing flag count for user {u.name}")
                    return

                flags_to_next_rank = next_flag_rank.count - flag_count
                #flags

                #Replace flags to next rank with custom goal if its flag count is lower than the next rank
                custom_goal = custom_goals.get_custom_goal_for_user(u.id)
                if custom_goal is not None:
                    if custom_goal[0] is not None and custom_goal[0] < next_flag_rank.count:
                        flags_to_next_rank = custom_goal[0] - flag_count

                #If the user is closer than 20 flags to his next rank, move him to the high priority queue
                hp_users = []
                if self.thread_list is not None:
                    hp_users = self.thread_list[1].users
                if flags_to_next_rank <= 20 and u.id not in (u.id for o in hp_users):
                    self.swap_priority(u, next_flag_rank)
                    auto_logger.info(f"[LP->HP] User {u.name} is {flags_to_next_rank} flags away from their next rank and was therefore moved to the high priority queue.")
                elif u.id not in (u.id for o in hp_users):
                    auto_logger.info(f"[LP] {u.name} needs {flags_to_next_rank} more flags for their next rank.")

                #Update scoreboard
                update_scoreboard(flag_count, self.utils.config.score_board_fkey, u)
                time.sleep(5)

            except TypeError as e:
                auto_logger.error(e)
                auto_logger.info(f"[LP] Checking flags for user {u.name} failed.")
            except BaseException as e:
                auto_logger.error("[LP]] Critical Error while checking flags:")
                auto_logger.error(e)


    def check_flags_hp(self):
        if len(self.users) > 0:
            for u in self.users:
                try:
                    #Obtain the current flag count and the next flag rank
                    flag_count = 0
                    next_flag_rank = None

                    try:
                        flag_count = check_flags.get_flag_count_for_user(u.id, self.utils)
                        next_flag_rank = Struct(**check_flags.get_next_flag_rank(check_flags.get_current_flag_rank(flag_count)))
                    except NoApiKeyError:
                        auto_logger.error("No API Key specified, unable to check flags.")
                        return
                    except InvalidUserIdError:
                        auto_logger.error(f"The user id was invalid while checking user {u.name}.")
                        return
                    except NonExistentUserIdError:
                        auto_logger.error(f"The user id for {u.name} appears to not belong to an actual user.")
                        return
                    except NotEnoughFlagsError:
                        next_flag_rank = Struct(**check_flags.get_next_flag_rank())
                    except (IndexError, ValueError) as e:
                        auto_logger.error(f"Error while parsing flag count for user {u.name}")
                        return

                    flags_to_next_rank = next_flag_rank.count - flag_count

                    #Replace flags to next rank with custom goal if its flag count is lower than the next rank
                    is_custom_goal = False
                    custom_goal = custom_goals.get_custom_goal_for_user(u.id)
                    if custom_goal is not None:
                        if custom_goal[0] is not None and custom_goal[0] < next_flag_rank.count:
                            flags_to_next_rank = custom_goal[0] - flag_count
                            is_custom_goal = True

                    #If the user has reached the flags to their next or custom rank, move them to the low priority queue
                    if flags_to_next_rank <= 0:
                        next_rank_desc = ""
                        if next_flag_rank.description is not None:
                            next_rank_desc = f" ({next_flag_rank.description})"
                        self.swap_priority(u, check_flags.get_next_flag_rank(next_flag_rank))
                        if is_custom_goal:
                            custom_msg = ""
                            if custom_goal[1] is not None:
                                custom_msg = f" They set a custom message for this event: {custom_goal[1]}"


                            self.utils.post_message(f"Congratulations to @{u.name} for reaching their custom goal of {custom_goal[0]} helpful flags!{custom_msg}")
                            custom_goals.delete_custom_goal(u.id)
                            auto_logger.info(f"[HP->LP] User {u.name} has reached their custom rank and is therefore moved to the low priority queue")
                        else:
                            self.utils.post_message(f"Congratulations to @{u.name} for reaching the rank {next_flag_rank.title}{next_rank_desc} by surpassing {next_flag_rank.count} helpful flags!")
                            auto_logger.info(f"[HP->LP] User {u.name} has reached their next rank and is therefore moved to the low priority queue")
                    else:
                        auto_logger.info(f"[HP] {u.name} needs {flags_to_next_rank} more flags for their next rank.")


                    #Update scoreboard
                    update_scoreboard(flag_count, self.utils.config.score_board_fkey, u)
                except TypeError as e:
                    auto_logger.error(e)
                    auto_logger.info(f"[LP] Checking flags for user {u.name} failed.")
                except BaseException as e:
                    auto_logger.error("[HP]] Critical Error while checking flags:")
                    auto_logger.error(e)

    def swap_priority(self, user, next_rank):
        """
        Swap the priority of a user to check
        """

        if self.priority == 1:
            #From high priority to low priority
            try:
                self.users.remove(user)
                self.thread_list[1].next_ranks = [r for r in self.thread_list[1].next_ranks if r[0] != user.id]
            except ValueError:
                pass
        else:
            #From low priority to high priority
            try:
                self.thread_list[1].users.append(user)
                self.thread_list[1].next_ranks.append((user.id, next_rank))
            except ValueError:
                pass
