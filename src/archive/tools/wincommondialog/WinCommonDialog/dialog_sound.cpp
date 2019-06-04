
#include "utils.h"
#include <mmsystem.h>

const char* documentationSound =
    "WinCommonDialog sound soundname\n"
    "(Returns exit code 0 on success, 1 on failure.)\n"
    "\n"
    "soundname can be path to .wav file\n"
    "or one of:\n"
    "'Asterisk' 'Default' 'Exclamation' 'Question'";


int dialog_sound(int argc, _TCHAR* argv[])
{
    LPCTSTR soundname = getArgument(1, argc, argv);
    if (!soundname)
    {
        puts(documentationSound);
        return 1;
    }
    
    // don't specify SND_ASYNC because this process will likely close before playback.
    LPCTSTR soundalias = NULL;
    DWORD flags = 0;
    BOOL result = FALSE;
    
    if (stringsEqual(soundname, _T("Asterisk")))
    {
        soundalias = (LPCTSTR)SND_ALIAS_SYSTEMASTERISK;
    }
    else if (stringsEqual(soundname, _T("Default")))
    {
        soundalias = (LPCTSTR)SND_ALIAS_SYSTEMDEFAULT;
    }
    else if (stringsEqual(soundname, _T("Exclamation")))
    {
        soundalias = (LPCTSTR)SND_ALIAS_SYSTEMEXCLAMATION;
    }
    else if (stringsEqual(soundname, _T("Question")))
    {
        soundalias = (LPCTSTR)SND_ALIAS_SYSTEMQUESTION;
    }
    
    if (soundalias)
    {
        result = PlaySound(soundalias, NULL, flags | SND_ALIAS_ID);
    }
    else
    {
        result = PlaySound(soundname, NULL, flags | SND_FILENAME);
    }

    // returns exit code 0 on success, 1 on failure.
    return result ? 0 : 1;
}
