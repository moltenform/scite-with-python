
#pragma once

#include "util.h"

// forward declarations to avoid including full sqlite header
typedef struct sqlite3 *psqlite3;
typedef struct sqlite3_stmt *psqlite3_stmt;

typedef struct SSIdbAccess_t
{
	psqlite3 m_db;
	psqlite3_stmt* m_stmts;
} SSIdbAccess;


SSIdbAccess* SSIdbAccess_Create(const char* szDbName);
void SSIdbAccess_Close(SSIdbAccess* obj);

SsiE SSIdbAccess_AddSchema(SSIdbAccess* pSSIdbAccess);
SsiE SSIdbAccess_PrepareSqlAll(SSIdbAccess* pDb);
SsiE SSIdbAccess_PrepareSqlQueries(SSIdbAccess* pDb);
SsiE SSIdbAccess_InsertCatalog(SSIdbAccess* pDb, int nHash, int nFileid);

SsiE SSIdbAccess_InsertSrcFile(SSIdbAccess* pDb, const char* szFile, UINT64 nLastMod, uint* outnId);
SsiE SSIdbAccess_TxnStart(SSIdbAccess* pDb);
SsiE SSIdbAccess_TxnCommit(SSIdbAccess* pDb);
SsiE SSIdbAccess_TxnAbort(SSIdbAccess* pDb);
SsiE SSIdbAccess_AddCatalogSrcIndex(SSIdbAccess* pDb);

SsiE SSIdbAccess_GetLastModified(SSIdbAccess* pDb, const char* szFile, UINT64*outnLastMod, uint*outnRowId);
SsiE SSIdbAccess_DeleteFromCatalogWhereSrcId(SSIdbAccess* pDb, uint nRowId);
SsiE SSIdbAccess_UpdateLastModified(SSIdbAccess* pDb, uint nRowId, UINT64 lastmodactual);
SsiE SSIdbAccess_CountFileRows(SSIdbAccess* pDb, uint* nFileRows);

typedef bool(*PfnQueryCatalogCallback)(void* context, const char* szFilename, const char* szSearch);
SsiE SSIdbAccess_QueryCatalog(SSIdbAccess* pdbAccess, int nHash, const char* szWord, PfnQueryCatalogCallback pfn, void* context);

