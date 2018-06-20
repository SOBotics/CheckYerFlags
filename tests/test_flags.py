from flagbot import flags
from flagbot import ranks
from config import debug_config as config

def test_check_own_flags():
    flags.check_own_flags(message(), utils())
    assert True #Nothing failed = all good

def test_check_flags():
    flagdata = flags.check_flags(None, None, config, 1, False)
    assert flagdata["flag_count"] >= 55 and flagdata["next_rank"] is ranks.ranks[0]

def test_check_flags_fail():
    flagdata = flags.check_flags(None, None, config, 4733879, False)
    assert not flagdata["flag_count"] <= 2000 and flagdata["next_rank"] is not ranks.ranks[0]

def test_get_current_flag_rank():
    current_flag_rank = flags.get_current_flag_rank(ranks.ranks[9]["count"])
    assert current_flag_rank is ranks.ranks[9]

def test_get_next_flag_rank():
    current_flag_rank = flags.get_current_flag_rank(ranks.ranks[9]["count"])
    next_flag_rank = flags.get_next_flag_rank(current_flag_rank)
    assert next_flag_rank is ranks.ranks[10]

class utils:
    @staticmethod
    def reply_to(message, reply):
        return

class user:
    id = 1

class message:
    user = user()