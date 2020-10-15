# iDeemYouWorthy

The two purposes of this program:

 1. Check Spotify for changes to your playlists, downloading the new tracks.
 2. Add the local versions of your Spotify playlists to iTunes.
 
Ultimately, the goal is to have a script that you can have running in the background, keeping your iTunes library up-to-date with Spotify.

___

Using **Spotify** for your music is great because you can access it from anywhere, you don't have to worry about the local files, and it's super easy to use.

Storing music locally (like on **iTunes**) is great because there aren't any ongoing costs, it's more versatile, and you aren't reliant on a corporate entity.

So, this aims to combine the best of both worlds. The program is taking shape, but still isn't functional. You shouldn't use this yet.

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

\#9 and #10 are still being built.

### Libraries

This program uses:

 - [deemix](https://old.reddit.com/r/deemix) to download the tracks.
 - The iTunes COM library to interface with iTunes. It's available from [Apple's developer website](https://developer.apple.com/download/more/) (search for "iTunes"). You need a free developer account. A digital version of the iTunes COM libary can be found [here](http://www.joshkunz.com/iTunesControl/). To see how to use Windows COM with Python, check [this](https://code.activestate.com/recipes/498241-scripting-itunes-for-windows-with-python/) out.
 - [Spotipy](https://spotipy.readthedocs.io/en/2.12.0/), a Python library for Spotify's web API.

___

## Legality

What are they gonna do, stab me?
