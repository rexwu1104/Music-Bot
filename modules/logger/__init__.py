import logging
import colorlog

from colorlog import *

class Formatter(logging.Formatter):
    name: str

    FORMATS = {
        logging.DEBUG: "%(bold)s%(asctime)s %(bold_white)s%(levelname)s    %(red)s%(name)s %(reset)s%(message)s",
        logging.INFO: "%(bold)s%(asctime)s %(bold_blue)s%(levelname)s     %(red)s%(name)s %(reset)s%(message)s",
        logging.WARNING: "%(bold)s%(asctime)s %(bold_yellow)s%(levelname)s  %(red)s%(name)s %(reset)s%(message)s",
        logging.ERROR: "%(bold)s%(asctime)s %(bold_red)s%(levelname)s    %(red)s%(name)s %(reset)s%(message)s",
        logging.CRITICAL: "%(bold)s%(asctime)s %(red)s%(levelname)s %(red)s%(name)s %(reset)s%(message)s"
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