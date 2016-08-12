# scite-with-python
SciTE with Python extensibility

Building in Linux

~~~~
# install prereqs
sudo apt-get install libgtk2.0-dev
sudo apt-get install python2.7-dev

# build scintilla and scite
mkdir ~/scite-with-python
cd ~/scite-with-python
git clone https://github.com/downpoured/scite-with-python.git
cd scite-with-python/src/scite/scintilla/gtk
make
cd ../../scite/gtk
make
sudo make install

# run scite
/usr/bin/SciTE_with_python
~~~~
