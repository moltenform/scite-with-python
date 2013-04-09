
#include "dbaccess.h"
#include "sqlite3.h"

const char* szSchema[] = {
"CREATE TABLE TblSourceFiles \
( \
srcfileid INTEGER PRIMARY KEY AUTOINCREMENT,\
srcfilepath TEXT NOT NULL collate nocase,\
lastmodified NUMERIC NOT NULL\
);",
"CREATE TABLE TblCatalog \
( \
stringhash INTEGER NOT NULL, \
srcfileid INTEGER NOT NULL \
);",
};
const char* szAddIndex = 
"CREATE INDEX Ix_stringhash ON TblCatalog(stringhash)";
const char* szCountRows = 
"SELECT COUNT(*) FROM TblSourceFiles;";

// These queries are pre-compiled and re-used
enum SqlOps
{
	SqlOps_QueryCatalog,
	SqlOps_GetLastModified,
	SqlOps_InsertTableSrc,
	SqlOps_InsertTableCatalog,
	SqlOps_DeleteFromCatalogWhereSrcId,
	SqlOps_UpdateLastModified,
	SqlOps_MAX
};
const char* SqlOps_Sql[SqlOps_MAX];
void SSIdbAccess_GlobalInit()
{
	for (int i=0; i<SqlOps_MAX; i++) SqlOps_Sql[i] = null;
	SqlOps_Sql[SqlOps_QueryCatalog] = 
		"SELECT srcfilepath FROM TblSourceFiles INNER JOIN "
		"TblCatalog on TblCatalog.srcfileid = TblSourceFiles.srcfileid "
		"WHERE stringhash=?";
	SqlOps_Sql[SqlOps_GetLastModified] = 
		"SELECT srcfileid, lastmodified FROM TblSourceFiles WHERE srcfilepath=?";
	SqlOps_Sql[SqlOps_InsertTableSrc] = 
		"INSERT INTO TblSourceFiles "
		"(srcfileid,srcfilepath,lastmodified) values (NULL,?,?)";
	SqlOps_Sql[SqlOps_InsertTableCatalog] = 
		"INSERT INTO TblCatalog "
		"(stringhash,srcfileid) values (?,?)";
	SqlOps_Sql[SqlOps_DeleteFromCatalogWhereSrcId] = 
		"DELETE FROM TblCatalog WHERE srcfileid=?";
	SqlOps_Sql[SqlOps_UpdateLastModified] = 
		"UPDATE TblSourceFiles SET lastmodified=? WHERE srcfileid=?";
	for (int i=0; i<SqlOps_MAX; i++) assertTrue(SqlOps_Sql[i]!=null);
}

SSIdbAccess* SSIdbAccess_Create(const char* szDbName)
{
	SSIdbAccess_GlobalInit();
	sqlite3* db = null;
	// use nomutex because our processing is now singlethreaded
	int rc = sqlite3_open_v2(szDbName, &db, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | 
		SQLITE_OPEN_NOMUTEX, NULL);
	if (rc || !db)
	{
		fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
		sqlite3_close(db);
		return null;
    }
	SSIdbAccess* obj = (SSIdbAccess*) malloc(sizeof(SSIdbAccess));
	obj->m_db = db;
	obj->m_stmts = (sqlite3_stmt**) calloc(SqlOps_MAX, sizeof(sqlite3_stmt*));
	return obj;
}

void SSIdbAccess_Close(SSIdbAccess* obj)
{
	if (!obj) return;
	free_fn(obj->m_db, sqlite3_close);
	if (obj->m_stmts)
		for (int i=0; i<SqlOps_MAX; i++)
			free_fn(obj->m_stmts[i], sqlite3_finalize);
	free_free(obj->m_stmts);
	free_free(obj);
}

// a macro will add a line number, for aid in debugging
SsiE SSIdbAccess_RunSql(SSIdbAccess* pSSIdbAccess, const char* szSql, int nLine)
{
	char *szErrMsg = 0;
	int rc = sqlite3_exec(pSSIdbAccess->m_db, szSql, null, 0, &szErrMsg);
    if (rc!=SQLITE_OK) {
      fprintf(stderr, "SQL error: %s\n", szErrMsg);
      free_fn(szErrMsg, sqlite3_free);
	  return ssierrp("sql error on dbaccess.cpp line", nLine);
    }
	return SsiEOk;
}
#define SSIdbAccess_RunSqlM(pSSIdbAccess, szSql) SSIdbAccess_RunSql((pSSIdbAccess), (szSql), __LINE__)

