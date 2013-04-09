
// S-Box hash.
// From http://www.team5150.com/~andrew/noncryptohashzoo/SBox.html
// Sbox originally by Bret Mulvey, modified by Andrew @ Team5150.
// Modified by Ben Fisher to support streaming (when string length not known in advance)

#pragma once
#include "util.h"

typedef unsigned int u32;
// table used by hash algorithm
extern u32* SBoxTable;
// arbitrary constant for hash
const int nHashseed = 0x9dce366b;

// used to truncate the result to 24bits
#ifndef Test_SmallBuffer
#define Hash_tmpMask 0x00ffffff
#else
#define Hash_tmpMask 0x000000ff
#endif

// Use these macros to hash a string one character at a time.
// see Hash_getHashValue for example usage.
// the value is not valid until Hash_Finalize is called.
#define Hash_Reset(h) do {(h) = nHashseed;} while (0)
#define Hash_AddChar(h, c) do {(h) = ((h) ^ SBoxTable[(c)] ) * 3; } while (0)
#define Hash_Finalize(h, len) do {(h) += ((h) >> 22 ) ^ ((h) << 4 ); (h)+=(u32)(len); (h)&=Hash_tmpMask; } while (0)

// get hash value of a string, if the entire string is known.
inline u32 Hash_getHashValue(const char* s)
{
	size_t len = strlen(s);
	u32 h = 0;
	Hash_Reset(h);
	for (size_t i=0; i<len; i++)
		Hash_AddChar(h, s[i]);

	Hash_Finalize(h, len);
	return h;
}

// make hash case-insensitive.
// it's nice that after calling this, there is no further perf. cost
void Hash_makecaseinsensitive();

// asserts and definitions
C_ASSERT(sizeof(u32)==4);
C_ASSERT(sizeof(char)==1);

#ifdef _MSC_VER
#define FINLINE __forceinline
#else
#define FINLINE __attribute__ ((always_inline))
#endif


