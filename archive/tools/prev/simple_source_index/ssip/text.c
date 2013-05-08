#include "util.h"
#include "text.h"
#include "hash.h"
#include "dbaccess.h"


// if a term is likely to be present in every file,
// it doesn't need to be indexed.
// it's cheap to see if a term is blacklisted because of our hashing.
const char* g_arrBlacklist[] = {
	"include", "pragma", "ifdef", "ifndef", "endif", "define",
	"if", "else", "while", "for", "do",
	"void", "char", "int", "long", "unsigned", "const",
	"bool", "true", "false", "TRUE", "FALSE",
	"return", "", "inline",
	 };

// g_arrMemoryIndicator is a chunk of memory used to quickly check if a particular term
// has already been encountered in this file. We hash the term and check that byte.
bool g_bInited = false;
char* g_arrMemoryIndicator = null;
#ifndef Test_SmallBuffer
const int g_arraySize = 0x00ffffff + 1; // 2^24, 16Mb
#else
const int g_arraySize = 0x000000ff + 1; // 2^8, 256b
#endif

// clear g_arrMemoryIndicator, mark off the blacklisted terms.
static void text_resetMemoryIndicator()
{
	memset(g_arrMemoryIndicator, 0, g_arraySize * sizeof(char));
	for (int i=0; i<_countof(g_arrBlacklist); i++)
		g_arrMemoryIndicator[Hash_getHashValue(g_arrBlacklist[i])] = 1;
}

// indicates whether the given character is a letter, number, or underscore.
// if so, then it is part of a word.
int g_mapCharType[256] = {0};

// allocate memory.
void text_init()
{
	memset(g_mapCharType, 0, sizeof(g_mapCharType));
	for (char c='a'; c<='z'; c++)
		g_mapCharType[c] = 1;
	for (char c='A'; c<='Z'; c++)
		g_mapCharType[c] = 1;
	for (char c='0'; c<='9'; c++)
		g_mapCharType[c] = 1;
	g_mapCharType['_'] = 1;
	
	if (!g_arrMemoryIndicator)
	{
		g_arrMemoryIndicator = (char*) malloc(g_arraySize * sizeof(char));
	}
	if (!g_arrMemoryIndicator)
	{
		printerrfmt("malloc failed.");
		g_bInited = false;
		return;
	}

	g_bInited = true;
}
// free memory.
void text_uninit()
{
	free_free(g_arrMemoryIndicator);
}


// check for collisions with a blacklisted term.
bool text_checkIsBlacklisted(const char* s)
{
	u32 nHashCheck = Hash_getHashValue(s);
	for (int i=0; i<_countof(g_arrBlacklist); i++)
		if (nHashCheck == Hash_getHashValue(g_arrBlacklist[i]))
			return true;
	return false;
}

// walk through a file, adding terms to the database.
static SsiE text_processFile_impl(FILE* fin, SSIdbAccess* pDbAccess, uint nFileid, uint nMinWordlen)
{
	if (!g_bInited) return ssierr("forgot to call text_setup()?");
	text_resetMemoryIndicator();
	
	const int bufsize = 1024*8;
	char buffer[bufsize];
	
	char charCurrent = ' ';
	bool bInsideWord = false;
	uint nWordLen = 0;
	u32 hash = 0;
	Hash_Reset(hash);

	while (!feof(fin))
	{
		// stream through the file, instead of loading it all into memory
		size_t nChars = fread(buffer, sizeof(char), bufsize, fin);
		for (size_t i=0; i<nChars; i++)
		{
			charCurrent = buffer[i];
			
			if (charCurrent == '\0')
				return ssierr("null char in file");
			
			// chartype is 1 if this is part of a word.
			int chartype = g_mapCharType[charCurrent];
			if (!bInsideWord && chartype!=1)
			{
				// outside of a word, nothing needed
			}
			else if (!bInsideWord && chartype==1)
			{
				// start a new word
				Hash_AddChar(hash, charCurrent);
				nWordLen++;
				bInsideWord = true;
			}
			else if (bInsideWord && chartype==1)
			{
				// add char to current word
				Hash_AddChar(hash, charCurrent);
				nWordLen++;
			}
			else if (bInsideWord && chartype!=1)
			{
				// word is finished.
				// don't include single letters/numbers.
				if (nWordLen > 1 && nWordLen>=nMinWordlen)
				{
					Hash_Finalize(hash, nWordLen);
					if (!g_arrMemoryIndicator[hash])
					{
						SsiE serr = SSIdbAccess_InsertCatalog(pDbAccess, hash, nFileid);
						if (serr) return serr;
						g_arrMemoryIndicator[hash] = 1;
					}
				}
				Hash_Reset(hash);
				nWordLen = 0;
				bInsideWord = false;
			}
		}
	}
	
	return SsiEOk;
}

