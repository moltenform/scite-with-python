
#include "util.h"
#include "sip.h"
#include "dbaccess.h"
#include "text.h"
#include "hash.h"

// filename for database.
const char* g_szDbName = "ssip.db";

// examine each file. If it has been modified more recently than we've seen, process it.
static SsiE SsipIndexer_CallbackWalk_I(SsipIndexer* pIndexer, const char* szFilename)
{
	bool bNeedsProcessing = true;
	uint nRowId = 0;
	UINT64 nLastmodActual = OS_GetLastModified(szFilename);
	if (!pIndexer->m_bFullUpdate)
	{
		UINT64 nLastmodFromDb = 0;
		SsiE serr = SSIdbAccess_GetLastModified(pIndexer->m_dbAccess, szFilename, &nLastmodFromDb, &nRowId);
		if (serr) return serr;
		// if it actually was in the db
		if (nRowId != 0)
		{
			// if it's up to date
			if (nLastmodFromDb != 0 && nLastmodActual == nLastmodFromDb)
				bNeedsProcessing = false;
		}
	}
	// clear previous contents
	if (!pIndexer->m_bFullUpdate && bNeedsProcessing && nRowId!=0)
	{
		SsiE serr = SSIdbAccess_PrepareSqlAll(pIndexer->m_dbAccess);
		if (serr) return serr;
		serr = SSIdbAccess_DeleteFromCatalogWhereSrcId(pIndexer->m_dbAccess, nRowId);
		if (serr) return serr;
		serr = SSIdbAccess_UpdateLastModified(pIndexer->m_dbAccess, nRowId, nLastmodActual);
		if (serr) return serr;
	}
	// insert into db
	if (nRowId == 0)
	{
		SsiE serr = SSIdbAccess_PrepareSqlAll(pIndexer->m_dbAccess);
		if (serr) return serr;
		serr = SSIdbAccess_InsertSrcFile(pIndexer->m_dbAccess, szFilename, nLastmodActual, &nRowId);
		if (serr) return serr;
	}
	// go!
	if (bNeedsProcessing)
	{
		if (!pIndexer->m_bFullUpdate && pIndexer->m_bVerbose)
			printwrnfmt("Updating %s\n", szFilename);
		SsiE serr = text_processFile(pIndexer->m_dbAccess, szFilename, nRowId, pIndexer->m_nMinWordlen);
		if (serr) return serr;
	}
	return SsiEOk;
}

// examine each file. Set flag on the indexer object if an error occurs
bool SsipIndexer_CallbackWalk(void* obj, const char* szFilename)
{
	SsipIndexer* pIndexer = (SsipIndexer*) obj;
	bool bIsSrc = IsSrcFileExtensionArr(szFilename, pIndexer->m_rgFileExts, _countof(pIndexer->m_rgFileExts));
	if (!bIsSrc) return true;

	pIndexer->m_nFilesPresent++;
	SsiE serr = SsipIndexer_CallbackWalk_I(pIndexer, szFilename);
	if (serr) { pIndexer->m_errFlag = serr; return false; }
	return true;
}

