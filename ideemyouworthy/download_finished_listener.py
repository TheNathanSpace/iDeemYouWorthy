import json
from logging import Logger
from pathlib import Path

from deemix.__main__ import LogListener
from tinytag import TinyTag

from downloaded_track import DownloadedTrack
from track_manager import TrackManager
from youtube_manager import YoutubeManager


class DownloadFinishedListener(LogListener):
    def __init__(self, track_manager: TrackManager, youtube_manager: YoutubeManager, logger: Logger):
        self.track_manager = track_manager
        self.youtube_manager = youtube_manager

        self.logger: Logger = logger

        self.first_complete = False
        self.downloaded_number = 0

    def send(self, message, value = None):
        if message == "updateQueue" and "error" in value and "Track not available" in value["error"]:
            downloaded_track: DownloadedTrack
            for downloaded_track in self.track_manager.deezer_tracks:
                if downloaded_track.deezer_uuid == value["uuid"]:
                    self.downloaded_number += 1

                    self.logger.info(f"[{str(self.downloaded_number)}/{str(len(self.track_manager.deezer_tracks))}] Couldn't get track {downloaded_track.key} from deezer; will use YouTube")

                    downloaded_track.deezer_uuid = None
                    downloaded_track.youtube_tags = self.track_manager.get_track_data(downloaded_track.key)

                    split_uri = downloaded_track.key.split(":")
                    search_string = self.youtube_manager.get_search_string(split_uri[2])
                    first_result = self.youtube_manager.search(search_string)
                    downloaded_track.youtube_url = first_result
                    downloaded_track.update_traits()
                    self.track_manager.youtube_tracks.append(downloaded_track)
                    self.track_manager.deezer_tracks.remove(downloaded_track)

        if message == "updateQueue" and "downloaded" in value:
            if value["downloaded"]:
                # {'uuid': self.queueItem.uuid, 'downloaded': True, 'downloadPath': writepath}
                downloaded_track: DownloadedTrack
                for downloaded_track in self.track_manager.deezer_tracks:
                    if downloaded_track.deezer_uuid == value["uuid"]:
                        self.downloaded_number += 1

                        downloaded_track.deezer_uuid = value["uuid"]
                        downloaded_track.download_location = Path(value["downloadPath"])
                        tags = TinyTag.get(value["downloadPath"])
                        self.logger.info(f"[{str(self.downloaded_number)}/{str(len(self.track_manager.deezer_tracks))}] Downloaded {str(tags.title)}")

                        downloaded_track.store_to_master_file()
                        break
