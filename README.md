# SciTE-with-Python

A fork of the SciTE code editor that lets you quickly write plugins in Python.

* 26 built-in plugins for quickly editing html/xml, debugging .py scripts, and jumping to the definition of a method or function in Python or C

* Plugins can insert and delete text, restyle ranges of text to underline or highlight, and automate nearly every editor action

* Plugins read/write files on disk, shell out to other tools, and use the Python standard library

* Plugins can register for events like OnKey and OnOpen, listen for multi-key keyboard shortcuts, and even show an interactive GUI inside the code editor
    
* Customize keyboard bindings on all platforms by editing menukey in a properties file

* Find-text-in-files has regular expression support

* When multiple editor windows are open, the current search term is shared between processes
    
* [Usage and features](https://downpoured.github.io/scite-with-python/070/usage_and_features.html)

* [Writing plugins](https://downpoured.github.io/scite-with-python/070/writing_plugins.html)

* [View the default Windows keyboard bindings](https://downpoured.github.io/scite-with-python/070/html/BindingsWin32.html)

* [View the default GTK keyboard bindings](https://downpoured.github.io/scite-with-python/070/html/BindingsGTK.html)

* [View the API reference](https://downpoured.github.io/scite-with-python/070/html/SciTEWithPythonAPIReference.html)

## Windows

* install [Python 2.7](https://www.python.org/downloads/windows/), use the Windows x86 MSI installer

* download scite-with-python.zip and uncompress 

* open SciTE.exe

## Linux

    # install prereqs
    sudo apt-get install libgtk2.0-dev
    sudo apt-get install python2.7-dev

    # build scintilla
    mkdir ~/scite-with-python
    cd ~/scite-with-python
    git clone https://github.com/downpoured/scite-with-python.git
    cd scite-with-python/src/scite/scintilla/gtk
    make
    
    # build scite
    cd ../../scite/gtk
    make
    sudo make install

    # run scite
    SciTE_with_python

