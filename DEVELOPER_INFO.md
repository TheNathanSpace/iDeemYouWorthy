# Developer Info

Feel free to take a look at how it works! The code isn't obfuscated and I think it's reasonably understandable. Feel free to [shoot me a message](README.md#contact-information) if you have any questions.

## Methodology

Here's an overview of how it works:

1. Authorizes with your Spotify account.
2. Retrieves playlist data from Spotify.
3. Checks for changes:
     - New playlists
     - New tracks in playlists
4. Checks against previously downloaded tracks to see what needs to be downloaded.

So now the program knows the tracks you've added to your Spotify playlists, and it can start downloading the changes.

5. Authorizes with your deezer account.
6. Downloads the new tracks using deemix.
7. Downloads the rest of the new tracks using youtube_dl.
8. Stores the tracks in playlist format: JSON, m3u, and iTunes, as appropriate.

## Libraries

Some of the main libraries iDeemYouWorthy uses:

 - [deemix](https://old.reddit.com/r/deemix) to download the tracks.
 - The iTunes COM library to interface with iTunes. Its documentation is available from [Apple's developer website](https://developer.apple.com/download/more/) (search for "iTunes"). You need a free developer account. A digital version of the documentation can be found [here](http://www.joshkunz.com/iTunesControl/). To see how to use Windows COM with Python, check [this](https://code.activestate.com/recipes/498241-scripting-itunes-for-windows-with-python/) out.
 - [Spotipy](https://spotipy.readthedocs.io/en/2.12.0/), a Python library for Spotify's web API.
 - [youtube_dl](https://youtube-dl.org/) to download YouTube videos.
 - [youtube_search](https://github.com/joetats/youtube_search) to search for YouTube videos.