//creates a db file and adds the schema.
SsiE SSIdbAccess_AddSchema(SSIdbAccess* pSSIdbAccess)
{
	for (int i=0; i<_countof(szSchema); i++)
	{
		SsiE serr = SSIdbAccess_RunSqlM(pSSIdbAccess, szSchema[i]);
		if (serr) return serr;
	}
	return SsiEOk;
}
SsiE SSIdbAccess_AddCatalogSrcIndex(SSIdbAccess* pSSIdbAccess)
{
	printf("Indexing...\n");
	SsiE serr = SSIdbAccess_RunSqlM(pSSIdbAccess, szAddIndex);
	if (serr) return serr;
	return SsiEOk;
}

// prepare all sql queries.
SsiE SSIdbAccess_PrepareSqlAll(SSIdbAccess* pDb)
{
	for (int i=0; i<SqlOps_MAX; i++)
	{
		if (pDb->m_stmts[i])
			continue;
		int rc = sqlite3_prepare_v2(pDb->m_db, 
			SqlOps_Sql[i], -1/*read until null*/, &pDb->m_stmts[i], 0);
		if (rc!=SQLITE_OK || !pDb->m_stmts[i])
			return ssierrp("error preparing statement #", i);
	}
	return SsiEOk;
}

// prepare just the queries needed for retrieval. saves time if db was up to date.
SsiE SSIdbAccess_PrepareSqlQueries(SSIdbAccess* pDb)
{
	C_ASSERT(SqlOps_QueryCatalog+1 == SqlOps_GetLastModified);
	for (int i=SqlOps_QueryCatalog; i<=SqlOps_GetLastModified; i++)
	{
		if (pDb->m_stmts[i])
			continue;
		int rc = sqlite3_prepare_v2(pDb->m_db, 
			SqlOps_Sql[i], -1/*read until null*/, &pDb->m_stmts[i], 0);
		if (rc!=SQLITE_OK || !pDb->m_stmts[i])
			return ssierrp("error preparing statement #", i);
	}
	return SsiEOk;
}


static inline SsiE SSIdbAccess_InsertHelper(int rc, SSIdbAccess* pDb, SqlOps nOp, const char* szReadableName)
{
	if (rc!=SQLITE_OK) return ssierrp("error binding data.", nOp);
	rc = sqlite3_step(pDb->m_stmts[nOp]);
	if (rc!=SQLITE_DONE) {
		printf("query name %s", szReadableName);
		return ssierrp("error running query.", nOp);
	}
	return SsiEOk;
}

SsiE SSIdbAccess_InsertCatalog(SSIdbAccess* pDb, int nHash, int nFileid)
{
	sqlite3_reset(pDb->m_stmts[SqlOps_InsertTableCatalog]);
	int rc = SQLITE_OK;
	if (rc==SQLITE_OK) rc = sqlite3_bind_int(pDb->m_stmts[SqlOps_InsertTableCatalog], 1, nHash);
	if (rc==SQLITE_OK) rc = sqlite3_bind_int(pDb->m_stmts[SqlOps_InsertTableCatalog], 2, nFileid);
	return SSIdbAccess_InsertHelper(rc, pDb, SqlOps_InsertTableCatalog, "SqlOps_InsertTableCatalog");
}

SsiE SSIdbAccess_DeleteFromCatalogWhereSrcId(SSIdbAccess* pDb, uint nRowId)
{
	sqlite3_reset(pDb->m_stmts[SqlOps_DeleteFromCatalogWhereSrcId]);
	int rc = sqlite3_bind_int(pDb->m_stmts[SqlOps_DeleteFromCatalogWhereSrcId], 1, nRowId);
	return SSIdbAccess_InsertHelper(rc, pDb, SqlOps_DeleteFromCatalogWhereSrcId, "SqlOps_DeleteFromCatalogWhereSrcId");
}

SsiE SSIdbAccess_UpdateLastModified(SSIdbAccess* pDb, uint nRowId, UINT64 lastmodactual)
{
	sqlite3_reset(pDb->m_stmts[SqlOps_UpdateLastModified]);
	int rc = SQLITE_OK;
	if (rc==SQLITE_OK) rc = sqlite3_bind_int64(pDb->m_stmts[SqlOps_UpdateLastModified], 1, lastmodactual);
	if (rc==SQLITE_OK) rc = sqlite3_bind_int(pDb->m_stmts[SqlOps_UpdateLastModified], 2, nRowId);
	return SSIdbAccess_InsertHelper(rc, pDb, SqlOps_UpdateLastModified, "SqlOps_UpdateLastModified");
}


