import logging
import os
from logging.handlers import TimedRotatingFileHandler
from colorlog import ColoredFormatter
import app.utils.config as config


LOG_DIR = config.LOG_PATH
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logger = logging.getLogger("ChemCaptcha")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging,config.TERMINAL_LOG_LEVEL))

CONSOLE_LOG_FORMAT = (
    "%(log_color)s%(levelname)-8s%(reset)s "
    "%(blue)s%(asctime)s%(reset)s "
    "[%(cyan)s%(filename)s:%(lineno)d%(reset)s] "
    "%(message)s"
)

console_formatter = ColoredFormatter(
    CONSOLE_LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    }
)
console_handler.setFormatter(console_formatter)

FILE_LOG_FORMAT = (
    "%(levelname)-8s "
    "%(asctime)s "
    "[%(filename)s:%(lineno)d] "
    "%(message)s"
)
file_formatter = logging.Formatter(FILE_LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

file_handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "app.log"),
    when='D',
    interval=1,
    backupCount=30,
    encoding='utf-8'
)
file_handler.setLevel(getattr(logging,config.FILE_LOG_LEVEL))
file_handler.setFormatter(file_formatter)

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

if __name__ == '__main__':
    logger.debug("这是一条 debug 消息，用于调试。")
    logger.info("这是一条 info 消息，表示一切正常。")
    logger.warning("这是一条 warning 消息，提醒有潜在问题。")
    logger.error("这是一条 error 消息，发生了错误。")
    logger.critical("这是一条 critical 消息，发生了严重错误！")