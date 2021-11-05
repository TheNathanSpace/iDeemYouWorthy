import collections
import json
import logging
import os
from pathlib import Path

from deemix.downloader import Downloader
from deezer import Deezer

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

# print("If you haven't already, be sure to install required dependencies by running the following command (see the README):")
# print("    pip install -r requirements.txt")
# print("(If you have errors, try: python -m pip install -r requirements.txt)")
# print()
import android_manager
import util
from account_manager import AccountManager
from download_finished_listener import DownloadFinishedListener
from downloaded_track import DownloadedTrack
from log_manager import LogManager
from playlist_manager import PlaylistManager
from track_manager import TrackManager
from youtube_manager import YoutubeManager

print("Welcome to iDeemYouWorthy!")
print()

log_manager = LogManager()
logger = logging.getLogger('iDYW')

got_settings = False
if Path(Path.cwd().parents[0] / "user_settings.json").exists():
    user_settings_dict = json.loads(Path(Path.cwd().parents[0] / "user_settings.json").read_text(encoding = "utf-8"))
    if user_settings_dict["always_use_user_settings"]:
        get_user_playlists = user_settings_dict["get_user_playlists"]
        get_custom_playlists = user_settings_dict["get_custom_playlists"]
        use_itunes = user_settings_dict["use_itunes"]
        fix_itunes = user_settings_dict["fix_itunes"]
        make_m3u = user_settings_dict["make_m3u"]
        verify_path_lengths = user_settings_dict["verify_path_lengths"]
        copy_to_android = user_settings_dict["copy_to_android"]
        logger.info("Loaded settings from user_settings.json (change \"always_use_user_settings\" to stop this)")
        got_settings = True
    else:
        use_user_settings = input("Load settings from user_settings.json? (will save for future runs) [y/n] ") == "y"
        if use_user_settings:
            user_settings_dict["always_use_user_settings"] = True
            get_user_playlists = user_settings_dict["get_user_playlists"]
            get_custom_playlists = user_settings_dict["get_custom_playlists"]
            use_itunes = user_settings_dict["use_itunes"]
            fix_itunes = user_settings_dict["fix_itunes"]
            make_m3u = user_settings_dict["make_m3u"]
            verify_path_lengths = user_settings_dict["verify_path_lengths"]
            copy_to_android = user_settings_dict["copy_to_android"]
            Path(Path.cwd().parents[0] / "user_settings.json").write_text(json.dumps(user_settings_dict, indent = 4, ensure_ascii = True), encoding = "utf-8")
            logger.info("Loaded settings from user_settings.json. Stored this preference for the future.")
            got_settings = True

if not got_settings:
    logger.debug("Requesting user settings input")
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
youtube_manager = YoutubeManager(log_manager, logger, account_manager.spotipy, music_directory, youtube_tag_dict)

playlist_manager = PlaylistManager(logger = logger, account_manager = account_manager)

if get_user_playlists:
    playlist_manager.retrieve_spotify_playlists()
if get_custom_playlists:
    playlist_manager.retrieve_custom_playlists()

if len(playlist_manager.playlists) == 0:
    logger.info("You aren't tracking any playlists! I'm all done! :)")
    quit()

playlist_manager.create_playlist_files()

unique_spotify_tracks: list = []
len1 = playlist_manager.get_unique_tracks(unique_spotify_tracks)

all_custom_tracks: list = []
len2 = playlist_manager.get_custom_tracks(all_custom_tracks)

logger.info(f"Found {str(len1 + len2)} new tracks in total")

track_manager = TrackManager(logger = logger, account_manager = account_manager)
track_manager.unique_spotify_tracks = unique_spotify_tracks
track_manager.custom_tracks = all_custom_tracks

listener = DownloadFinishedListener(track_manager = track_manager, logger = logger)
logger.info("Converting Spotify tracks to deezer and YouTube, this might take a while...")
track_manager.process_spotify_tracks(deezer_object = deezer_object, listener = listener, youtube_manager = youtube_manager)
track_manager.process_custom_tracks(youtube_manager = youtube_manager)

if len(track_manager.deezer_tracks) + len(track_manager.youtube_tracks) == 0:
    logger.info("Downloading 0 tracks!")

if len(track_manager.deezer_tracks) != 0:
    listener.deezer_tracks_to_download = len(track_manager.deezer_tracks)
    downloaded_track: DownloadedTrack
    for downloaded_track in track_manager.deezer_tracks:
        downloader = Downloader(dz = deezer_object, downloadObject = downloaded_track.deezer_single, settings = account_manager.deezer_settings, listener = listener)
        listener.downloader = downloader
        downloader.start()

if len(track_manager.youtube_tracks) != 0:
    youtube_manager.in_process_list = track_manager.youtube_tracks.copy()
    youtube_manager.all_tracks_to_download = track_manager.youtube_tracks.copy()
    listener.youtube_manager = youtube_manager
    youtube_manager.start_download_process()
    youtube_manager.add_tags()

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

playlist_manager.add_new_tracks(use_itunes = use_itunes)

if fix_itunes:
    track_manager.verify_itunes()

if make_m3u:
    playlist_manager.create_m3u()

if copy_to_android:
    while True:
        logger.info("Copying music to Android, this might take a while...")
        os.system("adb start-server")

        try:
            android_manager.transfer_all(logger)
            break
        except Exception as e:
            logger.error("Error copying files to Android:")
            logger.error(e)
            logger.info("The adb server might not be running, or check for a confirmation dialogue on your device!")
            retry = input("Retry file transfer? [y/n] ") == "y"
            if not retry:
                break

logger.info("All done! :) Enjoy the music!")
