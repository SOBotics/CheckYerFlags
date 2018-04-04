"""Background process for checking flag counts"""

from threading import Thread

from flagbot import flags


class AutoFlagThread(Thread):
    def __init__(self, event, utils, config, logging, priority, users, thread_list, next_rank = None):
        Thread.__init__(self)
        self.stopped = event
        self.config = config
        self.logging = logging
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
        for u in self.users:
            self.logging.info("Checking user {} now...".format(u.name))
            flagdata = flags.check_flags(None, None, self.config, u.id, False)
            flags_to_next_rank = flagdata["next_rank"]["count"] - flagdata["flag_count"]
            self.logging.info("{} needs {} more flags for their next rank.".format(u.name, flags_to_next_rank))
            #if flags_to_next_rank <= 20:
            if flags_to_next_rank <= 2050:
                self.swap_priority(u, flagdata["next_rank"])
                print("{} just needs {} more helpful flags for their next rank, {}".format(u.name, flags_to_next_rank, flagdata["next_rank"]["title"]))
                self.logging.info("User {} is {} flags away from their next rank and therefore moved to the high priority queue".format(u.name, flags_to_next_rank))


    def check_flags_hp(self):
        if len(self.users) > 0:
            for u in self.users:
                self.logging.info("Checking user {} high-priority now...".format(u.name))
                flagdata = flags.check_flags(None, None, self.config, u.id, False)
                flags_to_next_rank = self.next_rank["count"] - flagdata["flag_count"]
                if flags_to_next_rank <= 0:
                    self.utils.post_message("{} has reached the rank *Static*")
                else:
                    self.logging.info("{} needs {} more flags for their next rank.".format(u.name, flags_to_next_rank))

    def swap_priority(self, user, next_rank):
        if self.priority == 1:
            #From high priority to low priority
            self.users.remove(user)
            self.thread_list[0].users.append(user)
        else:
            #From low priority to high priority
            self.users.remove(user)
            self.thread_list[1].users.append(user)
            self.thread_list[0].next_rank = next_rank