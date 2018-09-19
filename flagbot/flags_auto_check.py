"""Background process for checking flag counts"""
from threading import Thread
import requests
from requests import HTTPError
from flagbot import flags, custom_goals
from flagbot.logger import auto_logger


class AutoFlagThread(Thread):
    def __init__(self, event, utils, config, priority, room, thread_list, next_ranks = []):
        Thread.__init__(self)
        self.stopped = event
        self.utils = utils
        self.config = config
        self.priority = priority
        self.users = []
        self.room = room
        self.thread_list = thread_list
        self.next_ranks = next_ranks

    def run(self):
        if self.priority == 1:
            #High priority
            while not self.stopped.wait(300):
                self.check_flags_hp()
        else:
            self.check_flags_lp()
            while not self.stopped.wait(1800):
                self.check_flags_lp()

    def check_flags_lp(self):
        cu = self.room.get_current_users()
        self.users = self.utils.checkable_user_ids(cu)
        for u in self.users:
            try:
                flagdata = flags.check_flags(None, None, self.config, u.id, False)
                flags_to_next_rank = flagdata["next_rank"]["count"] - flagdata["flag_count"]
                custom_goal = custom_goals.get_custom_goal_for_user(u.id)
                if custom_goal is not None and custom_goal < flags_to_next_rank:
                    flags_to_next_rank = custom_goal - flagdata["flag_count"]
                if flags_to_next_rank <= 20 and u.id not in (u.id for o in self.thread_list[1].users):
                    self.swap_priority(u, flagdata["next_rank"])
                    auto_logger.info(f"[Moved] User {u.name} is {flags_to_next_rank} flags away from their next rank and is therefore moved to the high priority queue")
                elif u.id not in (u.id for o in self.thread_list[1].users):
                    auto_logger.info(f"[LP] {u.name} needs {flags_to_next_rank} more flags for their next rank.")

                if flagdata["flag_count"] >= 500 and self.config["score_board_fkey"] != "":
                    try:
                        r = requests.post("https://rankoverflow.philnet.ch/api/scoreboard/add", json={"fkey": self.config["score_board_fkey"], "user_id": u.id, "flag_count": flagdata["flag_count"]})
                        if r.status_code != 200:
                            auto_logger.warn(f"Couldn't send flag data to scoreboard for user {u.name}")
                    except HTTPError:
                        auto_logger.warn(f"Couldn't send flag data to scoreboard for user {u.name}")
            except TypeError as e:
                auto_logger.error(e)
                auto_logger.info(f"[LP] Checking flags for user {u.name} failed.")


    def check_flags_hp(self):
        if len(self.users) > 0:
            for u in self.users:
                custom_rank = False
                flagdata = flags.check_flags(None, None, self.config, u.id, False)
                flags_to_next_rank = flagdata["next_rank"]["count"] - flagdata["flag_count"] # This is used as fallback, but under normal circumstances, this value should overwritten
                for next_rank in self.next_ranks:
                    if next_rank[0] is u.id:
                        flags_to_next_rank = next_rank[1]["count"] - flagdata["flag_count"]

                custom_goal = custom_goals.get_custom_goal_for_user(u.id)
                if custom_goal is not None and custom_goal < flags_to_next_rank:
                    flags_to_next_rank = custom_goal - flagdata["flag_count"]
                    custom_rank = True

                if flags_to_next_rank <= 0:
                    next_rank_desc = ""
                    if next_rank[1]['description'] is not None:
                        next_rank_desc = f" ({next_rank[1]['description']})"
                    self.swap_priority(u, flagdata["next_rank"])
                    if custom_rank:
                        self.utils.post_message(f"Congratulations to @{u.name} for reaching their custom goal of {custom_goal} helpful flags!")
                    else:
                        self.utils.post_message(f"Congratulations to @{u.name} for reaching the rank {next_rank[1]['title']}{next_rank_desc} by surpassing {next_rank[1]['count']} helpful flags!")
                    auto_logger.info(f"[Moved] User {u.name} has reached their next rank and is therefore moved to the low priority queue")
                else:
                    auto_logger.info(f"[HP] {u.name} needs {flags_to_next_rank} more flags for their next rank.")
                if flagdata["flag_count"] >= 500 and self.config["score_board_fkey"] != "":
                    try:
                        r = requests.post("https://rankoverflow.philnet.ch/api/scoreboard/add", json={"fkey": self.config["score_board_fkey"], "user_id": u.id, "flag_count": flagdata["flag_count"]})
                        if r.status_code != 200:
                            auto_logger.warn(f"Couldn't send flag data to scoreboard for user {u.name}")
                    except HTTPError:
                        auto_logger.warn(f"Couldn't send flag data to scoreboard for user {u.name}")

    def swap_priority(self, user, next_rank):
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
