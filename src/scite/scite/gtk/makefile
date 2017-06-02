# Make file for SciTE on Linux or compatible OS
# Copyright 1998-2010 by Neil Hodgson <neilh@scintilla.org>
# The License.txt file describes the conditions under which this software may be distributed.
# This makefile assumes GCC 4.x is used and changes will be needed to use other compilers.
# GNU make does not like \r\n line endings so should be saved to CVS in binary form.

.SUFFIXES: .cxx .o .h .a .c
ifdef CLANG
# Can choose aspect to sanitize: address and undefined can simply change SANITIZE but for
# thread also need to create Position Independent Executable -> search online documentation
SANITIZE = address
#SANITIZE = undefined
CXX = clang++ -fsanitize=$(SANITIZE) -Wno-deprecated-register
CC = clang -fsanitize=$(SANITIZE) -Wno-empty-body
endif

ifdef GTK3
GTKVERSION=gtk+-3.0
else
GTKVERSION=gtk+-2.0
endif

# For the Gnome desktop stuff to work, prefix must point to where Gnome thinks it is.
CONFIGFLAGS:=$(shell pkg-config --cflags $(GTKVERSION))
CONFIGLIB:=$(shell pkg-config --libs $(GTKVERSION) gthread-2.0 gmodule-no-export-2.0)
CONFIGTHREADS:=
gnomeprefix:=$(shell pkg-config --variable=prefix $(GTKVERSION) 2>/dev/null)
ifndef prefix
ifdef gnomeprefix
  prefix=$(gnomeprefix)
else
  prefix=/usr
endif
endif
datadir=$(prefix)/share
pixmapdir=$(datadir)/pixmaps
bindir=$(prefix)/bin
SYSCONF_PATH=$(prefix)/share/scite_with_python

INSTALL=install

PROG	= ../bin/SciTE_with_python

all: $(PROG)

vpath %.h ../src ../../scintilla/include
vpath %.cxx ../src

INCLUDEDIRS=-I ../../scintilla/include -I ../src
ifdef CHECK_DEPRECATED
DEPRECATED=-DGDK_PIXBUF_DISABLE_DEPRECATED -DGDK_DISABLE_DEPRECATED -DGTK_DISABLE_DEPRECATED
endif
CXXBASEFLAGS=-W -Wall -pedantic -DGTK -DSCI_LEXER -DPIXMAP_PATH=\"$(pixmapdir)\" -DSYSCONF_PATH=\"$(SYSCONF_PATH)\" $(INCLUDEDIRS) $(DEPRECATED)

ifdef DEBUG
CXXTFLAGS=-DDEBUG -g $(CXXBASEFLAGS)
else
CXXTFLAGS=-DNDEBUG -Os $(CXXBASEFLAGS)
endif

ifndef NO_PYTHON
PY_OBJS = PythonExtension.o
PY_LIBS = -lpython2.7
INCLUDEDIRS=-I ../../scintilla/include -I ../src -I /usr/include/python2.7
endif

ifdef INCLUDE_LUA
LUA_CORE_OBJS = lapi.o lcode.o ldebug.o ldo.o ldump.o lfunc.o lgc.o llex.o \
		lmem.o lobject.o lopcodes.o lparser.o lstate.o lstring.o \
		ltable.o ltm.o lundump.o lvm.o lzio.o

LUA_LIB_OBJS =	lauxlib.o lbaselib.o ldblib.o liolib.o lmathlib.o ltablib.o \
		lstrlib.o loadlib.o loslib.o linit.o

LUA_OBJS = LuaExtension.o $(LUA_CORE_OBJS) $(LUA_LIB_OBJS)

vpath %.c ../lua/src ../lua/src/lib

INCLUDEDIRS=-I ../../scintilla/include -I ../src -I../lua/include

.c.o:
	$(CC) $(CFLAGS) $(INCLUDEDIRS) -DLUA_USE_POSIX $(CXXTFLAGS) -c $< -o $@

else
CXXTFLAGS+=-DNO_LUA
endif

CXXTFLAGS:=$(CXXTFLAGS)

UNAME:=$(shell uname -s)
ifeq ($(UNAME), Linux)
LIBDL:=-ldl
endif
ifneq (,$(findstring GNU,$(UNAME)))
LIBDL:=-ldl
endif
ifeq ($(UNAME), Darwin)
CXXTFLAGS:=$(CXXTFLAGS) -Dunix
endif

