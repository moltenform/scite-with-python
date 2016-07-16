#include "WinCommonDialog.h"
#include "dialog_file.h"

//#include "input_dialog/InputBox.h"
#include "my_input_dialog.h"

#include <string>

const char* documentationTextinput =
"WinCommonDialog text {title} {prompt} {defaultval=""}\n"
"(Returns result through stdout.)\n"
"\n"
"Displays dialog where user can input plain text.\n"
"Returns \"\" if user cancels.\n"
"Exit code non-zero on error.\n";

int dialog_textinput(int argc, _TCHAR* argv[])
{
	if (argc <= 1 || stringequal(argv[1],_T("/?"))) { puts(documentationTextinput); return ErrorResult; }

	_TCHAR* dlgtitle = get_argument(1, argc, argv);
	_TCHAR* dlgprompt = get_argument(2, argc, argv);
	_TCHAR* dlgdefault = NULL;
	if (argc >= 4) dlgdefault = get_argument(3, argc, argv);

	_TCHAR bufferResult[MAXSTRINGLENGTH];
	_tcscpy(bufferResult, L"");

	MyInputDialog dlg;
	dlg.CreateAndShow(dlgtitle, dlgprompt, dlgdefault, bufferResult);
	
	_putts(bufferResult);


	return 0;
}

