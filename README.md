# SciTE-with-Python

A fork of the SciTE code editor that lets you quickly write plugins in Python.

* 26 built-in plugins for quickly editing html/xml, debugging .py scripts, and jumping to the definition of a method or function in Python or C

* Plugins can insert and delete text, restyle ranges of text to underline or highlight, and automate nearly every editor action

* Plugins read/write files on disk, shell out to other tools, and use the Python standard library

* Plugins can register for events like OnKey and OnOpen, listen for multi-key keyboard shortcuts, and even show an interactive GUI inside the code editor
    
* Customize keyboard bindings on all platforms by editing menukey in a properties file

* Find-text-in-files has regular expression support

* When multiple editor windows are open, the current search term is shared between processes
    
* [Usage and features](https://moltenjs.com/page/scite-with-python/doc/features.html)

* [Writing plugins](https://moltenjs.com/page/scite-with-python/doc/writingplugin.html)

* [View the default GTK keyboard bindings](https://moltenjs.com/page/scite-with-python/doc/keyslinux.html)

* [View the default Windows keyboard bindings](https://moltenjs.com/page/scite-with-python/doc/keyswin.html)

* [View the API reference](https://moltenjs.com/page/scite-with-python/doc/writingpluginapi.html)

## Windows

* install [Python 2.7](https://www.python.org/downloads/windows/), use the Windows x86 MSI installer

* download [scite_with_python_0_7_2_win32.zip](https://github.com/moltenjs/scite-with-python/releases/download/v0.7.2/scite_with_python_0_7_2_win32.zip)

* uncompress everything in the .zip

* open SciTE.exe (no "install" needed)

## Linux

    (install prereqs)
    sudo apt-get install libgtk2.0-dev
    sudo apt-get install python2.7-dev
    
    (build scintilla)
    cd ~/Downloads
    wget https://github.com/moltenjs/scite-with-python/archive/v0.7.2.tar.gz
    tar -xzf v0.7.2.tar.gz
    cd scite-with-python-0.7.2/src/scite/scintilla/gtk
    make
    
    (build scite)
    cd ../../scite/gtk
    make
    sudo make install

    (run scite)
    SciTE_with_python

[Additional documentation](https://moltenjs.com/page/scite-with-python/doc/)
