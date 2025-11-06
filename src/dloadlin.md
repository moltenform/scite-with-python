
<a href="../README.md" style="color:black; text-decoration:underline">Back</a>

### Download (Linux)

run the following in a terminal,

    (use apt-get or your system's package manager (yum, pacman, etc))
    sudo apt-get install libgtk2.0-dev
    sudo apt-get install build-essential
    sudo apt-get install xclip
    sudo apt-get install git
    
    cd ~/Downloads
    git clone https://github.com/moltenform/scite-with-python.git
    cd scite-with-python
    wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
    tar -xzf Python-2.7.18.tgz
    cd Python-2.7.18
    ./configure
    make
    cd ../src/scite/scintilla/gtk
    make
    cd ../../scite/gtk
    make -f makefile_custom_py
    sudo make -f makefile_custom_py install
    SciTE_with_python

<p>&nbsp;</p><a href="../README.md" style="color:black; text-decoration:underline">Back</a>
