#include "WinCommonDialog.h"
#include "dialog_file.h"

#include <string>

const char* documentationFile =
"WinCommonDialog file {dialog} {filetype=*} {startdir=.}\n"
"(Returns result through stdout.)\n"
"\n"
"Displays dialog where user can choose file.\n"
"Dialog should be one of:\n"
"open\n"
"openmult\n"
"save\n"
//"dir\n"
"\n"
"filetype, if present, should be in the format \"bmp\" (not \"*.bmp\")\n"
"Otherwise, defaults to All files *.*\n"
"Returns \"<cancel>\" if user cancels.\n"
"Exit code non-zero on error.\n";

int dialog_file(int argc, _TCHAR* argv[])
{
	if (argc <= 1 || stringequal(argv[1],_T("/?"))) { puts(documentationFile); return ErrorResult; }

	_TCHAR* dlgtype = get_argument(1, argc, argv);
	_TCHAR* filetype = NULL;
	_TCHAR* startdir = NULL;
	if (argc >= 3) filetype = get_argument(2, argc, argv);
	if (argc >= 4) startdir = get_argument(3, argc, argv);

	if (stringequal(dlgtype, _T("openmult")))
		return dialog_file_open(filetype, startdir, true);
	else if (stringequal(dlgtype, _T("open")))
		return dialog_file_open(filetype, startdir, false);
	else if (stringequal(dlgtype, _T("save")))
		return dialog_file_save(filetype, startdir);
	//else if (stringequal(dlgtype, _T("dir")))
	//	return dialog_file_dir(startdir);
	
	return 0;


}




int dialog_file_open(_TCHAR* filetype, _TCHAR* startdir, bool bMult)
{
	// the following is wasteful if not select-multiple, but I guess these days that doesn't matter as much
	enum {maxBufferSize=16384}; // 2048 is maximum common dialog buffer size according to mfc...

	_TCHAR bufFileType[256];
	_TCHAR bufResults[maxBufferSize];
	bufResults[0] = '\0';

	OPENFILENAME ofn;
	ZeroMemory(&ofn, sizeof(ofn));
	ofn.lStructSize = sizeof(ofn);
	ofn.hwndOwner = NULL;
	ofn.hInstance = NULL;
	ofn.lpstrFile = bufResults;
	ofn.nMaxFile = maxBufferSize;

	if (filetype==NULL || stringequal(filetype,_T("*")))
		ofn.lpstrFilter = _T("All Files\0*.*\0\0");
	else
	{
		ZeroMemory(&bufFileType, sizeof(bufFileType)); // important. Otherwise it will keep reading past the string.
		_snwprintf(bufFileType,sizeof(bufFileType), _T("%s Files|*.%s||"), filetype, filetype);
		// sprintf and strcpy *stop* upon hitting a \0. So, we use | first, and then replace with \0 later.
		// replace | with \0
		for(int i=0;i<sizeof(bufFileType);i++) {if (bufFileType[i]=='|') {bufFileType[i]='\0';}}
		ofn.lpstrFilter = bufFileType;
	}
	ofn.lpstrCustomFilter = NULL;
	ofn.nMaxCustFilter = NULL;
	ofn.nFilterIndex = 0; //which filter is active
	//ofn.lpstrTitle = Let the OS decide, it will localize

	// it is possible that this is NULL, but that is intentional. If null it will use current directory as expected
	ofn.lpstrInitialDir = startdir; 

	ofn.Flags =
		OFN_HIDEREADONLY | // hide "Open as read only" checkbox
		OFN_EXPLORER |		
		OFN_PATHMUSTEXIST |
		OFN_FILEMUSTEXIST;

	if (bMult)
		ofn.Flags |= OFN_ALLOWMULTISELECT;

	if (GetOpenFileName(&ofn))
	{
		if (!bMult || _tcslen(ofn.lpstrFile) > static_cast<size_t>(ofn.nFileOffset))
		{
			// Chose one file. ofn.lpstrFile contains the full path of the file.
			_putts(ofn.lpstrFile);
		}
		else
		{
			// Chose multiple files. ofn.lpstrFile contains 1) the directory 2-n) the file names
			_putts(ofn.lpstrFile); // prints the directory name

			_TCHAR *p = ofn.lpstrFile + _tcslen(ofn.lpstrFile) + 1; //advance past the \0 of the first string
			while (*p) {
				_putts(p); // print the file name
				// go to next char pos after \0
				p += _tcslen(p) + 1;
			}
		}
	}
	else 
	{
		fputs("<cancel>", stdout);
	}
	//std::stringstream stream;	//stream.str().c_str(); //std::string h;
	return 0;
}

