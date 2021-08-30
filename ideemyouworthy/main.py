import collections
import json
import logging
import os
import shutil
from pathlib import Path

import deemix
import deezer
from deemix.downloader import Downloader
from deemix.plugins import spotify
from deemix.utils.localpaths import getConfigFolder
import deemix.settings as settings
from deezer import Deezer

import androidmanager
import util
from accountmanager import AccountManager
from playlistmanager import PlaylistManager
from trackmanager import TrackManager
from downloadfinishedlistener import DownloadFinishedListener
from logmanager import LogManager
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

print("If you haven't already, be sure to install required dependencies by running the following command (see the README):")
print("    pip install -r requirements.txt")
print("(If you have errors, try: python -m pip install -r requirements.txt)")
print()

log_manager = LogManager()
logger = logging.getLogger('iDYW')

use_nathan = input("Use Nathan's patented Secret Settings?™ (Optimized for Android) [y/n] ") == "y"
if use_nathan:
    get_user_playlists = False
    get_custom_playlists = True
    use_itunes = False
    fix_itunes = False
    make_m3u = True
    verify_path_lengths = True
    copy_to_android = True
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
    copy_to_android = input("Copy music and playlists to Android Music folder? (Won't waste time overwriting, make sure to enable USB debugging) [y/n] ") == "y"

account_manager = AccountManager(logger)
account_manager.login_spotify()

deezer_object = Deezer()
account_manager.login_deezer(deezer_object)

music_directory = str(Path.cwd().parents[0] / "music")

youtube_tag_dict = collections.OrderedDict()
youtube_manager = YoutubeManager(log_manager, logger, account_manager.spotify_manager, music_directory, youtube_tag_dict)

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

if new_playlists is None:
    logger.info("You aren't tracking any playlists! I'm all done! :)")
    quit()

playlist_manager.create_playlist_files(new_playlists)

track_manager = TrackManager(logger, account_manager)

playlist_changes = track_manager.find_new_tracks(new_playlists)

tracks_to_download = track_manager.clear_duplicate_downloads(playlist_changes)

if len(tracks_to_download) > 0:
    logger.debug("Downloading " + str(len(tracks_to_download)) + " tracks total")
    configFolder = getConfigFolder()
    settings = settings.load(configFolder)
    settings["downloadLocation"] = music_directory

    deemix_spotify_settings_file = configFolder / "spotify" / "settings.json"
    deemix_spotify_settings = json.loads(deemix_spotify_settings_file.read_text())
    deemix_spotify_settings["clientId"] = account_manager.account_info_dict["SPOTIFY_CLIENT_ID"]
    deemix_spotify_settings["clientSecret"] = account_manager.account_info_dict["SPOTIFY_CLIENT_SECRET"]

    with open(deemix_spotify_settings_file, 'w') as f:
        json.dump(deemix_spotify_settings, f, indent = 2)

    spotify_helper = spotify.Spotify(configFolder)
    spotify_helper.checkCredentials()
    spotify_helper.loadSettings()

    downloaded_tracks = collections.OrderedDict()

    listener = DownloadFinishedListener(logger, downloaded_tracks, track_manager, new_playlists, playlist_changes, use_itunes)

    queue_list = list()
    youtube_list = list()

    logger.info("Converting Spotify tracks, this might take a while...")
    for track in tracks_to_download:
        split_uri = track.split(":")

        if split_uri[1] == "local":
            track_manager.store_problematic_track(track)
        else:
            spotify_url = "https://open.spotify.com/" + split_uri[1] + "/" + split_uri[2]

            try:
                download_object = deemix.generateDownloadObject(dz = deezer_object, link = spotify_url, bitrate = deezer.TrackFormats.MP3_320, plugins = {"spotify": spotify_helper}, listener = listener)

                deezer_uuid = "track_" + str(download_object.id) + "_3"
                downloaded_tracks[track] = deezer_uuid

                queue_list.append(download_object)

            except Exception as e:
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
        listener.youtube_manager = youtube_manager

    if len(queue_list) != 0:
        listener.deezer_tracks_to_download = len(queue_list)
        for download_object in queue_list:
            downloader = Downloader(dz = deezer_object, downloadObject = download_object, settings = settings, listener = listener)
            listener.downloader = downloader
            downloader.start()

    else:
        youtube_manager.update_objects(downloaded_tracks, new_playlists, playlist_changes, use_itunes, track_manager)
        youtube_manager.start_download_process()

    if youtube_num != 0:
        youtube_manager.add_tags()

else:
    logger.info("Downloading 0 tracks")

logger.info("Fixing track file paths and updating playlists, this might take a while...")
if verify_path_lengths:
    logger.debug("Verifying file path lengths")

    master_track_file = Path(Path.cwd().parent / "cache" / "track_master_list.json")
    master_track_dict = json.loads(master_track_file.read_text(encoding = "utf-8"))

    for playlist_uri in master_track_dict:
        download_location = Path(master_track_dict[playlist_uri]["download_location"])
        new_path = util.shorten_android_path(download_location, logger)

        if new_path is not None:
            master_track_dict[playlist_uri]["download_location"] = new_path.as_posix()
            master_track_file.write_text(json.dumps(master_track_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")

if fix_itunes:
    track_manager.verify_itunes()

if make_m3u:
    playlist_manager.create_m3u()

if not track_manager.has_finished_queue:
    track_manager.finished_queue([], new_playlists, playlist_changes, use_itunes)

if copy_to_android:
    while True:
        logger.info("Copying music to Android, this might take a while...")
        os.system("adb start-server")

        try:
            androidmanager.transfer_all(logger)
            break
        except Exception as e:
            logger.error("Error copying files to Android:")
            logger.error(e)
            logger.info("The adb server might not be running, or check for a confirmation dialogue on your device!")
            retry = input("Retry file transfer? [y/n] ") == "y"
            if not retry:
                break

logger.info("All done! :) Enjoy the music!")
