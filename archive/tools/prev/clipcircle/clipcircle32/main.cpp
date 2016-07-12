/*
Clipcircle32
Ben Fisher, 2011. Released under the GPLv3 license.
http://halfhourhacks.blogspot.com
See clipcircle.txt for more information.

Build settings:
Use Unicode character set.
Linker/system/subsystem should be Windows.
*/

#include "common.h"
#include "sendinput.h"
#include "clipcircle.h"

const int CLIPC_HOTKEY_SPPASTE = 2;
const int CLIPC_HOTKEY_QUIT = 3;
const int WM_MY_TRAY_ICON = (WM_USER + 2); // message for icon messages
const int TASKBARICON_uId = 0x300; // taskbar icons are identified by hWnd and uID.

const WCHAR* g_wzClassName = L"bfisher_Clipcircle32";
const WCHAR* g_wzTip = L"ClipCircle32";
HWND g_vhWndMain = NULL;
HWND g_vhNextClipViewer = NULL;
ClipCircle g_ClipCircle;

void TrayIconMsg(UINT32 idTaskbar,  UINT32 iMessage)
{
	if (idTaskbar != TASKBARICON_uId)
		return;

	if (iMessage != WM_RBUTTONDOWN)
		return;

	SetForegroundWindow(g_vhWndMain);

	HMENU hMenu = CreatePopupMenu();
	Assert(hMenu);
	const int nIdInfo = 1;
	BOOL ret = AppendMenu(hMenu, MF_STRING | MF_ENABLED, nIdInfo, L"Info");
	Assert(ret);
	POINT ptCursorPos;
	ret = GetCursorPos(&ptCursorPos);
	Assert(ret);

	INT32 nSelected = TrackPopupMenuEx(hMenu, TPM_RETURNCMD, ptCursorPos.x, ptCursorPos.y, g_vhWndMain, NULL);
	DestroyMenu(hMenu);
	
	if (nSelected == nIdInfo)
	{
		MessageBoxA(NULL, "ClipCircle32, by Ben Fisher, 2011\n\n"
			"Press Win+Escape to quit\nPress Win+V to paste\n", "ClipCircle32", MB_OK);
	}
}

LRESULT CALLBACK WndProc(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
	switch (uMsg)
	{
	case WM_CREATE:
		g_vhNextClipViewer = SetClipboardViewer(hWnd); 
		break;
	case WM_CHANGECBCHAIN: 
		// If the next window is closing, repair the chain. 
		if ((HWND) wParam == g_vhNextClipViewer) 
			g_vhNextClipViewer = (HWND) lParam; 
		// Otherwise, pass the message to the next link. 
		else if (g_vhNextClipViewer != NULL) 
			SendMessage(g_vhNextClipViewer, uMsg, wParam, lParam); 
	 
		break;
	case WM_DRAWCLIPBOARD:  // clipboard contents changed. 
		// get it
		if (OpenClipboard(NULL))
		{
			if (IsClipboardFormatAvailable(CF_UNICODETEXT))
			{
				HANDLE hClipboardData = GetClipboardData(CF_UNICODETEXT);
				WCHAR *pchData = (WCHAR*)GlobalLock(hClipboardData);
				g_ClipCircle.OnClipChange(pchData);
				GlobalUnlock(hClipboardData);
			}
			CloseClipboard();
		}

        // Pass the message to the next window in clipboard viewer chain.
        SendMessage(g_vhNextClipViewer, uMsg, wParam, lParam); 
        break;

	case WM_HOTKEY:
		{
		switch(wParam)
		{
		case CLIPC_HOTKEY_QUIT:
			{
			NOTIFYICONDATA nid = { 0 };
			nid.cbSize = sizeof(nid);
			nid.hWnd = g_vhWndMain;
			nid.uID = TASKBARICON_uId;
			Shell_NotifyIcon(NIM_DELETE, &nid);
			PostQuitMessage(0);
			break;
			}
		
		case CLIPC_HOTKEY_SPPASTE:
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
		TrayIconMsg((UINT32)wParam, (UINT32)lParam);
		break;
		}

	default:
		break;
	}
	return DefWindowProc(hWnd, uMsg, wParam, lParam);
}

BOOL StartApplication(int nCmdShow, HINSTANCE hInst)
{
	WNDCLASSEX wc = {0};
	wc.cbSize = sizeof(WNDCLASSEX); 
	wc.style = 0;
	wc.lpfnWndProc = (WNDPROC)WndProc;
	wc.hInstance = hInst;
	wc.hbrBackground = (HBRUSH)(COLOR_WINDOW+1);
	wc.lpszClassName = g_wzClassName;
	if (RegisterClassEx(&wc) == 0)
		return FALSE;

	g_vhWndMain = CreateWindow(g_wzClassName, g_wzClassName, WS_OVERLAPPED, 0, 0, 0, 0, HWND_MESSAGE, NULL, hInst, NULL);
	if (g_vhWndMain == NULL)
		return FALSE;

	NOTIFYICONDATA nid = { 0 };
#ifdef NOTIFYICONDATA_V3_SIZE
	UINT cbSize = NOTIFYICONDATA_V3_SIZE;
#else
	UINT cbSize = sizeof(NOTIFYICONDATA);
#endif
	nid.cbSize = cbSize; // support Windows XP/Srvr 2003
	nid.hWnd = g_vhWndMain;
	nid.uID = TASKBARICON_uId;
	nid.uFlags = NIF_ICON | NIF_TIP | NIF_MESSAGE;
	if (OS_FileExists(L"icon.ico"))
		nid.hIcon = (HICON) LoadImage(NULL, L"icon.ico", IMAGE_ICON, 16, 16, LR_LOADFROMFILE);
	else
		nid.hIcon = LoadIcon(NULL, IDI_APPLICATION);

	nid.uCallbackMessage = WM_MY_TRAY_ICON;
	wcscpy_s(nid.szTip, _countof(nid.szTip), g_wzTip);
	Shell_NotifyIcon(NIM_ADD, &nid);

	return TRUE;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
	// if already running, quit
	if (FindWindow(g_wzClassName, NULL))
		return 0;

	if (StartApplication(nCmdShow, hInstance))
	{
		RegisterHotKey(g_vhWndMain, CLIPC_HOTKEY_SPPASTE , MOD_WIN , 'V'); //MOD_NOREPEAT
		RegisterHotKey(g_vhWndMain, CLIPC_HOTKEY_QUIT, MOD_WIN, VK_ESCAPE);
		MSG msg;
		while (GetMessage(&msg, NULL, 0, 0)) 
		{
			TranslateMessage(&msg);
			DispatchMessage(&msg);
		}
		UnregisterHotKey(g_vhWndMain, CLIPC_HOTKEY_SPPASTE);
		UnregisterHotKey(g_vhWndMain, CLIPC_HOTKEY_QUIT);
		ChangeClipboardChain(g_vhWndMain, g_vhNextClipViewer); 
	}
	return 0;
}

