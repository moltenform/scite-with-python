
#pragma once

#define _WIN32_WINNT 0x0500
#define _WIN32_IE 0x0500

#include <windows.h>
#include <ShellAPI.h>
#include <stdio.h>

#define StringStartsWith(s1,s2) (strncmp((s1), (s2), strlen(s2))==0)
#define StringAreEqual(s1, s2) (strcmp((s1),(s2))==0)


#define null NULL
inline void DisplayWarning(const char* sz)
{
	::MessageBoxA(0, sz, "clipcircle32", 0);
}

typedef const char* SsiE;
#define SsiEOk ((SsiE) null)

inline void assertEqual_impl(int a, int b, int lineno, const char* file)
{
	if (a!=b) {
		printf("Assertion failure on line %d file %s! %d != %d\n", lineno,file,a,b);
		__debugbreak();
		//system("pause");
	}
}
inline void assertTrue_impl(bool b, int lineno, const char* file)
{
	assertEqual_impl(b?1:0,1,lineno, file);
}
#define assertEqual(a,b) assertEqual_impl((a),(b),__LINE__, __FILE__)
#define assertTrue(b) assertTrue_impl((b),__LINE__, __FILE__)

inline SsiE ssierrp_impl(const char* msg, int n, int lineno, const char* file)
{
#if 1
	printf("line %d of file %s\n", lineno, file);
#endif
	printf("Error:%s (%d)\n", msg,n);
	__debugbreak();
	return msg;
}
inline SsiE ssierr_impl(const char* msg, int lineno, const char* file)
{
#if 1
	printf("line %d of file %s\n", lineno, file);
#endif
	printf("Error:%s\n", msg);
	__debugbreak();
	return msg;
}
#define ssierrp(a,b) ssierrp_impl((a),(b),__LINE__, __FILE__)
#define ssierr(a) ssierr_impl((a),__LINE__, __FILE__)
