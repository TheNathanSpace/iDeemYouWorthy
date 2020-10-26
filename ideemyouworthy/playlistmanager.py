import json
import collections
from pathlib import Path
from urllib.parse import urlparse
from posixpath import basename, dirname


class PlaylistManager:

    def __init__(self, logger, account_manager):
        self.logger = logger

        self.account_manager = account_manager
        self.spotify_manager = account_manager.spotify_manager

        self.master_playlist_file = Path(Path.cwd().parents[0] / "cache" / "saved_playlists.json")
        Path.mkdir(Path.cwd().parents[0] / "cache", exist_ok = True)
        if not self.master_playlist_file.exists():
            self.master_playlist_file.touch()
            self.master_playlist_file.write_text(json.dumps({}))
            self.logger.log("Created master playlist file")

        self.custom_playlist_file = Path(Path.cwd().parents[0] / "custom_playlists.json")
        if not self.custom_playlist_file.exists():
            self.custom_playlist_file.touch()
            sample_custom_playlists = collections.OrderedDict()
            sample_custom_playlists["https://open.spotify.com/playlist/3p22aU2NEvY8KErZAoWSJD"] = "[example--will not be used]"
            sample_custom_playlists["https://open.spotify.com/playlist/2JD9j9iGtPGaupLf0NwZXe"] = "[example--will not be used]"
            self.custom_playlist_file.write_text(json.dumps(sample_custom_playlists, indent = 4))
            self.logger.log("Created custom playlist file")

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
        self.logger.log("Starting user playlist retrieval")
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

        self.logger.log("Finished user playlist retrieval")
        return new_playlists

    def create_playlist_files(self, new_playlists):
        Path.mkdir(Path.cwd().parents[0] / "playlists", exist_ok = True)

        new_file_count = 0
        for playlist in new_playlists:
            file_path = Path.cwd().parents[0] / "playlists" / (playlist + ".json")
            if not file_path.exists():
                file_path.touch()
                file_path.write_text(json.dumps({}))
                new_file_count += 1

        self.logger.log("Created " + str(new_file_count) + " new playlist files")

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

            if not custom_playlists_dict[playlist] == "[example--will not be used]":
                parsed_dict[playlist_object["name"]] = uri_playlist

        self.logger.log("Read custom playlists")

        return parsed_dict

    def add_custom_playlist(self, playlist_url):
        custom_playlists_dict = json.loads(self.custom_playlist_file.read_text())
        custom_playlists_dict[playlist_url] = ""
        self.store_custom_playlists(custom_playlists_dict)
        self.logger.log("Added custom playlist: " + playlist_url)

    def delete_custom_playlist(self, playlist_url):
        custom_playlists_dict = json.loads(self.custom_playlist_file.read_text())
        del custom_playlists_dict[playlist_url]
        self.store_custom_playlists(custom_playlists_dict)
        self.logger.log("Removed custom playlist: " + playlist_url)
