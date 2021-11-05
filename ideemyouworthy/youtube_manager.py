import json
import os
import re
from logging import Logger
from pathlib import Path

import mutagen
from youtube_search import YoutubeSearch
from mutagen.id3 import ID3, TIT2, TRCK, TALB, TPE1
from mutagen import File

import yt_dlp

import util
from downloaded_track import DownloadedTrack
from log_manager import LogManager, YTLogger


class YoutubeManager:
    def __init__(self, log_manager: LogManager, logger: Logger, spotify_manager, music_directory, youtube_tag_dict):
        self.logger = logger
        self.spotify_manager = spotify_manager

        self.base_url = "https://www.youtube.com"
        self.music_directory = music_directory
        self.current_downloaded_track: DownloadedTrack = None

        self.in_process_list = None

        self.currently_downloading = False

        self.all_tracks_to_download = None
        self.current_download_count = 0

        self.youtube_tag_dict = youtube_tag_dict

        self.extra_track_playlists = None

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
            'quiet': True,
            'logger': YTLogger(log_manager.yt_logger)
        }

        Path.mkdir(Path.cwd().parents[0] / "cache", exist_ok = True)
        self.master_track_file = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}), encoding = "utf-8")
            self.logger.debug("Created master track file")

        self.youtube_dl_manager = yt_dlp.YoutubeDL(ydl_opts)

        self.logger.debug("Initialized YouTube manager")

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
        self.logger.debug("Starting YouTube downloads")
        self.logger.info("---  YouTube downloads:  ---")

        self.currently_downloading = True
        self.continue_download_process()

    def continue_download_process(self):
        self.current_download_count += 1
        with self.youtube_dl_manager as youtube_dl_manager:
            self.current_downloaded_track: DownloadedTrack = self.in_process_list.pop()
            try:
                youtube_dl_manager.download([self.base_url + self.current_downloaded_track.youtube_url])
            except Exception as e:
                self.logger.error("Couldn't download track from YouTube:")
                self.logger.error(e)

                if len(self.in_process_list) != 0:
                    self.continue_download_process()

    def progress_hook(self, response):
        if response["status"] == "finished":
            file_name = response["filename"]
            fake_path = re.search("(.*\.)([a-zA-Z1-9]*)$", file_name).group(1) + "mp3"

            self.current_downloaded_track.youtube_tags["filepath"] = fake_path
            self.current_downloaded_track.download_location = Path(fake_path)
            self.current_downloaded_track.store_to_master_file()

            self.logger.info("[" + str(self.current_download_count) + "/" + str(len(self.all_tracks_to_download)) + "] Downloaded " + fake_path)

            if len(self.in_process_list) != 0:
                self.continue_download_process()

    def add_tags(self):
        self.logger.debug("Started adding tags to YouTube tracks")
        tag_count = 0
        downloaded_track: DownloadedTrack
        for downloaded_track in self.all_tracks_to_download:
            if "name" in downloaded_track.youtube_tags:
                file_path = Path(downloaded_track.youtube_tags["filepath"])

                try:
                    tagged_file = ID3()
                except mutagen.id3.ID3NoHeaderError:
                    tagged_file = File()
                    tagged_file.add_tags()
                    tagged_file.save()
                    tagged_file = ID3()

                if downloaded_track.youtube_tags["name"]:
                    tagged_file["TIT2"] = TIT2(encoding = 3, text = downloaded_track.youtube_tags["name"])
                if downloaded_track.youtube_tags["track_number"]:
                    try:
                        tagged_file["TRCK"] = TRCK(encoding = 3, text = str(downloaded_track.youtube_tags["track_number"]))
                    except:
                        tagged_file["TRCK"] = TRCK(encoding = 3, text = u"1")
                if downloaded_track.youtube_tags["album"]:
                    tagged_file["TALB"] = TALB(encoding = 3, text = downloaded_track.youtube_tags["album"])
                if downloaded_track.youtube_tags["artist"]:
                    tagged_file["TPE1"] = TPE1(encoding = 3, text = downloaded_track.youtube_tags["artist"])

                tagged_file.save(file_path)

                while True:
                    try:
                        file_path.rename(file_path)
                    except:
                        continue
                    break

                new_path = Path(file_path.parent / Path(util.clean_path_child(f"{downloaded_track.youtube_tags['artist']} - {downloaded_track.youtube_tags['name']}.mp3")))

                os.rename(file_path, new_path)
                downloaded_track.download_location = new_path
                downloaded_track.store_to_master_file()
                tag_count += 1

        self.logger.debug(f"Finished adding tags to {tag_count} YouTube tracks")
