
#include "util.h"

INPUT arInput[255];
C_ASSERT(_countof(arInput) % 2 == 1); // should be an odd number
INPUT arCtrlV[15];
INPUT arWinbackdown[1];
bool g_fInited = false;

/*
Because the windows key is currently down, system will react as if this were 
win-ctrl-v. could possibly create new thread and sleep. but better to 
temporarily 'unpress' the windows key.
*/

SsiE sendinput_ctrlv()
{
	if (!g_fInited)
		return ssierr("not inited");

	UINT ret = ::SendInput(_countof(arCtrlV), arCtrlV, sizeof(arCtrlV[0]));
	if (!ret)
		DisplayWarning("::SendInput failed");
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
	memset(arCtrlV, 0, sizeof(arCtrlV));
	for (int i=0; i<_countof(arCtrlV); i++)
		arCtrlV[i].type = INPUT_KEYBOARD;
	// 1) win key up
	arCtrlV[0].ki.wVk = VK_LWIN;
	arCtrlV[0].ki.dwFlags = KEYEVENTF_KEYUP;
	// 2) v key up
	arCtrlV[1].ki.wVk = 'V';
	arCtrlV[1].ki.dwFlags = KEYEVENTF_KEYUP;
	// 3) ctrl key down
	arCtrlV[2].ki.wVk = VK_LCONTROL; 
	// 4) v key down
	arCtrlV[3].ki.wVk = 'V'; // v key
	// 5) v key up
	arCtrlV[4].ki.wVk = 'V';
	arCtrlV[4].ki.dwFlags = KEYEVENTF_KEYUP;
	// 6) ctrl key up
	arCtrlV[5].ki.wVk = VK_LCONTROL; 
	arCtrlV[5].ki.dwFlags = KEYEVENTF_KEYUP;
	// 7) shift down
	arInput[6].ki.wVk = VK_LSHIFT;
	// 8) left down
	arInput[7].ki.wVk = VK_LEFT;
	arInput[8].ki.wVk = VK_LEFT;
	arInput[8].ki.dwFlags = KEYEVENTF_KEYUP;
	arInput[9].ki.wVk = VK_LEFT;
	arInput[10].ki.wVk = VK_LEFT;
	arInput[10].ki.dwFlags = KEYEVENTF_KEYUP;
	arInput[11].ki.wVk = VK_LEFT;
	arInput[12].ki.wVk = VK_LEFT;
	arInput[12].ki.dwFlags = KEYEVENTF_KEYUP;
	// shift up
	arInput[13].ki.wVk = VK_LSHIFT;
	arInput[13].ki.dwFlags = KEYEVENTF_KEYUP;
	// win back down
	arInput[14].ki.wVk = VK_LWIN;

	// 7) win key down
	memset(arWinbackdown, 0, sizeof(arWinbackdown));
	arWinbackdown[0].type = INPUT_KEYBOARD;
	arWinbackdown[0].ki.wVk = VK_LWIN;

	memset(arInput, 0, sizeof(arInput));
	arInput[0].type = INPUT_KEYBOARD;
	arInput[0].ki.wVk = VK_LSHIFT;
	for (int i=0; i<_countof(arInput)-2; i++)
	{
		arInput[i+1].type = INPUT_KEYBOARD;
		arInput[i+1].ki.wVk = VK_LEFT;
		arInput[i+1].ki.wScan = 0;
		arInput[i+1].ki.dwFlags = 
			(i%2==0) ? 0 : KEYEVENTF_KEYUP;
		arInput[i+1].ki.time = 0;
		arInput[i+1].ki.dwExtraInfo = 0;
	}
	arInput[_countof(arInput)-1].type = INPUT_KEYBOARD;
	arInput[_countof(arInput)-1].ki.wVk = VK_LSHIFT;
	arInput[_countof(arInput)-1].ki.dwFlags = KEYEVENTF_KEYUP;

	// http://www.codeguru.com/forum/showthread.php?t=377393
	// http://www.teachers.ash.org.au/dbrown/virtualdub/capture.htm
	g_fInited = true;
}

