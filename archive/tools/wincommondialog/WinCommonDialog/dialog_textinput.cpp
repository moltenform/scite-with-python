
#include "utils.h"
#include "resource.h"
#include <string>

const char* documentationTextinput =
	"WinCommonDialog text title prompt (defaultvalue)\n"
	"(Returns result through stdout.)\n"
	"\n"
	"Displays dialog where user can input plain text.\n"
	"Returns in the form \"|text|(user typed string here)|\n"
	"Returns |text_cancel| if user cancels.\n";




void GetTextFromDialog(_TCHAR* title, _TCHAR* prompt, _TCHAR* defaultText, 
	std::wstring& result, bool& canceled, bool& error);

int dialog_textinput(int argc, _TCHAR* argv[])
{
	_TCHAR* title = getArgument(1, argc, argv);
	_TCHAR* prompt = getArgument(2, argc, argv);
	_TCHAR* defaultText = getArgument(3, argc, argv);
	
	
	if (!title || !prompt)
	{
		puts(documentationTextinput);
		return 1;
	}
	else
	{
		std::wstring result;
		bool canceled = false, error = false;
		GetTextFromDialog(title, prompt, defaultText, result, canceled, error);
		if (error)
		{
			return 1;
		}
		else if (canceled)
		{
			traceString(L"|text_cancel|");
			return 0;
		}
		else
		{
			traceString(L"|text|");
			traceString(result.c_str());
			traceString(L"|");
			return 0;
		}
	}
}

class MyInputDialog
{
	std::wstring _title;
	std::wstring _prompt;
	std::wstring _defaultText;
	std::wstring _inputContents;
	bool _canceled;
	static BOOL CALLBACK TextInputDlg(HWND hDlg, UINT msg, WPARAM wParam, LPARAM lParam);
	
public:
	MyInputDialog(_TCHAR* title, _TCHAR* prompt, _TCHAR* defaultText)
	{
		_title = title;
		_prompt = prompt;
		_defaultText = defaultText ? defaultText : L"";
		_canceled = false;
	}
	
	void Show(std::wstring& outResult, bool& canceled, bool& error)
	{
		outResult = L"";
		canceled = false;
		error = false;
		
		// start the dialog, and pass in the 'this' pointer as context
		INT_PTR result = DialogBoxParam(NULL, MAKEINTRESOURCE(IDD_DIALOG1),
			NULL, reinterpret_cast<DLGPROC>(TextInputDlg), 
			reinterpret_cast<LPARAM>(this));
		
		if (result == -1)
		{
			printf("DialogBoxParam failed with error %d\n", GetLastError());
			error = true;
		}
		else
		{
			canceled = _canceled;
			outResult = _canceled ? L"" : _inputContents;
		}
	}
};

BOOL CenterWindow(HWND hwnd)
{
	RECT rc = {0};
	GetWindowRect(hwnd, &rc);
	return SetWindowPos(hwnd, 0, 
		(GetSystemMetrics(SM_CXSCREEN) - rc.right)/2,
		(GetSystemMetrics(SM_CYSCREEN) - rc.bottom)/2,
		0, 0, SWP_NOZORDER|SWP_NOSIZE);
}

int ControlIDOfCommand(unsigned long wParam)
{
	return wParam & 0xffff;
}

BOOL CALLBACK MyInputDialog::TextInputDlg(HWND hDlg, UINT msg, WPARAM wParam, LPARAM lParam)
{
	switch (msg)
	{
		case WM_INITDIALOG:
		{
			MyInputDialog* pthis = reinterpret_cast<MyInputDialog*>(lParam);
			if (pthis)
			{
				SetDlgItemText(hDlg, IDC_EDIT1, pthis->_defaultText.c_str());
				SetDlgItemText(hDlg, IDC_THESTATIC1, pthis->_prompt.c_str());
				SetWindowText(hDlg, pthis->_title.c_str());
				SetProp(hDlg, L"stored_this_pointer", (HANDLE)lParam);
			}
			
			// to give the edit control focus when the form is started, instead of SendDlgItemMessage
			// and WM_SETFOCUS, just edit the .rc file and make the edit control first in the list.
			CenterWindow(hDlg);
			return TRUE;
		}
		case WM_CLOSE:
		{
			SendMessage(hDlg, WM_COMMAND, IDCANCEL, 0);
			break;
		}
		case WM_COMMAND:
		{
			if (ControlIDOfCommand(wParam) == IDCANCEL)
			{
				EndDialog(hDlg, IDCANCEL);
				
				MyInputDialog* pthis = reinterpret_cast<MyInputDialog*>(
					GetProp(hDlg, L"stored_this_pointer"));
				if (pthis)
				{
					pthis->_canceled = true;
				}
				
				return FALSE;
			}
			else if (ControlIDOfCommand(wParam) == IDOK) 
			{
				// if more than 16k chars are given, it will just truncate.
				const int bufferSize = 16384;
				WCHAR bufResults[bufferSize] = {0};
				GetDlgItemText(hDlg, IDC_EDIT1, bufResults, bufferSize);
				
				MyInputDialog* pthis = reinterpret_cast<MyInputDialog*>(
					GetProp(hDlg, L"stored_this_pointer"));
				if (pthis)
				{
					pthis->_inputContents = bufResults;
				}
				
				EndDialog(hDlg, ControlIDOfCommand(wParam));
				return TRUE;
			}
			break;
		}
	}

	return FALSE;
}

void GetTextFromDialog(_TCHAR* title, _TCHAR* prompt, _TCHAR* defaultText, 
	std::wstring& result, bool& canceled, bool& error)
{
	MyInputDialog dlg(title, prompt, defaultText);
	dlg.Show(result, canceled, error);
}

