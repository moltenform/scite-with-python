#include "wincommondialog.h"
#include "windows.h"

#define MAXSTRINGLENGTH 2048

class MyInputDialog
{
	


public:

const _TCHAR* title;
const _TCHAR* prompt;
const _TCHAR* defaultText;

int CreateAndShow(_TCHAR* title, _TCHAR* prompt, _TCHAR* defaultText, _TCHAR* buffer);

};

BOOL CALLBACK TextInputDlg(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam);