import json
from pathlib import Path
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

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': music_directory + '/YouTube/' + '%(title)s.mp3',
            'noplaylist': True,
            'continue_dl': True,
            'progress_hooks': [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', }]
        }

        self.master_track_file = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
        if not self.master_track_file.exists():
            self.master_track_file.touch()
            self.master_track_file.write_text(json.dumps({}))
            self.logger.log("Created master track file")

        self.youtube_dl_manager = youtube_dl.YoutubeDL(ydl_opts)
        self.logger.log("Finished setting up youtube_manager")

    def search_yt(self, search_string):
        return YoutubeSearch(search_string, max_results = 1).to_dict()

    def get_search_string(self, spotify_id):
        track_item = self.spotify_manager.track(spotify_id)
        track_name = track_item["name"]
        track_artist = track_item["artists"][0]["name"]
        search_string = track_name + " " + track_artist + " lyrics"
        return search_string

    def start_download_process(self):
        self.logger.log("Starting YouTube downloads")

        self.currently_downloading = True

        with self.youtube_dl_manager as youtube_dl_manager:
            self.current_download_url = self.url_list.pop()
            youtube_dl_manager.download([self.base_url + self.current_download_url])

    def continue_download_process(self):
        with self.youtube_dl_manager as youtube_dl_manager:
            self.current_download_url = self.url_list.pop()
            youtube_dl_manager.download([self.base_url + self.current_download_url])

    def progress_hook(self, response):
        if response["status"] == "finished":
            file_name = response["filename"]

            for track in self.downloaded_tracks:
                if self.downloaded_tracks[track] == self.current_download_url:
                    self.downloaded_tracks[track] = {"youtube_url": self.current_download_url, "download_location": file_name}

            if len(self.url_list) != 0:
                self.continue_download_process()
            else:
                self.currently_downloading = False
                self.logger.log("Finished YouTube downloads")
                self.track_manager.finished_queue(self.downloaded_tracks, self.new_playlists, self.playlist_changes, self.use_itunes)

    def update_objects(self, downloaded_tracks, new_playlists, playlist_changes, use_itunes, track_manager):
        self.downloaded_tracks = downloaded_tracks
        self.new_playlists = new_playlists
        self.playlist_changes = playlist_changes
        self.use_itunes = use_itunes
        self.track_manager = track_manager
