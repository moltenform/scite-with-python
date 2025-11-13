
<a href="../README.md" style="color:black; text-decoration:underline">Back</a>

### Build from source (optional)

download [Microsoft Visual C++ Compiler for Python 2.7](https://web.archive.org/web/20210106040224/https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi)

(you must use this compiler version for C runtime compatibility. SHA-256 is 070474db76a2e625513a5835df4595df9324d820f9cc97eab2a596dcbc2f5cbf)

make a destination directory, such as `C:\path\scite-with-python`

save VCForPython27.msi to `C:\path\scite-with-python`

open an Administrator cmd prompt. One way to open this is to press Windows-X, go to the little menu that appears in the bottom right of the screen, and choose "Open Cmd Prompt (Admin)".

run `cd C:\path\scite-with-python`

run `msiexec /i VCForPython27.msi ALLUSERS=1`

then, open any cmd prompt that can run git,

run `cd C:\path\scite-with-python`

`git clone https://github.com/moltenform/scite-with-python.git`

then, open any cmd prompt, and run

`"C:\Program Files (x86)\Common Files\Microsoft\Visual C++ for Python\9.0\vcvarsall.bat"`

if there is no such file, try this instead

`"C:\Program Files\Common Files\Microsoft\Visual C++ for Python\9.0\vcvarsall.bat"`

then unzip `src/scite/scite/python/libs.zip` into `src/scite/scite/python/libs`

(there should now be a file `src/scite/scite/python/libs/python27.lib`)

unzip `src/scite/scite/bin/pythonbinaries.zip` into `src/scite/scite/bin`

(there should now be a file `src/scite/scite/bin/python27.dll`)

unzip `src/scite/scite/bin/tools_internal/wincommondialog/wincommondialog.zip` into `src/scite/scite/bin/tools_internal/wincommondialog`

(there should now be a file `src/scite/scite/bin/tools_internal/wincommondialog/wincommondialog.exe`)

then run these commands,

`cd "C:\path\scite-with-python\scite-with-python\src\scite\scintilla\win32"`

`nmake -f scintilla.mak`

`cd "C:\path\scite-with-python\scite-with-python\src\scite\scite\win32"`

`nmake -f scite.mak`

a few plugins require Python 2.7 to be installed on your computer, but they aren't necessary in most situations.

* to get those plugins running, you can install [Python 2.7](https://www.python.org/downloads/windows/), use the Windows x86 MSI installer. 

   * then, press Ctrl+; to open `SciTEGlobal.properties`
   
   * at the bottom of this file where it says `customcommand.externalpython=` make sure this is the correct path to python 2.7 `pythonw.exe`
   
   * save changes

everything is now compiled, you can run

`"C:\path\scite-with-python\scite-with-python\src\scite\scite\bin\SciTE.exe"`

to start SciTE.

<p>&nbsp;</p><a href="../README.md" style="color:black; text-decoration:underline">Back</a>