.cxx.o:
	$(CXX) --std=c++0x $(CONFIGFLAGS) $(CXXTFLAGS) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f *.o *.plist $(PROG)

analyze:
	clang --analyze $(CONFIGFLAGS) $(CXXTFLAGS) $(CXXFLAGS) *.cxx ../src/*.cxx
	# Could analyze Lua implementation as well but won't be fixing the warnings so its just noise
	#clang --analyze $(CONFIGFLAGS) $(CXXTFLAGS) $(CXXFLAGS) *.cxx ../src/*.cxx ../lua/src/*.c ../lua/src/lib/*.c

deps:
	$(CXX) -MM $(CONFIGFLAGS) $(CXXTFLAGS) *.cxx ../src/*.cxx | sed -e 's/\/usr.* //' | grep [a-zA-Z] >deps.mak

# make should be run in ../../scintilla/gtk to compile all the lexers.
COMPLIB=../../scintilla/bin/scintilla.a

$(PROG): SciTEGTK.o GUIGTK.o Widget.o \
FilePath.o SciTEBase.o FileWorker.o Cookie.o Credits.o SciTEBuffers.o SciTEIO.o StringList.o \
ExportHTML.o ExportPDF.o ExportRTF.o ExportTEX.o ExportXML.o \
MatchMarker.o StringHelpers.o \
PropSetFile.o MultiplexExtension.o DirectorExtension.o SciTEProps.o StyleDefinition.o StyleWriter.o Utf8_16.o \
	JobQueue.o GTKMutex.o IFaceTable.o $(COMPLIB) $(LUA_OBJS) $(PY_OBJS) $(PY_LIBS)
	$(CXX) `$(CONFIGTHREADS)` -rdynamic -Wl,--as-needed -Wl,--version-script lua.vers -DGTK $^ -o $@ $(CONFIGLIB) $(LIBDL) -lm -lstdc++

# Automatically generate header dependencies with "make deps"
include deps.mak

# The two last install commands will fail if Gnome is not installed or is not at $(prefix).
# This is OK - just means no SciTE in the Gnome Applications menu
install:
	$(INSTALL) -m 755 -d $(DESTDIR)$(bindir) $(DESTDIR)$(SYSCONF_PATH)

	$(INSTALL) -m 755 $(PROG) $(DESTDIR)$(bindir)

	cp -r ../bin/doc $(DESTDIR)$(SYSCONF_PATH)/doc
	chmod -R 0644 $(DESTDIR)$(SYSCONF_PATH)/doc
	cp -r ../bin/properties $(DESTDIR)$(SYSCONF_PATH)/properties
	chmod -R 0644 $(DESTDIR)$(SYSCONF_PATH)/properties
	cp -r ../bin/tools_external $(DESTDIR)$(SYSCONF_PATH)/tools_external
	chmod -R 0644 $(DESTDIR)$(SYSCONF_PATH)/tools_external
	cp -r ../bin/tools_internal $(DESTDIR)$(SYSCONF_PATH)/tools_internal
	chmod -R 0644 $(DESTDIR)$(SYSCONF_PATH)/tools_internal
	
	for files in ../bin/*.py ../bin/*.zip; \
	do \
		$(INSTALL) -m 644 $$files $(DESTDIR)$(SYSCONF_PATH); \
	done
	
	# set directories to 755 to allow access
	find $(DESTDIR)$(SYSCONF_PATH) -type d -exec chmod 755 {} \;

ifdef gnomeprefix
	$(INSTALL) -m 755 -d $(DESTDIR)$(datadir)/applications $(DESTDIR)$(pixmapdir)
	$(INSTALL) -m 755 SciTE_with_python.desktop $(DESTDIR)$(datadir)/applications/SciTE_with_python.desktop
	$(INSTALL) -m 644 Sci48Mpy.png $(DESTDIR)$(pixmapdir)/Sci48Mpy.png
endif

uninstall:
	rm -f $(DESTDIR)$(bindir)/SciTE_with_python
	rm -rf $(DESTDIR)$(SYSCONF_PATH)
ifdef gnomeprefix
	rm -f $(DESTDIR)$(datadir)/applications/SciTE_with_python.desktop
	rm -f $(DESTDIR)$(pixmapdir)/Sci48Mpy.png
endif
