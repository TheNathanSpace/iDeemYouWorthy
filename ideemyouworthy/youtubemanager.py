import json
import re
import subprocess
from pathlib import Path
import os, sys

import mutagen
from tinytag import TinyTag
from youtube_search import YoutubeSearch

import youtube_dl


class YoutubeManager:
    def __init__(self, logger, spotify_manager, music_directory):
        self.logger = logger
        self.spotify_manager = spotify_manager

        self.base_url = "https://www.youtube.com"
        self.music_directory = music_directory
        self.current_download_url = ""

        self.url_list = None

        self.currently_downloading = False

        self.youtube_tracks_to_download = None
        self.current_download_count = 0

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': music_directory + '/YouTube/' + '%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
            'noplaylist': True,
            'continue_dl': True,
            'quiet': True
        }

        self.master_track_file = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.info("Created master track file")

        # self.youtube_tag_cache_file = Path(Path.cwd().parents[0] / "cache" / "youtube_tags.json")
        # if not self.youtube_tag_cache_file.exists():
        #     self.youtube_tag_cache_file.touch()
        #     self.youtube_tag_cache_file.write_text(json.dumps({}), encoding = "utf-8")
        #     self.logger.info("Created YouTube tag cache file")

        self.youtube_dl_manager = youtube_dl.YoutubeDL(ydl_opts)
        self.logger.info("Finished setting up youtube_manager")

    def get_search_string(self, spotify_id):
        track_item = self.spotify_manager.track(spotify_id)
        track_name = track_item["name"]
        track_artist = track_item["artists"][0]["name"]
        search_string = track_name + " " + track_artist + " lyrics"

        # full_uri = "spotify:track:" + spotify_id
        # tags_dict = {}
        # tags_dict["title"] = track_name
        # tags_dict["album_artist"] = track_artist
        #
        # full_tags_dict = json.loads(self.youtube_tag_cache_file.read_text())
        # full_tags_dict[full_uri] = tags_dict
        # self.youtube_tag_cache_file.write_text(full_tags_dict, encoding = "utf-8")

        return search_string

    def search(self, search_string):
        search_result_dict = YoutubeSearch(search_string, max_results = 1).to_dict()
        first_result = search_result_dict[0]["url_suffix"]
        return first_result

    def start_download_process(self):
        self.logger.info("Starting YouTube downloads")

        self.currently_downloading = True
        self.current_download_count += 1

        with self.youtube_dl_manager as youtube_dl_manager:
            self.current_download_url = self.url_list.pop()
            youtube_dl_manager.download([self.base_url + self.current_download_url])

    def continue_download_process(self):
        self.current_download_count += 1
        with self.youtube_dl_manager as youtube_dl_manager:
            self.current_download_url = self.url_list.pop()
            youtube_dl_manager.download([self.base_url + self.current_download_url])

    def progress_hook(self, response):
        if response["status"] == "finished":
            file_name = response["filename"]
            file_name = re.search("(.*\.)([a-zA-Z1-9]*)$", file_name).group(1) + "mp3"

            print("[" + str(self.current_download_count) + "/" + str(self.youtube_tracks_to_download) + "] Downloaded " + file_name)

            # spotify_uri = None
            #
            # # downloaded_tracks uses full spotify uri
            # full_tags_dict = json.loads(self.youtube_tag_cache_file.read_text())
            # tags_dict = full_tags_dict[spotify_uri]
            # tags_dict["title"]
            # tags_dict["album_artist"]

            for track in self.downloaded_tracks:
                if self.downloaded_tracks[track] == self.current_download_url:
                    self.downloaded_tracks[track] = {"youtube_url": self.current_download_url, "download_location": file_name}

                    master_track_dict = json.loads(self.master_track_file.read_text(encoding = "utf-8"))
                    master_track_dict[track] = self.downloaded_tracks[track]
                    self.master_track_file.write_text(json.dumps(master_track_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")
                    break

                    # spotify_uri = track

            # from mutagen.easyid3 import EasyID3
            # from mutagen.id3 import ID3
            # from mutagen import File, MutagenError
            # try:
            #     tagged_file = EasyID3(file_name)
            # except mutagen.id3.ID3NoHeaderError:
            #     tagged_file = File(file_name)
            #     print(tagged_file.items())
            #     tagged_file.add_tags()
            #     tagged_file.save()
            #     tagged_file = EasyID3(file_name)
            #
            # tagged_file["title"] = file_name
            # tagged_file.save()

            # TODO: Add tags here

            if len(self.url_list) != 0:
                self.continue_download_process()
            else:
                self.currently_downloading = False
                self.logger.info("Finished YouTube downloads")
                self.track_manager.finished_queue(self.downloaded_tracks, self.new_playlists, self.playlist_changes, self.use_itunes)

    def update_objects(self, downloaded_tracks, new_playlists, playlist_changes, use_itunes, track_manager):
        self.downloaded_tracks = downloaded_tracks
        self.new_playlists = new_playlists
        self.playlist_changes = playlist_changes
        self.use_itunes = use_itunes
        self.track_manager = track_manager
