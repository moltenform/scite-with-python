
#include "utils.h"
#include <commdlg.h>
#include <string>

const char* documentationFile =
    "WinCommonDialog file dialogtype (filetype) (startdir)\n"
    "(Returns result through stdout.)\n"
    "\n"
    "Displays dialog where user can choose file.\n"
    "Dialogtype should be one of:\n"
    "open\n"
    "openmult\n"
    "save\n"
    "\n"
    "filetype, if present, should be in the format \"bmp\" (not \"*.bmp\")\n"
    "Otherwise, defaults to All files *.*\n"
    "Returns \"|file_cancel|\" if user cancels.\n";



int dialog_file_open(_TCHAR* filetype, _TCHAR* startdir, bool mult);
int dialog_file_save(_TCHAR* filetype, _TCHAR* startdir);
int dialog_file(int argc, _TCHAR* argv[])
{
    _TCHAR* dlgtype = getArgument(1, argc, argv);
    _TCHAR* filetype = getArgument(2, argc, argv);
    _TCHAR* startdir = getArgument(3, argc, argv);
    
    if (dlgtype && stringsEqual(dlgtype, _T("openmult")))
    {
        return dialog_file_open(filetype, startdir, true);
    }
    else if (dlgtype && stringsEqual(dlgtype, _T("open")))
    {
        return dialog_file_open(filetype, startdir, false);
    }
    else if (dlgtype && stringsEqual(dlgtype, _T("save")))
    {
        return dialog_file_save(filetype, startdir);
    }
    else
    {
        puts(documentationFile);
        return 1;
    }
}

int dialog_file_open(_TCHAR* filetype, _TCHAR* startdir, bool mult)
{
    const int bufferSize = 16384;
    _TCHAR bufResults[bufferSize] = {0};

    OPENFILENAME ofn = {0};
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = NULL;
    ofn.hInstance = NULL;
    ofn.lpstrFile = bufResults;
    ofn.nMaxFile = bufferSize;

    std::wstring filter;
    if (filetype == NULL || stringsEqual(filetype, _T("*")))
    {
        filter = L"All Files|*.*||";
    }
    else
    {
        filter += filetype;
        filter += L" Files|*.";
        filter += filetype;
        filter += L"||";
    }
    
    replaceCharWithNulChar(filter, L'|');
    ofn.lpstrFilter = filter.c_str();
    ofn.lpstrCustomFilter = NULL;
    ofn.nMaxCustFilter = NULL;
    ofn.nFilterIndex = 0; // which filter is active
    ofn.lpstrInitialDir = startdir; // if this is null, uses current directory as expected

    ofn.Flags = OFN_HIDEREADONLY | // hide "Open as read only" checkbox
        OFN_EXPLORER |		
        OFN_PATHMUSTEXIST |
        OFN_FILEMUSTEXIST;

    if (mult)
    {
        ofn.Flags |= OFN_ALLOWMULTISELECT;
    }

    if (GetOpenFileName(&ofn))
    {
        size_t offset = static_cast<size_t>(ofn.nFileOffset);
        if (!mult || stringLength(ofn.lpstrFile) > offset)
        {
            // chose one file. ofn.lpstrFile contains the full path of the file.
            traceString(L"|file|");
            traceString(ofn.lpstrFile);
            traceString(L"|");
        }
        else
        {
            // multiple strings were returned within this string, separated by nul chars.
            // chose multiple files. ofn.lpstrFile contains 1) the directory 2-n) the file names
            traceString(L"|file|");
            traceString(ofn.lpstrFile);
            traceString(L"|");

            //advance past the nul char of the first string
            const _TCHAR *p = ofn.lpstrFile + stringLength(ofn.lpstrFile) + 1; 
            while (*p)
            {
                traceString(p);
                traceString(L"|");
                
                // go to next char pos after nul char
                p += stringLength(p) + 1;
            }
        }
    }
    else 
    {
        fputs("|file_cancel|", stdout);
    }
    
    return 0;
}

int dialog_file_save(_TCHAR* filetype, _TCHAR* startdir)
{
    const int bufferSize = 16384;
    _TCHAR bufResults[bufferSize] = {0};

    OPENFILENAME ofn = {0};
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = NULL;
    ofn.hInstance = NULL;
    ofn.lpstrFile = bufResults;
    ofn.nMaxFile = bufferSize;

    std::wstring filter;
    if (filetype == NULL || stringsEqual(filetype, _T("*")))
    {
        filter = L"All Files|*.*||";
    }
    else
    {
        filter += filetype;
        filter += L" Files|*.";
        filter += filetype;
        filter += L"||";
    }
    
    replaceCharWithNulChar(filter, L'|');
    ofn.lpstrFilter = filter.c_str();
    ofn.lpstrCustomFilter = NULL;
    ofn.nMaxCustFilter = NULL;
    ofn.nFilterIndex = 0; // which filter is active
    ofn.lpstrInitialDir = startdir; // if this is null, uses current directory as expected

    ofn.Flags = OFN_HIDEREADONLY |
        OFN_OVERWRITEPROMPT;

    if (GetSaveFileName(&ofn))
    {
        // ofn.lpstrFile contains the full path of the file.
        traceString(L"|file|");
        traceString(ofn.lpstrFile);
        traceString(L"|");
    }
    else
    {
        traceString(L"|file_cancel|");
    }
    
    return 0;
}

