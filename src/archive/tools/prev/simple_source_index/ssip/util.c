
#include <stdio.h>
#include <string.h>
#include "util.h"


bool StringEndsWith(const char* s1, const char*s2)
{
	size_t len1=strlen(s1), len2=strlen(s2);
	if (len2>len1) return false;
	return strcmp(s1+len1-len2, s2)==0;
}
// same as StringEndsWith, but uses previously-computed lengths.
static inline bool StringEndsWithLen(const char* s1, size_t len1, const char* s2, size_t len2)
{
	if (len2>len1) return false;
	return strcmp(s1+len1-len2, s2)==0;
}

SsiE GetFileExts(const char* szIni, UINT64* rgExts, size_t lenRgExts)
{
	// get file extensions
	int nExtensionsGot = 0;
	for (int i=1; i<=lenRgExts; i++)
	{
		char szSettingName[MAX_PATH];
		sprintf_s(szSettingName, _countof(szSettingName), "extension%d", i);
		char szExt[MAX_PATH] = {0};
		bool bRet = GetSettingString(szIni, szSettingName, szExt, _countof(szExt));
		if (bRet && szExt[0])
		{
			rgExts[nExtensionsGot++] = GetFileExtensionAsNumber(szExt);
		}
	}
	if (nExtensionsGot == 0)
	{
		assertTrue(6<lenRgExts);
		rgExts[0] = GetFileExtensionAsNumber("cpp");
		rgExts[1] = GetFileExtensionAsNumber("h");
		rgExts[2] = GetFileExtensionAsNumber("c");
		rgExts[3] = GetFileExtensionAsNumber("hpp");
		rgExts[4] = GetFileExtensionAsNumber("idl");
		rgExts[5] = GetFileExtensionAsNumber("cxx");
		rgExts[6] = GetFileExtensionAsNumber("hxx");
	}

	{
		char szSrcDir[MAX_PATH] = {0};
		bool bRet = GetSettingString(szIni, "srcdir0", szSrcDir, _countof(szSrcDir));
		if (bRet || szSrcDir[0]) return ssierr("do not set srcdir0.");

		bRet = GetSettingString(szIni, "srcdir10", szSrcDir, _countof(szSrcDir));
		if (bRet || szSrcDir[0]) return ssierr("do not set srcdir10, only 9 dirs supported now.");

		bRet = GetSettingString(szIni, "extension0", szSrcDir, _countof(szSrcDir));
		if (bRet || szSrcDir[0]) return ssierr("do not set extension0.");

		bRet = GetSettingString(szIni, "extension10", szSrcDir, _countof(szSrcDir));
		if (bRet || szSrcDir[0]) return ssierr("do not set extension10, only 9 extensions supported now.");
	}

	return SsiEOk;
}


// returns false for empty string, missing property, or invalid file
bool GetSettingString(const char* szProfileFile, const char* szSettingName, char* szBufret, uint nBufsize)
{
	szBufret[0] = '\0';
	DWORD ret = ::GetPrivateProfileString("main", szSettingName, NULL, szBufret, nBufsize, szProfileFile);
	if (ret == 0 || szBufret[0]=='\0')
		return false;
	else 
		return true;
}

uint GetSettingInt(const char* szProfileFile, const char* szSettingName, uint nDefault)
{
	return ::GetPrivateProfileInt("main", szSettingName, nDefault, szProfileFile);
}

