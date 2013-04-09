
#include "util.h"

/*
Because the windows key is currently down, system will react as if this were 
win-ctrl-v. could possibly create new thread and sleep. but better to 
temporarily 'unpress' the windows key.
*/

void PrintDebugsendinput(int nLen, INPUT* arinput, int nStart, int nAll, int nw)
{
	char buf[256];
	sprintf(buf, "C:\\pydev\\pyaudio_here\\progs\\clipcircle\\clipcircle32\\dbgoutsendinput%d.txt", nw);
	FILE* f = fopen(buf, "w");
	for (int i=0; i<nAll; i++)
	{
		if (i==nStart) fprintf(f, "--start--\n");
		if (i==nStart+nLen) fprintf(f, "--end--\n");
		const char* sname= "unknown";
		if (arinput[i].ki.wVk == 0) sname = "0";
		else if (arinput[i].ki.wVk == VK_LCONTROL) sname = "VK_LCONTROL";
		else if (arinput[i].ki.wVk == 'V') sname = "'V'";
		else if (arinput[i].ki.wVk == VK_LSHIFT) sname = "VK_LSHIFT";
		else if (arinput[i].ki.wVk == VK_LEFT) sname = "VK_LEFT";
		const char* snamen = (arinput[i].ki.dwFlags & KEYEVENTF_KEYUP) ? "(up)" : "";
		fprintf(f, "%d) %s %s\n", i, sname, snamen);
		//const WCHAR* fmt = (i==m_ptr ? L"(%d):%s\n" : L"%d:%s\n");
		//fprintf(f, fmt, i, m_items[i]);
	}
	fclose(f);
}

SsiE sendinput_ctrlv(const WCHAR* wz)
{
	if (!*wz)
		return SsiEOk;
	int nPrintLength = 1;
	while(*(++wz))
		nPrintLength += (*(wz-1)==L'\r' && *(wz)==L'\n') ? 0 : 1;

	::Sleep(200); // wait for the Win and V key to be released. (hack)

	INPUT arL[64];
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
	int nWhereShiftStarts = t;
	int nGoLeft = min(_countof(arL)/2 - t, nPrintLength);
	for (int i=0; i<nGoLeft; i++)
	{
		t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_EXTENDEDKEY;
		t++; arL[t].ki.wVk = VK_LEFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP |  KEYEVENTF_EXTENDEDKEY;
	}
	// shift up
	t++; arL[t].ki.wVk = VK_LSHIFT; arL[t].ki.dwFlags = KEYEVENTF_KEYUP;

	int th=0;
	PrintDebugsendinput(t+1, arL, 0, _countof(arL), th++);
	ret = ::SendInput(t+1, arL, sizeof(arL[0]));
	if (!ret)
		DisplayWarning("::SendInput failed");

	// go left a bit more, if needed
	int nCurrentClipsize = nPrintLength - nGoLeft;
	while (nCurrentClipsize > 0)
	{
		int thisbatch = min(nCurrentClipsize, nGoLeft);
		if (thisbatch < nGoLeft)
		{
			arL[nWhereShiftStarts+1+2*thisbatch].ki.wVk = VK_LSHIFT;
			arL[nWhereShiftStarts+1+2*thisbatch].ki.dwFlags = KEYEVENTF_KEYUP;
		}
		PrintDebugsendinput(thisbatch*2+1+1, arL, nWhereShiftStarts, _countof(arL), th++);
		ret = ::SendInput(thisbatch*2+1+1, arL + nWhereShiftStarts, sizeof(arL[0]));
		if (!ret)
			DisplayWarning("::SendInput failed");
		nCurrentClipsize -= thisbatch;
	}


	return SsiEOk;
}

void sendinput_setup()
{
}

