import json
import collections
from pathlib import Path

from deemix.utils.localpaths import getConfigFolder
from deemix.app.settings import Settings
from deemix.app.spotifyhelper import SpotifyHelper
from deemix.api.deezer import Deezer
from deemix.app.queuemanager import QueueManager
from deemix.app.messageinterface import MessageInterface

from accountmanager import AccountManager
from playlistmanager import PlaylistManager
from trackmanager import TrackManager

account_manager = AccountManager()
account_manager.login_spotify()

playlist_manager = PlaylistManager(account_manager)

old_playlists = playlist_manager.read_old_playlists()
new_playlists = playlist_manager.get_new_playlists()

playlist_manager.store_playlists(new_playlists)

track_manager = TrackManager(account_manager)

playlist_changes = track_manager.find_new_tracks(new_playlists)

tracks_to_download = track_manager.clear_duplicate_downloads(playlist_changes)


configFolder = getConfigFolder()
settings = Settings(configFolder).settings
settings["downloadLocation"] = str(Path.cwd().parents[0] / "music")
sp = SpotifyHelper(configFolder)
qm = QueueManager()

deezer_object = Deezer()

account_manager.login_deezer(deezer_object)

# dz.login_via_arl("8275c01b2a1f89f1370fb6f9e054cfadf34dc3e461ca312a9108f03bc8a53da458de5cf115b3a97802184ddf1fc661faaf7b09aafef3ec14e2cf4bf404fc47b67cf7da4fc0338ec216e66a8c9dacb7d5f671d14a82dfa1b334ca59c0b142906d")

class MyMessageInterface(MessageInterface):
    def send(self, message, value = None):
        if message == "updateQueue" and "downloaded" in value:
            if value["downloaded"] == True:
                # {'uuid': self.queueItem.uuid, 'downloaded': True, 'downloadPath': writepath}
                for track in downloaded_tracks:
                    if downloaded_tracks[track] == value["uuid"]:
                        downloaded_tracks[track] = {"deezer_uuid": value["uuid"], "download_location": value["downloadPath"]}
                
                if len(qm.queue) == 0:
                    track_manager.finished_queue(downloaded_tracks, new_playlists, playlist_changes)

my_interface = MyMessageInterface()

downloaded_tracks = collections.OrderedDict()

queue_list = list()
for track in tracks_to_download:
    split_uri = track.split(":")

    spotify_url = "https://open.spotify.com/" + split_uri[1] + "/" + split_uri[2]
    deezer_id = sp.get_trackid_spotify(deezer_object, split_uri[2], False, None)

    if not deezer_id == 0:
        deezer_uuid = "track_" + str(deezer_id) + "_3"
        downloaded_tracks[track] = deezer_uuid
        
        queue_list.append("https://www.deezer.com/en/track/" + str(deezer_id))

qm.addToQueue(deezer_object, sp, queue_list, settings, interface = my_interface)

"""
 - MessageInterface
 - Post-queue
 - API calls?
"""