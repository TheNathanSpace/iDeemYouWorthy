import collections
import json
import os
from logging import Logger
from posixpath import basename, dirname
from pathlib import Path
from urllib.parse import urlparse

from spotipy import SpotifyException

import util
from account_manager import AccountManager
from downloaded_track import DownloadedTrack
from playlist import Playlist


def url_to_uri(url):
    parse_object = urlparse(url)
    if parse_object.netloc == "open.spotify.com" and dirname(parse_object.path) == "/playlist":
        return "spotify:playlist:" + basename(parse_object.path)
    else:
        return None


class PlaylistManager:

    def __init__(self, logger: Logger, account_manager: AccountManager):
        self.logger: Logger = logger
        self.account_manager: AccountManager = account_manager

        self.playlists: list = []

        self.master_track_file: Path = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.debug("Created master track file")

        self.custom_playlist_file = Path(Path.cwd().parents[0] / "custom_playlists.json")
        if not self.custom_playlist_file.exists():
            self.custom_playlist_file.touch()
            sample_custom_playlists = collections.OrderedDict()

            sample_custom_playlists["https://open.spotify.com/playlist/37i9dQZF1xD8shr5OgBdbQ"] = {"custom_tracks": ["Cotton Eye Joe - Rednex", "Video Killed the Radio Star - The Buggles"]}
            sample_custom_playlists["https://open.spotify.com/playlist/AlsoAfaKePlaLisT"] = []
            self.custom_playlist_file.write_text(json.dumps(sample_custom_playlists, indent = 4, ensure_ascii = False), encoding = "utf-8")
            self.logger.debug("Created custom playlist file")

        self.master_playlist_file = Path(Path.cwd().parents[0] / "cache" / "saved_playlists.json")
        Path.mkdir(Path.cwd().parents[0] / "cache", exist_ok = True)
        if not self.master_playlist_file.exists():
            self.master_playlist_file.touch()
            self.master_playlist_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.debug("Created master playlist file")

        self.playlists_directory = Path.cwd().parents[0] / "playlists"
        Path.mkdir(self.playlists_directory, exist_ok = True)

        self.logger.debug("Initialized playlist manager")

    def retrieve_spotify_playlists(self):
        self.logger.debug("Starting user playlist retrieval")
        spotify_username = self.account_manager.account_info_dict["SPOTIFY_USERNAME"]
        playlists = self.account_manager.spotipy.user_playlists(spotify_username)
        user_playlists = {}
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                playlist_name = util.clean_path_child(playlist['name'])
                user_playlists[playlist['uri']] = playlist_name

            if playlists['next']:
                playlists = self.account_manager.spotipy.next(playlists)
            else:
                playlists = None

        for uri_name in user_playlists:
            new_playlist: Playlist = Playlist(spotify_uri = uri_name, name = user_playlists[uri_name], logger = self.logger, account_manager = self.account_manager)
            self.playlists.append(new_playlist)

        self.logger.info(f"Retrieved your {len(user_playlists)} Spotify playlists")

    def retrieve_custom_playlists(self):
        self.logger.debug("Starting custom playlist retrieval")

        original_custom_playlists = json.loads(self.custom_playlist_file.read_text())

        valid_count = 0
        for playlist_url in original_custom_playlists:
            playlist_uri = url_to_uri(playlist_url)
            uri_array = playlist_uri.split(":")
            try:
                playlist_object = self.account_manager.spotipy.playlist(uri_array[2], fields = "name")
                playlist_name = util.clean_path_child(playlist_object["name"])
                original_custom_playlists[playlist_url]["name"] = playlist_name

                playlist: Playlist = Playlist(spotify_uri = playlist_uri, name = playlist_name, logger = self.logger, account_manager = self.account_manager)
                if "custom_tracks" in original_custom_playlists[playlist_url]:
                    playlist.custom_track_strings = original_custom_playlists[playlist_url]["custom_tracks"]
                else:
                    playlist.custom_track_strings = []
                    original_custom_playlists[playlist_url]["custom_tracks"] = []

                self.playlists.append(playlist)
                valid_count += 1

            except SpotifyException as e:
                self.logger.error(f"Playlist {playlist_url} is not a valid Spotify playlist! (will ignore)")
                self.logger.debug(e)

        self.custom_playlist_file.write_text(json.dumps(original_custom_playlists, indent = 4, ensure_ascii = False), encoding = "utf-8")
        self.logger.info(f"Retrieved {valid_count} valid custom playlists")

    def create_playlist_files(self):
        for playlist in self.playlists:
            playlist.create_playlist_file()

        for playlist in self.playlists:
            playlist.save_cover_art()

        self.logger.debug("Created playlist track and art files")

    def get_unique_tracks(self, unique_spotify_tracks: list):
        self.logger.debug("Getting new Spotify tracks")
        master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
        master_track_set = util.dict_to_set(master_track_dict)

        tracks_to_download = set()

        for playlist in self.playlists:
            playlist_changes_set = util.dict_to_set(playlist.find_new_tracks())

            differences = playlist_changes_set.difference(master_track_set)  # Checks against already downloaded tracks

            tracks_to_download = tracks_to_download.union(differences)  # Checks against other lists so a new one isn't downloaded twice

        for track in tracks_to_download:
            unique_spotify_tracks.append(track)

        self.logger.debug("Cleared unnecessary Spotify downloads")
        return len(unique_spotify_tracks)

    def get_custom_tracks(self, custom_tracks: list):
        self.logger.debug("Getting new custom tracks")

        master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
        master_track_set = util.dict_to_set(master_track_dict)

        tracks_to_download = set()

        for playlist in self.playlists:
            differences = set(playlist.custom_track_strings).difference(master_track_set)  # Checks against already downloaded tracks
            tracks_to_download = tracks_to_download.union(differences)  # Checks against other lists so a new one isn't downloaded twice

        for track in tracks_to_download:
            custom_tracks.append(track)

        return len(tracks_to_download)

    def add_new_tracks(self, use_itunes: bool):
        playlist: Playlist
        for playlist in self.playlists:
            playlist.playlist_file.write_text(json.dumps([]))
            downloaded_track: DownloadedTrack
            for spotify_uri in (*playlist.spotify_tracks, *playlist.custom_track_strings):
                playlist.add_track(spotify_uri)
                if use_itunes:
                    playlist.add_track_to_itunes(spotify_uri)

    def create_m3u(self):
        self.logger.info("Creating m3u files")
        master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))

        for playlist in self.playlists:
            playlist_file_path = Path.cwd().parents[0] / "playlists" / (playlist.name + ".json")
            playlist_tracks = json.loads(playlist_file_path.read_text())

            playlist_m3u = Path(Path.cwd().parents[0] / "playlists" / (playlist.name + ".m3u"))
            if not playlist_m3u.exists():
                playlist_m3u.touch()
            else:
                playlist_m3u.write_text("")

            with playlist_m3u.open("a", encoding = 'utf-8') as append_file:
                append_file.write("#EXTM3U\n")
                append_file.write("#EXTIMG: front cover\n")
                append_file.write(playlist.name + ".jpg\n")
                for track in playlist_tracks:
                    try:
                        track_file_path = master_track_dict[track]["download_location"]
                        hard_path = Path(track_file_path)
                        relative_path = os.path.relpath(path = hard_path, start = playlist_m3u.parent)
                        append_file.write(str(relative_path) + "\n")
                    except Exception as e:
                        self.logger.error(f"Exception when writing m3u file for {playlist_m3u.as_posix()}:")
                        self.logger.error(e)
