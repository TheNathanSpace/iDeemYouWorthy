from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self):
        Path.mkdir(Path.cwd().parents[0] / "logs", exist_ok = True)
        file_string = (str(datetime.now()) + ".log").replace(":", "꞉")
        self.log_file = Path(Path.cwd().parents[0] / "logs" / file_string)
        self.log_file.touch()

    def log(self, message):
        time = datetime.now()
        time = "[" + str(time) + "]: "
        with self.log_file.open("a") as append_file:
            append_file.write(time + message + "\n")
