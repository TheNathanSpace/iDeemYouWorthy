import json
from pathlib import Path

from deemix.app.messageinterface import MessageInterface
from tinytag import TinyTag


class DownloadFinishedMessageInterface(MessageInterface):
    def __init__(self, logger, downloaded_tracks, track_manager, new_playlists, playlist_changes, queue_manager, use_itunes):
        self.logger = logger

        self.downloaded_tracks = downloaded_tracks
        self.track_manager = track_manager
        self.new_playlists = new_playlists
        self.playlist_changes = playlist_changes
        self.queue_manager = queue_manager

        self.use_itunes = use_itunes

        self.youtube_manager = None

        self.deezer_tracks_to_download = None

        self.master_track_file = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.info("Created master track file")

    def send(self, message, value = None):
        if message == "updateQueue" and "downloaded" in value:
            if value["downloaded"]:
                # {'uuid': self.queueItem.uuid, 'downloaded': True, 'downloadPath': writepath}
                for track in self.downloaded_tracks:
                    if self.downloaded_tracks[track] == value["uuid"]:
                        self.downloaded_tracks[track] = {"deezer_uuid": value["uuid"], "download_location": value["downloadPath"]}
                        tags = TinyTag.get(value["downloadPath"])
                        print("[" + str(self.deezer_tracks_to_download - len(self.queue_manager.queue)) + "/" + str(self.deezer_tracks_to_download) + "] Downloaded " + tags.title)

                        master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
                        master_track_dict[track] = self.downloaded_tracks[track]
                        self.master_track_file.write_text(json.dumps(master_track_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")
                        break

        if len(self.queue_manager.queue) == 0 and not self.track_manager.has_finished_queue:
            self.track_manager.has_finished_queue = True

            if self.youtube_manager is None:
                self.track_manager.finished_queue(self.downloaded_tracks, self.new_playlists, self.playlist_changes, self.use_itunes)
            else:
                self.youtube_manager.update_objects(self.downloaded_tracks, self.new_playlists, self.playlist_changes, self.use_itunes, self.track_manager)
                self.youtube_manager.start_download_process()
