#include "util.h"
#include "sendinput.h"

//takes unicode, but composed characters or non-BMP characters 
//will cause selection to be incorrect.
// todo: take mutex so that only one instance runs.
// (or just check for a window with same name)

#include <stdio.h>
#include "main.h"
#include "cliputils.h"
#include "clipcircle.h"

// subsystem to Windows
// pch output removed
// use unicode.
// clean exits important because of clip watcher.

HINSTANCE vhInst;
HWND vhWndMain;
HICON vhIcon;
TCHAR* szClassName = TEXT("Clipcircle32bfisher");
TCHAR szInfoTitle[] = TEXT("ClipCircle32");
HWND vhNextClipViewer = null;
ClipCircle g_ClipCircle;

#define Assert(f) if (!(f)) __debugbreak();

void FShowSystemTrayIconMenu()
{
	HMENU hMenu = ::CreatePopupMenu();
	Assert(hMenu);
	const INT32 idInfo = 1;

	if (!::AppendMenu(hMenu, MF_STRING | MF_ENABLED, idInfo, L"Info"))
	{
		Assert(false);
	}
	POINT ptCursorPos;
	if (!::GetCursorPos(&ptCursorPos))
	{
		Assert(false);
	}
	SetForegroundWindow(vhWndMain);
	UINT uFlags = TPM_RIGHTALIGN | TPM_BOTTOMALIGN |TPM_RETURNCMD;
	INT32 iSelected = ::TrackPopupMenuEx(hMenu, uFlags, ptCursorPos.x, ptCursorPos.y, vhWndMain, NULL );
	::DestroyMenu(hMenu);
	
	if (iSelected == idInfo)
	{
		MessageBoxA(NULL, "ClipCircle32, by Ben Fisher, 2011\n\n"
			"Press Win+Alt+Esc to quit\nPress Win+V to paste\n", "ClipCircle32", MB_OK);
	}
}


void OnTrayIcon(UINT32 idTaskbar,  UINT32 iMessage)
{
	if (idTaskbar != mwid_TaskBarIco)
		return;

	switch (iMessage)
	{
		case WM_RBUTTONDOWN:
				FShowSystemTrayIconMenu();
				break;
	}
}

LRESULT CALLBACK WndProc(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
	switch (uMsg)
	{
	case WM_CREATE:
		vhNextClipViewer = ::SetClipboardViewer(hWnd); 
		break;
	case WM_CHANGECBCHAIN: 
		// If the next window is closing, repair the chain. 
		if ((HWND) wParam == vhNextClipViewer) 
			vhNextClipViewer = (HWND) lParam; 
		// Otherwise, pass the message to the next link. 
		else if (vhNextClipViewer != NULL) 
			SendMessage(vhNextClipViewer, uMsg, wParam, lParam); 
	 
		break;
	case WM_DRAWCLIPBOARD:  // clipboard contents changed. 
		// get it
		if (OpenClipboard(NULL))
		{
			if (::IsClipboardFormatAvailable(CF_UNICODETEXT))
			{
				HANDLE hClipboardData = GetClipboardData(CF_UNICODETEXT);
				WCHAR *pchData = (WCHAR*)GlobalLock(hClipboardData);
				g_ClipCircle.OnClipChange(pchData);
				GlobalUnlock(hClipboardData);
			}
			CloseClipboard();
		}

        // Pass the message to the next window in clipboard viewer chain.
        SendMessage(vhNextClipViewer, uMsg, wParam, lParam); 
        break;

	case WM_HOTKEY:
		{
		switch(wParam)
		{
		case CLIPC_QUIT:
			{
			NOTIFYICONDATA nid = { 0 };
			nid.cbSize = sizeof(nid);
			nid.hWnd = vhWndMain;
			nid.uID = mwid_TaskBarIco;
			Shell_NotifyIcon(NIM_DELETE, &nid);
			PostQuitMessage(0);
			break;
			}
		
		case CLIPC_SPPASTE:
			{
			g_ClipCircle.PasteAndCycle();
			break;
			}
		
		default:
			{
			MessageBoxA(NULL, "clipcircle: unknown msg", "clipcircle", MB_OK);
			break;
			}
		}
		break;
		}
	case WM_MY_TRAY_ICON:
		{
		OnTrayIcon((UINT32)wParam, (UINT32)lParam);
		break;
		}

	default:
		break;
	}
	return DefWindowProc(hWnd, uMsg, wParam, lParam);
}

BOOL FInitApplication(int nCmdShow)
{
	WNDCLASSEX wcex = { 0 };
	wcex.cbSize = sizeof(WNDCLASSEX); 

	wcex.style			= CS_HREDRAW | CS_VREDRAW;
	wcex.lpfnWndProc	= (WNDPROC)WndProc;
	wcex.hInstance		= vhInst;
	wcex.hbrBackground	= (HBRUSH)(COLOR_WINDOW+1);
	wcex.lpszClassName	= szClassName;
	if (RegisterClassEx(&wcex) == 0)
		return FALSE;

	vhWndMain = CreateWindow(szClassName, szClassName, WS_OVERLAPPED, 0, 0, 0, 0, HWND_MESSAGE, NULL, vhInst, NULL);
	if (vhWndMain == NULL)
		return FALSE;

	RegisterHotKey(vhWndMain, CLIPC_SPPASTE , MOD_WIN , 'V'); //MOD_NOREPEAT
	RegisterHotKey(vhWndMain, CLIPC_QUIT, MOD_WIN|MOD_ALT, VK_ESCAPE);

	sendinput_setup();

	// if I want to support // Windows XP/Srvr 2003 read docs

	NOTIFYICONDATA nid = { 0 };
	nid.cbSize = sizeof(nid);
	nid.hWnd = vhWndMain;
	nid.uID = mwid_TaskBarIco;
	nid.uFlags = NIF_ICON|NIF_TIP | NIF_MESSAGE;
	// NIF_MESSAGE is important!
	nid.hIcon = LoadIcon(NULL, IDI_APPLICATION);
	nid.uCallbackMessage = WM_MY_TRAY_ICON;
	//nid.hBalloonIcon = LoadIcon(NULL, IDI_APPLICATION);
	//http://msdn.microsoft.com/en-us/library/windows/desktop/bb773352%28v=vs.85%29.aspx
	memcpy(nid.szTip, szInfoTitle, sizeof(szInfoTitle));
	Shell_NotifyIcon(NIM_ADD, &nid);

	return TRUE;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
	vhInst = hInstance;

	if (FInitApplication(nCmdShow))
	{
		MSG msg;
		while (GetMessage(&msg, NULL, 0, 0)) 
		{
			TranslateMessage(&msg);
			DispatchMessage(&msg);
		}
		UnregisterHotKey(vhWndMain, CLIPC_SPPASTE);
		UnregisterHotKey(vhWndMain, CLIPC_QUIT);
		::ChangeClipboardChain(vhWndMain, vhNextClipViewer); 

	}
	return 0;
}
