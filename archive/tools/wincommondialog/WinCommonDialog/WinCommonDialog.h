//#define UNICODE
//Defined automatically by Visual studio "Use Unicode Character Set" setting in properties

#define WIN32_LEAN_AND_MEAN
#include "Windows.h"
#include <tchar.h>
#include <iostream>

#define ErrorResult 99


_TCHAR* get_argument(int index, int argc, _TCHAR** argv);

bool stringequal(const _TCHAR* s1, const _TCHAR* s2);