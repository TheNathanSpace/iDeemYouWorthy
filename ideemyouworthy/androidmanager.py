import os
from logging import Logger
from pathlib import Path
from typing import List

from ppadb.client import Client as AdbClient
from ppadb.device import Device


def transfer_all(logger: Logger):
    music_path = Path.cwd().parents[0] / "music"
    playlists_path = Path.cwd().parents[0] / "playlists"

    # Default is "127.0.0.1" and 5037
    client = AdbClient(host = "127.0.0.1", port = 5037)
    if len(client.devices()) == 0:
        logger.info("No phone connected! Can't copy files.")
        return

    devices: List[Device] = client.devices()

    device = devices[0]

    transferred_count = 0

    all_music: List[Path] = []
    for dirname, dirnames, filenames in os.walk(music_path):
        for filename in filenames:
            all_music.append(Path(os.path.join(dirname, filename)))

    for file in all_music:
        file_name = file.name
        file_parent = file.parents[0].name
        android_path = f"/storage/emulated/0/Music/music/{file_parent}/{file_name}"
        exists = "No such file or directory" not in device.shell(f"ls \"{android_path}\"")
        if not exists:
            device.push(file, android_path)
            transferred_count += 1

    all_playlists: List[Path] = []
    for dirname, dirnames, filenames in os.walk(playlists_path):
        for filename in filenames:
            all_playlists.append(Path(os.path.join(dirname, filename)))

    for file in all_playlists:
        file_name = file.name
        android_path = f"/storage/emulated/0/Music/playlists/{file_name}"
        exists = "No such file or directory" not in device.shell(f"ls \"{android_path}\"")
        if not exists:
            device.push(file, android_path)
            transferred_count += 1

    logger.info(f"Copied {transferred_count} files to your Android!")
