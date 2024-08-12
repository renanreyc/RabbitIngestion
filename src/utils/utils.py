import logging

class Utils:
    INFO = logging.INFO
    DEBUG = logging.DEBUG

    def __init__(self):
        self.logger = None

    def start_logging(self, title_stap, logging_mode = INFO):
        self.title_stap = title_stap

        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s", level=logging_mode
        )


        self.logger = logging.getLogger(name=self.title_stap)

    def logging_status(self, msg):
        self.logger.info(msg)