
# use with nmake, nmake -f wincommondialog.mak

# set variables
EXECUTABLE_NAME = wincommondialog.exe
DIR_SRC = .
DIR_INCLUDE = ..\include
DIR_BIN = .\bin
DIR_BIN_X86 = $(DIR_BIN)\x86
DIR_INTERMEDIATE = .\intermediate
DIR_INTERMEDIATE_X86 = $(DIR_INTERMEDIATE)\x86

SRC_FILES= \
  $(DIR_SRC)\main.cpp \
  $(DIR_SRC)\printx.cpp

# description block
# /EHsc for exception handling
# /Fe - to define binary output destination directory
# /I - to provide path to header file(s)
$(EXECUTABLE_NAME) : $(SRC_FILES)
  cl /EHsc /Fe$(DIR_BIN_X86)\$(EXECUTABLE_NAME) /I$(DIR_INCLUDE) $(SRC_FILES)
  copy *.obj $(DIR_INTERMEDIATE_X86)
  del *.obj

# build application
wincommondialog: $(EXECUTABLE_NAME)

# create output directories
create_dirs:
 @if not exist $(DIR_BIN_X86) mkdir $(DIR_BIN_X86)
 @if not exist $(DIR_INTERMEDIATE_X86) mkdir $(DIR_INTERMEDIATE_X86)

# delete output directories
clean:
 @if exist $(DIR_BIN) rmdir /S /Q $(DIR_BIN)
 @if exist $(DIR_INTERMEDIATE) rmdir /S /Q $(DIR_INTERMEDIATE)

# create directories and build application
all: clean create_dirs wincommondialog

