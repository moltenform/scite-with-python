
#include "util.h"

INPUT arInput[512]; 
//C_ASSERT(_countof(arEvents) % 2 == 1); // should be an odd number
INPUT arCtrlV[4];
bool g_fInited = false;

/*
Because the windows key is currently down, system will react as if this were 
win-ctrl-v. could possibly create new thread and sleep. but better to 
temporarily 'unpress' the windows key.
*/


DWORD WINAPI ThreadProc (LPVOID lpdwThreadParam )
{
	//::Sleep(400);

	UINT ret = ::SendInput(_countof(arCtrlV), arCtrlV, sizeof(arCtrlV[0]));
	if (!ret)
		DisplayWarning("::SendInput failed");
	return 0;
}

SsiE sendinput_ctrlv()
{
	if (!g_fInited)
		return ssierr("not inited");
DWORD dwThreadId;
//	::CreateThread(NULL, //Choose default security
//0, //Default stack size
//&ThreadProc,
////Routine to execute
//(LPVOID) null, //Thread parameter
//0, //Immediately run the thread
//&dwThreadId //Thread Id
//);
ThreadProc(null);
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
	//memset(arCtrlV, 0, sizeof(arCtrlV));
	//for (int i=0; i<_countof(arCtrlV); i++)
	//	arCtrlV[i].type = INPUT_KEYBOARD;
	//// 1) ctrl key down
	//arCtrlV[0].ki.wVk = VK_LCONTROL; 
	//// 2) v key down
	//arCtrlV[1].ki.wVk = 56; // v key
	//// 3) v key up
	//arCtrlV[2].ki.wVk = 56;
	//arCtrlV[2].ki.dwFlags = KEYEVENTF_KEYUP;
	//// 4) ctrl key up
	//arCtrlV[3].ki.wVk = VK_LCONTROL; 
	//arCtrlV[3].ki.dwFlags = KEYEVENTF_KEYUP;

	memset(arCtrlV, 0, sizeof(arCtrlV));
	for (int i=0; i<_countof(arCtrlV); i++)
		arCtrlV[i].type = INPUT_KEYBOARD;
	// 2) v key down
	arCtrlV[0].ki.wVk = VK_LWIN ; // v key
	arCtrlV[0].ki.dwFlags = KEYEVENTF_KEYUP;
	// 3) v key up
	arCtrlV[1].ki.wVk = VK_LWIN ;
	arCtrlV[1].ki.dwFlags = KEYEVENTF_KEYUP;
	// 2) v key down
	arCtrlV[2].ki.wVk = 'V'; // v key
	// 3) v key up
	arCtrlV[3].ki.wVk = 'V';
	arCtrlV[3].ki.dwFlags = KEYEVENTF_KEYUP;

	memset(arInput, 0, sizeof(arInput));
	arInput[0].type = INPUT_KEYBOARD;
	arInput[0].ki.wVk = VK_LSHIFT;
	for (int i=1; i<_countof(arInput); i++)
	{
		arInput[i].type = INPUT_KEYBOARD;
		arInput[i].ki.wVk = VK_LEFT;
		arInput[i].ki.wScan = 0;
		arInput[i].ki.dwFlags = 
			(i%2==1) ? 0 : KEYEVENTF_KEYUP;
		arInput[i].ki.time = 0;
		arInput[i].ki.dwExtraInfo = 0;
	}

	// http://www.codeguru.com/forum/showthread.php?t=377393
	// http://www.teachers.ash.org.au/dbrown/virtualdub/capture.htm
	g_fInited = true;
}

