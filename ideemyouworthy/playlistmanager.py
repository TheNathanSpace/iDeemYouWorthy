import json
import collections
import os
from logging import Logger
from pathlib import Path
from urllib.parse import urlparse
from posixpath import basename, dirname

import requests
import win32com
from spotipy import SpotifyException

import util


class PlaylistManager:

    def __init__(self, logger: Logger, account_manager):
        self.logger = logger

        self.account_manager = account_manager
        self.spotify_manager = account_manager.spotify_manager

        self.master_playlist_file = Path(Path.cwd().parents[0] / "cache" / "saved_playlists.json")
        Path.mkdir(Path.cwd().parents[0] / "cache", exist_ok = True)
        if not self.master_playlist_file.exists():
            self.master_playlist_file.touch()
            self.master_playlist_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.debug("Created master playlist file")

        self.custom_playlist_file = Path(Path.cwd().parents[0] / "custom_playlists.json")
        if not self.custom_playlist_file.exists():
            self.custom_playlist_file.touch()
            sample_custom_playlists = collections.OrderedDict()
            sample_custom_playlists["https://open.spotify.com/playlist/3p22aU2NEvY8KErZAoWSJD"] = "[example--will not be used]"
            sample_custom_playlists["https://open.spotify.com/playlist/2JD9j9iGtPGaupLf0NwZXe"] = "[example--will not be used]"
            self.custom_playlist_file.write_text(json.dumps(sample_custom_playlists, indent = 4, ensure_ascii = False), encoding = "utf-8")
            self.logger.debug("Created custom playlist file")

    def uri_to_url(self, uri):
        uri_array = uri.split(":")
        if uri_array[0] == "spotify" and uri_array[1] == "playlist":
            return "https://open.spotify.com/playlist/" + uri_array[2]
        else:
            return None

    def url_to_uri(self, url):
        parse_object = urlparse(url)
        if parse_object.netloc == "open.spotify.com" and dirname(parse_object.path) == "/playlist":
            return "spotify:playlist:" + basename(parse_object.path)
        else:
            return None

    def store_user_playlists(self, new_playlists):
        self.master_playlist_file.write_text(json.dumps(new_playlists, indent = 4, ensure_ascii = False), encoding = "utf-8")

    def store_custom_playlists(self, new_playlists):
        self.custom_playlist_file.write_text(json.dumps(new_playlists, indent = 4, ensure_ascii = False), encoding = "utf-8")

    def get_new_user_playlists(self):
        self.logger.debug("Starting user playlist retrieval")
        spotify_username = self.account_manager.account_info_dict["SPOTIFY_USERNAME"]
        playlists = self.spotify_manager.user_playlists(spotify_username)
        user_playlists = collections.OrderedDict()
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                playlist_name = util.clean_path_child(playlist['name'])
                user_playlists[playlist_name] = playlist['uri']

            if playlists['next']:
                playlists = self.spotify_manager.next(playlists)
            else:
                playlists = None

        self.logger.info("Retrieved your Spotify playlists")

        self.get_playlist_artwork(user_playlists)

        return user_playlists

    def read_custom_playlists(self):
        original_custom_playlists = json.loads(self.custom_playlist_file.read_text())
        cleaned_custom_playlists = original_custom_playlists.copy()

        for playlist in original_custom_playlists:
            uri_playlist = self.url_to_uri(playlist)
            uri_array = uri_playlist.split(":")

            try:
                playlist_object = self.spotify_manager.playlist(uri_array[2], fields = "name")

                playlist_name = util.clean_path_child(playlist_object["name"])

                Path.mkdir(Path.cwd().parents[0] / "playlists", exist_ok = True)
                del cleaned_custom_playlists[playlist]

                if not original_custom_playlists[playlist] == "[example--will not be used]":
                    cleaned_custom_playlists[playlist_name] = uri_playlist
                    original_custom_playlists[playlist] = playlist_name

            except SpotifyException as e:
                self.logger.error(f"Playlist {playlist} is not a valid Spotify playlist! (will ignore)")
                del cleaned_custom_playlists[playlist]

        self.get_playlist_artwork(cleaned_custom_playlists)

        self.store_custom_playlists(original_custom_playlists)

        return cleaned_custom_playlists

    def get_playlist_artwork(self, playlists_dict):
        for playlist in playlists_dict:
            uri_playlist = self.url_to_uri(playlist)
            uri_array = uri_playlist.split(":")

            playlist_object = self.spotify_manager.playlist(uri_array[2], fields = "name")
            playlist_name = util.clean_path_child(playlist_object["name"])

            playlist_cover_url = self.spotify_manager.playlist_cover_image(uri_array[2])[0]["url"]

            playlist_cover_file = Path(Path.cwd().parents[0] / "playlists" / (playlist_name + ".jpg"))
            if not playlist_cover_file.exists():
                playlist_cover_file.touch()

            with open(playlist_cover_file, 'wb') as handle:
                response = requests.get(playlist_cover_url, stream = True)

                if not response.ok:
                    self.logger.warning("Couldn't get playlist artwork:")
                    self.logger.warning(response)

                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

    def create_playlist_files(self, new_playlists):
        Path.mkdir(Path.cwd().parents[0] / "playlists", exist_ok = True)

        new_file_count = 0
        for playlist in new_playlists:
            file_path = Path.cwd().parents[0] / "playlists" / (playlist + ".json")
            if not file_path.exists():
                file_path.touch()
                file_path.write_text(json.dumps({}), encoding = "utf-8")
                new_file_count += 1

        self.logger.debug("Created " + str(new_file_count) + " new playlist files")

    def add_custom_playlist(self, playlist_url):
        custom_playlists_dict = json.loads(self.custom_playlist_file.read_text())
        custom_playlists_dict[playlist_url] = ""
        self.store_custom_playlists(custom_playlists_dict)
        self.logger.debug("Added custom playlist: " + playlist_url)

    def delete_custom_playlist(self, playlist_url):
        custom_playlists_dict = json.loads(self.custom_playlist_file.read_text())
        del custom_playlists_dict[playlist_url]
        self.store_custom_playlists(custom_playlists_dict)
        self.logger.debug("Removed custom playlist: " + playlist_url)

    def delete_stored_playlist(self, playlist):
        custom_playlists_dict = json.loads(self.custom_playlist_file.read_text())
        for custom_playlist in custom_playlists_dict:
            if custom_playlists_dict[custom_playlist] == playlist:
                self.delete_custom_playlist(custom_playlist)

        self.store_custom_playlists(custom_playlists_dict)

        stored_playlists_dict = json.loads(self.master_playlist_file.read_text())
        for stored_playlist in stored_playlists_dict:
            if stored_playlist == playlist:
                del stored_playlists_dict[stored_playlist]

        self.store_user_playlists(stored_playlists_dict)

        itunes = win32com.client.Dispatch("iTunes.Application")

        itunes_sources = itunes.Sources
        itunes_playlists = None
        for source in itunes_sources:
            if source.Kind == 1:
                itunes_playlists = source.Playlists

        itunes_playlists_dict = {}
        playlists_left = itunes_playlists.Count
        while playlists_left != 0:
            playlist = itunes_playlists.Item(playlists_left)
            blacklist = {"Voice Memos", "Genius", "Audiobooks", "Podcasts", "TV Shows", "Movies", "Library", "Music"}
            if playlist.Name not in blacklist:
                itunes_playlists_dict[playlist.Name] = playlist
            playlists_left -= 1

        for itunes_playlist in itunes_playlists_dict:
            if itunes_playlist == playlist:
                itunes_playlists_dict[itunes_playlist].Delete()

    def create_m3u(self):
        playlist_dict = json.loads(self.master_playlist_file.read_text())
        custom_dict = self.read_custom_playlists()
        playlist_dict = {**playlist_dict, **custom_dict}

        master_track_file = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        master_track_dict = json.loads(master_track_file.read_text(encoding = "utf-8"))

        for playlist in playlist_dict:
            playlist_file_path = Path.cwd().parents[0] / "playlists" / (playlist + ".json")
            playlist_tracks = json.loads(playlist_file_path.read_text())

            playlist_m3u = Path(Path.cwd().parents[0] / "playlists" / (playlist + ".m3u"))
            if not playlist_m3u.exists():
                playlist_m3u.touch()
            else:
                playlist_m3u.write_text("")

            with playlist_m3u.open("a", encoding = 'utf-8') as append_file:
                append_file.write("#EXTM3U\n")
                append_file.write("#EXTIMG: front cover\n")
                append_file.write(playlist + ".jpg\n")
                for track in playlist_tracks:
                    try:
                        track_file_path = master_track_dict[track]["download_location"]
                        hard_path = Path(track_file_path)
                        relative_path = os.path.relpath(path = hard_path, start = playlist_m3u.parent)
                        append_file.write(str(relative_path) + "\n")
                    except Exception as e:
                        self.logger.error("Exception when writing m3u file:")
                        self.logger.error(e)
