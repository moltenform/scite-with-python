
#pragma once
#include <limits.h>
#include <stdio.h>

#ifdef _WIN32
#define OS_SEP "\\"
#include "util_win32.h"
typedef UINT uint;
#else
#define OS_SEP "/"
#error linux not yet supported.
#endif

#define null NULL

#define StringStartsWith(s1,s2) (strncmp((s1), (s2), strlen(s2))==0)
#define StringAreEqual(s1, s2) (strcmp((s1),(s2))==0)
#define StringAreEqualN(s1, s2, len) (strncmp((s1),(s2),(len))==0)
bool StringEndsWith(const char* s1, const char* s2);

inline UINT64 GetFileExtensionAsNumber(const char* szFilename)
{
	// position just after the '.'.
	UINT64 ret = 0;
	for (int i=0; i<64/8; i++)
	{
		if (!szFilename[i]) break;
		if (szFilename[i]=='\\') return 0;
		ret |= ((UINT64)tolower(szFilename[i])) << ((UINT64)(8*i));
	}
	return ret;
}

inline bool IsSrcFileExtensionArr(const char* szFilename, const UINT64* rgExts, size_t lenRgExts)
{
	const char* szPeriod = strrchr(szFilename, '.');
	if (!szPeriod || !*(szPeriod+1)) return false;
	UINT64 num = GetFileExtensionAsNumber(szPeriod+1);
	for (size_t i=0; i<lenRgExts; i++)
	{
		if (!rgExts[i]) return false;
		if (rgExts[i] == num) return true;
	}
	return false;
}

// test with a small buffer (many collisions):
// #define Test_SmallBuffer
// break into debugger on error
// #define DebugAssertions

// do not use 'printf' except for temporary debugging code
#define printerrfmt(...) do {printf("error:"); printf(__VA_ARGS__); printf("\n"); } while(0)
#define printwrnfmt(...) do {printf("warning:"); printf(__VA_ARGS__); printf("\n"); } while(0)

// Asserts. verify a condition that should always hold.
inline void assertEqual_impl(int a, int b, int lineno, const char* file)
{
	if (a!=b) {
		printerrfmt("Assertion failure on line %d file %s! %d != %d", lineno,file,a,b);
#ifdef DebugAssertions
		__debugbreak();
#endif
	}
}
inline void assertTrue_impl(bool b, int lineno, const char* file)
{
	assertEqual_impl(b?1:0,1,lineno, file);
}
#define assertEqual(a,b) assertEqual_impl((a),(b),__LINE__, __FILE__)
#define assertTrue(b) assertTrue_impl((b),__LINE__, __FILE__)

// The SsiE type generally represents an irrecoverable error condition.
// SsiEOk is defined as null, so that the concise code "if serr (quit)" is possible.
typedef const char* SsiE;
#define SsiEOk ((SsiE) null)
inline SsiE ssierrp_impl(const char* msg, int n, int lineno, const char* file)
{
	printerrfmt(":%s (%d)", msg,n);
	printerrfmt("line %d of file %s", lineno, file);
#ifdef DebugAssertions
	__debugbreak();
#endif
	return msg;
}
inline SsiE ssierr_impl(const char* msg, int lineno, const char* file)
{
	printerrfmt(":%s", msg);
	printerrfmt("line %d of file %s", lineno, file);
#ifdef DebugAssertions
	__debugbreak();
#endif
	return msg;
}

#define ssierrp(a,b) ssierrp_impl((a),(b),__LINE__, __FILE__)
#define ssierr(a) ssierr_impl((a),__LINE__, __FILE__)

// get setting from config file
bool GetSettingString(const char* szProfileFile, const char* szSettingName, char* szBufret, uint nBufsize);
uint GetSettingInt(const char* szProfileFile, const char* szSettingName, uint nDefault);

SsiE GetFileExts(const char* szIni, UINT64* rgExts, size_t lenRgExts);


// wrappers for memory freeing.
// these exist for visual consistency, one can line up the constructor and destructor and see correspondence.
// for this reason it's recommended to call free_nop on stack-allocated members of a struct in cleanup.
#define free_nop(p) 
#define free_free(p) do { free((p)); (p) = null;} while (0)
#define free_fn(p, fn) do {fn((p)); void* _unused=(void*) &(fn); (p) = null;} while (0)
// '_unused' is present to make sure a function was actually provided.


