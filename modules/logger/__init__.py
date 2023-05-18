import logging
import colorlog

from colorlog import *

class Formatter(logging.Formatter):
    name: str

    FORMATS = {
        logging.DEBUG: "%(asctime)s %(bold_white)s[%(name)s-%(levelname)s]%(reset)s\t%(white)s%(message)s",
        logging.INFO: "%(asctime)s %(bold_white)s[%(name)s-%(levelname)s]%(reset)s\t\t%(white)s%(message)s",
        logging.WARNING: "%(asctime)s %(bold_yellow)s[%(name)s-%(levelname)s]%(reset)s\t%(white)s%(message)s",
        logging.ERROR: "%(asctime)s %(red)s[%(name)s-%(levelname)s]%(reset)s\t%(white)s%(message)s",
        logging.CRITICAL: "%(asctime)s %(bold_red)s[%(name)s-%(levelname)s]%(reset)s\t%(white)s%(message)s"
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = ColoredFormatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

class Logger(logging.Logger):
    def __init__(self, name: str) -> None:
        super().__init__(name, logging.DEBUG)
        
        handler = colorlog.StreamHandler()
        handler.setFormatter(Formatter())
        
        self.addHandler(handler)