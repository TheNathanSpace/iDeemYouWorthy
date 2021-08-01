import logging
from datetime import datetime
from pathlib import Path


class LogManager:
    def __init__(self):
        Path.mkdir(Path.cwd().parents[0] / "logs", exist_ok = True)
        file_string = (str(datetime.now()) + ".log").replace(":", "꞉")
        self.log_file = Path(Path.cwd().parents[0] / "logs" / file_string)
        self.log_file.touch()

        default_logger = logging.getLogger()
        default_logger.setLevel(logging.WARNING)

        self.deemix_logger = logging.getLogger('deemix')
        self.deemix_logger.setLevel(logging.WARNING)

        self.yt_logger = logging.getLogger('youtube-dl')
        self.yt_logger.setLevel(logging.WARNING)

        self.logger = logging.getLogger('iDYW')
        main_handler = logging.FileHandler(filename = str(self.log_file), mode = "a")
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt = "[%(asctime)s.%(msecs)03d][%(name)s:%(levelname)s]: %(message)s", datefmt = datefmt)
        main_handler.setFormatter(formatter)
        main_handler.setLevel(logging.INFO)

        self.deemix_logger.addHandler(main_handler)
        self.yt_logger.addHandler(main_handler)
        self.logger.addHandler(main_handler)

        self.logger.setLevel(logging.INFO)
        # todo: this only outputs to file :/
        # should move most things to debug
        # then print info for the user to know what's going on

class YTLogger(object):
    def __init__(self, yt_logger: logging.Logger):
        self.yt_logger = yt_logger

    def debug(self, msg):
        self.yt_logger.debug(msg)
        pass

    def warning(self, msg):
        self.yt_logger.warning(msg)
        pass

    def error(self, msg):
        self.yt_logger.error(msg)
