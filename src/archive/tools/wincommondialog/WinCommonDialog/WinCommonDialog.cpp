
// WinCommonDialog  Copyright (C) 2008  Ben Fisher
// This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
// This is free software, and you are welcome to redistribute it
// under certain conditions.
    
// uses Unicode Character Set, see makefile
// requires "winmm.lib", see linker flags in makefile

#include "utils.h"

const char * documentation = 
    "WinCommonDialog.exe, Ben Fisher 2008\n"
    "A wrapper over simple Windows dialogs, using return code to pass result.\n"
    "\n"
    "This is divided into different functions. For more specific help, type:\n"
    "WinCommonDialog simple /?\n"
    "WinCommonDialog color /?\n"
    "WinCommonDialog file /?\n"
    "WinCommonDialog sound /?\n"
    "WinCommonDialog text /?\n\n";

int dialog_simple(int argc, _TCHAR* argv[]);
int dialog_color(int argc, _TCHAR* argv[]);
int dialog_file(int argc, _TCHAR* argv[]);
int dialog_sound(int argc, _TCHAR* argv[]);
int dialog_textinput(int argc, _TCHAR* argv[]);

int _tmain(int argc, _TCHAR* argv[])
{
    // in general, return code 0 means success,
    // return code 1 means missing or invalid parameter,
    // other return codes have specific meaning to a module.
    
    _TCHAR* mode = getArgument(1, argc, argv);
    if (mode && stringsEqual(mode, _T("simple")))
    {
        return dialog_simple(argc - 1, &argv[1]);
    }
    else if (mode && stringsEqual(mode, _T("color")))
    {
        return dialog_color(argc - 1, &argv[1]);
    }
    else if (mode && stringsEqual(mode, _T("file")))
    {
        return dialog_file(argc - 1, &argv[1]);
    }
    else if (mode && stringsEqual(mode, _T("sound")))
    {
        return dialog_sound(argc - 1, &argv[1]);
    }
    else if (mode && stringsEqual(mode, _T("text")))
    {
        return dialog_textinput(argc - 1, &argv[1]);
    }
    else
    {
        puts(documentation);
        return 1;
    }
}
