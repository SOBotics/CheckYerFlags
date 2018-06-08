import logging
import sys

def setup_logger(name, log_file, level=logging.INFO, mode = "a", to_console=False):
    formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.FileHandler(log_file, mode=mode)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    if to_console:
        logger.addHandler(logging.StreamHandler(sys.stdout))

    return logger

main_logger = setup_logger('Main', 'CheckYerFlags.log', to_console=True)
auto_logger = setup_logger('Auto', 'AutoCheck.log', mode="w")
logging.getLogger("chatoverflow").setLevel(logging.WARNING)