# SciTE-with-Python

A fork of the SciTE code editor that lets you add your own plugins in Python.

* Plugins can insert and delete text and automate nearly every editor action

* Plugins can register for events like OnKey and OnOpen, listen for multi-key keyboard shortcuts, and even show an interactive GUI inside the code editor

* 26 built-in plugins for quickly editing html/xml, debugging .py scripts, and jumping to the definition of a method or function in Python or C
    
* Customize keyboard bindings on all platforms by editing menukey in a properties file

* When multiple editor windows are open, the current search term is shared between processes
    
* [Read more here](https://moltenform.com/page/scite-with-python/doc/)

## Linux

Run the following,

    sudo apt-get install libgtk2.0-dev
    sudo apt-get install python2.7-dev
    
    cd ~/Downloads
    wget https://github.com/moltenform/scite-with-python/archive/v0.7.2.tar.gz
    tar -xzf v0.7.2.tar.gz
    cd scite-with-python-0.7.2/src/scite/scintilla/gtk
    make
    
    cd ../../scite/gtk
    make
    sudo make install

    SciTE_with_python

## Windows

* unless you already have Python 2.7 installed, install [Python 2.7](https://www.python.org/downloads/windows/), use the Windows x86 MSI installer

* download [scite_with_python_0_7_2_win32.zip](https://github.com/moltenform/scite-with-python/releases/download/v0.7.2/scite_with_python_0_7_2_win32.zip)

* unzip scite_with_python_0_7_2_win32.zip

* open SciTE.exe


