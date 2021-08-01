# iDeemYouWorthy

The two purposes of this program:

 1. Check Spotify for changes to your playlists, downloading the new tracks.
 2. Generate local versions of your Spotify playlists in iTunes and m3u files.

Ultimately, the goal is to have a script that you can run whenever you want, keeping your local library up-to-date with Spotify.

## Usage

iDeemYouWorthy is written for [Python 3](https://www.python.org/downloads/). 

### Installation/Operation

Download the `.zip` file from [Releases](https://github.com/TheKingElessar/iDeemYouWorthy/releases). Unzip it. In the main directory (the one with the `README.md` file), open a terminal and run this command: `pip install -r requirements.txt`. This should automatically install required dependencies.

Then, open a terminal in the subdirectory `ideemyouworthy`, and start the `main.py` file using one of the following commands. It will depend on how your Python environment is set up.

 - `python main.py`
 - `python3 main.py`
 - `main.py`
 
It should be pretty straightforward from there. Music will be downloaded into the `music` directory, which will be at the same level as the `ideemyouworthy` folder containing the code. To keep your directory clean, you should keep the entire thing in a parent directory, for example: `D:/Downloaded Music/ideemyouworthy`.

You'll need to add your Spotify and deezer account information to the `account_info.json` file. This file will be generated upon the first execution of `main.py`. Once it's there, gather the information following the steps below and paste it in. To verify the `.json` file is still formatted correctly, you can use https://jsonlint.com.

You will be able to get the playlists from your Spotify account. You can also (or alternatively, on its own) specify playlists to track in the `custom_playlists.json` file. Once the file is generated after the first run, you can add URLs. The URL should be the key, and the string should be empty. Use https://jsonlint.com to verify it's formatted correctly.

You are not giving me your password! These tokens are used to *avoid* sharing your password. All of this data is stored locally in the `account_info.json` file, and is sent exclusively to Spotify and deezer. It is safe.

#### Account Info

##### Finding `SPOTIFY_USERNAME`

 1. Go to https://open.spotify.com/. Sign into your account.
 2. In the top right, click your display name, then `Account`.
 3. Your `Username` should be the first field on this page.

##### Finding `SPOTIFY_CLIENT_ID`

 1. Go to https://developer.spotify.com/dashboard/login. Sign into your account.
 2. Select `CREATE AN APP`.
 3. The `App name` and `App description` are irrelevant. Click `CREATE` when you're ready.
 4. In the application's menu, click `Edit Settings`. Add the URL `http://example.com` in the `Redirect URIs` field. Save it.
 5. Your `Client ID` will be near the top right, under the app name/description.

##### Finding `SPOTIFY_CLIENT_SECRET`

 1. In the same app you created above, click `SHOW CLIENT SECRET`.
 2. Your `Client Secret` will appear.
 
##### Finding `DEEZER_ARL`

 1. Follow the instructions [here](https://web.archive.org/web/20200917142534/https://notabug.org/RemixDevs/DeezloaderRemix/wiki/Login+via+userToken). When you are told to enter the ARL into Deezloader, skip that.
 2. You should have your `ARL` copied.

##### Example

In the end, your `account_info.json` file should look something like this:

```
{
    "SPOTIFY_USERNAME": "sf08ug804h302gn02200g42",
    "SPOTIFY_CLIENT_ID": "gi8h492gneisowo3ggs",
    "SPOTIFY_CLIENT_SECRET": "fgn8932hfiewnoi32g42",
    "DEEZER_ARL": "g4j02g9jeiodsjgo4ww"
}
```

#### Updating

When updating, you'll need to replace the following files:
 
 - The `ideemyouworthy` directory
 - `requirements.txt`

The recommended method is:

1. Download the latest `.zip` release
2. Unzip it
3. Copy the above files
4. Paste them in your main iDeemYouWorthy directory, replacing the current versions

Then, update dependencies by running this command in your main directory: `pip install -r requirements.txt`

## FAQ/Misc. Notes

Does this download duplicate tracks if you have two playlists with the same track?
 > This doesn't download the same track twice. It keeps track of which tracks are in what playlist and where they're stored, so there is only one file for each track. Deezer automatically keeps it from downloading a track in the same file location, and iDeemYouWorthy keeps track of downloaded tracks so it can add them to playlists.

I'm getting some stack overflow error!
> This happens when you overload deemix, trying to download too many tracks at once. The best fix is to only download something like 500 tracks at a time. Use the custom playlist file to control which playlists are downloaded.

#### Misc. notes:

> **You cannot (*should not*) track two playlists that have the same name.** I haven't tested it, but it would cause *so many problems*. It would have been *very* annoying for me to have built this program with that in mind. Why would you even have two playlists with the same name in the first place?

> If you have local files in your Spotify playlist, they'll be printed to `cache/problematic_tracks.txt`. You can figure out what to do with them.

## Rational

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