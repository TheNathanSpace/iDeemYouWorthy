/*
	File:		ExtractSelectedArtwork.js

	Contains:	JScript to save artwork for the currently selected tracks to files.
				The files are saved to a folder named "SavedArtwork".

	Written by:	Jeff Miller

	Copyright:	Copyright (c)2004 Apple Computer, Inc.

	Change History (most recent first):
	
		$Log: ExtractSelectedArtwork.js,v $
		Revision 1.2  2004/01/19 23:18:10  jeffmill
		Handle no selection case.
		
		Revision 1.1  2004/01/19 19:34:10  jeffmill
		First checked in.
		
*/

// JScript doesn't have access to the ITArtworkFormat enumeration, redefine the values here
var ITArtworkFormatUnknown	= 0;
var ITArtworkFormatJPEG		= 1;
var ITArtworkFormatPNG		= 2;
var ITArtworkFormatBMP		= 3;

function ArtworkFormatToFileExtension(artworkFormat)
{
	switch (artworkFormat)
	{
		case ITArtworkFormatUnknown:
			return ".unk";
			break;
	
		case ITArtworkFormatJPEG:
			return ".jpg";
			break;
	
		case ITArtworkFormatPNG:
			return ".png";
			break;
	
		case ITArtworkFormatBMP:
			return ".bmp";
			break;

		default:
			return ".unk";
			break;
	}
}

var		fileSystem = new ActiveXObject("Scripting.FileSystemObject");
var		iTunesApp = WScript.CreateObject("iTunes.Application");
var		savedCount = 0;
var		artworkFolder;

// get a collection of the currently selected tracks
var		selectedTracks = iTunesApp.SelectedTracks;

if (selectedTracks != undefined)
{
	var		numTracks = selectedTracks.Count;

	while (numTracks > 0)
	{
		var		currTrack = selectedTracks.Item(numTracks);
		
		// get the artwork collection for the current track
		var		currArtworks = currTrack.Artwork;
		var		numArtworks = currArtworks.Count;
		
		while (numArtworks > 0)
		{
			var	artwork = currArtworks.Item(numArtworks);
			var	artworkFileName;
			
			// is this the first artwork we've processed?
			if (savedCount == 0)
			{
				// yes, set up the artwork directory
				if (fileSystem.FolderExists("SavedArtwork"))
				{
					// delete any existing directory
					fileSystem.DeleteFolder("SavedArtwork", true);
				}
				
				fileSystem.CreateFolder("SavedArtwork");
				
				artworkFolder = fileSystem.GetFolder("SavedArtwork");
			}
			
			// name of file is "...SavedArtwork\TrackName 1.jpg", for example
			// we make no attempt to get a unique name, so if two tracks have the same name you just get 1 file
			artworkFileName = artworkFolder.Path + "\\" + currTrack.Name +
				" " + numArtworks + ArtworkFormatToFileExtension(artwork.Format);
			
			artwork.SaveArtworkToFile(artworkFileName);
			
			savedCount++;
			
			numArtworks--;
		}
		
		numTracks--;
	}
}

if (savedCount == 0)
{
	WScript.Echo("No artwork files were created.");
}
else if (savedCount == 1)
{
	WScript.Echo("1 artwork file was created.");
}
else
{
	WScript.Echo(savedCount + " artwork files were created.");
}
