import logging
from datetime import datetime
from pathlib import Path


class LogManager:
    def __init__(self):
        Path.mkdir(Path.cwd().parents[0] / "logs", exist_ok = True)
        file_string = (str(datetime.now()) + ".log").replace(":", "꞉")
        self.log_file = Path(Path.cwd().parents[0] / "logs" / file_string)
        self.log_file.touch()

        self.deemix_logger = logging.getLogger('deemix')
        self.deemix_logger.setLevel(logging.INFO)

        self.yt_logger = logging.getLogger('youtube-dl')
        self.yt_logger.setLevel(logging.INFO)

        self.system_logger = logging.getLogger()

        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt = "[%(asctime)s.%(msecs)03d][%(name)s:%(levelname)s]: %(message)s", datefmt = datefmt)

        self.logger = logging.getLogger('iDYW')
        self.logger.setLevel(logging.DEBUG)

        main_handler = logging.FileHandler(filename = str(self.log_file), mode = "a")
        main_handler.setFormatter(formatter)
        main_handler.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        system_handler = logging.FileHandler(filename = str(self.log_file), mode = "a")
        system_handler.setFormatter(formatter)
        system_handler.setLevel(logging.WARNING)

        self.system_logger.addHandler(main_handler)
        self.deemix_logger.addHandler(main_handler)
        self.yt_logger.addHandler(main_handler)
        self.logger.addHandler(main_handler)
        self.logger.addHandler(stream_handler)


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
