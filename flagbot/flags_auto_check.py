"""Background process for checking flag counts"""
import logging
from threading import Thread

import sys

from flagbot import flags


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
        logging.basicConfig(filename="AutoFlags.log", level=logging.INFO, filemode="a", format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        logging.getLogger("chatexchange").setLevel(logging.WARNING)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        for u in self.users:
            logging.info("Checking user {} low-prio now...".format(u.name))
            flagdata = flags.check_flags(None, None, self.config, u.id, False)
            flags_to_next_rank = flagdata["next_rank"]["count"] - flagdata["flag_count"]
            logging.info("{} needs {} more flags for their next rank.".format(u.name, flags_to_next_rank))
            if flags_to_next_rank <= 10:
                self.swap_priority(u, flagdata["next_rank"])
                print("{} just needs {} more helpful flags for their next rank, {}".format(u.name, flags_to_next_rank, flagdata["next_rank"]["title"]))
                logging.info("User {} is {} flags away from their next rank and therefore moved to the high priority queue".format(u.name, flags_to_next_rank))


    def check_flags_hp(self):
        if len(self.users) > 0:
            for u in self.users:
                logging.info("Checking user {} high-prio now...".format(u.name))
                flagdata = flags.check_flags(None, None, self.config, u.id, False)
                flags_to_next_rank = flagdata["next_rank"]["count"] - flagdata["flag_count"]
                flags_from_current_rank = flagdata["flag_count"] - flagdata["current_rank"]["count"]
                if flags_to_next_rank <= 0 and flags_from_current_rank > 10:
                    self.swap_priority(u, flagdata["next_rank"])
                    self.utils.post_message("{} has reached the rank {} ({}) for {} helpful flags. Congratulations!".format(u.name, flagdata["next_rank"]["title"], flagdata["next_rank"]["description"], flagdata["next_rank"]["count"]))
                    logging.info("User {} has reach their next rank and therefore moved to the low priority queue".format(u.name, flags_to_next_rank))
                    logging.warning("Method 'flags_to_next_rank <= 600 and flags_from_current_rank > 10' ran")
                elif flags_from_current_rank <= 10:
                    self.swap_priority(u, flagdata["next_rank"])
                    self.utils.post_message("{} has reached the rank {} ({}) for {} helpful flags. Congratulations!".format(u.name, flagdata["current_rank"]["title"], flagdata["current_rank"]["description"], flagdata["current_rank"]["count"]))
                    logging.info("User {} has reach their next rank and therefore moved to the low priority queue".format(u.name, flags_to_next_rank))
                    logging.warning("Method 'flags_from_current_rank <= 10' ran")
                else:
                    logging.info("{} needs {} more flags for their next rank.".format(u.name, flags_to_next_rank))

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