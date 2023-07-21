import sys
from loguru import logger


class Logger:

    def __init__(self):
        self.logger = logger

    def format_console(self, config=None):

        if config is not None:
            self.logger.remove()

        self.logger.add(sys.stdout, **config)
        return self.logger

    def format_file(self, config):
        self.logger.add(**config)
        return self.logger
