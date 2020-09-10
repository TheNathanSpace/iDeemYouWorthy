/*
	File:		RemoveUserPlaylists.js

	Contains:	JScript to remove all non-smart user playlists from the main library.

	Written by:	Jeff Miller

	Copyright:	Copyright (c)2004 Apple Computer, Inc.

	Change History (most recent first):
	
		$Log: RemoveUserPlaylists.js,v $
		Revision 1.2  2004/02/06 19:19:59  jeffmill
		Don't fail if we try to delete a locked playlist.
		
		Revision 1.1  2004/01/12 20:57:04  jeffmill
		First checked in.
		
*/

var ITPlaylistKindUser = 2;
var	iTunesApp = WScript.CreateObject("iTunes.Application");
var	deletedPlaylists = 0;
var	mainLibrary = iTunesApp.LibrarySource;
var	playlists = mainLibrary.Playlists;
var	numPlaylists = playlists.Count;

while (numPlaylists != 0)
{
	var	currPlaylist = playlists.Item(numPlaylists);
	
	// is this a user playlist?
	if (currPlaylist.Kind == ITPlaylistKindUser)
	{
		// yes, is it a dumb playlist?
		if (!currPlaylist.Smart)
		{
			try
			{
				// yes, delete it
				currPlaylist.Delete();
				deletedPlaylists++;
			}
			catch (exception)
			{
				// ignore errors (e.g. trying to delete a locked playlist)
			}
		}
	}
	
	numPlaylists--;
}

if (deletedPlaylists > 0)
{
	if (deletedPlaylists == 1)
	{
		WScript.Echo("Removed 1 user playlist.");
	}
	else
	{
		WScript.Echo("Removed " + deletedPlaylists + " user playlists.");
	}
}
else
{
	WScript.Echo("No user playlists were removed.");
}
