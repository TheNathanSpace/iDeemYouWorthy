import json
from logging import Logger
from pathlib import Path

from deemix.__main__ import LogListener
from tinytag import TinyTag


class DownloadFinishedListener(LogListener):
    def __init__(self, logger: Logger, downloaded_tracks, track_manager, new_playlists, playlist_changes, use_itunes):
        self.logger = logger

        self.downloaded_tracks = downloaded_tracks
        self.track_manager = track_manager
        self.new_playlists = new_playlists
        self.playlist_changes = playlist_changes
        self.downloader = None

        self.use_itunes = use_itunes

        self.youtube_manager = None

        self.deezer_tracks_to_download = None

        self.master_track_file = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.debug("Created master track file")

        self.first_complete = False
        self.downloaded_number = 0

    def send(self, message, value = None):
        if message == "updateQueue" and "downloaded" in value:
            if value["downloaded"]:
                # {'uuid': self.queueItem.uuid, 'downloaded': True, 'downloadPath': writepath}
                for track in self.downloaded_tracks:
                    if self.downloaded_tracks[track] == value["uuid"]:
                        if not self.first_complete:
                            self.logger.info("---  deezer downloads:  ---")
                            self.first_complete = True

                    self.downloaded_number += 1

                    self.downloaded_tracks[track] = {"deezer_uuid": value["uuid"], "download_location": Path(value["downloadPath"]).as_posix()}
                    tags = TinyTag.get(value["downloadPath"])
                    self.logger.info("[" + str(self.downloaded_number) + "/" + str(self.deezer_tracks_to_download) + "] Downloaded " + str(tags.title))

                    master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
                    master_track_dict[track] = self.downloaded_tracks[track]
                    self.master_track_file.write_text(json.dumps(master_track_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")
                    break

        if self.downloaded_number == self.deezer_tracks_to_download and not self.track_manager.has_finished_queue:
            self.track_manager.has_finished_queue = True

            if self.youtube_manager is None:
                self.track_manager.finished_queue(self.downloaded_tracks, self.new_playlists, self.playlist_changes, self.use_itunes)
            else:
                self.youtube_manager.update_objects(self.downloaded_tracks, self.new_playlists, self.playlist_changes, self.use_itunes, self.track_manager)
                self.youtube_manager.start_download_process()
