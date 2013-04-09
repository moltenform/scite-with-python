
#include "util.h"

//INPUT arInput[255];
//C_ASSERT(_countof(arInput) % 2 == 1); // should be an odd number
//INPUT arCtrlV[15];
int g_length=0;
//INPUT arWinbackdown[1];
bool g_fInited = false;

/*
Because the windows key is currently down, system will react as if this were 
win-ctrl-v. could possibly create new thread and sleep. but better to 
temporarily 'unpress' the windows key.
*/

DWORD WINAPI MyThreadFunction( LPVOID lpParam ) 
{ 
	::Sleep(400);
	INPUT arL[16];
	int t = -1; UINT ret;

	memset(arL, 0, sizeof(arL)); t=-1;
	t++; arL[t].ki.wVk = 'R'; // v key
	//// 5) v key up
	t++; arL[t].ki.wVk = 'R'; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;

	// 7) shift down
	//t++; arL[t].ki.wVk = VK_LSHIFT;
	//// 8) left down
	//t++; arL[t].ki.wVk = VK_LEFT;
	//t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//t++; arL[t].ki.wVk = VK_LEFT;
	//t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//t++; arL[t].ki.wVk = VK_LEFT;
	//t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//// shift up
	//t++; arL[t].ki.wVk = VK_LSHIFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
	ret = ::SendInput(t+1, arL, sizeof(arL[0]));
	if (!ret)
		DisplayWarning("::SendInput failed");

	::MessageBoxA(null, "kk", "kk", 0);

    return 0; 
}

SsiE sendinput_ctrlv()
{
	if (!g_fInited)
		return ssierr("not inited");

	::Sleep(400);
	INPUT arL[16];
	int t = -1; UINT ret;

	memset(arL, 0, sizeof(arL)); t=-1;
	arL[0].ki.wVk = 'U'; // v key
	//// 5) v key up
	arL[1].ki.wVk = 'U'; arL[1].ki.dwFlags = KEYEVENTF_KEYUP;

	// 7) shift down
	//t++; arL[t].ki.wVk = VK_LSHIFT;
	//// 8) left down
	//t++; arL[t].ki.wVk = VK_LEFT;
	//t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//t++; arL[t].ki.wVk = VK_LEFT;
	//t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//t++; arL[t].ki.wVk = VK_LEFT;
	//t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//// shift up
	//t++; arL[t].ki.wVk = VK_LSHIFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
	ret = ::SendInput(2, arL, sizeof(arL[0]));
	if (!ret)
		DisplayWarning("::SendInput failed");

	::MessageBoxA(null, "kkooilo", "kkghhgj", 0);

	DWORD threadid;
	//::CreateThread( 
 //           NULL,                   // default security attributes
 //           0,                      // use default stack size  
 //           MyThreadFunction,       // thread function name
 //           null,          // argument to thread function 
 //           0,                      // use default creation flags 
 //           &threadid);   // returns the thread identifier 

	//UINT ret = ::SendInput(g_length, arCtrlV, sizeof(arCtrlV[0]));
	//if (!ret)
	//	DisplayWarning("::SendInput failed");
	/*ret = ::SendInput(_countof(arInput), arInput, sizeof(arInput[0]));
	if (!ret)
		DisplayWarning("::SendInput failed");

	ret = ::SendInput(_countof(arWinbackdown), arWinbackdown, sizeof(arWinbackdown[0]));
	if (!ret)
		DisplayWarning("::SendInput failed");*/

	return SsiEOk;
}
SsiE sendinput_leftarrow(int nHowManyTimes)
{
	int eventsLeft = nHowManyTimes;
	while (true)
	{
		//if (eventsLeft < _countof(arEvents)/2)
		{
			
		}
		//else
		{
			//eventsLeft -= 
		}
	}

}


void sendinput_setup()
{
	// set up arCtrlV
	/*memset(arCtrlV, 0, sizeof(arCtrlV));
	for (int i=0; i<_countof(arCtrlV); i++)
		arCtrlV[i].type = INPUT_KEYBOARD;
	int t=-1;*/

	// ^ ctrl, !alt, +shift, #win, <left, >right

	//// 1) win key up
	//t++; arCtrlV[t].ki.wVk = VK_LWIN; arCtrlV[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//// 2) v key up
	//t++; arCtrlV[t].ki.wVk = 'V'; arCtrlV[t].ki.dwFlags = KEYEVENTF_KEYUP;
	////// 3) ctrl key down
	////t++; arCtrlV[t].ki.wVk = VK_LCONTROL; 
	////// 4) v key down
	//t++; arCtrlV[t].ki.wVk = 'U'; // v key
	////// 5) v key up
	//t++; arCtrlV[t].ki.wVk = 'U'; arCtrlV[t].ki.dwFlags = KEYEVENTF_KEYUP;
	////// 6) ctrl key up
	////t++; arCtrlV[t].ki.wVk = VK_LCONTROL; arCtrlV[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//// 7) shift down
	////t++; arInput[t].ki.wVk = VK_LSHIFT;
	//// 8) left down
	//t++; arInput[t].ki.wVk = VK_LEFT;
	//t++; arInput[t].ki.wVk = VK_LEFT; arInput[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//t++; arInput[t].ki.wVk = VK_LEFT;
	//t++; arInput[t].ki.wVk = VK_LEFT; arInput[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//t++; arInput[t].ki.wVk = VK_LEFT;
	//t++; arInput[t].ki.wVk = VK_LEFT; arInput[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//// shift up
	////t++; arInput[t].ki.wVk = VK_LSHIFT; arInput[t].ki.dwFlags = KEYEVENTF_KEYUP;
	//// win back down
	////arInput[t].ki.wVk = VK_LWIN;
	//g_length = t;

	//// 7) win key down
	//memset(arWinbackdown, 0, sizeof(arWinbackdown));
	//arWinbackdown[0].type = INPUT_KEYBOARD;
	//arWinbackdown[0].ki.wVk = VK_LWIN;

	//memset(arInput, 0, sizeof(arInput));
	//arInput[0].type = INPUT_KEYBOARD;
	//arInput[0].ki.wVk = VK_LSHIFT;
	//for (int i=0; i<_countof(arInput)-2; i++)
	//{
	//	arInput[i+1].type = INPUT_KEYBOARD;
	//	arInput[i+1].ki.wVk = VK_LEFT;
	//	arInput[i+1].ki.wScan = 0;
	//	arInput[i+1].ki.dwFlags = 
	//		(i%2==0) ? 0 : KEYEVENTF_KEYUP;
	//	arInput[i+1].ki.time = 0;
	//	arInput[i+1].ki.dwExtraInfo = 0;
	//}
	//arInput[_countof(arInput)-1].type = INPUT_KEYBOARD;
	//arInput[_countof(arInput)-1].ki.wVk = VK_LSHIFT;
	//arInput[_countof(arInput)-1].ki.dwFlags = KEYEVENTF_KEYUP;

	// http://www.codeguru.com/forum/showthread.php?t=377393
	// http://www.teachers.ash.org.au/dbrown/virtualdub/capture.htm
	g_fInited = true;
}

