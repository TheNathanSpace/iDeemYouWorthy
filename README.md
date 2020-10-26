# iDeemYouWorthy

The two purposes of this program:

 1. Check Spotify for changes to your playlists, downloading the new tracks.
 2. Add the local versions of your Spotify playlists to iTunes.
 
Ultimately, the goal is to have a script that you can have running in the background, keeping your iTunes library up-to-date with Spotify.

___

Using **Spotify** for your music is great because you can access it from anywhere, you don't have to worry about the local files, and it's super easy to use.

Storing music locally (like on **iTunes**) is great because there aren't any ongoing costs, it's more versatile, and you aren't reliant on a corporate entity.

So, this aims to combine the best of both worlds.


## Contents

The program files can be found in the directory `ideemyouworthy`. `main.py` is the main script; run that. It's written for [Python 3.8](https://www.python.org/downloads/). 

After I hit 2.0 (GUI!) I'll probably package it into a nice `.exe`.

Check out the [changelog](CHANGELOG.md)!

### Installation/Operation

Download the `.zip` file in "Releases". Unzip it. Navigate to `ideemyouworthy` with a terminal and run `main.py` using one of the following commands. It will depend on how your Python environment is set up.

 - `python main.py`
 - `python3 main.py`
 - `main.py`
 
It should be pretty straightforward from there. 

You'll need to add your Spotify and deezer account information to the `account_info.json` file. This file will be generated upon the first execution of `main.py`. Once it's there, gather the information following the steps below and paste it in. To verify the `.json` file is still formatted correctly, you can use https://jsonlint.com.

You will be able to get the playlists from your Spotify account. You can also (or alternatively, on its own) specify playlists to track in the `custom_playlists.json` file. Once the file is generated after the first run, you can add URLs. The URL should be the key, and the string should be empty. Use https://jsonlint.com to verify it's formatted correctly.

You are not giving me your password! These tokens are used to *avoid* sharing your password. All of this data is stored locally in the `account_info.json` file, and is sent exclusively to Spotify and deezer. It is safe.

##### Finding `SPOTIFY_USERNAME`

 1. Go to https://open.spotify.com/. Sign into your account.
 2. In the top right, click your display name, then `Account`.
 3. Your `Username` should be the first field on this page.

##### Finding `SPOTIFY_CLIENT_ID`

 1. Go to https://developer.spotify.com/dashboard/login. Sign into your account.
 2. Select `CREATE AN APP`.
 3. The `App name` and `App description` are irrelevant. Click `CREATE` when you're ready.
 4. Your `Client ID` will be near the top right, under the app name/description.

##### Finding `SPOTIFY_CLIENT_SECRET`

 1. In the same app you created above, click `SHOW CLIENT SECRET`.
 2. Your `Client Secret` will appear.
 
##### Finding `DEEZER_ARL`

 1. Follow the instructions [here](https://web.archive.org/web/20200917142534/https://notabug.org/RemixDevs/DeezloaderRemix/wiki/Login+via+userToken). When you are told to enter the ARL into Deezloader, skip that.
 2. You should have your `ARL` copied.


## Methodology

Here's an overview of how it works:

1. Authorizes with your Spotify account.
2. Retrieves playlist data from Spotify.
3. Retrieves playlist data from iTunes.
4. Checks for new Spotify playlists (compared to the last time the program ran).
5. Checks for changes in the playlist contents (compared to the last time the program ran).
6. Checks the new tracks against previously downloaded tracks (from the last time the program ran).

So now the program knows the tracks you've added to your Spotify playlists, and it can start downloading the changes.

7. Authorizes with your deezer account.
8. Downloads the new tracks using deemix.
9. Adds the tracks to iTunes in the appropriate playlists.
10. Stores the latest versions of the following for the next time the program is run:
      - Playlists
	  - Playlist contents
	  - Downloaded tracks

### Libraries

This program uses:

 - [deemix](https://old.reddit.com/r/deemix) to download the tracks.
 - The iTunes COM library to interface with iTunes. It's available from [Apple's developer website](https://developer.apple.com/download/more/) (search for "iTunes"). You need a free developer account. A digital version of the iTunes COM library can be found [here](http://www.joshkunz.com/iTunesControl/). To see how to use Windows COM with Python, check [this](https://code.activestate.com/recipes/498241-scripting-itunes-for-windows-with-python/) out.
 - [Spotipy](https://spotipy.readthedocs.io/en/2.12.0/), a Python library for Spotify's web API.


## Legality

What are they gonna do, stab me?