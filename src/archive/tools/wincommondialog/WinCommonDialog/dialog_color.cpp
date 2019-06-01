
#include "utils.h"
#include <commdlg.h>

const char* documentationColor =
	"WinCommonDialog color\n"
	"(Returns result through stdout.)\n"
	"\n"
	"Displays dialog where user can choose color.\n"
	"The result red, green, blue is printed to stdout, each are numbers in decimal.\n"
	"Returns \"|color_cancel|\" if user cancels.\n";



int dialog_color(int argc, _TCHAR* argv[])
{
	if (argc > 1 && stringsEqual(argv[1], _T("/?")))
	{
		puts(documentationColor);
		return 1;
	}

	COLORREF acrCustClr[16] = {0}; // array of custom colors 
	DWORD rgbCurrent = 0;        // initial color (black)
	
	CHOOSECOLOR cc = {0};
	cc.lStructSize = sizeof(cc);
	cc.hwndOwner = NULL;
	cc.lpCustColors = (LPDWORD) acrCustClr;
	cc.rgbResult = rgbCurrent;
	cc.Flags = CC_FULLOPEN | CC_RGBINIT;
	
	if (ChooseColor(&cc))
	{
		rgbCurrent = cc.rgbResult;
		
		int r = (int) GetRValue(rgbCurrent);
		int g = (int) GetGValue(rgbCurrent);
		int b = (int) GetBValue(rgbCurrent);
		wprintf(L"|color|%d|%d|%d|", r, g, b);
	}
	else
	{
		traceString(L"|color_cancel|");
	}
	
	return 0;
}
