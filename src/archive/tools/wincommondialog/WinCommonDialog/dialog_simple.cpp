
#include "utils.h"

const char* documentationSimple =
    "WinCommonDialog simple dialogtype title text\n"
    "(Returns result through exit code.)\n"
    "\n"
    "Types:\n"
    "yesno\treturns 8 if yes, 4 if no.\n"
    "okcancel\treturns 8 if ok, 2 if cancel.\n"
    "yesnocancel\treturns 8 if yes, 4 if no, 2 if cancel\n"
    "info\n"
    "error\n"
    "warning\n";



int dialog_simple(int argc, _TCHAR* argv[])
{
    _TCHAR* type = getArgument(1, argc, argv);
    _TCHAR* title = getArgument(2, argc, argv);
    _TCHAR* text = getArgument(3, argc, argv);
    if (!type || !title || !text)
    {
        puts(documentationSimple);
        return 1;
    }

    if (stringsEqual(type, _T("yesno")))
    {
        int result = MessageBox(NULL, text, title,  MB_YESNO | MB_ICONQUESTION);
        return (result == IDYES) ? 8 : 4;
    }
    else if (stringsEqual(type, _T("okcancel")))
    {
        int result = MessageBox(NULL, text, title,  MB_OKCANCEL | MB_ICONQUESTION);
        return (result == IDOK) ? 8 : 2;
    }
    else if (stringsEqual(type, _T("yesnocancel")))
    {
        int result = MessageBox(NULL, text, title,  MB_YESNOCANCEL | MB_ICONQUESTION);
        return (result == IDYES) ? 8 :
            (result == IDNO) ? 4 : 2;
    }
    else if (stringsEqual(type, _T("info")))
    {
        (void)MessageBox(NULL, text, title,  MB_OK | MB_ICONINFORMATION);
        return 0;
    }
    else if (stringsEqual(type, _T("error")))
    {
        (void)MessageBox(NULL, text, title,  MB_OK | MB_ICONERROR);
        return 0;
    }
    else if (stringsEqual(type, _T("warning")))
    {
        (void)MessageBox(NULL, text, title,  MB_OK | MB_ICONWARNING);
        return 0;
    }
    else
    {
        puts(documentationSimple);
        return 1;
    }
}

