from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json


class AccountManager:

    def __init__(self, logger):
        self.logger = logger

        self.account_info_file = Path(Path.cwd().parents[0] / "account_info.json")
        self.account_info_dict = {"SPOTIFY_USERNAME": "", "SPOTIFY_CLIENT_ID": "", "SPOTIFY_CLIENT_SECRET": "",
                                  "DEEZER_ARL": ""}

        if not self.account_info_file.exists():

            self.account_info_file.touch()
            self.account_info_file.write_text(json.dumps(self.account_info_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")

            self.logger.info("Created account info file")

            print("User must add login information (to file account_info.json)")
            input("Press enter once login information has been added")

            self.logger.info("User claims account info has been entered")
        else:
            self.account_info_dict = json.loads(self.account_info_file.read_text())
            self.logger.info("User account info loaded")

        self.spotify_scope = "playlist-read-private playlist-read-collaborative"
        self.spotify_manager = None

    def login_spotify(self):
        self.logger.info("Attempting to authorize with Spotify")
        auth_manager = SpotifyOAuth(client_id = self.account_info_dict["SPOTIFY_CLIENT_ID"],
                                    client_secret = self.account_info_dict["SPOTIFY_CLIENT_SECRET"],
                                    redirect_uri = "https://example.com", scope = self.spotify_scope,
                                    cache_path = str(Path.cwd().parents[0] / "cache" / "spotify_token_cache.json"),
                                    username = self.account_info_dict["SPOTIFY_USERNAME"])
        self.spotify_manager = spotipy.Spotify(auth_manager = auth_manager)
        self.logger.info("Authorized with Spotify")

    def login_deezer(self, deezer_object):
        self.logger.info("Attempting to authorize with Deezer")
        logged_in = deezer_object.login_via_arl(self.account_info_dict["DEEZER_ARL"])
        self.logger.info("Authorized with Deezer: " + str(logged_in))
