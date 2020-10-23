from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os

class AccountManager():

    def __init__(self):
        self.account_info_file = Path(Path.cwd().parents[0] / "account_info.json")
        print(str(self.account_info_file))
        self.account_info_dict = {"SPOTIFY_USERNAME": "", "SPOTIFY_CLIENT_ID": "", "SPOTIFY_CLIENT_SECRET": "", "DEEZER_ARL": ""}
        
        if not self.account_info_file.exists():
            self.account_info_file.touch()
            self.account_info_file.write_text(json.dumps(self.account_info_dict, indent = 4))
            print("User must add login information")
            input("Press enter once login information has been added")
        else:
            self.account_info_dict = json.loads(self.account_info_file.read_text())
            
        # os.environ['SPOTIPY_CLIENT_ID'] = self.account_info_dict["SPOTIFY_CLIENT_ID"]
        # os.environ['SPOTIPY_CLIENT_SECRET'] = self.account_info_dict["SPOTIFY_CLIENT_SECRET"]
        # os.environ['SPOTIPY_REDIRECT_URI'] = 'https://localhost'

        self.spotify_scope = "playlist-read-private playlist-read-collaborative"
        self.spotify_manager = None
        
    def login_spotify(self):
        auth_manager = SpotifyOAuth(client_id = self.account_info_dict["SPOTIFY_CLIENT_ID"], client_secret = self.account_info_dict["SPOTIFY_CLIENT_SECRET"], redirect_uri = "https://example.com", scope = self.spotify_scope, cache_path = str(Path.cwd().parents[0] / "cache" / "spotify_token_cache.json"), username = self.account_info_dict["SPOTIFY_USERNAME"])
        self.spotify_manager = spotipy.Spotify(auth_manager = auth_manager)
                    
    def login_deezer(self, deezer_object):
        deezer_object.login_via_arl(self.account_info_dict["DEEZER_ARL"])