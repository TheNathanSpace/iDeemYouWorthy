# iDeemYouWorthy

The two purposes of this program:

 1. Check Spotify for changes to your playlists, downloading the new tracks.
 2. Add the local versions of your Spotify playlists to iTunes.
 
Ultimately, the goal is to have a script that you can have running in the background, keeping your iTunes library up-to-date with Spotify.

___

Using **Spotify** for your music is great because you can access it from anywhere, you don't have to worry about the local files, and it's super easy to use.

Storing music locally (like on **iTunes**) is great because there aren't any ongoing costs, it's more versatile, and you aren't reliant on a corporate entity.

So, this aims to combine the best of both worlds.

___

## Contents

`find_playlists.py` is the main script.

There are a lot of random files annd folders lying around right now; once the prototype is finished I'll be cleaning it up and probably packaging it into a nice `.exe`.

___

## Methodology

Here's an overview of how it works:

1. Authorizes with your Spotify account.
2. Retrieves playlist data from Spotify.
3. Retrieves playlist data from iTunes.
4. Checks for new Spotify playlists (compared to the last time the program ran).
5. Checks for changes in the playlist contents (compared to the last time the program ran).
6. Checks the new tracks against previously downloaded tracks (from the last time the program ran).

So now the program knows the tracks you've added to your Spotify playlists, and it can start downloading the changes.

7. Authorizes with your Deezer account.
8. Downloads the new tracks using deemix.
9. Adds the tracks to iTunes in the appropriate playlists.
10. Stores the latest versions of the following for the next time the program is run:
      - Playlists
	  - Playlist contents
	  - Downloaded tracks

### Libraries

This program uses:

 - [deemix](https://old.reddit.com/r/deemix) to download the tracks.
 - The iTunes COM library to interface with iTunes. It's available from [Apple's developer website](https://developer.apple.com/download/more/) (search for "iTunes"). You need a free developer account. A digital version of the iTunes COM libary can be found [here](http://www.joshkunz.com/iTunesControl/). To see how to use Windows COM with Python, check [this](https://code.activestate.com/recipes/498241-scripting-itunes-for-windows-with-python/) out.
 - [Spotipy](https://spotipy.readthedocs.io/en/2.12.0/), a Python library for Spotify's web API.

___

## Limitations

I'm not gonna make it check iTunes to see if you messed with the playlists. At the moment, if you delete songs from the iTunes playlist, it won't replace it. I might add it later but we'll see.

___

## Legality

What are they gonna do, stab me?

___

## Changelog

### Future Plans

 - GUI to sign in to Spotify and Deezer, store credentials on a local file
 - The ability to add other playlists to track
 - Check iTunes playlists to resync if a user modifies it (with option to disable)
 - Ability to check files and try to update cache based on local files (won't be perfect, so will be prompted by user)
 - Refactor into better organized files to add error messages/logging

### 1.0

Rise, my creation! Go forth and conquer!

Featuring:

 - Hardcoded to use my dev Spotify account
 - Downloads all of your playlists, and only your playlists
 - No bugs that I can find...?
