
# use with nmake, nmake -f wincommondialog.mak all

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

# $< apparently gets expanded to .\*.cpp
# /EHsc for exception handling
# /Fe - to define binary output destination directory
# /I - to provide path to header file(s)
{$(DIR_SRC)}.cpp{$(DIR_INTERMEDIATE_X86)}.obj ::
        @echo Compiling...
 cl /c /EHsc /Fo$(DIR_INTERMEDIATE_X86)\ /I$(DIR_INCLUDE) $<

$(EXECUTABLE_NAME) : $(DIR_INTERMEDIATE_X86)\*.obj
   @echo Linking $(EXECUTABLE_NAME)...
   link /out:$(DIR_BIN_X86)\$(EXECUTABLE_NAME) $(DIR_INTERMEDIATE_X86)\*.obj

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


