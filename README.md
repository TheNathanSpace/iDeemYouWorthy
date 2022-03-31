# iDeemYouWorthy

This program automatically pulls playlists from Spotify, downloads the music, and creates local versions of the playlists. Primarily, it's to be used with iTunes or Android to transfer the playlists to a phone, keeping your local libraries up-to-date with Spotify.

## Usage

iDeemYouWorthy is written for [Python 3](https://www.python.org/downloads/). 

### Installation/Operation

1. Download the `.zip` file from [Releases](https://github.com/TheKingElessar/iDeemYouWorthy/releases). Unzip it. 
2. In the main directory (the one with the `README.md` file), open a terminal and run `pip install -r requirements.txt` (or `python -m pip install -r requirements.txt` if you get an error message). This should automatically install required dependencies.  
3. Open a terminal in the subdirectory `ideemyouworthy`, and start the `main.py` file using a command like `python main.py` (exact command might depond on how your Python environment is set up).
4. The program will generate several files on its initial run. You'll need to enter your [account information](ACCOUNT_INFO.md) and [custom playlists](#choosing-playlists), if applicable.

The program will prompt you for user input, so you can specify which playlists to get, whether to copy to iTunes, etc.

It should be pretty straightforward from there. Music will be downloaded into the `music` directory, which will be at the same level as the `ideemyouworthy` folder containing the code. To keep your directory clean, you should keep the entire thing in a parent directory. For example: `D:/Downloaded Music/ideemyouworthy` contains the `.py` files.

#### Choosing Playlists

You can have the program download every playlist from your Spotify account. You can also (or alternatively, on its own) specify playlists to track in the `custom_playlists.json` file. Once the file is generated after the first run, you can add playlist URLs. The URL should be the key to a JSON dictionary/object. Use https://jsonlint.com to verify it's formatted correctly. Example:

```
{
    "https://open.spotify.com/playlist/37i9dQZF1xD8shr5OgBdbQ": {
        "custom_tracks": [
            "Cotton Eye Joe - Rednex Lyrics",
            "Video Killed the Radio Star - The Buggles Lyrics"
        ]
    }
}
```

As you can see, this is also how you can add custom tracks. The custom tracks are sourced from YouTube, so enter the search string you want used.

#### Android File Transfer

As of 1.12, there's an option to automatically copy new files to a connected Android device. By new files, I mean it won't overwrite existing files, saving lots of time.

This feature requires USB debugging to be enabled on the Android device:

> On Android 4.2 and higher, the Developer options screen is hidden by default. To make it visible, go to `Settings > About phone` and tap `Build number` seven times. Return to the previous screen to find Developer options at the bottom.
> Once Developer options are enabled, you can enable USB Debugging.

You'll also need [Android Platform Tools](https://developer.android.com/studio/releases/platform-tools) for the `adb` tool. When you unzip the file, move the directory containing all the files to wherever you want it installed. Then you can add that directory to your `PATH` environmental variable [like so](https://helpdeskgeek.com/windows-10/add-windows-path-environment-variable/).

Now, in a terminal, run the command `adb start-server`. When you first connect your phone, it might ask you if you want to allow some connection; allow it.

Everything should work now!

#### User Settings

If you don't want to be prompted to enter your preferences every time, you can manually enter your settings in `user_settings.json` once and load it every time. For example:

```
{
    "always_use_user_settings": false,
    "get_user_playlists": false,
    "get_custom_playlists": true,
    "use_itunes": false,
    "fix_itunes": false,
    "make_m3u": true,
    "verify_path_lengths": true,
    "copy_to_android": true
}
```

You have to specify every one of these settings, or you'll run into problems. Setting `always_use_user_settings` to `true` will make it always load the settings without asking you to load them.

##### Storing Past Playlist Versions

If you uncomment (remove the `#`) [line 142 of `playlist.py`](/ideemyouworthy/playlist.py#L142), the `[playlist].json` files will be backed up each time they're changed. That can be used if you want to store past versions of the playlist.

#### Updating

When updating, you'll need to replace the following files:
 
 - The `ideemyouworthy` directory
 - `requirements.txt`

The recommended method is:

1. Download the latest `.zip` release
2. Unzip it
3. Copy the above files
4. Paste them in your main iDeemYouWorthy directory, replacing the current versions

Then, update dependencies by running this command in your main directory: `pip install -r requirements.txt` or `python -m pip install -r requirements.txt`.

## FAQ/Misc. Notes

Does this download duplicate tracks if you have two playlists with the same track?
 > This doesn't download the same track twice. It keeps track of which tracks are in what playlist and where they're stored, so there is only one file for each track. Deezer automatically keeps it from downloading a track in the same file location, and iDeemYouWorthy keeps track of downloaded tracks so it can add them to playlists.

I'm getting some stack overflow error!
> This happened to me in the past when I overloaded deemix, trying to download too many tracks at once. The best fix is to only download something like 500 tracks at a time. Use the custom playlist file to control which playlists are downloaded.

#### Misc. notes:

 - You can't track two playlists with the same name. Sorry.
 - If you have local files in your Spotify playlist, they'll be printed to `cache/problematic_tracks.txt`. You can figure out what to do with them.

## Motivation

Using **Spotify** for your music is great because you can access it from anywhere, you don't have to worry about local files, and it's super easy to use.

Storing music locally (like on **iTunes**) is great because there aren't any ongoing costs, it's more versatile, and you aren't reliant on a third-party.

So, this aims to combine the best of both worlds.

## Contact Information

Please let me know if you have trouble with anything! You can open a [GitHub issue](https://github.com/TheKingElessar/iDeemYouWorthy/issues), or contact me through any of these methods.

**Discord:** TheKingElessar#3226

**Reddit:** /u/TheKingElessar

**Email:** thekingelessar1@gmail.com

## Legality

What are they gonna do, ~~stab me~~ storm my Capitol?