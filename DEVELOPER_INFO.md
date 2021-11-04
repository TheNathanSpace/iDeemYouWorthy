# Developer Info

Feel free to take a look at how it works! The code isn't obfuscated and I think it's reasonably understandable. Feel free to [shoot me a message](README.md#contact-information) if you have any questions.

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
9. Downloads the rest of the new tracks using youtube_dl.
10. Adds the tracks to iTunes in the appropriate playlists.
11. Stores the latest versions of the following for the next time the program is run:
      - Playlists
	  - Playlist contents
	  - Downloaded tracks

## Libraries

Some of the main libraries iDeemYouWorthy uses:

 - [deemix](https://old.reddit.com/r/deemix) to download the tracks.
 - The iTunes COM library to interface with iTunes. Its documentation is available from [Apple's developer website](https://developer.apple.com/download/more/) (search for "iTunes"). You need a free developer account. A digital version of the documentation can be found [here](http://www.joshkunz.com/iTunesControl/). To see how to use Windows COM with Python, check [this](https://code.activestate.com/recipes/498241-scripting-itunes-for-windows-with-python/) out.
 - [Spotipy](https://spotipy.readthedocs.io/en/2.12.0/), a Python library for Spotify's web API.
 - [youtube_dl](https://youtube-dl.org/) to download YouTube videos.
 - [youtube_search](https://github.com/joetats/youtube_search) to search for YouTube videos.