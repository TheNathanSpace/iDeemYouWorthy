import json
from logging import Logger
from pathlib import Path

from deemix.__main__ import LogListener
from tinytag import TinyTag

from DownloadedTrack import DownloadedTrack
from TrackManagerNew import TrackManagerNew


class DownloadFinishedListenerNew(LogListener):
    def __init__(self, track_manager: TrackManagerNew, logger: Logger):
        self.track_manager = track_manager
        self.logger: Logger = logger

        self.first_complete = False
        self.downloaded_number = 0

    def send(self, message, value = None):
        if message == "updateQueue" and "downloaded" in value:
            if value["downloaded"]:
                # {'uuid': self.queueItem.uuid, 'downloaded': True, 'downloadPath': writepath}
                downloaded_track: DownloadedTrack
                for downloaded_track in self.track_manager.deezer_tracks:
                    if downloaded_track.deezer_uuid == value["uuid"]:
                        if not self.first_complete:
                            self.logger.info("---  deezer downloads:  ---")
                            self.first_complete = True

                        self.downloaded_number += 1

                        downloaded_track.deezer_uuid = value["uuid"]
                        downloaded_track.download_location = Path(value["downloadPath"])
                        tags = TinyTag.get(value["downloadPath"])
                        self.logger.info("[" + str(self.downloaded_number) + "/" + str(len(self.track_manager.deezer_tracks)) + "] Downloaded " + str(tags.title))

                        downloaded_track.store_to_master_file()
                        break
