
#pragma once

#include <windows.h>

// the callback should return false to stop iteration.
// takes a maximum depth to prevent infinite recursion if there are loops caused by symlinks.
typedef bool(*PfnWalkfilesCallback)(void* context, const char* szFilename);
bool WalkThroughFiles(const char* szDir, void* context, PfnWalkfilesCallback callback, int nMaxdepth);

inline bool OS_FileExists(const char *szFilename)
{
    DWORD fileAttr = ::GetFileAttributes(szFilename);
	if (INVALID_FILE_ATTRIBUTES == fileAttr)
        return false;
    if (fileAttr & FILE_ATTRIBUTE_DIRECTORY)
		return false;
	return true;
}

inline bool OS_DirExists(const char *szFilename)
{
    DWORD fileAttr = ::GetFileAttributes(szFilename);
	if (INVALID_FILE_ATTRIBUTES == fileAttr)
        return false;
    if (fileAttr & FILE_ATTRIBUTE_DIRECTORY)
		return true;
	return false;
}
inline bool OS_ReallyDelete(const char* szFilename)
{
	::DeleteFile(szFilename);
	return !OS_FileExists(szFilename);
}
inline UINT64 OS_GetLastModified(const char* szFilename)
{
	BOOL bOk;
    WIN32_FILE_ATTRIBUTE_DATA fileInfo;

    if (NULL == szFilename)
        return 0;

	bOk = ::GetFileAttributesEx(szFilename, GetFileExInfoStandard, (void*)&fileInfo);
    if (!bOk)
        return 0;

	// convert from filetime (unsafe to cast due to alignment)
	ULARGE_INTEGER ull;
	ull.HighPart = fileInfo.ftLastWriteTime.dwHighDateTime;
	ull.LowPart = fileInfo.ftLastWriteTime.dwLowDateTime;
	return ull.QuadPart;
}
inline UINT64 OS_GetFileSize(const char* szFilename)
{
	BOOL bOk;
    WIN32_FILE_ATTRIBUTE_DATA fileInfo;

    if (NULL == szFilename)
        return 0;

	bOk = ::GetFileAttributesEx(szFilename, GetFileExInfoStandard, (void*)&fileInfo);
    if (!bOk)
        return 0;
	
	ULARGE_INTEGER ull;
	ull.HighPart = fileInfo.nFileSizeHigh;
	ull.LowPart = fileInfo.nFileSizeLow;
	return ull.QuadPart;
}
inline bool OS_GetOwnPath(char* szBuf, UINT nBufsize)
{
	return !!::GetModuleFileName(NULL, szBuf, nBufsize);
}
