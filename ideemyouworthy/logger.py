import logging
from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self):
        Path.mkdir(Path.cwd().parents[0] / "logs", exist_ok = True)
        file_string = (str(datetime.now()) + ".log").replace(":", "꞉")
        self.log_file = Path(Path.cwd().parents[0] / "logs" / file_string)
        self.log_file.touch()

        default_logger = logging.getLogger()
        default_logger.setLevel(logging.WARNING)

        deemix_logger = logging.getLogger('deemix')
        deemix_logger.setLevel(logging.WARNING)

        self.logger = logging.getLogger('iDeemYouWorthy')
        main_handler = logging.FileHandler(filename = str(self.log_file), mode = "a")
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt = "[%(asctime)s.%(msecs)03d][%(name)s:%(levelname)s]: %(message)s", datefmt = datefmt)
        main_handler.setFormatter(formatter)
        main_handler.setLevel(logging.INFO)

        deemix_logger.addHandler(main_handler)
        self.logger.addHandler(main_handler)
        self.logger.setLevel(logging.INFO)

    # Deprecated
    def log(self, message):
        time = datetime.now()
        log_message = "[" + str(time) + "]: "
        with self.log_file.open("a") as append_file:
            append_file.write(log_message + message + "\n")
