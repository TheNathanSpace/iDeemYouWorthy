import json
from pathlib import Path
import win32com.client
import util
import collections
from tinytag import TinyTag


class TrackManager:

    def __init__(self, logger, account_manager):
        self.logger = logger
        self.account_manager = account_manager
        self.spotify_manager = account_manager.spotify_manager

        self.master_track_file = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.info("Created master track file")

        self.problematic_tracks_file = Path(Path.cwd().parents[0] / "cache" / "problematic_tracks.txt")
        if not self.problematic_tracks_file.exists():
            self.problematic_tracks_file.touch()
            self.logger.info("Created skipped local tracks file")

        self.has_finished_queue = False

    def get_playlist_tracks(self, playlist_id, fields):
        results = self.spotify_manager.playlist_tracks(playlist_id, fields = fields)
        tracks = results['items']
        while results['next']:
            results = self.spotify_manager.next(results)
            tracks.extend(results['items'])
        return tracks

    def find_new_tracks(self, new_playlists):
        playlist_changes = collections.OrderedDict()

        for playlist in new_playlists:
            playlist_file_path = Path.cwd().parents[0] / "playlists" / (playlist + ".json")
            old_playlist_songs = json.loads(playlist_file_path.read_text())
            new_playlist_songs = collections.OrderedDict()

            playlist_response = self.get_playlist_tracks(new_playlists[playlist], 'items.track.uri, next')

            index = 0
            for track in playlist_response:
                tracks_dict = playlist_response[index]['track']
                track_uri = tracks_dict["uri"]
                new_playlist_songs[track_uri] = None

                index += 1

            playlist_differences = new_playlist_songs.copy()
            to_remove = set()
            for track in playlist_differences:
                if track in old_playlist_songs:
                    to_remove.add(track)

            for track in to_remove:
                playlist_differences.pop(track, None)

            playlist_changes[playlist] = playlist_differences
            self.logger.info(playlist + ": Found " + str(len(playlist_differences)) + " new tracks")

            playlist_file_path.write_text(json.dumps(new_playlist_songs, indent = 4, ensure_ascii = False), encoding = "utf-8")

        return playlist_changes

    def clear_duplicate_downloads(self, playlist_changes):
        master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
        master_track_set = util.dictToSet(master_track_dict)

        tracks_to_download = set()

        for playlist in playlist_changes:
            playlist_changes_set = util.dictToSet(playlist_changes[playlist])

            differences = playlist_changes_set.difference(master_track_set)  # Checks against already downloaded tracks

            tracks_to_download = tracks_to_download.union(differences)  # Checks against other lists so a new one isn't downloaded twice

        self.logger.info("Cleared unnecessary downloads")
        return tracks_to_download

    def finished_queue(self, downloaded_tracks, new_playlists, playlist_changes, use_itunes):
        self.has_finished_queue = True
        self.logger.info("deezer and YouTube queues finished downloading")

        old_master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
        # for track in downloaded_tracks:
        #     if track not in old_master_track_dict and isinstance(downloaded_tracks[track], dict):
        #         old_master_track_dict[track] = downloaded_tracks[track]
        #
        # self.master_track_file.write_text(json.dumps(old_master_track_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")
        # self.logger.info("Saved master track list to file")

        if use_itunes:
            self.logger.info("Using iTunes")
            itunes = win32com.client.Dispatch("iTunes.Application")
            self.logger.info("iTunes opened")
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

            for playlist in new_playlists:
                if playlist not in itunes_playlists_dict.keys():
                    new_playlist = itunes.CreatePlayList(playlist)
                    itunes_playlists_dict[playlist] = new_playlist

            # Cycle through playlist changes
            for playlist in playlist_changes:
                for track in playlist_changes[playlist]:
                    if track in old_master_track_dict and isinstance(old_master_track_dict[track], dict):  # (this will be true unless there was a downloading error)
                        itunes_playlists_dict[playlist].AddFile(old_master_track_dict[track]["download_location"])

            self.logger.info("Finished updating iTunes")
        else:
            self.logger.info("Not using iTunes")

    def fix_itunes(self, itunes_playlists_dict, playlist_edits):
        self.logger.info("Starting to fix iTunes")
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
                            ""
                            self.logger.warn("What just happened? This isn't good.")
            if playlist_edits[playlist]["missing_tracks"]:
                for missing_track in playlist_edits[playlist]["missing_tracks"]:
                    # (technically moving right ahead without checking for the file to exist could be bad if it was deleted from the master list but not the playlist list?)
                    try:
                        itunes_playlists_dict[playlist].AddFile(missing_track)
                        missing_count += 1

                    except:
                        self.logger.warn(missing_track + " could not be added to iTunes. The max file path length on Windows is 260; the length of this file path is " + str(len(missing_track)))
                        file_path_length = str(len(missing_track))
                        self.logger.info(missing_track + " could not be added to iTunes. File path length: " + file_path_length)
                        self.store_problematic_track("(" + file_path_length + ") " + missing_track)

            self.logger.info(playlist + ": Removed " + str(extra_count) + " extra tracks")
            self.logger.info(playlist + ": Added " + str(missing_count) + " missing tracks")

    # This verifies that the iTunes and cached playlists agree
    def verify_itunes(self):
        self.logger.info("Starting to verify iTunes is up-to-date")
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
            official_playlist_dict = json.loads(playlist_file_path.read_text())  # todo: this doesn't allow other playlists in itunes
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

            extra_tracks_names = util.dictToSetValues(extra_tracks)
            missing_tracks_names = util.dictToSetValues(missing_tracks)

            playlist_edits[playlist] = collections.OrderedDict()
            playlist_edits[playlist]["extra_tracks"] = extra_tracks
            playlist_edits[playlist]["missing_tracks"] = missing_tracks

        self.fix_itunes(itunes_playlists_dict, playlist_edits)

    def store_problematic_track(self, local_track):
        with self.problematic_tracks_file.open("a") as append_file:
            append_file.write(local_track + "\n")