// make sure database is up to date.
static SsiE Sip_RunUpdate_I(SsipIndexer* pIndexer)
{
	pIndexer->m_bVerbose = GetSettingInt(pIndexer->m_szIniFile, "verbose", 0) > 0;
	pIndexer->m_nMinWordlen = GetSettingInt(pIndexer->m_szIniFile, "min_word_len", 5);
	if (pIndexer->m_bFullUpdate && OS_FileExists(g_szDbName))
	{
		bool b = OS_ReallyDelete(g_szDbName);
		if (!b) return ssierr("Could not delete existing db");
	}
	// db doesn't already exist, so create it.
	if (!pIndexer->m_bFullUpdate && !OS_FileExists(g_szDbName))
		pIndexer->m_bFullUpdate = true;

	assertTrue(!pIndexer->m_dbAccess);
	pIndexer->m_dbAccess = SSIdbAccess_Create(g_szDbName);
	if (!pIndexer->m_dbAccess) return ssierr("SSIdbAccess_Create failed");
	
	if (pIndexer->m_bFullUpdate)
	{
		SsiE serr = SSIdbAccess_AddSchema(pIndexer->m_dbAccess);
		if (serr) return serr;
	}
	SsiE serr = SSIdbAccess_PrepareSqlQueries(pIndexer->m_dbAccess);
	if (serr) return serr;
	serr = SSIdbAccess_AsyncModeStart(pIndexer->m_dbAccess);
	if (serr) return serr;
	serr = SSIdbAccess_TxnStart(pIndexer->m_dbAccess);
	if (serr) return serr;

	// get file extensions
	serr = GetFileExts(pIndexer->m_szIniFile, pIndexer->m_rgFileExts, _countof(pIndexer->m_rgFileExts));
	if (serr) return serr;


	// walk through the files and add them to the db.
	uint nMaxDirDepth = GetSettingInt(pIndexer->m_szIniFile, "maxdirdepth", 18);
	const int nDirsReadFromIni = 9;
	for (int i=1; i <= nDirsReadFromIni; i++)
	{
		char szSettingName[MAX_PATH];
		sprintf_s(szSettingName, _countof(szSettingName), "srcdir%d", i);
		char szSrcDir[MAX_PATH] = {0};
		bool bRet = GetSettingString(pIndexer->m_szIniFile, szSettingName, szSrcDir, _countof(szSrcDir));
		if (bRet && szSrcDir[0])
		{
			pIndexer->m_errFlag = SsiEOk;
			bool b = WalkThroughFiles(szSrcDir, (void*)pIndexer, &SsipIndexer_CallbackWalk, nMaxDirDepth);
			if (pIndexer->m_errFlag) return pIndexer->m_errFlag;
			if (!b) return ssierr("WalkThroughFiles failed");
		}
	}
	if (pIndexer->m_bFullUpdate && pIndexer->m_nFilesPresent==0)
		return ssierr("No files seen. Make sure ssip.cfg file specifies srcdir1=c:\\path\\to\\src");

	serr = SSIdbAccess_TxnCommit(pIndexer->m_dbAccess);
	if (serr) return serr;
	serr = SSIdbAccess_AsyncModeStop(pIndexer->m_dbAccess);
	if (serr) return serr;
	
	// check for staleness (if many files have been deleted)
	if (!pIndexer->m_bFullUpdate && (pIndexer->m_bVerbose || pIndexer->m_nFilesPresent > 100))
	{
		uint nFilesInDb = 0;
		serr = SSIdbAccess_CountFileRows(pIndexer->m_dbAccess, &nFilesInDb);
		if (serr) return serr;
		assertTrue(nFilesInDb > 0);
		assertTrue(nFilesInDb >= pIndexer->m_nFilesPresent);
		if (pIndexer->m_bVerbose && nFilesInDb>pIndexer->m_nFilesPresent)
			printwrnfmt("Stale files:%d", nFilesInDb - pIndexer->m_nFilesPresent);
		if (nFilesInDb - pIndexer->m_nFilesPresent > 50)
			printwrnfmt("There are some stale files in db (the db is a bit bigger than necessary).");
	}

	return SsiEOk;
}

SsiE Sip_RunUpdate_Internal(const char* szIni, bool bFullupdate)
{
	SsipIndexer* pIndexer = SsipIndexer_Create(szIni);
	if (!pIndexer) return ssierr("SsipIndexer_Create failed");
	pIndexer->m_bFullUpdate = bFullupdate;
	SsiE serr = Sip_RunUpdate_I(pIndexer);
	free_fn(pIndexer, SsipIndexer_Close);
	return serr;
}
void SipHigh_RunUpdate(const char* szIni, bool bFullupdate)
{
	text_init();
	Sip_RunUpdate_Internal(szIni, bFullupdate);
	text_uninit();
}

// print results. looks in the target file for the string.
bool Sip_Search_Callback(void* obj, const char* szFilename, const char* szSearch)
{
	SsipIndexer* pIndexer = (SsipIndexer*) obj;
	if (OS_FileExists(szFilename))
	{
		SsiE serr = text_findinfile(szFilename, szSearch, true, true);
		if (serr) { pIndexer->m_errFlag = serr; return false; }
		// possible loophole? if two files have exactly the same lastmod time and swap their names.
		// renaming won't change lastmod time, so we wouldn't notice any difference.
	}
	else
	{
		if (pIndexer->m_bVerbose)
			printwrnfmt("Result is in missing file...");
	}
	return true;
}
static SsiE Sip_RunSearch_I(SsipIndexer* pIndexer, const char* szTerm)
{
	if (text_checkIsBlacklisted(szTerm))
	{
		printerrfmt("No results! The term you entered is likely to be present in every file, so it was not indexed."
			" (It's also possible that the term you entered has a hash collision with a blacklisted term).");
		return SsiEOk;
	}
	if (strlen(szTerm) == 1)
	{
		printerrfmt("Input too short! We don't index single characters.");
		return SsiEOk;
	}
	if (strlen(szTerm) < pIndexer->m_nMinWordlen)
	{
		printerrfmt("Input too short! The .cfg has specified min_word_len=%d.", pIndexer->m_nMinWordlen);
		return SsiEOk;
	}
	if (strstr(szTerm, " ") || strstr(szTerm, "\t"))
	{
		printerrfmt("We don't index whitespace, so this query won't yield results.");
		return SsiEOk;
	}
	int nHash = Hash_getHashValue(szTerm);
	SsiE serr = SSIdbAccess_QueryCatalog(pIndexer->m_dbAccess, nHash, szTerm, Sip_Search_Callback, pIndexer);
	if (serr) return serr;
	return SsiEOk;
}

