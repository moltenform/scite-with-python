#include "wincommondialog.h"
#include "my_input_dialog.h"

#include "resource.h"

_TCHAR* g_returnvalue;


int MyInputDialog::CreateAndShow(_TCHAR* title, _TCHAR* prompt, _TCHAR* defaultText, _TCHAR* bufferOutput)
{
	g_returnvalue = bufferOutput;
	this->title = title;
	this->prompt = prompt;
	this->defaultText = defaultText;
	
//password char? SendDlgItemMessage(hWndDlg, IDC_INPUTEDIT, EM_SETPASSWORDCHAR, CURR_INPUTBOX.password_char, 0);

// do dialog
	INT_PTR result = DialogBoxParam(NULL, MAKEINTRESOURCE(IDD_DIALOG1)/*"IDD_DIALOG1"*/, NULL, reinterpret_cast<DLGPROC>(TextInputDlg), reinterpret_cast<LPARAM>(this));
	if (result == -1) {
		printf("error number %d", GetLastError());
		return 100;
	}

	return 0;
}

void CenterWindow( HWND hwnd )
{
    RECT rc ;
    GetWindowRect ( hwnd, &rc ) ;
    SetWindowPos( hwnd, 0, 
        (GetSystemMetrics(SM_CXSCREEN) - rc.right)/2,
        (GetSystemMetrics(SM_CYSCREEN) - rc.bottom)/2,
         0, 0, SWP_NOZORDER|SWP_NOSIZE );
}
int ControlIDOfCommand(unsigned long wParam) { return wParam & 0xffff; }

/*
windows api information:
http://zetcode.com/tutorials/winapi/firststeps/
http://www.toymaker.info/Games/html/windows_api.html
SetWindowText
http://msdn.microsoft.com/en-us/library/ms633546(VS.85).aspx
DialogBox Procedures
http://msdn.microsoft.com/en-us/library/ms644995(VS.85).aspx
DialogBoxParam Function
http://msdn.microsoft.com/en-us/library/ms645465(VS.85).aspx
*/

BOOL TextInputDialogMsg(void* context, HWND hDlg, UINT message, WPARAM wParam) 
{

	switch (message) {

	case WM_INITDIALOG: {
			
			MyInputDialog*caller = reinterpret_cast<MyInputDialog*>(context);
			if (caller)
			{
				if (caller->defaultText)
					SetDlgItemText(hDlg, IDC_EDIT1, caller->defaultText);
				if (caller->prompt)
					SetDlgItemText(hDlg, IDC_THESTATIC1, caller->prompt);
				if (caller->title)
					SetWindowText(hDlg, caller->title);
			}
			
			CenterWindow(hDlg);

			SendDlgItemMessage(hDlg, IDC_EDIT1, EM_LIMITTEXT, MAXSTRINGLENGTH, 1);
			//SendDlgItemMessage(hDlg, IDC_EDIT1, WM_SETFOCUS, 0, 0); //give it initial focus
			//SendDlgItemMessage(hDlg, IDC_EDIT1, EM_SETSEL, 0, 4);  //give it initial focus
			//instead, set focus, simply by editing rc.rc and making the Edit control the first one in the list.
			return TRUE;
		}
		break;
	case WM_CLOSE:
		SendMessage(hDlg, WM_COMMAND, IDCANCEL, 0);
		break;

	case WM_COMMAND:
		if (ControlIDOfCommand(wParam) == IDCANCEL)
		{
			EndDialog(hDlg, IDCANCEL);
			_tcscpy(g_returnvalue, L"<cancel>");
			return FALSE;
		} 
		else if (ControlIDOfCommand(wParam) == IDOK) 
		{

			GetDlgItemText(hDlg, IDC_EDIT1, g_returnvalue, MAXSTRINGLENGTH);

			
			EndDialog(hDlg, ControlIDOfCommand(wParam));
			return TRUE;
		}
		break;
	}

	return FALSE;
}


BOOL CALLBACK TextInputDlg(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam) 
{
	return TextInputDialogMsg((void*) lParam, hDlg, message, wParam);
}





