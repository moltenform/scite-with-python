
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
int IsSrcFileExtension(const char* szFilename)
{
	size_t nlen = strlen(szFilename);
	size_t nlast = nlen-1;
	if (nlast > 1 && szFilename[nlast-1]=='.')
	{
		if (szFilename[nlast]=='c' || szFilename[nlast]=='C')
			return 1;
		if	(szFilename[nlast]=='h' || szFilename[nlast]=='H')
			return 2;
	}
	else if (nlen > 4 && szFilename[nlen-4]=='.')
	{
		if (StringEndsWithLen(szFilename, nlen, "cpp", 3) ||
			StringEndsWithLen(szFilename, nlen, "CPP", 3) ||
			StringEndsWithLen(szFilename, nlen, "cxx", 3) ||
			StringEndsWithLen(szFilename, nlen, "CXX", 3))
			return 1;
		if (StringEndsWithLen(szFilename, nlen, "hpp", 3) ||
			StringEndsWithLen(szFilename, nlen, "HPP", 3) ||
			StringEndsWithLen(szFilename, nlen, "hxx", 3) ||
			StringEndsWithLen(szFilename, nlen, "HXX", 3) ||
			StringEndsWithLen(szFilename, nlen, "idl", 3) ||
			StringEndsWithLen(szFilename, nlen, "Idl", 3) ||
			StringEndsWithLen(szFilename, nlen, "IDL", 3))
			return 2;
	}
	return 0;
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

