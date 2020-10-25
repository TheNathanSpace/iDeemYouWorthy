import json
import collections
from pathlib import Path
from urllib.parse import urlparse
from posixpath import basename, dirname


class PlaylistManager:

    def __init__(self, account_manager):
        self.account_manager = account_manager
        self.spotify_manager = account_manager.spotify_manager

        self.master_playlist_file = Path(Path.cwd().parents[0] / "cache" / "saved_playlists.json")
        Path.mkdir(Path.cwd().parents[0] / "cache", exist_ok = True)
        if not self.master_playlist_file.exists():
            self.master_playlist_file.touch()
            self.master_playlist_file.write_text(json.dumps({}))

        # Should warn that this contains unwanted playlists
        self.custom_playlist_file = Path(Path.cwd().parents[0] / "custom_playlists.json")
        if not self.custom_playlist_file.exists():
            self.custom_playlist_file.touch()
            sample_custom_playlists = collections.OrderedDict()
            sample_custom_playlists["https://open.spotify.com/playlist/3p22aU2NEvY8KErZAoWSJD"] = ""
            sample_custom_playlists["https://open.spotify.com/playlist/2JD9j9iGtPGaupLf0NwZXe"] = ""
            self.custom_playlist_file.write_text(json.dumps(sample_custom_playlists, indent = 4))

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

    def get_new_user_playlists(self):
        spotify_username = self.account_manager.account_info_dict["SPOTIFY_USERNAME"]
        playlists = self.spotify_manager.user_playlists(spotify_username)
        new_playlists = collections.OrderedDict()
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                new_playlists[playlist['name']] = playlist['uri']
            if playlists['next']:
                playlists = self.spotify_manager.next(playlists)
            else:
                playlists = None

        return new_playlists

    def read_user_playlists(self):
        old_playlists = collections.OrderedDict()

        if self.master_playlist_file.exists():
            old_playlists = json.loads(self.master_playlist_file.read_text())

        return old_playlists

    def create_playlist_files(self, new_playlists):
        Path.mkdir(Path.cwd().parents[0] / "playlists", exist_ok = True)

        # Make file for each playlist here
        for playlist in new_playlists:
            file_path = Path.cwd().parents[0] / "playlists" / (playlist + ".json")
            if not file_path.exists():
                file_path.touch()
                file_path.write_text(json.dumps({}))

    def store_user_playlists(self, new_playlists):
        self.master_playlist_file.write_text(json.dumps(new_playlists, indent = 4))

    def store_custom_playlists(self, new_playlists):
        self.custom_playlist_file.write_text(json.dumps(new_playlists, indent = 4))

    def read_custom_playlists(self):
        custom_playlists_dict = json.loads(self.custom_playlist_file.read_text())
        parsed_dict = custom_playlists_dict.copy()

        for playlist in custom_playlists_dict:
            uri_playlist = self.url_to_uri(playlist)
            uri_array = uri_playlist.split(":")

            playlist_object = self.spotify_manager.playlist(uri_array[2], fields = "name")

            del parsed_dict[playlist]
            parsed_dict[playlist_object["name"]] = uri_playlist

        return parsed_dict

    def add_custom_playlist(self, playlist_url):
        custom_playlists_dict = json.loads(self.custom_playlist_file.read_text())
        custom_playlists_dict[playlist_url] = ""
        self.store_custom_playlists(custom_playlists_dict)

    def delete_custom_playlist(self, playlist_url):
        custom_playlists_dict = json.loads(self.custom_playlist_file.read_text())
        del custom_playlists_dict[playlist_url]
        self.store_custom_playlists(custom_playlists_dict)
