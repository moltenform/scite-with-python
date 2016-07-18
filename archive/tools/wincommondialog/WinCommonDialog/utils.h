
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tchar.h>
#include <iostream>
#include <string>

void replaceCharWithNulChar(std::wstring& str, WCHAR ch);

_TCHAR* getArgument(int index, int argc, _TCHAR** argv);

bool stringsEqual(const _TCHAR* s1, const _TCHAR* s2);

size_t stringLength(const _TCHAR* s1);

void traceString(const _TCHAR* s1, bool newline = false);

std::wstring GetDlgItemText(HWND dlg, int itemId, DWORD& lastError);
