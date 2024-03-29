import json
import re
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Dict

import requests
import win32com.client
from spotipy import SpotifyException

import util
from account_manager import AccountManager


class Playlist:

    def __init__(self, spotify_uri: str, name: str, logger: Logger, account_manager: AccountManager):
        self.spotify_uri: str = spotify_uri
        self.name = name
        self.logger: Logger = logger
        self.is_valid: bool = None

        self.account_manager = account_manager

        self.get_spotify_data()

        if name is not None:
            self.playlist_file: Path = Path.cwd().parents[0] / "playlists" / (self.name + ".json")
            self.cover_file: Path = Path(Path.cwd().parents[0] / "playlists" / (self.name + ".jpg"))
        else:
            self.playlist_file = None
            self.cover_file = None

        self.spotify_tracks: list = []
        self.newly_added: list = []
        self.custom_track_strings: list = []

        self.master_track_file: Path = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.debug("Created master track file")

        self.itunes_playlist = None

    def get_id(self):
        uri_array = self.spotify_uri.split(":")
        return uri_array[2]

    def get_spotify_data(self):
        uri_array = self.spotify_uri.split(":")

        try:
            playlist_object = self.account_manager.spotipy.playlist(uri_array[2], fields = "name")

            playlist_name = util.clean_path_child(playlist_object["name"])
            self.name = playlist_name
            self.playlist_file: Path = Path.cwd().parents[0] / "playlists" / (self.name + ".json")
            self.cover_file: Path = Path(Path.cwd().parents[0] / "playlists" / (self.name + ".jpg"))

        except SpotifyException as e:
            self.logger.error(f"Playlist {self.spotify_uri} is not a valid Spotify playlist!")
            self.is_valid = False

        self.is_valid = True

    def create_playlist_file(self):
        Path.mkdir(Path.cwd().parents[0] / "playlists", exist_ok = True)

        if not self.playlist_file.exists():
            self.playlist_file.touch()
            self.playlist_file.write_text(json.dumps([]), encoding = "utf-8")

        self.logger.debug(f"Created new playlist: {self.name}")

    def save_cover_art(self):
        cover_list = self.account_manager.spotipy.playlist_cover_image(self.get_id())
        if len(cover_list) <= 0:
            return

        playlist_cover_url = cover_list[0]["url"]
        if not self.cover_file.exists():
            self.cover_file.touch()

        with open(self.cover_file, 'wb') as handle:
            response = requests.get(playlist_cover_url, stream = True)

            if not response.ok:
                self.logger.warning(f"Couldn't get playlist artwork for {self.name}:")
                self.logger.warning(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

    def retrieve_songs(self):
        self.spotify_tracks = []
        results = self.account_manager.spotipy.playlist_tracks(self.get_id(), fields = "items.track.uri, next")
        tracks = results['items']
        while results['next']:
            results = self.account_manager.spotipy.next(results)
            tracks.extend(results['items'])

        index = 0
        for track in tracks:
            tracks_dict = tracks[index]['track']
            track_uri = tracks_dict["uri"]
            self.spotify_tracks.append(track_uri)

            index += 1

        return self.spotify_tracks

    def archive_version(self, archive_dict: Dict):
        playlist_folder: Path = self.playlist_file.parent
        archive_folder = Path(playlist_folder / "archive")

        new_archive_file = Path(archive_folder / f"{self.name}_archive_{(str(datetime.now())).replace(':', '꞉')}.json")
        current_version_text = self.playlist_file.read_text(encoding = 'utf-8')

        if self.name in archive_dict:
            old_time = archive_dict[self.name][0]
            old_time_string = old_time.strftime("%Y-%m-%d %H:%M:%S.%f").replace(":", "꞉")
            old_filename = self.name + "_archive_" + old_time_string + ".json"
            old_text = (archive_folder / Path(old_filename)).read_text(encoding = 'utf-8')
            if old_text == current_version_text:
                return

        new_archive_file.touch()
        new_archive_file.write_text(current_version_text, encoding = 'utf-8')

    def load_tracks_from_file(self):
        if self.playlist_file.exists():
            tracks = json.loads(self.playlist_file.read_text(encoding = "utf-8"))
            return tracks
        return None

    def find_new_tracks(self):
        new_tracks = self.retrieve_songs()
        old_tracks = self.load_tracks_from_file()

        newly_added = new_tracks.copy()
        already_added = []
        for track in newly_added:
            if track in old_tracks:
                already_added.append(track)

        will_be_removed = []
        for track in old_tracks:
            if track not in newly_added:
                will_be_removed.append(track)

        for track in already_added:
            newly_added.remove(track)

        self.newly_added = newly_added

        return newly_added

    def add_track(self, track_key: str):
        playlist_dict: list = json.loads(self.playlist_file.read_text(encoding = "utf-8"))
        playlist_dict.append(track_key)
        self.playlist_file.write_text(json.dumps(playlist_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")

    def add_track_to_itunes(self, track_key: str):
        itunes = win32com.client.Dispatch("iTunes.Application")
        self.logger.debug("iTunes opened")
        itunes_sources = itunes.Sources
        itunes_playlists = None
        for source in itunes_sources:
            if source.Kind == 1:
                itunes_playlists = source.Playlists

        playlists_left = itunes_playlists.Count
        while playlists_left != 0:
            itunes_playlist = itunes_playlists.Item(playlists_left)
            if itunes_playlist.Name == self.name:
                self.itunes_playlist = itunes_playlist
            playlists_left -= 1

        if self.itunes_playlist is None:
            self.itunes_playlist = itunes.CreatePlayList(self.name)

        old_master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
        self.itunes_playlist.AddFile(old_master_track_dict[track_key]["download_location"])

    def update_playlist_file(self):
        old_master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
        self.playlist_file.write_text(json.dumps([]))

        for track_uri in self.spotify_tracks:
            if track_uri in old_master_track_dict:
                self.add_track(track_uri)
