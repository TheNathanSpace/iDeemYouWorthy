import os
import json
import collections
from pathlib import Path

class PlaylistManager():

    def __init__(self, account_manager):
        self.account_manager = account_manager
        self.spotify_manager = account_manager.spotify_manager
        
        self.master_playlist_file = Path(Path.cwd().parents[0] / "cache" / "saved_playlists.json")
        Path.mkdir(Path.cwd().parents[0] / "cache", exist_ok = True)
        if not self.master_playlist_file.exists():
            self.master_playlist_file.touch()
            self.master_playlist_file.write_text(json.dumps({}))


    def get_new_playlists(self):
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

    def read_old_playlists(self):
        old_playlists = collections.OrderedDict()

        if self.master_playlist_file.exists():
            old_playlists = json.loads(self.master_playlist_file.read_text())
            
        return old_playlists
            
    def store_playlists(self, new_playlists):
        Path.mkdir(Path.cwd().parents[0] / "playlists", exist_ok = True)

        # Make file for each playlist here
        for playlist in new_playlists:
            file_path = Path.cwd().parents[0] / "playlists" / (playlist + ".json")
            if not file_path.exists():
                file_path.touch()
                file_path.write_text(json.dumps({}))
        
        self.master_playlist_file.write_text(json.dumps(new_playlists, indent = 4))