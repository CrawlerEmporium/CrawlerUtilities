import logging
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self, location="logs", fileName="bot", logName="logger"):
        self.logger = logging.getLogger(logName)
        self.discord_logger = logging.getLogger("discord")

        fh = TimedRotatingFileHandler(f"{location}/{fileName}.log", when="midnight", interval=1, backupCount=90)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s'))
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s : %(message)s'))

        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.discord_logger.setLevel(logging.INFO)
        self.discord_logger.addHandler(fh)
