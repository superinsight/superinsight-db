import logging
import traceback
from environment import Environment


class CommonLogger:

    logger = None

    def __init__(self, logger=None, handler=None):
        self.logger = logger or logging.getLogger(Environment.logger_name)
        self.logger.setLevel(logging.INFO)
        if handler is not None:
            self.logger.addHandler(handler)
        else:
            stream_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

    def info(self, *messages):
        self.logger.info(" ".join(str(m) for m in messages))

    def debug(self, *messages):
        self.logger.debug(" ".join(str(m) for m in messages))

    def warning(self, *messages):
        self.logger.warning(" ".join(str(m) for m in messages))

    def error(self, err):
        self.logger.error("*" * 100)
        self.logger.error(err)
        self.logger.error(traceback.format_exc())
