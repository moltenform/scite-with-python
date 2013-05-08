
// Simplistic Source Indexing Processor
// Ben Fisher, 2011. Released under the GPLv3 license.

// the only hash collisions that hurt us are strings that collide with blacklisted strings, in which case we warn user.
// if two strings within a file collide, ok, because we've marked one of them off in memory, so we'll still search that file.
// if input term collides with another term in db, ok, because we'll just run through that file and not find hits.

// Possible improvements:
// Store the last-modified time of the entire directory, maybe in the .cfg file, for an even quicker check.
// For the find-in-files implementation, use my own strstr code that also counts newlines, for better speed.
// See if calling SSIdbAccess_AddCatalogSrcIndex is worth costs.
// Add built-in support for searching for two consecutive terms
// Automatically rebuild db in case of many deleted files (stale file entries)

#include "util.h"
#include "sip.h"

int main(int argc, char* argv[])
{
	const char* szUsage = "ssip.exe, 2011, by Ben Fisher\n\n"
		"This program indexes source code into a sqlite database for quick searching.\n"
		"First, create a ssip.cfg file to specify which directories to look in.\n\n"
		"Usage:\n"
		"\tssip -s word\t\tSearch for a word\n"
		"\tssip -start\t\tRe-build index from scratch\n"
		"\tssip -noindex word\t\tSearch for a word without using index\n"
		"\tssip -noindexnowhole word\t\tSearch for a word without using index\n"
		"\n\n";

	// ensure .cfg file exists.
	const char* szIni = "." OS_SEP "ssip.cfg"; // .\ssip.cfg works. ssip.cfg does not.
	if (!OS_FileExists(szIni))
		szIni = ".." OS_SEP "ssip.cfg";
	if (!OS_FileExists(szIni))
	{
		puts("Could not find ssip.cfg. Use ssipexample.cfg as an example.\n");
		return 1;
	}

	if (argc == 2 && StringAreEqual(argv[1], "-start"))
		SipHigh_RunUpdate(szIni, true);
	else if (argc == 3 && StringAreEqual(argv[1], "-s"))
		SipHigh_RunSearch(szIni, argv[2]);
	else if (argc == 3 && StringAreEqual(argv[1], "-noindex"))
		SipHigh_FindInFiles(szIni, argv[2], true /*wholeword*/);
	else if (argc == 3 && StringAreEqual(argv[1], "-noindexnowhole"))
		SipHigh_FindInFiles(szIni, argv[2], false /*wholeword*/);
	else
		puts(szUsage);
	
	return 0;
}


