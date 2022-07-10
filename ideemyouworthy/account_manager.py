from copy import deepcopy
from logging import Logger
from pathlib import Path

import deemix
import spotipy
from deemix.plugins import spotify
from deemix.utils.localpaths import getConfigFolder
from deezer import Deezer
from spotipy.oauth2 import SpotifyOAuth
import json
import deemix.settings as settings


class AccountManager:

    def __init__(self, logger: Logger):
        self.logger = logger

        configFolder = getConfigFolder()
        loaded_settings = deemix.settings.load(configFolder)
        music_directory = Path.cwd().parents[0] / "music"
        loaded_settings["downloadLocation"] = music_directory.as_posix()
        self.deezer_settings = loaded_settings

        self.account_info_file = Path(Path.cwd().parents[0] / "account_info.json")
        self.account_info_dict = {"SPOTIFY_USERNAME": "", "SPOTIFY_CLIENT_ID": "", "SPOTIFY_CLIENT_SECRET": "",
                                  "DEEZER_ARL": ""}

        if not self.account_info_file.exists():

            self.account_info_file.touch()
            self.account_info_file.write_text(json.dumps(self.account_info_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")

            self.logger.debug("Created account info file")

            self.logger.info("You must add your login information to account_info.json!")
            input("Press enter once login information has been added.")

            self.logger.debug("User says account info has been entered")

        else:
            self.account_info_dict = json.loads(self.account_info_file.read_text())
            self.logger.debug("User account info loaded")

        self.spotify_scope = "playlist-read-private playlist-read-collaborative"
        self.spotipy = None
        self.spotify_helper = None

    def login_spotify(self):
        self.logger.debug("Attempting to authorize with Spotify (Spotipy)")
        auth_manager = SpotifyOAuth(client_id = self.account_info_dict["SPOTIFY_CLIENT_ID"],
                                    client_secret = self.account_info_dict["SPOTIFY_CLIENT_SECRET"],
                                    redirect_uri = "https://example.com", scope = self.spotify_scope,
                                    cache_path = str(Path.cwd().parents[0] / "cache" / "spotify_token_cache.json"),
                                    username = self.account_info_dict["SPOTIFY_USERNAME"])
        self.spotipy = spotipy.Spotify(auth_manager = auth_manager)
        self.logger.info("Authorized with Spotify")

        deemix_spotify_settings_file = getConfigFolder() / "spotify" / "settings.json"
        if not deemix_spotify_settings_file.exists():
            deemix_spotify_settings_file.parent.mkdir(parents = True, exist_ok = True)
            deemix_spotify_settings_file.touch()
            deemix_spotify_settings_file.write_text(json.dumps({}))

        deemix_spotify_settings = json.loads(deemix_spotify_settings_file.read_text())
        deemix_spotify_settings["clientId"] = self.account_info_dict["SPOTIFY_CLIENT_ID"]
        deemix_spotify_settings["clientSecret"] = self.account_info_dict["SPOTIFY_CLIENT_SECRET"]

        with open(deemix_spotify_settings_file, 'w') as f:
            json.dump(deemix_spotify_settings, f, indent = 2)

        self.spotify_helper = spotify.Spotify(getConfigFolder())

        if not self.spotify_helper.enabled:
            self.logger.debug(f"Could not enable deezer/Spotify, retrying...")

            self.spotify_helper.loadSettings()

            if not self.spotify_helper.enabled:
                self.logger.debug(f"STILL could not enable deezer/Spotify, retrying...")

                self.spotify_helper.setCredentials(clientId = self.account_info_dict["SPOTIFY_CLIENT_ID"], clientSecret = self.account_info_dict["SPOTIFY_CLIENT_SECRET"])
                self.spotify_helper.checkCredentials()

                if not self.spotify_helper.enabled:
                    self.logger.debug(f"STILL COULDN'T enable deezer/Spotify. That's a problem.")

        self.logger.debug("Setup deezer Spotify helper")

    def login_deezer(self, deezer_object: Deezer):
        self.logger.debug("Attempting to authorize with Deezer")
        logged_in = deezer_object.login_via_arl(self.account_info_dict["DEEZER_ARL"])
        if logged_in:
            self.logger.info("Authorized with Deezer")
        else:
            self.logger.info("Unable to authorize with Deezer! This will likely cause lots of problems.")
