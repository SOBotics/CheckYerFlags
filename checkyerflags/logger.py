import logging, logging.handlers
import sys

def _setup_logger(name, log_file, level=logging.INFO, to_console=False):
    """
    Set up a logger
    """
    handler =  logging.handlers.TimedRotatingFileHandler(log_file, when="w0", backupCount=5)
    formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    if to_console:
        logger.addHandler(logging.StreamHandler(sys.stdout))

    return logger

main_logger = _setup_logger('Main', 'CheckYerFlags.log', to_console=True)
auto_logger = _setup_logger('Auto', 'AutoCheck.log')
logging.getLogger("chatoverflow").setLevel(logging.WARNING)