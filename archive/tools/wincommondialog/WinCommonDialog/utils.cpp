
#include "utils.h"

// some windows APIs use a list of strings (actually one long string with nul-characters as delimiters)
void replaceCharWithNulChar(std::wstring& str, WCHAR ch)
{
	for (unsigned int i = 0; i < str.length(); i++)
	{
		if (str[i] == ch)
		{
			str[i] = L'\0';
		}
	}
}

// helper for retrieving arguments, returns null if the argument is missing
_TCHAR* getArgument(int index, int argc, _TCHAR** argv)
{
	if (argc > 1 && stringsEqual(argv[1], L"/?"))
	{
		// user has asked for documentation only, 
		// return null no matter what argument is asked for
		return NULL;
	}
	else if (index >= argc)
	{
		return NULL;
	}
	else
	{
		return argv[index];
	}
}

bool stringsEqual(const _TCHAR* s1, const _TCHAR* s2)
{
	return wcscmp(s1, s2) == 0;
}

size_t stringLength(const _TCHAR* s1)
{
	return wcslen(s1);
}

void traceString(const _TCHAR* s1, bool newline)
{
	if (newline)
	{
		wprintf(L"%s\n", s1);
	}
	else
	{
		wprintf(L"%s", s1);
	}
}
