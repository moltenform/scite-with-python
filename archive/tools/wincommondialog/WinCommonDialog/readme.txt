
WinCommonDialog.exe, Ben Fisher 2008,
GPL v3
A wrapper over simple Windows dialogs, using return code to pass result.
https://github.com/downpoured/scite-with-python

This is divided into different functions. For details, use one of the following,
WinCommonDialog simple /?
WinCommonDialog color /?
WinCommonDialog file /?
WinCommonDialog sound /?
WinCommonDialog text /?
	
Building
This tool doesn't have to be build with a specific compiler, but it makes sense to use msvc 9.0 because 
scite-with-python already has a dependency on that c runtime.
It's the same c runtime that will be installed when python 2.7 is installed.

- Install compiler
	Microsoft Visual C++ Compiler for Python 2.7
	Freely available at https://www.microsoft.com/en-us/download/confirmation.aspx?id=44266
	Download VCForPython27.msi,
	then in an admin prompt, run
	msiexec /i VCForPython27.msi ALLUSERS=1
	The package will be installed to C:\Program Files (x86)\Common Files\Microsoft\Visual C++ for Python\9.0
	
- Build WinCommonDialog
	Open a command prompt 
	cd to C:\Program Files (x86)\Common Files\Microsoft\Visual C++ for Python\9.0
	run vcvarsall.bat
	cd to WinCommonDialog
	run nmake -f WinCommonDialog.mak all
	

