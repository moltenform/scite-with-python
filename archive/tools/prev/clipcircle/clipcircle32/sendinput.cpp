
#include "common.h"

// This function sends the keystrokes Ctrl-V to the current window,
// and then uses Shift-Left to select what was pasted.
bool SendKeyboardInputToWindow(const WCHAR* wz)
{
	if (!wz || !wz[0])
		return true;

	// Count length of string, so that we press shift-left the correct number of times.
	// (newlines counted as one char). This won't handle composed unicode, but they'll still be pasted correctly.
	int nPrintLength = 1;
	while(*(++wz))
		nPrintLength += (*(wz-1)==L'\r' && *wz==L'\n') ? 0 : 1;
	
	// There's an effective limit on how much text can be selected, because we can send window messages faster than
	// the receiving app can respond to them. A message loop queue by default is limited to 10,000, and if this queue
	// is full, subsequent events are lost, which isn't good because the shift key is left down.
	// Also, some apps are slow at selecting a lot of text, like notepad.
	const int MaxSelectLength = 1000;
	if (nPrintLength > MaxSelectLength)
		nPrintLength = 0;

	// Hack: wait for Win and V key to be released.
	// alternative would be to artificially send a key-up event for Win and V, not really any better.
	Sleep(200);

	// It's better to simulate Ctrl-V than simulate typing the string.
	// 1) faster than sending many events
	// 2) sure to support newline characters and unicode/exotic characters.
	const int nInputsLength = 2048;
	INPUT arInput[nInputsLength];
	memset(arInput, 0, sizeof(arInput)); 
	for (int i=0; i<_countof(arInput); i++)
		arInput[i].type = INPUT_KEYBOARD;

	// Keep track of nWhereShiftStarts, so that the same array can be re-used later.
	int n = -1;

	// Send Ctrl+V
	n++; arInput[n].ki.wVk = VK_LCONTROL;
	n++; arInput[n].ki.wVk = 'V';
	n++; arInput[n].ki.wVk = 'V'; arInput[n].ki.dwFlags = KEYEVENTF_KEYUP;
	n++; arInput[n].ki.wVk = VK_LCONTROL; arInput[n].ki.dwFlags = KEYEVENTF_KEYUP;

	// Send Shift+Left, as many times as possible
	n++; arInput[n].ki.wVk = VK_LSHIFT;
	int nWhereShiftStarts = n;
	int nGoLeft = min(_countof(arInput)/2 - n, nPrintLength);
	for (int i=0; i<nGoLeft; i++)
	{
		n++; arInput[n].ki.wVk = VK_LEFT; arInput[n].ki.dwFlags = KEYEVENTF_EXTENDEDKEY;
		n++; arInput[n].ki.wVk = VK_LEFT; arInput[n].ki.dwFlags = KEYEVENTF_KEYUP |  KEYEVENTF_EXTENDEDKEY;
	}
	n++; arInput[n].ki.wVk = VK_LSHIFT; arInput[n].ki.dwFlags = KEYEVENTF_KEYUP;

	// Send input
	Assert(n < _countof(arInput));
	UINT ret = SendInput(n+1, arInput, sizeof(arInput[0]));
	if (!ret)
	{
		DisplayWarning("SendInput failed");
		return false;
	}

	// In the past, a loop here would use nWhereShiftStarts and nGoLeft 
	// but now that there is a MaxSelectLength, this logic isn't needed.
	return true;
}

