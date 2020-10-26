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
from logger import Logger

logger = Logger()

account_manager = AccountManager(logger)
account_manager.login_spotify()

playlist_manager = PlaylistManager(logger, account_manager)

get_user_playlists = input("Use Spotify account playlists? [y/n] ")

new_playlists = None
if get_user_playlists == "y":
    new_playlists = playlist_manager.get_new_user_playlists()
    playlist_manager.store_user_playlists(new_playlists)

get_custom_playlists = input("Use custom playlists (set in custom_playlists.json)? [y/n] ")

new_custom_playlists = None
if get_custom_playlists == "y":
    new_custom_playlists = playlist_manager.read_custom_playlists()

if new_playlists and new_custom_playlists:
    new_playlists = {**new_playlists, **new_custom_playlists}
elif new_custom_playlists and not new_playlists:
    new_playlists = new_custom_playlists

use_itunes = input("Update iTunes? [y/n] ")

playlist_manager.create_playlist_files(new_playlists)

track_manager = TrackManager(logger, account_manager)

playlist_changes = track_manager.find_new_tracks(new_playlists)

tracks_to_download = track_manager.clear_duplicate_downloads(playlist_changes)

if len(tracks_to_download) > 0:
    logger.log("Downloading " + str(len(tracks_to_download)) + " tracks")
    configFolder = getConfigFolder()
    settings = Settings(configFolder).settings
    settings["downloadLocation"] = str(Path.cwd().parents[0] / "music")
    spotify_helper = SpotifyHelper(configFolder)
    queue_manager = QueueManager()

    deezer_object = Deezer()

    account_manager.login_deezer(deezer_object)

    downloaded_tracks = collections.OrderedDict()
    message_interface = DownloadFinishedMessageInterface(logger, downloaded_tracks, track_manager, new_playlists, playlist_changes, queue_manager, use_itunes)

    queue_list = list()
    for track in tracks_to_download:
        split_uri = track.split(":")

        if split_uri[1] == "local":
            track_manager.store_local_tracks(track)
        else:
            spotify_url = "https://open.spotify.com/" + split_uri[1] + "/" + split_uri[2]
            deezer_id = spotify_helper.get_trackid_spotify(deezer_object, split_uri[2], False, None)

            if not deezer_id == 0:
                deezer_uuid = "track_" + str(deezer_id) + "_3"
                downloaded_tracks[track] = deezer_uuid

                queue_list.append("https://www.deezer.com/en/track/" + str(deezer_id))

    queue_manager.addToQueue(deezer_object, spotify_helper, queue_list, settings, interface = message_interface)
else:
    logger.log("Downloading 0 tracks")

if use_itunes:
    track_manager.verify_itunes()
