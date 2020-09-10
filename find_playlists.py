import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import collections
from pathlib import Path

def dictToSet(dict_to_convert):
    returned_set = set()
    for key in dict_to_convert:
        returned_set.add(key)
    return returned_set

os.environ['SPOTIPY_CLIENT_ID'] = '4b9af52471714ee6a7f44bf2c68c7eae'
os.environ['SPOTIPY_CLIENT_SECRET'] = ''
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://example.com'

scope = "playlist-read-private playlist-read-collaborative"

token = spotipy.util.prompt_for_user_token("0iiohbbq3rib2z3jnmd1piqia", scope)
sp = None

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

playlists = sp.user_playlists('0iiohbbq3rib2z3jnmd1piqia')
new_playlists = collections.OrderedDict()
while playlists:
    for i, playlist in enumerate(playlists['items']):
        new_playlists[playlist['name']] = playlist['uri']
#        print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))

    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None

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

master_track_list = json.loads(master_track_file.read_text())
master_track_set = dictToSet(master_track_list)

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
settings = Settings(configFolder)
sp = SpotifyHelper(configFolder)
qm = QueueManager()

split_uri = None
for track in tracks_to_download:
    split_uri = track.split(":")
    break

dz = Deezer()

# arl = None
# if Path(configFolder / '.arl').exists():
    # print(Path(configFolder / '.arl'))
    # with open(Path(configFolder / '.arl'), 'r') as f:
        # arl = f.readline().rstrip("\n")
    # dz.login_via_arl(arl)

import os.path as path
if path.isfile(path.join(configFolder, '.arl')):
    with open(path.join(configFolder, '.arl'), 'r') as f:
        arl = f.readline().rstrip("\n")
    dz.login_via_arl(arl)

dz.login_via_arl("8275c01b2a1f89f1370fb6f9e054cfadf34dc3e461ca312a9108f03bc8a53da458de5cf115b3a97802184ddf1fc661faaf7b09aafef3ec14e2cf4bf404fc47b67cf7da4fc0338ec216e66a8c9dacb7d5f671d14a82dfa1b334ca59c0b142906d")
print("Logged in: ", dz.logged_in)

spotify_url = "https://open.spotify.com/" + split_uri[1] + "/" + split_uri[2]
deezer_id = sp.get_trackid_spotify(dz, split_uri[2], False, None)
qm.addToQueue(dz, sp, "https://www.deezer.com/en/track/" + str(deezer_id), settings.settings, None, None)

# So how do I know what file I can work with, without having to request *more* information from Deezer or Spotify? I only have access to the URI.
# The tracks will be in the form "Artist - Album"/"Artist - Track.mp3".
# So you need to store:
#   Artist
#   Album
#   Track
# Honestly, the best solution is probably just to grab the info from Spotify on the inital pass, then store everything in a dict inside the sets. Get the name of the first album artist.
# You may need several sets—one with just the URI, one with all of the info. Or, better, use the URI set to lookup the data in a dict.

# So now:
#   tracks_to_download is a set containing the URIs of new tracks that need to be downloaded
#   playlist_changes is a dictionary containing sets assigned to playlist names (maybe should change to URI? URI file names, file contains actual playlist name? to fix duplicate playlist names)


# After songs are downloaded, combine master_track_set and tracks_to_download