int dialog_file_save(_TCHAR* filetype, _TCHAR* startdir)
{
	enum {maxBufferSize=512};

	_TCHAR bufFileType[256];
	_TCHAR bufResults[maxBufferSize];
	bufResults[0] = '\0';

	OPENFILENAME ofn;
	ZeroMemory(&ofn, sizeof(ofn));
	ofn.lStructSize = sizeof(ofn);
	ofn.hwndOwner = NULL;
	ofn.hInstance = NULL;
	ofn.lpstrFile = bufResults;
	ofn.nMaxFile = maxBufferSize;

	if (filetype==NULL || stringequal(filetype,_T("*")))
		ofn.lpstrFilter = _T("All Files\0*.*\0\0");
	else
	{
		ZeroMemory(&bufFileType, sizeof(bufFileType)); // important. Otherwise it will keep reading past the string.
		_snwprintf(bufFileType,sizeof(bufFileType), _T("%s Files|*.%s||"), filetype, filetype);
		// sprintf and strcpy *stop* upon hitting a \0. So, we use | first, and then replace with \0 later.
		// replace | with \0
		for(int i=0;i<sizeof(bufFileType);i++) {if (bufFileType[i]=='|') {bufFileType[i]='\0';}}
		ofn.lpstrFilter = bufFileType;
	}
	ofn.lpstrCustomFilter = NULL;
	ofn.nMaxCustFilter = NULL;
	ofn.nFilterIndex = 0; //which filter is active
	//ofn.lpstrTitle = Let the OS decide, it will localize

	// it is possible that this is NULL, but that is intentional. If null it will use current directory as expected
	ofn.lpstrInitialDir = startdir; 

	ofn.Flags = OFN_HIDEREADONLY | // hide "Open as read only" checkbox
		OFN_OVERWRITEPROMPT;

	if (GetSaveFileName(&ofn))
	{
		//ofn.lpstrFile contains the full path of the file.
		_putts(ofn.lpstrFile);
	}
	else 
	{
		fputs("<cancel>", stdout);
	}
	return 0;
}


/*
_TCHAR* g_dir_startdir = NULL; //can be on the stack, since dialog_file_dir will still be in memory.
//not thread safe or re-entrant though.
int WINAPI dir_SHBrowseCallBack( HWND hWnd, UINT uMsg, LPARAM lParam, LPARAM lpData )
{
	if ( uMsg == BFFM_INITIALIZED )
	{
		// Set initial directory
		if ( g_dir_startdir )
		{
			::SendMessage( hWnd,
			BFFM_SETSELECTION,
			TRUE,
			LPARAM(g_dir_startdir)
			);
		}
	}
	return 0;
}

int dialog_file_dir( _TCHAR* startdir)
{
	g_dir_startdir = (startdir) ? startdir : NULL;

	BROWSEINFO bi = {0};
	bi.hwndOwner = NULL;
	//bi.lpszTitle; use default OS title
	bi.ulFlags   = BIF_RETURNONLYFSDIRS | BIF_USENEWUI;
	bi.lpfn = BFFCALLBACK( dir_SHBrowseCallBack );
	bi.lParam = NULL;

	//~ LPMALLOC shellMalloc = 0; 		//what is this??????
	//~ SHGetMalloc(&shellMalloc);
	LPCITEMIDLIST pidl = ::SHBrowseForFolderA(&bi);

	_TCHAR bufDirectory[MAXPATH];
	bool result = false;
	if (pidl)
		result = ::SHGetPathFromIDListA(pidl, bufDirectory) != FALSE;
	//~ shellMalloc->Release();
	
	if (result)
		_putts(bufDirectory);
	else 
		fputs("<cancel>", stdout);
	g_dir_startdir = NULL;
	return 0;
}
*/