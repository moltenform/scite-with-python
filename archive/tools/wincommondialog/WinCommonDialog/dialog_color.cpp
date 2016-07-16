#include "WinCommonDialog.h"
#include "dialog_color.h"



const char* documentationColor =
"WinCommonDialog color\n"
"(Returns result through stdout.)\n"
"\n"
"Displays dialog where user can choose color.\n"
"The result is printed to stdout, a number in decimal.\n"
"Use WinAPI functions GetRValue and so on to split into RGB.\n"
"Returns \"<cancel>\" if user cancels.\n"
"Exit code non-zero on error.\n";



int dialog_color(int argc, _TCHAR* argv[])
{
	if (argc > 1 && stringequal(argv[1],_T("/?"))) { puts(documentationColor); return ErrorResult; }


	//http://msdn.microsoft.com/en-us/library/ms646829(VS.85).aspx

	COLORREF acrCustClr[16]; // array of custom colors 
	ZeroMemory(acrCustClr, sizeof(acrCustClr));
	DWORD rgbCurrent = 0;        // initial color selection (black)
	CHOOSECOLOR cc;

	ZeroMemory(&cc, sizeof(cc));
	cc.lStructSize = sizeof(cc);
	cc.hwndOwner = NULL;
	cc.lpCustColors = (LPDWORD) acrCustClr;
	cc.rgbResult = rgbCurrent;
	cc.Flags = CC_FULLOPEN | CC_RGBINIT;
		
	if (ChooseColor(&cc)==TRUE) 
	{
		rgbCurrent = cc.rgbResult;
		printf("%ld", rgbCurrent);
		
		/*int r = (int) GetRValue(rgbCurrent); printf("%d,%d,%d", r,g,b);*/ 
		//This is human-readable but harder to parse
	}
	else fputs("<cancel>", stdout);
	return 0;
}
