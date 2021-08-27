import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, List


def compare_playlists(playlist_one_path: Path, playlist_two_path: Path):
    playlist_one_songs: List = list(json.loads(playlist_one_path.read_text()))
    playlist_two_songs: List = list(json.loads(playlist_two_path.read_text()))

    playlist_one_exclusives = []
    for track_uri in playlist_one_songs:
        if track_uri not in playlist_two_songs:
            playlist_one_exclusives.append(track_uri)

    playlist_two_exclusives = []
    for track_uri in playlist_two_songs:
        if track_uri not in playlist_one_songs:
            playlist_two_exclusives.append(track_uri)

    master_track_file = Path(Path.cwd().parents[0] / "cache" / "track_master_list.json")
    master_track_dict = json.loads(master_track_file.read_text(encoding = "utf-8"))
    for index, item in enumerate(playlist_one_exclusives):
        if item in master_track_dict:
            playlist_one_exclusives[index] = master_track_dict[item]["download_location"]
    for index, item in enumerate(playlist_two_exclusives):
        if item in master_track_dict:
            playlist_two_exclusives[index] = master_track_dict[item]["download_location"]

    output_path = Path.cwd().parents[0] / "output"
    output_path.mkdir(exist_ok = True)
    file_string = (str(datetime.now()) + "_comparison.json").replace(":", "꞉")
    output_path = output_path / file_string
    output_dict = {f"{playlist_one_path.as_posix()}": {"exclusives": playlist_one_exclusives}, f"{playlist_two_path.as_posix()}": {"exclusives": playlist_two_exclusives}}
    output_path.write_text(json.dumps(output_dict, indent = 4, ensure_ascii = False), encoding = "utf-8")

    print(f"File output saved to {output_path.as_posix()}")


print("Which playlists would you like to compare?")
one = input("Playlist 1: ")
two = input("Playlist 2: ")

valid = True
try:
    if not Path(one).exists():
        one_path = Path.cwd().parents[0] / "playlists" / f"{one}.json"
        if one_path.exists():
            one = one_path
except:
    print("That's not a playlist! Enter a playlist name or file path.")
    valid = False

try:
    if not Path(two).exists():
        two_path = Path.cwd().parents[0] / "playlists" / f"{two}.json"
        if two_path.exists():
            two = two_path
except:
    print("That's not a playlist! Enter a playlist name or file path.")
    valid = False

if valid:
    compare_playlists(one, two)
