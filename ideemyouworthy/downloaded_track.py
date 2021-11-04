import json
from collections import OrderedDict
from logging import Logger
from pathlib import Path

from deemix.types.DownloadObjects import Single


class DownloadedTrack:

    def __init__(self, key: str, deezer_uuid: str, youtube_url: str, download_location: Path, logger: Logger):
        self.key = key
        self.deezer_uuid = deezer_uuid
        self.youtube_url = youtube_url
        self.download_location: Path = download_location
        self.logger = logger

        self.deezer_single: Single = None

        self.is_youtube = self.deezer_uuid is None and self.youtube_url is not None
        self.is_custom = "spotify:track:" not in self.key and self.youtube_url is not None

        self.is_downloaded = False

        self.youtube_tags = {}

        self.master_track_file: Path = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.debug("Created master track file")

    def update_traits(self):
        self.is_youtube = self.deezer_uuid is None and self.youtube_url is not None
        self.is_custom = "spotify:track:" not in self.key and self.youtube_url is not None

    def create_track_dict(self):
        track_dict = OrderedDict()
        if self.is_youtube:
            track_dict["youtube_url"] = self.youtube_url
        else:
            track_dict["deezer_uuid"] = self.deezer_uuid

        track_dict["download_location"] = self.download_location.as_posix()

        return track_dict

    def store_to_master_file(self):
        master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
        master_track_dict[self.key] = self.create_track_dict()
        self.master_track_file.write_text(json.dumps(master_track_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")
