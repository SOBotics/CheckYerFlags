from flagbot import flags
import config as config

def test_flag_check():
    flagdata = flags.check_flags(None, None, config.debug_config, 1, False)
    assert int(flagdata["flag_count"]) is 55