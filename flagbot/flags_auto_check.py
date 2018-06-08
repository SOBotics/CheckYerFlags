"""Background process for checking flag counts"""

from threading import Thread
from flagbot import flags
from flagbot.logger import auto_logger


class AutoFlagThread(Thread):
    def __init__(self, event, utils, config, priority, users, thread_list, next_rank = None):
        Thread.__init__(self)
        self.stopped = event
        self.utils = utils
        self.config = config
        self.priority = priority
        self.users = users
        self.thread_list = thread_list
        self.next_rank = next_rank

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
        """auto_logger.basicConfig(filename="AutoFlags.log", level=auto_logger.INFO, filemode="a", format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        auto_logger.getLogger("chatexchange").setLevel(auto_logger.WARNING)
        auto_logger.getLogger().addHandler(auto_logger.StreamHandler(sys.stdout))"""


        for u in self.users:
            if not u.is_moderator:
                flagdata = flags.check_flags(None, None, self.config, u.id, False)
                flags_to_next_rank = flagdata["next_rank"]["count"] - flagdata["flag_count"]
                auto_logger.info(f"{u.name} needs {flags_to_next_rank} more flags for their next rank.")
                if flags_to_next_rank <= 10:
                    self.swap_priority(u, flagdata["next_rank"])
                    auto_logger.info("User {} is {} flags away from their next rank and is therefore moved to the high priority queue".format(u.name, flags_to_next_rank))


    def check_flags_hp(self):
        if len(self.users) > 0:
            for u in self.users:
                auto_logger.info("Checking user {} high-prio now...".format(u.name))
                flagdata = flags.check_flags(None, None, self.config, u.id, False)
                flags_to_next_rank = flagdata["next_rank"]["count"] - flagdata["flag_count"]
                flags_from_current_rank = flagdata["flag_count"] - flagdata["current_rank"]["count"]
                if flags_to_next_rank <= 0 and flags_from_current_rank > 10:
                    self.swap_priority(u, flagdata["next_rank"])
                    self.utils.post_message("{} has reached the rank {} ({}) for {} helpful flags. Congratulations!".format(u.name, flagdata["next_rank"]["title"], flagdata["next_rank"]["description"], flagdata["next_rank"]["count"]))
                    self.utils.post_message("@Filnor ^")
                    auto_logger.info("User {} has reach their next rank and is therefore moved to the low priority queue".format(u.name, flags_to_next_rank))
                elif flags_from_current_rank <= 10:
                    self.swap_priority(u, flagdata["next_rank"])
                    self.utils.post_message("{} has reached the rank {} ({}) for {} helpful flags. Congratulations!".format(u.name, flagdata["current_rank"]["title"], flagdata["current_rank"]["description"], flagdata["current_rank"]["count"]))
                    auto_logger.info("User {} has reach their next rank and therefore moved to the low priority queue".format(u.name, flags_to_next_rank))
                    auto_logger.warning("Method 'flags_from_current_rank <= 10' ran")
                else:
                    auto_logger.info("{} needs {} more flags for their next rank.".format(u.name, flags_to_next_rank))

    def swap_priority(self, user, next_rank):
        if self.priority == 1:
            #From high priority to low priority
            try:
                self.users.remove(user)
                self.thread_list[0].users.append(user)
            except ValueError:
                pass
        else:
            #From low priority to high priority
            try:
                self.users.remove(user)
                self.thread_list[1].users.append(user)
                self.thread_list[0].next_rank = next_rank
            except ValueError:
                pass