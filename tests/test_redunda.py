from flagbot import redunda, logger
import config

def test_ping_redunda():
    rd = redunda.RedundaThread(None, config.debug_config, logger.main_logger)
    result = rd.ping_redunda()

    assert result

def test_ping_redunda_fail():
    conf = config.debug_config
    conf["redundaKey"] = "invalid key"

    rd = redunda.RedundaThread(None, conf, logger.main_logger)
    result = rd.ping_redunda()

    assert not result