#include "WinCommonDialog.h"
#include "dialog_simple.h"

#include "Mmsystem.h"

const char* documentationSound =
"WinCommonDialog sound {soundname}\n"
"(Returns result through exit code.)\n"
"\n"
"async is 0 or 1, 1 for true\n"
"Sound name can be path to .wav file\n"
"or one of:\n"
"'Asterisk' 'Default' 'Exclamation' 'Question'"
;


int dialog_sound(int argc, _TCHAR* argv[])
{
	if (argc <= 1 || stringequal(argv[1],_T("/?"))) { puts(documentationSound); return ErrorResult; }
	
	_TCHAR* soundname = get_argument(1, argc, argv);
	
	// it turns out that async doesn't really work - probably because the process closes and stops playback.
	// however, since this will be spawned from lnzscript, the result will essentially be asyn anyways

	LPCTSTR pszSound = NULL;
	DWORD flags = 0; // note, SND_ASYNC does not work
	BOOL res;
	if (stringequal(soundname,_T("Asterisk"))) pszSound=(LPCTSTR)SND_ALIAS_SYSTEMASTERISK;
	else if (stringequal(soundname,_T("Default"))) pszSound=(LPCTSTR)SND_ALIAS_SYSTEMDEFAULT;
	else if (stringequal(soundname,_T("Exclamation"))) pszSound=(LPCTSTR)SND_ALIAS_SYSTEMEXCLAMATION;
	else if (stringequal(soundname,_T("Question"))) pszSound=(LPCTSTR)SND_ALIAS_SYSTEMQUESTION;

	
	if (pszSound!=NULL)
	{
		res = PlaySound(pszSound, NULL, flags | SND_ALIAS_ID);
	}
	else
	{
		pszSound = soundname;
		res = PlaySound(soundname, NULL, flags | SND_FILENAME);
	}

	return res==TRUE ? 0 : ErrorResult;
	
}