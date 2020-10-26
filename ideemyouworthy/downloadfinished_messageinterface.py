from deemix.app.messageinterface import MessageInterface


class DownloadFinishedMessageInterface(MessageInterface):
    def __init__(self, logger, downloaded_tracks, track_manager, new_playlists, playlist_changes, queue_manager):
        self.logger = logger

        self.downloaded_tracks = downloaded_tracks
        self.track_manager = track_manager
        self.new_playlists = new_playlists
        self.playlist_changes = playlist_changes
        self.queue_manager = queue_manager

    def send(self, message, value = None):  # TODO: Is there a way to make this more modular so that if it crashes it doesn't lose the progress? I think deezer should make it okay, but still...
        if message == "updateQueue" and "downloaded" in value:
            if value["downloaded"]:
                # {'uuid': self.queueItem.uuid, 'downloaded': True, 'downloadPath': writepath}
                for track in self.downloaded_tracks:
                    if self.downloaded_tracks[track] == value["uuid"]:
                        self.downloaded_tracks[track] = {"deezer_uuid": value["uuid"], "download_location": value["downloadPath"]}

                if len(self.queue_manager.queue) == 0:
                    self.track_manager.finished_queue(self.downloaded_tracks, self.new_playlists, self.playlist_changes)