SsiE Sip_RunSearch_Internal(const char* szIni, const char* szTerm)
{
	SsipIndexer* pIndexer = SsipIndexer_Create(szIni);
	if (!pIndexer) return ssierr("SsipIndexer_Create failed");
	pIndexer->m_bFullUpdate = false;
	SsiE serr = Sip_RunUpdate_I(pIndexer);
	if (!serr) serr = Sip_RunSearch_I(pIndexer, szTerm);
	free_fn(pIndexer, SsipIndexer_Close);
	return serr;
}

void SipHigh_RunSearch(const char* szIni, const char* szTerm)
{
	text_init();
	Sip_RunSearch_Internal(szIni, szTerm);
	text_uninit();
}



// temporary struct to pass data to callback.
typedef struct StructFindInFilesWalkT
{
	const char* szSearch;
	bool bWholeWord;
	int nFilesPresent;
	UINT64 rgFileExtensions[10]; 
} StructFindInFilesWalk;
bool Ssip_FindInFilesWalk(void* obj, const char* szFilename)
{
	StructFindInFilesWalk* pWalk = (StructFindInFilesWalk*) obj;
	bool bIsSrc = IsSrcFileExtensionArr(szFilename, pWalk->rgFileExtensions, _countof(pWalk->rgFileExtensions) );
	if (!bIsSrc) return true;
	
	SsiE serr = text_findinfile(szFilename, pWalk->szSearch, pWalk->bWholeWord, false);
	if (serr) return false;

	pWalk->nFilesPresent++;
	return true;
}

// search files, without using the index.
// useful because it can search for partial strings.
SsiE SipHigh_FindInFilesInternal(const char* szIni, const char* szTerm, bool bWholeWord)
{
	StructFindInFilesWalk structFindInFilesWalk = {0};
	structFindInFilesWalk.szSearch = szTerm;
	structFindInFilesWalk.bWholeWord = bWholeWord;
	structFindInFilesWalk.nFilesPresent = 0;
	
	// get file extensions
	SsiE serr = GetFileExts(szIni, structFindInFilesWalk.rgFileExtensions, _countof(structFindInFilesWalk.rgFileExtensions));
	if (serr) return serr;

	// walk through the files.
	uint nMaxDirDepth = GetSettingInt(szIni, "maxdirdepth", 12);
	const int nDifferentDirectoriesSupported = 9;
	for (int i = 1; i <= nDifferentDirectoriesSupported; i++)
	{
		char szSettingName[MAX_PATH];
		sprintf_s(szSettingName, _countof(szSettingName), "srcdir%d", i);
		char szSrcDir[MAX_PATH] = {0};
		bool bRet = GetSettingString(szIni, szSettingName, szSrcDir, _countof(szSrcDir));
		if (bRet && szSrcDir[0])
		{
			bool b = WalkThroughFiles(szSrcDir, (void*) &structFindInFilesWalk, &Ssip_FindInFilesWalk, nMaxDirDepth);
			if (!b) return ssierr("WalkThroughFiles failed");
		}
	}
	if (structFindInFilesWalk.nFilesPresent == 0)
		return ssierr("No files seen?. Make sure ssip.cfg file specifies srcdir1=c:\\path\\to\\src");
	
	return SsiEOk;
}
void SipHigh_FindInFiles(const char* szIni, const char* szTerm, bool bWholeWord)
{
	text_init();
	SipHigh_FindInFilesInternal(szIni, szTerm, bWholeWord);
	text_uninit();
}

