import collections
import json
import urllib.parse
from logging import Logger
from pathlib import Path

import deemix
import deezer
from tinytag import TinyTag

import util
from DownloadedTrack import DownloadedTrack
from accountmanager import AccountManager
from youtubemanager import YoutubeManager


class TrackManagerNew:

    # Methods:
    #  x Load playlists from custom_playlists.json
    #  x Load playlists from Spotify account
    # Fields:
    #  x List of Playlists
    #  x AccountManager

    def __init__(self, logger: Logger, account_manager: AccountManager):
        self.logger = logger
        self.account_manager = account_manager

        self.master_track_file: Path = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.debug("Created master track file")

        self.problematic_tracks_file = Path(Path.cwd().parents[0] / "cache" / "problematic_tracks.txt")
        if not self.problematic_tracks_file.exists():
            self.problematic_tracks_file.touch()
            self.logger.debug("Created problematic tracks file")

        self.unique_spotify_tracks: list = []
        self.custom_tracks: list = []

        self.youtube_tracks: list = []
        self.deezer_tracks: list = []

        self.logger.debug("Initialized track manager")

    def process_spotify_tracks(self, deezer_object: deezer.Deezer, listener, youtube_manager: YoutubeManager):
        for track in self.unique_spotify_tracks:
            self.assign_source(track, deezer_object, listener, youtube_manager)

    def process_custom_tracks(self, youtube_manager: YoutubeManager):
        for track_name in self.custom_tracks:
            self.assign_custom_track(track_name, youtube_manager)

    def assign_source(self, track_uri: str, deezer_object: deezer.Deezer, listener, youtube_manager: YoutubeManager):
        split_uri = track_uri.split(":")
        downloaded_track = DownloadedTrack(key = track_uri, deezer_uuid = None, youtube_url = None, download_location = None, logger = self.logger)

        is_youtube = False
        is_local = False
        if split_uri[1] == "local":
            is_youtube = True
            is_local = True
            self.store_problematic_track(track_uri)
        else:
            spotify_url = "https://open.spotify.com/" + split_uri[1] + "/" + split_uri[2]
            try:
                deezer_single = deemix.generateDownloadObject(dz = deezer_object, link = spotify_url, bitrate = deezer.TrackFormats.MP3_320, plugins = {"spotify": self.account_manager.spotify_helper}, listener = listener)

                deezer_uuid = "track_" + str(deezer_single.id) + "_3"
                downloaded_track.deezer_uuid = deezer_uuid
                downloaded_track.deezer_single = deezer_single

            except Exception as e:
                is_youtube = True

        if is_youtube:
            if not is_local:
                downloaded_track.youtube_tags = self.get_track_data(track_uri)
                search_string = youtube_manager.get_search_string(split_uri[2])
                first_result = youtube_manager.search(search_string)
            else:
                artist = urllib.parse.unquote(split_uri[2]).replace("+", " ")
                album = urllib.parse.unquote(split_uri[3]).replace("+", " ")
                title = urllib.parse.unquote(split_uri[4]).replace("+", " ")

                first_result = youtube_manager.search(f"{artist} {album} {title}")

            downloaded_track.youtube_url = first_result

        downloaded_track.update_traits()
        if not downloaded_track.is_youtube:
            self.deezer_tracks.append(downloaded_track)
        else:
            self.youtube_tracks.append(downloaded_track)

    def assign_custom_track(self, track_name: str, youtube_manager: YoutubeManager):
        downloaded_track = DownloadedTrack(key = track_name, deezer_uuid = None, youtube_url = None, download_location = None, logger = self.logger)

        first_result = youtube_manager.search(track_name)
        downloaded_track.youtube_url = first_result

        downloaded_track.update_traits()
        self.youtube_tracks.append(downloaded_track)

    def store_problematic_track(self, local_track):
        with self.problematic_tracks_file.open("a") as append_file:
            append_file.write(local_track + "\n")

    def get_track_data(self, uri):
        track = self.account_manager.spotipy.track(uri)
        track_data = {}
        track_data["name"] = track["name"]
        track_data["track_number"] = track["track_number"]
        track_data["album"] = track["album"]["name"]
        track_data["artist"] = track["artists"][0]["name"]

        return track_data

    # **************************************************************************************************
    # *  Now entering the DANGER ZONE of code I wrote long ago and haven't tested in a very long time  *
    # **************************************************************************************************

    def fix_itunes(self, itunes_playlists_dict, playlist_edits):
        self.logger.debug("Starting to fix iTunes")
        for playlist in playlist_edits:
            extra_count = 0
            missing_count = 0
            if playlist_edits[playlist]["extra_tracks"]:
                for extra_track in playlist_edits[playlist]["extra_tracks"]:
                    # Cycle through iTunes playlist, remove this track when you find it
                    for track in itunes_playlists_dict[playlist].Tracks:
                        try:
                            itunes_location = track.Location
                            if itunes_location == extra_track:
                                track.Delete()
                                extra_count += 1
                        except:
                            self.logger.warn("What just happened? This isn't good.")
            if playlist_edits[playlist]["missing_tracks"]:
                for missing_track in playlist_edits[playlist]["missing_tracks"]:
                    # (technically moving right ahead without checking for the file to exist could be bad if it was deleted from the master list but not the playlist list?)
                    try:
                        itunes_playlists_dict[playlist].AddFile(missing_track)
                        missing_count += 1

                    except:
                        self.logger.warning(missing_track + " could not be added to iTunes. The max file path length on Windows is 260; the length of this file path is " + str(len(missing_track)))
                        file_path_length = str(len(missing_track))
                        self.logger.info(missing_track + " could not be added to iTunes. File path length: " + file_path_length)
                        self.store_problematic_track("(" + file_path_length + ") " + missing_track)

            self.logger.info(f"Added {str(missing_count)} and removed {str(extra_count)} tracks from: " + playlist)

    # This verifies that the iTunes and cached playlists agree
    def verify_itunes(self):
        import win32com.client
        self.logger.debug("Starting to verify iTunes is up-to-date")
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

        playlist_edits = collections.OrderedDict()
        for playlist in itunes_playlists_dict:

            playlist_file_path = Path.cwd().parents[0] / "playlists" / (playlist + ".json")

            if not playlist_file_path.exists():
                continue

            official_playlist_dict = json.loads(playlist_file_path.read_text())
            official_locations = set()

            for track in official_playlist_dict:
                master_file_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
                if track in master_file_dict:
                    track_location = master_file_dict[track]["download_location"]
                    official_locations.add(track_location)

            itunes_locations = set()
            extra_tracks = collections.OrderedDict()  # Tracks in iTunes but not playlist files
            for track in itunes_playlists_dict[playlist].Tracks:
                try:
                    itunes_location = track.Location
                    itunes_locations.add(itunes_location)
                    if itunes_location not in official_locations:
                        extra_tracks[itunes_location] = track.Name  # Todo: Check if there are too many or too few of a track?

                except:
                    self.logger.warn("Found a non-local file. This isn't a problem but I think it might be interesting")

            missing_tracks = collections.OrderedDict()
            for track in official_locations:
                if track not in itunes_locations:
                    tags = TinyTag.get(track)
                    missing_tracks[track] = tags.title

            extra_tracks_names = util.dict_to_set_values(extra_tracks)
            missing_tracks_names = util.dict_to_set_values(missing_tracks)

            playlist_edits[playlist] = collections.OrderedDict()
            playlist_edits[playlist]["extra_tracks"] = extra_tracks
            playlist_edits[playlist]["missing_tracks"] = missing_tracks

        self.fix_itunes(itunes_playlists_dict, playlist_edits)
