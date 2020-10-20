import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import collections
from pathlib import Path
import win32com.client

def dictToSet(dict_to_convert):
    returned_set = set()
    for key in dict_to_convert:
        returned_set.add(key)
    return returned_set

os.environ['SPOTIPY_CLIENT_ID'] = '2e020c69cc5449f4ad351aff8465f6d6'
os.environ['SPOTIPY_CLIENT_SECRET'] = '98648713945c438bac66a98e0d78d247'
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://example.com'

scope = "playlist-read-private playlist-read-collaborative"

token = spotipy.util.prompt_for_user_token("pulybt4ljjlf0l9qs2ylh9du7", scope)
sp = None

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

playlists = sp.user_playlists('pulybt4ljjlf0l9qs2ylh9du7')
new_playlists = collections.OrderedDict()
while playlists:
    for i, playlist in enumerate(playlists['items']):
        new_playlists[playlist['name']] = playlist['uri']
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None

old_playlists = collections.OrderedDict()

Path.mkdir(Path.cwd() / "cache", exist_ok = True)
master_playlist_file = Path(Path.cwd() / "cache" / "saved_playlists.txt")
if master_playlist_file.exists():
    old_playlists = json.loads(master_playlist_file.read_text())
else:
    master_playlist_file.touch()
    
master_playlist_file.write_text(json.dumps(new_playlists))

old_playlists_set = dictToSet(old_playlists)
new_playlists_set = dictToSet(new_playlists)

Path.mkdir(Path.cwd() / "playlists", exist_ok = True)

# Make file for each playlist here
for playlist in new_playlists:
    file_path = Path.cwd() / "playlists" / (playlist + ".txt")
    if not file_path.exists():
        file_path.touch()
        file_path.write_text(json.dumps({}))

master_track_file = Path(Path.cwd() / "cache" / "track_master_list.txt")
if not master_track_file.exists():
    master_track_file.touch()
    master_track_file.write_text(json.dumps({}))

playlist_changes = collections.OrderedDict()

for playlist in new_playlists:
    file_path = Path.cwd() / "playlists" / (playlist + ".txt")
    old_playlist_songs = json.loads(file_path.read_text())
    new_playlist_songs = collections.OrderedDict()

    playlist_response = sp.playlist_items(new_playlists[playlist], fields = 'items.track.uri')

    playlist_response = playlist_response['items']
    index = 0
    for track in playlist_response:
        tracks_dict = playlist_response[index]['track']
        track_uri = tracks_dict["uri"]
        track_data = {}
        new_playlist_songs[track_uri] = None

        index += 1
            
    playlist_differences = new_playlist_songs.copy()
    to_remove = set()
    for track in playlist_differences:
        if track in old_playlist_songs:
            print("to remove")
            to_remove.add(track)
    
    for track in to_remove:
        print("removing")
        playlist_differences.pop(track, None)
            
    playlist_changes[playlist] = playlist_differences
    
    file_path.write_text(json.dumps(new_playlist_songs))

d = json.loads(master_track_file.read_text())
master_track_set = dictToSet(d)

tracks_to_download = set()

for playlist in playlist_changes:
    playlist_changes_set = dictToSet(playlist_changes[playlist])
    differences = playlist_changes_set.difference(master_track_set) # Checks against master list to avoid downloading again
    
    tracks_to_download = tracks_to_download.union(differences) # Checks against other lists so a new one isn't downloaded twice

from deemix.utils.localpaths import getConfigFolder
from deemix.app.settings import Settings
from deemix.app.spotifyhelper import SpotifyHelper, emptyPlaylist as emptySpotifyPlaylist
from deemix.api.deezer import Deezer
from deemix.app.queuemanager import QueueManager

configFolder = getConfigFolder()
settings = Settings(configFolder).settings
settings["downloadLocation"] = str(Path.cwd() / "music")
sp = SpotifyHelper(configFolder)
qm = QueueManager()

dz = Deezer()
    
import os.path as path
if path.isfile(path.join(configFolder, '.arl')):
    with open(path.join(configFolder, '.arl'), 'r') as f:
        arl = f.readline().rstrip("\n")
    dz.login_via_arl(arl)

dz.login_via_arl("8275c01b2a1f89f1370fb6f9e054cfadf34dc3e461ca312a9108f03bc8a53da458de5cf115b3a97802184ddf1fc661faaf7b09aafef3ec14e2cf4bf404fc47b67cf7da4fc0338ec216e66a8c9dacb7d5f671d14a82dfa1b334ca59c0b142906d")

def finished_queue():
    """ downloaded_tracks:
        {
            "spotify:track:1rqqCSm0Qe4I9rUvWncaom": {
                "deezer_uuid": "track_867154512_3",
                "download_location": "D:\\_python\\Deemix Playlists\\music\\The Glitch Mob - Chemicals - EP\\The Glitch Mob - Chemicals.mp3"
            }
        }
    """

    old_master_track_dict = json.loads(master_track_file.read_text())
    for track in downloaded_tracks:
        if not track in old_master_track_dict and isinstance(downloaded_tracks[track], dict):
            old_master_track_dict[track] = downloaded_tracks[track]

    master_track_file.write_text(json.dumps(old_master_track_dict))
    
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

    for playlist in new_playlists:
        if not playlist in itunes_playlists_dict.keys():
            new_playlist = itunes.CreatePlayList(playlist)
            itunes_playlists_dict[playlist] = new_playlist

    # Cycle through playlist changes
    for playlist in playlist_changes:
        print(json.dumps(playlist_changes[playlist]))
        for track in playlist_changes[playlist]:
            if track in old_master_track_dict and isinstance(old_master_track_dict[track], dict): # (this will be true unless there was a downloading error) 
                itunes_playlists_dict[playlist].AddFile(old_master_track_dict[track]["download_location"])

from deemix.app.messageinterface import MessageInterface
class MyMessageInterface(MessageInterface):
    def send(self, message, value = None):
        if message == "updateQueue" and "downloaded" in value:
            if value["downloaded"] == True:
                # {'uuid': self.queueItem.uuid, 'downloaded': True, 'downloadPath': writepath}
                for track in downloaded_tracks:
                    if downloaded_tracks[track] == value["uuid"]:
                        downloaded_tracks[track] = {"deezer_uuid": value["uuid"], "download_location": value["downloadPath"]}
                
                if len(qm.queue) == 0:
                    finished_queue()
                
my_interface = MyMessageInterface()

downloaded_tracks = collections.OrderedDict()

queue_list = list()
for track in tracks_to_download:
    split_uri = track.split(":")

    spotify_url = "https://open.spotify.com/" + split_uri[1] + "/" + split_uri[2]
    deezer_id = sp.get_trackid_spotify(dz, split_uri[2], False, None)

    if not deezer_id == 0:
        deezer_uuid = "track_" + str(deezer_id) + "_3"
        downloaded_tracks[track] = deezer_uuid
        
        queue_list.append("https://www.deezer.com/en/track/" + str(deezer_id))

qm.addToQueue(dz, sp, queue_list, settings, interface = my_interface)
