/*
	File:		RemoveDeadTracks.js

	Contains:	JScript to remove missing file tracks from the main library.

	Written by:	Jeff Miller

	Copyright:	Copyright (c)2004 Apple Computer, Inc.

	Change History (most recent first):
	
		$Log: RemoveDeadTracks.js,v $
		Revision 1.1  2004/01/10 02:18:37  jeffmill
		Check in a script that's actually useful.
		
*/

var ITTrackKindFile	= 1;
var	iTunesApp = WScript.CreateObject("iTunes.Application");
var	deletedTracks = 0;
var	mainLibrary = iTunesApp.LibraryPlaylist;
var	tracks = mainLibrary.Tracks;
var	numTracks = tracks.Count;
var	i;

while (numTracks != 0)
{
	var	currTrack = tracks.Item(numTracks);
	
	// is this a file track?
	if (currTrack.Kind == ITTrackKindFile)
	{
		// yes, does it have an empty location?
		if (currTrack.Location == "")
		{
			// yes, delete it
			currTrack.Delete();
			deletedTracks++;
		}
	}
	
	numTracks--;
}

if (deletedTracks > 0)
{
	if (deletedTracks == 1)
	{
		WScript.Echo("Removed 1 dead track.");
	}
	else
	{
		WScript.Echo("Removed " + deletedTracks + " dead tracks.");
	}
}
else
{
	WScript.Echo("No dead tracks were found.");
}
