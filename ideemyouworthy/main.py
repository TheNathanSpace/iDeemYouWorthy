import collections
import json
import logging
import os
import shutil
from pathlib import Path

from deemix.utils.localpaths import getConfigFolder
from deemix.app.settings import Settings
from deemix.app.spotifyhelper import SpotifyHelper
from deezer import Deezer
from deemix.app.queuemanager import QueueManager

import util
from accountmanager import AccountManager
from playlistmanager import PlaylistManager
from trackmanager import TrackManager
from downloadfinished_messageinterface import DownloadFinishedMessageInterface
from logger import Logger
from youtubemanager import YoutubeManager

# START TESTING

# delete_path = Path(Path.cwd().parent / "playlists")
# if delete_path.exists(): shutil.rmtree(delete_path)
#
# delete_path = Path(Path.cwd().parent / "music")
# if delete_path.exists(): shutil.rmtree(delete_path)
#
# delete_path = Path(Path.cwd().parent / "cache" / "track_master_list.json")
# if delete_path.exists(): os.remove(delete_path)

# END TESTING

log_manager = Logger()
logger = logging.getLogger('iDeemYouWorthy')

use_nathan = input("Use Nathan's patented Secret Settings?™ [y/n] ") == "y"
if use_nathan:
    get_user_playlists = False
    get_custom_playlists = True
    use_itunes = False
    fix_itunes = False
    make_m3u = True
    verify_path_lengths = True
else:
    get_user_playlists = input("Use Spotify account playlists? [y/n] ") == "y"
    get_custom_playlists = input("Use custom playlists (set in custom_playlists.json)? [y/n] ") == "y"
    use_itunes = input("Update iTunes? [y/n] ") == "y"
    if use_itunes:
        fix_itunes = input("Compare iTunes and cached versions of playlists to re-sync (fixes problems from program crash, also reverts user modifications)? [y/n] ") == "y"
    else:
        fix_itunes = False
    make_m3u = input("Make m3u files (stored in the playlists folder)? [y/n] ") == "y"
    verify_path_lengths = input("Rename files too long to copy to Android? [y/n] ") == "y"

account_manager = AccountManager(logger)
account_manager.login_spotify()

music_directory = str(Path.cwd().parents[0] / "music")

youtube_tag_dict = collections.OrderedDict()
youtube_manager = YoutubeManager(logger, account_manager.spotify_manager, music_directory, youtube_tag_dict)

playlist_manager = PlaylistManager(logger, account_manager)

new_playlists = None
if get_user_playlists:
    new_playlists = playlist_manager.get_new_user_playlists()
    playlist_manager.store_user_playlists(new_playlists)

new_custom_playlists = None
if get_custom_playlists:
    new_custom_playlists = playlist_manager.read_custom_playlists()

if new_playlists and new_custom_playlists:
    new_playlists = {**new_playlists, **new_custom_playlists}
elif new_custom_playlists and not new_playlists:
    new_playlists = new_custom_playlists

playlist_manager.create_playlist_files(new_playlists)

track_manager = TrackManager(logger, account_manager)

playlist_changes = track_manager.find_new_tracks(new_playlists)

tracks_to_download = track_manager.clear_duplicate_downloads(playlist_changes)

if len(tracks_to_download) > 0:
    logger.info("Downloading " + str(len(tracks_to_download)) + " tracks total")
    configFolder = getConfigFolder()
    settings = Settings(configFolder).settings
    settings["downloadLocation"] = music_directory

    deemix_spotify_settings_file = configFolder / "authCredentials.json"
    deemix_spotify_settings = json.loads(deemix_spotify_settings_file.read_text())
    deemix_spotify_settings["clientId"] = account_manager.account_info_dict["SPOTIFY_CLIENT_ID"]
    deemix_spotify_settings["clientSecret"] = account_manager.account_info_dict["SPOTIFY_CLIENT_SECRET"]

    with open(deemix_spotify_settings_file, 'w') as f:
        json.dump(deemix_spotify_settings, f, indent = 2)

    spotify_helper = SpotifyHelper(configFolder)

    queue_manager = QueueManager(spotify_helper)

    deezer_object = Deezer()

    account_manager.login_deezer(deezer_object)

    downloaded_tracks = collections.OrderedDict()
    message_interface = DownloadFinishedMessageInterface(logger, downloaded_tracks, track_manager, new_playlists, playlist_changes, queue_manager, use_itunes)

    queue_list = list()
    youtube_list = list()

    for track in tracks_to_download:
        split_uri = track.split(":")

        if split_uri[1] == "local":
            track_manager.store_problematic_track(track)
        else:
            spotify_url = "https://open.spotify.com/" + split_uri[1] + "/" + split_uri[2]
            deezer_id = spotify_helper.get_trackid_spotify(deezer_object, split_uri[2], False, None)

            if not deezer_id[0] == "0":
                deezer_uuid = "track_" + str(deezer_id[0]) + "_3"
                downloaded_tracks[track] = deezer_uuid

                queue_list.append("https://www.deezer.com/en/track/" + str(deezer_id[0]))
            else:
                youtube_tag_dict[track] = track_manager.get_track_data(track)

                search_string = youtube_manager.get_search_string(split_uri[2])
                first_result = youtube_manager.search(search_string)
                youtube_list.append(first_result)
                downloaded_tracks[track] = first_result

    logger.info("Downloading " + str(len(queue_list)) + " deezer tracks")
    logger.info("Downloading " + str(len(youtube_list)) + " YouTube tracks")

    youtube_num = len(youtube_list)

    if youtube_num != 0:
        youtube_manager.url_list = youtube_list
        youtube_manager.youtube_tracks_to_download = youtube_num
        message_interface.youtube_manager = youtube_manager

    if len(queue_list) != 0:
        message_interface.deezer_tracks_to_download = len(queue_list)
        queue_manager.addToQueue(deezer_object, queue_list, settings, interface = message_interface)
    else:
        youtube_manager.update_objects(downloaded_tracks, new_playlists, playlist_changes, use_itunes, track_manager)
        youtube_manager.start_download_process()

    if youtube_num != 0:
        youtube_manager.add_tags()

else:
    logger.info("Downloading 0 tracks")

if fix_itunes:
    track_manager.verify_itunes()

if make_m3u:
    playlist_manager.create_m3u()

if not track_manager.has_finished_queue:
    track_manager.finished_queue([], new_playlists, playlist_changes, use_itunes)

if verify_path_lengths:
    logger.info("Verifying file path lengths")

    master_track_file = Path(Path.cwd().parent / "cache" / "track_master_list.json")
    master_track_dict = json.loads(master_track_file.read_text(encoding = "utf-8"))

    for playlist_uri in master_track_dict:
        download_location = Path(master_track_dict[playlist_uri]["download_location"])
        new_path = util.shorten_android_path(download_location, logger)

        if new_path is not None:
            master_track_dict[playlist_uri]["download_location"] = new_path.as_posix()
            master_track_file.write_text(json.dumps(master_track_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")
