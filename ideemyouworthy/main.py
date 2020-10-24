import collections
from pathlib import Path

from deemix.utils.localpaths import getConfigFolder
from deemix.app.settings import Settings
from deemix.app.spotifyhelper import SpotifyHelper
from deemix.api.deezer import Deezer
from deemix.app.queuemanager import QueueManager

from accountmanager import AccountManager
from playlistmanager import PlaylistManager
from trackmanager import TrackManager
from downloadfinished_messageinterface import DownloadFinishedMessageInterface

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
spotify_helper = SpotifyHelper(configFolder)
queue_manager = QueueManager()

deezer_object = Deezer()

account_manager.login_deezer(deezer_object)

downloaded_tracks = collections.OrderedDict()
message_interface = DownloadFinishedMessageInterface(downloaded_tracks, track_manager, new_playlists, playlist_changes, queue_manager)

queue_list = list()
for track in tracks_to_download:
    split_uri = track.split(":")

    spotify_url = "https://open.spotify.com/" + split_uri[1] + "/" + split_uri[2]
    deezer_id = spotify_helper.get_trackid_spotify(deezer_object, split_uri[2], False, None)

    if not deezer_id == 0:
        deezer_uuid = "track_" + str(deezer_id) + "_3"
        downloaded_tracks[track] = deezer_uuid
        
        queue_list.append("https://www.deezer.com/en/track/" + str(deezer_id))

queue_manager.addToQueue(deezer_object, spotify_helper, queue_list, settings, interface = message_interface)

track_manager.verify_itunes()