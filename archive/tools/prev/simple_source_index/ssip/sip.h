
#pragma once

#include "util.h"
#include "dbaccess.h"

typedef struct SsipIndexer_t
{
	SsiE m_errFlag;
	char* m_szIniFile;
	SSIdbAccess* m_dbAccess;
	bool m_bFullUpdate;
	bool m_bVerbose;
	uint m_nFilesPresent;
	uint m_nMinWordlen;
	UINT64 m_rgFileExts[10];
} SsipIndexer;

inline SsipIndexer* SsipIndexer_Create(const char* szIniFile)
{
	SsipIndexer* obj = (SsipIndexer*) calloc(1, sizeof(SsipIndexer));
	obj->m_errFlag = SsiEOk;
	obj->m_szIniFile = strdup(szIniFile);
	obj->m_dbAccess = null;
	obj->m_bFullUpdate = false;
	obj->m_bVerbose = false;
	obj->m_nFilesPresent = 0;
	obj->m_nMinWordlen = 5;
	return obj;
}
inline void SsipIndexer_Close(SsipIndexer* obj)
{
	if (!obj) return;
	free_nop(obj->m_errFlag);
	free_free(obj->m_szIniFile);
	free_fn(obj->m_dbAccess, SSIdbAccess_Close);
	free_nop(obj->m_bFullUpdate);
	free_nop(obj->m_bVerbose);
	free_nop(obj->m_nFilesPresent);
	free_free(obj);
}

void SipHigh_RunUpdate(const char* szIni, bool bFullupdate);
void SipHigh_FindInFiles(const char* szIni, const char* szTerm, bool bWholeWord);
void SipHigh_RunSearch(const char* szIni, const char* szTerm);

