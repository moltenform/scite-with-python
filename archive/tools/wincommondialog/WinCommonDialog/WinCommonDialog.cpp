// WinCommonDialog.cpp : Defines the entry point for the console application
// See http://msdn.microsoft.com/en-us/library/ms645505(VS.85).aspx


// "Winmm.lib" added to External dependencies under Project settings/linker
// "Use Unicode Character Set" turned on in Project settings
// Pre-compiled headers turned off in Project settings

#include "WinCommonDialog.h"
#include "dialog_simple.h"
#include "dialog_file.h"
#include "dialog_color.h"
#include "dialog_sound.h"
#include "dialog_textinput.h"

const char * documentation = 
"WinCommonDialog.exe, Ben Fisher 2008, GPL\n"
"A wrapper over simple Windows dialogs, using return code to pass result.\n"
"Part of Launchorz, http://github.com/downpoured/lnzscript/\n"
"\n"
"This is divided into 3 different functions. For more specific help, type:\n"
"WinCommonDialog simple /?\n"
"WinCommonDialog color /?\n"
"WinCommonDialog file /?\n"
"WinCommonDialog sound /?\n"
"WinCommonDialog text /?\n"
"\n";


int _tmain(int argc, _TCHAR* argv[])
{
	if (argc<2) { puts(documentation); puts("\nNot enough arguments"); return ErrorResult; }

	_TCHAR* mode = get_argument(1, argc, argv);
	if (stringequal(mode,_T("simple")))
	{
		return dialog_simple(argc - 1, &argv[1]); // Pass arguments except name of program
	}
	else if (stringequal(mode,_T("color")))
	{
		return dialog_color(argc - 1, &argv[1]);
	}
	else if (stringequal(mode,_T("file")))
	{
		return dialog_file(argc - 1, &argv[1]);
	}
	else if (stringequal(mode,_T("sound")))
	{
		return dialog_sound(argc - 1, &argv[1]);
	}
	else if (stringequal(mode,_T("text")))
	{
		return dialog_textinput(argc - 1, &argv[1]);
	}
	else
	{
		puts("Dialog type was not recognized. Run with no arguments to see doc.");
		return ErrorResult;
	}

	return 0;
}

bool stringequal(const _TCHAR* s1, const _TCHAR* s2)
{
	return (wcscmp(s1, s2) == 0);
}

// Bounds-checking when retrieving argument. Checks if argument exists. If it doesn't quit program.
_TCHAR* get_argument(int index, int argc, _TCHAR** argv)
{
	if (index >= argc)
	{
		puts("Not enough arguments. Run without any arguments to see doc.");
		exit(ErrorResult);
		return 0;
	}
	return argv[index];
}
