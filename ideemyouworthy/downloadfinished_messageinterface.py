from deemix.app.messageinterface import MessageInterface

class DownloadFinishedMessageInterface(MessageInterface):
    def __init__(self, downloaded_tracks, track_manager, new_playlists, playlist_changes, queue_manager):
        self.downloaded_tracks = downloaded_tracks
        self.track_manager = track_manager
        self.new_playlists = new_playlists
        self.playlist_changes = playlist_changes
        self.queue_manager = queue_manager
    
    def send(self, message, value = None):
        if message == "updateQueue" and "downloaded" in value:
            if value["downloaded"] == True:
                # {'uuid': self.queueItem.uuid, 'downloaded': True, 'downloadPath': writepath}
                for track in self.downloaded_tracks:
                    if self.downloaded_tracks[track] == value["uuid"]:
                        self.downloaded_tracks[track] = {"deezer_uuid": value["uuid"], "download_location": value["downloadPath"]}
                
                if len(self.queue_manager.queue) == 0:
                    self.track_manager.finished_queue(self.downloaded_tracks, self.new_playlists, self.playlist_changes)