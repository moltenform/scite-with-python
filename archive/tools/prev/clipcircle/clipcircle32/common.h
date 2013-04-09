
#pragma once

// Keep compatibilty with WinXP.
#define _WIN32_WINNT 0x05010000
#define _WIN32_IE 0x0500

#include <windows.h>
#include <ShellAPI.h>
#include <stdio.h>

#ifdef NTDDI_WINXP
C_ASSERT(_WIN32_WINNT == NTDDI_WINXP);
#endif
#ifdef _WIN32_IE_IE50
C_ASSERT(_WIN32_IE == _WIN32_IE_IE50);
#endif

inline void DisplayWarning(const char* sz)
{
	MessageBoxA(0, sz, "clipcircle32", 0);
}

#ifdef DEBUG
#define Assert(b) do { if (!(b)) DisplayWarning("assertion failed"); } while(0)
#else
#define Assert(b)
#endif

// function based on the article "Using the Clipboard, Part I : Transferring Simple Text"
// by Tom Archer, http://www.codeproject.com/KB/clipboard/archerclipboard1.aspx
inline void SetClipboardString(const WCHAR* wz)
{
	if (wz && OpenClipboard(NULL))
	{
		// empty the Clipboard. Also allows Windows to free memory for prior contents.
		EmptyClipboard();

		// allocate space for string and NULL-term
		HGLOBAL hClipboardData = GlobalAlloc(GMEM_DDESHARE, sizeof(WCHAR)*(wcslen(wz)+1));

		WCHAR* pchData = (WCHAR*) GlobalLock(hClipboardData);
		wcscpy(pchData, wz);
		GlobalUnlock(hClipboardData);

		// now, set the Clipboard data, passsing the handle to global memory.
		SetClipboardData(CF_UNICODETEXT, hClipboardData);
		
		// close the Clipboard so that other apps can use it.
		CloseClipboard();
	}
}

inline bool OS_FileExists(const WCHAR* wz)
{
	DWORD dwAttributes = GetFileAttributes(wz);
	return dwAttributes != UINT_MAX;
}
