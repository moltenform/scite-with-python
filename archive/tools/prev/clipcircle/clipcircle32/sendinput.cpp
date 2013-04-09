
#include "util.h"

/*
Because the windows key is currently down, system will react as if this were 
win-ctrl-v. could possibly create new thread and sleep. but better to 
temporarily 'unpress' the windows key.
*/


SsiE sendinput_ctrlv(int nClipSize)
{
	::Sleep(200); // wait for the Win and V key to be released. (hack)

	INPUT arL[1024];
	int t = -1; UINT ret;
	memset(arL, 0, sizeof(arL)); 
	for (int i=0; i<_countof(arL); i++)
		arL[i].type = INPUT_KEYBOARD;

	t=-1;
	// Ctrl+V
	t++; arL[t].ki.wVk = VK_LCONTROL;
	t++; arL[t].ki.wVk = 'V';
	t++; arL[t].ki.wVk = 'V'; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
	t++; arL[t].ki.wVk = VK_LCONTROL; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;

	// select it.
	t++; arL[t].ki.wVk = VK_LSHIFT;
	int nGoLeft = min(_countof(arL)/2 - t - 16, nClipSize);
	for (int i=0; i<nGoLeft; i++)
	{
		t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_EXTENDEDKEY;
		t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP |  KEYEVENTF_EXTENDEDKEY;
	}
	// shift up
	t++; arL[t].ki.wVk = VK_LSHIFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;

	ret = ::SendInput(t+1, arL, sizeof(arL[0]));
	if (!ret)
		DisplayWarning("::SendInput failed");

	// go left a bit more, if needed
	int nCurrentClipsize = nClipSize - nGoLeft;
	while (nCurrentClipsize > 0)
	{
		nGoLeft = min(_countof(arL)/2 - t - 16, nCurrentClipsize);

		memset(arL, 0, sizeof(arL)); 
		for (int i=0; i<_countof(arL); i++)
			arL[i].type = INPUT_KEYBOARD;
		t=-1;

		t++; arL[t].ki.wVk = VK_LSHIFT;
		for (int i=0; i<nGoLeft; i++)
		{
			t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_EXTENDEDKEY;
			t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP |  KEYEVENTF_EXTENDEDKEY;
		}
		// shift up
		t++; arL[t].ki.wVk = VK_LSHIFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;
		ret = ::SendInput(t+1, arL, sizeof(arL[0]));
		if (!ret)
			DisplayWarning("::SendInput failed");

		nCurrentClipsize -= nGoLeft;
	}


	return SsiEOk;
}

void sendinput_setup()
{
}

