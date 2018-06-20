from flagbot import redunda, logger

def test_ping_redunda():
	config = {}
	config["redundaKey"] = ""

	rd = redunda.RedundaThread(None, config, logger.main_logger)
	result = rd.ping_redunda()

	assert result

def test_ping_redunda_fail():
	config = {}
	config["redundaKey"] = "invalid key"
	config["botVersion"] = "CI"

	rd = redunda.RedundaThread(None, config, logger.main_logger)
	result = rd.ping_redunda()

	assert not result