SsiE text_processFile(SSIdbAccess* pDbAccess, const char* szFilename, uint nFileid, uint nMinWordlen)
{
	// opening as text. will conveniently strip \r characters
	FILE* fin = fopen(szFilename, "r");
	if (!fin) return ssierr("could not read from file");
	SsiE serr = text_processFile_impl(fin, pDbAccess, nFileid, nMinWordlen);
	fclose(fin);
	if (serr) printerrfmt("Error in file %s", szFilename);
	return serr;
}


// load everything into memory. otherwise one would have to worry about the boundary of buffers/partial matches.
// see main.c, this could be improved, but it already seems better than SciTE's string search; no buffer copying.
static void text_findinfile_impl(FILE* fin, const char* szFilename, const char* szSearchString, bool bFindWhole, bool bExpectToFind)
{
	assertTrue(g_bInited);
	// re-use this 16mb buffer to hold the file
	char* g_arrFileContents = g_arrMemoryIndicator;
	g_arrFileContents[0] = '\0';
	size_t nChars = fread(g_arrFileContents, sizeof(char), g_arraySize, fin);
	if (nChars >= g_arraySize-1)
	{
		puts("file is too big\n");
		return;
	}
	if (strstr(szSearchString, "\n"))
	{
		puts("newline in search string - not supported.\n");
		return;
	}
	g_arrFileContents[nChars] = '\0';

	int nLinesSeen = 1;
	int nLastCharPos = 0;
	int nLastLinePrinted = -1;
	char* curpos = g_arrFileContents;
	char* nextpos = curpos;
	char* newlinebefore = g_arrFileContents;
	size_t len = strlen(szSearchString);
	bool bFoundOnce = false;
	
	while (nextpos = strstr(curpos, szSearchString))
	{
		bFoundOnce = true;
		// count newlines
		while (curpos < nextpos)
		{
			if (*(curpos++) == '\n')
			{
				newlinebefore = curpos;
				nLinesSeen++;
			}
		}
		
		if (nLinesSeen != nLastLinePrinted)
		{
			// only if it's a whole match
			// (start of file or preceded by non-word char) and
			// (followed by non-word char). Last char of doc is \0, so ok not to check bound here.
			if (!bFindWhole || 
				((nextpos==g_arrFileContents || g_mapCharType[*(nextpos-1)]!=1) &&
				(g_mapCharType[*(nextpos+len)]!=1)))
			{
				// now go forward until next newline and end the string
				char* newlineafter = curpos;
				while (*newlineafter && *newlineafter!='\n')
					newlineafter++;
				bool altered = (*newlineafter == '\n');
				if (altered) *newlineafter = '\0';

				// only show one char of leading whitespace
				char* printline = newlinebefore;
				while (*printline == '\t' || *printline==' ' && printline!=newlineafter)
					printline++;
				if (printline > g_arrFileContents)
				{
					if (*(printline-1)=='\t')
						*(printline-1) = ' ';
					if (*(printline-1)==' ')
						printline--;
				}
			
				// printing the actual result
				printf("%s:%d:%s\n", szFilename, nLinesSeen, printline);
				nLastLinePrinted = nLinesSeen;
				
				if (altered) *newlineafter = '\n';
			}
		}

		curpos = nextpos+len; // advance beyond match
	}
	if (!bFoundOnce && bExpectToFind)
		printwrnfmt("String not found. Hash collision?\n");
}

SsiE text_findinfile(const char* szFilename, const char* szSearchString, bool bWholeWord, bool bExpectToFind)
{
	// opening as text, will strip \r characters
	if (OS_GetFileSize(szFilename) >= g_arraySize-1 /*room for null*/)
	{
		printerrfmt("file %s is too big", szFilename);
		return ssierr("file is too big");
	}
	FILE* fin = fopen(szFilename, "r");
	if (!fin) { return ssierr("file not found"); }
	text_findinfile_impl(fin, szFilename, szSearchString, bWholeWord, bExpectToFind);
	fclose(fin);
	return SsiEOk;
}