SsiE SSIdbAccess_GetLastModified(SSIdbAccess* pDb, const char* szFile, UINT64*outnLastMod, uint*outnRowId)
{
	sqlite3_reset(pDb->m_stmts[SqlOps_GetLastModified]);
	// it's possible that use SQLITE_TRANSIENT isn't necessary here
	int rc = sqlite3_bind_text(pDb->m_stmts[SqlOps_GetLastModified], 1, szFile, -1, SQLITE_TRANSIENT);
	if (rc!=SQLITE_OK) return ssierrp("error binding data", rc);
	rc = sqlite3_step(pDb->m_stmts[SqlOps_GetLastModified]);
	if (rc==SQLITE_DONE)
	{
		*outnLastMod = 0;
		*outnRowId = 0;
	}
	else if (rc==SQLITE_ROW)
	{
		*outnRowId = (uint) sqlite3_column_int(pDb->m_stmts[SqlOps_GetLastModified], 0);
		*outnLastMod = (UINT64) sqlite3_column_int64(pDb->m_stmts[SqlOps_GetLastModified], 1);
	}
	else return ssierrp("error SSIdbAccess_GetLastModified", rc);
	return SsiEOk;
}

// warning: not thread safe, according to sqlite documentation!
SsiE SSIdbAccess_InsertSrcFile(SSIdbAccess* pDb, const char* szFile, UINT64 nLastMod, uint* outnId)
{
	sqlite3_reset(pDb->m_stmts[SqlOps_InsertTableSrc]);
	// use SQLITE_TRANSIENT because we might re-use the buffer that this came from.
	int rc = SQLITE_OK;
	if (rc==SQLITE_OK) rc = sqlite3_bind_text(pDb->m_stmts[SqlOps_InsertTableSrc], 1, szFile, -1, SQLITE_TRANSIENT);
	if (rc==SQLITE_OK) rc = sqlite3_bind_int64(pDb->m_stmts[SqlOps_InsertTableSrc], 2, nLastMod);
	
	SsiE serr = SSIdbAccess_InsertHelper(rc, pDb, SqlOps_InsertTableSrc, "SqlOps_InsertTableSrc");
	if (serr) return serr;
	sqlite3_int64 rowid = sqlite3_last_insert_rowid(pDb->m_db);
	if (rowid > UINT_MAX)
		return ssierr("SSIdbAccess_InsertSrcFile too many rows.");
	*outnId = (uint) rowid;
	return SsiEOk;
}

SsiE SSIdbAccess_CountFileRows(SSIdbAccess* pDb, uint* nFileRows)
{
	sqlite3_stmt* stmt = null;
	*nFileRows = 0;
	int rc = sqlite3_prepare_v2(pDb->m_db, szCountRows, -1/*read until null*/, &stmt, 0);
	if (rc!=SQLITE_OK || !stmt)
		return ssierrp("error preparing stmt count filerows", rc);
	
	int rcRow = sqlite3_step(stmt);
	if (rcRow == SQLITE_ROW)
		*nFileRows = sqlite3_column_int(stmt, 0);

	free_fn(stmt, sqlite3_finalize);
	if (rcRow != SQLITE_ROW)
		return ssierrp("error running stmt count filerows", rcRow);
	else
		return SsiEOk;
}

SsiE SSIdbAccess_TxnStart(SSIdbAccess* pDb)
{
	return SSIdbAccess_RunSqlM(pDb, "BEGIN TRANSACTION");
}
SsiE SSIdbAccess_TxnCommit(SSIdbAccess* pDb)
{
	return SSIdbAccess_RunSqlM(pDb, "COMMIT TRANSACTION");
}
SsiE SSIdbAccess_TxnAbort(SSIdbAccess* pDb)
{
	return SSIdbAccess_RunSqlM(pDb, "ROLLBACK TRANSACTION");
}

// look in database for matches, and run callback for each file.
// at this stage, false-positives are possible due to hash collisions or files that have been deleted.
// in the next stage, though, we look specifically for the string, and only show output for true matches.
SsiE SSIdbAccess_QueryCatalog(SSIdbAccess* pDb, int nHash, const char* szWord, PfnQueryCatalogCallback pfn, void* context)
{
	sqlite3_reset(pDb->m_stmts[SqlOps_QueryCatalog]);
	int rc = sqlite3_bind_int(pDb->m_stmts[SqlOps_QueryCatalog], 1, nHash);
	if (rc!=SQLITE_OK) return ssierrp("error binding data", rc);
	while (1)
	{
		int rcRow = sqlite3_step(pDb->m_stmts[SqlOps_QueryCatalog]);
		if (rcRow != SQLITE_DONE && rcRow != SQLITE_ROW)
			return ssierrp("error running RunCatalogQuery", rcRow);
		if (rcRow == SQLITE_DONE)
			break;

		const char* szFileName = (const char*) sqlite3_column_text(pDb->m_stmts[SqlOps_QueryCatalog], 0);
		bool bRet = pfn(context, szFileName, szWord);
		if (!bRet)
			return ssierr("Callback failed.");
	}
	
	return SsiEOk;
}

