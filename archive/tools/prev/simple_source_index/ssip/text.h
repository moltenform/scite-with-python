
#pragma once

#include "util.h"
#include "dbaccess.h"

void text_init();
void text_uninit();

bool text_checkIsBlacklisted(const char* s);
SsiE text_processFile(SSIdbAccess* pDbAccess, const char* szFilename, uint nFileid);
SsiE text_findinfile(const char* szFilename, const char* szSearchString, bool bWholeWord, bool bExpectToFind);

