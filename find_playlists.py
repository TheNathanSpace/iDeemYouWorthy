import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import collections
from pathlib import Path
import win32com.client

itunes = win32com.client.Dispatch("iTunes.Application")

def dictToSet(dict_to_convert):
    returned_set = set()
    for key in dict_to_convert:
        returned_set.add(key)
    return returned_set

os.environ['SPOTIPY_CLIENT_ID'] = ''
os.environ['SPOTIPY_CLIENT_SECRET'] = ''
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
#        print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))

    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None

itunes_sources = itunes.Sources
itunes_playlists = None
for source in itunes_sources:
    if source.Kind == 1: # ITSourceKindLibrary
        itunes_playlists = source.Playlists

itunes_playlists_set = set()
playlists_left = itunes_playlists.Count
while playlists_left != 0:
    playlist = itunes_playlists.Item(playlists_left).Name
    blacklist = {"Voice Memos", "Genius", "Audiobooks", "Podcasts", "TV Shows", "Movies", "Library", "Music"}
    if playlist not in blacklist:
        itunes_playlists_set.add(playlist)
    playlists_left -= 1

print(itunes_playlists_set)

old_playlists = collections.OrderedDict()
master_playlist_file = Path("saved_playlists.txt")
if Path("saved_playlists.txt").exists():
    old_playlists = json.loads(master_playlist_file.read_text())
    
master_playlist_file = Path("saved_playlists.txt")
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
        print("New playlist file created: " + playlist)
    if not playlist in itunes_playlists_set:
        new_playlist = itunes.CreatePlayList(playlist)

master_track_file = Path("track_master_list.txt")
if not master_track_file.exists():
    master_track_file.touch()
    master_track_file.write_text(json.dumps({}))
    print("New master track created")

playlist_changes = collections.OrderedDict()

for playlist in new_playlists:
    file_path = Path.cwd() / "playlists" / (playlist + ".txt")
    old_playlist_songs = json.loads(file_path.read_text())
    new_playlist_songs = collections.OrderedDict()

    playlist_response = sp.playlist_items(new_playlists[playlist], fields = 'items.track.name, items.track.uri, items.track.album.name, items.track.album.artists')

    playlist_response = playlist_response['items']
    index = 0
    for track in playlist_response:
        tracks_dict = playlist_response[index]['track']
        track_uri = tracks_dict["uri"]
        track_data = {}
        track_data["track_name"] = tracks_dict["name"]
        track_data["track_album_name"] = tracks_dict["album"]["name"]
        new_playlist_songs[track_uri] = track_data

        index += 1

    old_playlist_songs_set = dictToSet(old_playlist_songs)    
    new_playlist_songs_set = dictToSet(new_playlist_songs)

    differences = new_playlist_songs_set.difference(old_playlist_songs_set)

    playlist_changes[playlist] = differences

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
print(configFolder)
settings = Settings(configFolder).settings
print(settings["downloadLocation"])
settings["downloadLocation"] = str(Path.cwd() / "music")
print("Download location set to:", settings["downloadLocation"])
sp = SpotifyHelper(configFolder)
qm = QueueManager()

dz = Deezer()
    
import os.path as path
if path.isfile(path.join(configFolder, '.arl')):
    with open(path.join(configFolder, '.arl'), 'r') as f:
        arl = f.readline().rstrip("\n")
    dz.login_via_arl(arl)

dz.login_via_arl("8275c01b2a1f89f1370fb6f9e054cfadf34dc3e461ca312a9108f03bc8a53da458de5cf115b3a97802184ddf1fc661faaf7b09aafef3ec14e2cf4bf404fc47b67cf7da4fc0338ec216e66a8c9dacb7d5f671d14a82dfa1b334ca59c0b142906d")
print("Logged in: ", dz.logged_in)

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
            # Add to playlist here!!!
            
    master_track_file.write_text(json.dumps(old_master_track_dict))
    
    # If the happy MessageInterface message is sent you'll have to restructure this
    for playlist in playlist_changes:
        for track in playlist_changes[playlist]:
            if track in old_master_track_dict and isinstance(old_master_track_dict[track], dict):
                # Cycle through itunes playlists finding correct name
                playlists_left = itunes_playlists.Count
                while playlists_left != 0:
                    itunes_playlist = itunes_playlists.Item(playlists_left)
                    if itunes_playlist.Name == playlist:
                        itunes_playlist.AddFile(old_master_track_dict[track]["download_location"])
                        playlist_changes[playlist].remove(track) # Problem: Can't remove from set while iterating, so it just keeps adding the same track
                        print("Added", old_master_track_dict[track]["download_location"])
                    playlists_left -= 1

from deemix.app.messageinterface import MessageInterface
class MyMessageInterface(MessageInterface):
    def send(self, message, value = None):
        if message == "updateQueue" and "downloaded" in value:
            if value["downloaded"] == True:
                # {'uuid': self.queueItem.uuid, 'downloaded': True, 'downloadPath': writepath}
                spotify_uuid = None
                for track in downloaded_tracks:
                    if downloaded_tracks[track] == value["uuid"]:
                        downloaded_tracks[track] = {"deezer_uuid": value["uuid"], "download_location": value["downloadPath"]}
                
                finished_queue()
                
my_interface = MyMessageInterface()

downloaded_tracks = collections.OrderedDict()

split_uri = None
for track in tracks_to_download:
    split_uri = track.split(":")

    spotify_url = "https://open.spotify.com/" + split_uri[1] + "/" + split_uri[2]
    deezer_id = sp.get_trackid_spotify(dz, split_uri[2], False, None)

    deezer_uuid = "track_" + str(deezer_id) + "_3"
    downloaded_tracks[track] = deezer_uuid

    qm.addToQueue(dz, sp, "https://www.deezer.com/en/track/" + str(deezer_id), settings, interface = my_interface)

# So now:
#   tracks_to_download is a set containing the URIs of new tracks that need to be downloaded
#   playlist_changes is a dictionary containing sets assigned to playlist names (maybe should change to URI? URI file names, file contains actual playlist name? to fix duplicate playlist names)

# After adding the new songs to iTunes, update the stored version of the playlist in the playlists folder. Haven't added the saving capability.
