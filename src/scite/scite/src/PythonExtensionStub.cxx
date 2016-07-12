// SciTE Python Extension
// Ben Fisher, 2011

#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "PythonExtensionStub.h"

#ifdef _MSC_VER
// allow deprecated stdio, for PyRun_SimpleFileEx
#pragma warning(disable: 4996)

// allow unreferenced parameter, for PyObject methods
#pragma warning(disable: 4100)
#endif

#ifdef _WIN32
#include <windows.h>
#endif

#define ENABLEDEBUGTRACE 0
