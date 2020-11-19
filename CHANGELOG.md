# Changelog

#### Future Plans

 - GUI to sign in/add credentials, manage tracked playlists, and schedule auto-run
 - [youtube-dl](https://youtube-dl.org/) integration for tracks that can't be found on deezer

## 1.x (Terminal)

### 1.7

`youtube-dl` integration was surprisingly simple to add. Don't mind if I do!

##### Added

 - Now downloads tracks not found on deezer from YouTube. It gets the first result for the search string `[track name] + [track artist] + "lyrics"`—hopefully that's what you want!

### 1.6

I feel like this is finally reaching my original vision and it's something I can be proud of. Next stop, GUI!

I've decided that the 1.x branch will remain terminal-only. I'll try to backport features in the 2.x branch to 1.x so that, if you prefer using a terminal instead of the GUI, you can do so.

##### Added

 - Ability to compare iTunes and cached versions of playlists to re-sync if a user modifies it.
 - Dedicated [changelog](CHANGELOG.md).
 - Ability to track user-specified playlists, set in `custom_playlists.json`.
 - Logging (`logs` folder, new log each run).
 - Option to not use iTunes.
 - Ability to create `m3u` playlist files.

### 1.5

What's that? We're jumping *5 whole versions?* Yep, that's just how cool we are.

##### Added

 - Now reads user-written Spotify and deezer credentials from `account_info.json`.

##### Changed

 - Refactored the entire program to be more object-oriented and (hopefully) easier to read and develop.

### 1.0

Rise, my creation! Go forth and conquer!

##### Featuring

 - Hardcoded to use my dev Spotify account
 - Downloads all of your playlists, and only *your* playlists
 - No bugs that I can find...?
