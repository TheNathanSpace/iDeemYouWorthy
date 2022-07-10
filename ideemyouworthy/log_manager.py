import logging
from datetime import datetime
from pathlib import Path


class LogManager:
    def __init__(self):
        log_folder = Path(Path.cwd().parents[0] / "logs")
        Path.mkdir(log_folder, exist_ok = True)

        old_log_file = Path(log_folder / "latest.log")
        if old_log_file.exists():
            first_line = None
            with old_log_file.open(mode = "r") as opened:
                first_line = opened.readline()
            first_line = first_line.replace("\n", "").replace(":", "꞉")
            old_log_file.rename(f"{log_folder / first_line}")

        file_date_string = (str(datetime.now()) + ".log")
        file_string = "latest.log"
        self.log_file = Path(log_folder / file_string)
        self.log_file.touch()
        self.log_file.write_text(file_date_string + "\n", encoding = 'utf-8')

        self.deemix_logger = logging.getLogger('deemix')
        self.deemix_logger.setLevel(logging.DEBUG)

        self.yt_logger = logging.getLogger('youtube-dl')
        self.yt_logger.setLevel(logging.INFO)

        self.system_logger = logging.getLogger()

        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt = "[%(asctime)s.%(msecs)03d][%(name)s:%(levelname)s]: %(message)s", datefmt = datefmt)

        self.logger = logging.getLogger('iDYW')
        self.logger.setLevel(logging.DEBUG)

        main_handler = logging.FileHandler(filename = str(self.log_file), mode = "a", encoding = 'utf-8')
        main_handler.setFormatter(formatter)
        main_handler.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        system_handler = logging.FileHandler(filename = str(self.log_file), mode = "a", encoding = 'utf-8')
        system_handler.setFormatter(formatter)
        system_handler.setLevel(logging.CRITICAL)

        self.system_logger.addHandler(system_handler)
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
