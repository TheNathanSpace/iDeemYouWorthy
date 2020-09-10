iTunesCOM.chm

Compressed HTML help file containing the documentation on the iTunes COM
interface.  It's built directly from the IDL files, so anything you see
documented is guaranteed to be available in iTunes.

iTunesCOMInterface.h
iTunesCOMInterface_i.c

The iTunes COM header file (along with IID constants), needed for building clients in a high level
language like C++.  Note that the type library is built into iTunes.exe,
you can browse it using OLEView or similar tools.

SampleScripts folder

A few sample JScripts that use the iTunes COM interface:

CreateAlbumPlaylists.js

Iterates over all tracks in your library, creates a new playlist for
each album, and adds the tracks for that album to the playlist.

ExtractSelectedArtwork.js

Creates a folder named "SavedArtwork" and extracts artwork from the
currently selected tracks in the track list to this folder.

RemoveDeadTracks.js

Iterates over your library and removes any tracks that can no longer be
found on disk.

RemoveUserPlaylists.js

Deletes all non-smart user playlists your library.
