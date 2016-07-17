
# use with nmake, nmake -f wincommondialog.mak all

# set variables
EXECUTABLE_NAME = wincommondialog.exe
DIR_SRC = .
DIR_INCLUDE = ..\include
DIR_BIN = .\bin
DIR_BIN_X86 = $(DIR_BIN)\x86
DIR_INTERMEDIATE = .\obj
DIR_INTERMEDIATE_X86 = $(DIR_INTERMEDIATE)\x86


# prob not needed
# /analyze-
# /Fd"Release\vc140.pdb"
# /errorReport:prompt
# /Fp"Release\WinCommonDialog.pch" 
# /Fo"Release\" 
# /Fa"Release\"
# /Zi makes a pdb
# /Zc:inline removes certain unused data 
# /Zc:inline
  
# linker try without
# /MANIFEST
# /PDB:"Release\WinCommonDialog.pdb"
# /DEBUG
# /PGD:"Release\WinCommonDialog.pgd"
# /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /ManifestFile:"Release\WinCommonDialog.exe.intermediate.manifest"
# /ERRORREPORT:PROMPT
  

# /GS Buffer Security Check
# /Zc:wchar_t means to add wchar_t as a built-in type 
# /Zc:forScope Force Conformance in for Loop Scope
# /Gm- means to disable Minimal Rebuild
# /O2 optimize for speed
# /fp:precise, use precise floating point
# /Gd use cdecl (default)
# /Oy- don't omit frame pointer
# /MT: multithread, static runtime library
COMPILERFLAGS=/GS  /Zc:wchar_t    /Zc:forScope  /Gm- /O2  /fp:precise /Gd /Oy- /MT

# warning level 3
# treat warnings as errors
WARNINGS= /W3 /WX
ADD_PREPROCESSOR_DEFINES=/D "WIN32" /D "NDEBUG" /D "_CONSOLE" /D "_UNICODE" /D "UNICODE"

# /EHsc for exception handling
# /Fe - to define binary output destination directory
# /I - to provide path to header file(s)
ALLCOMPILERFLAGS=/c /EHsc $(COMPILERFLAGS) $(WARNINGS) $(ADD_PREPROCESSOR_DEFINES)

# /OPT:REF eliminates functions and data that are never referenced
# /OPT:ICF  perform identical COMDAT folding
# /SAFESEH contains a table of safe exception handlers.
# /TLBID sets TypeLib id
LINKERFLAGS=/INCREMENTAL:NO /DYNAMICBASE:NO /MACHINE:X86 /OPT:REF /OPT:ICF /SAFESEH /TLBID:1 
LINKERLIBS="Winmm.lib" "kernel32.lib" "user32.lib" "gdi32.lib" "winspool.lib" "comdlg32.lib" "advapi32.lib" "shell32.lib" "ole32.lib" "oleaut32.lib" "uuid.lib" "odbc32.lib" "odbccp32.lib"

# specify console app
# include compiled resources
ALLLINKERFLAGS=/SUBSYSTEM:CONSOLE $(DIR_INTERMEDIATE)\wcdresources.res $(LINKERLIBS) $(LINKERFLAGS)


#  /l 409 means LANG_ENGLISH,SUBLANG_ENGLISH_US
#  /fo$@  creates a .RES file named resname using script-file.
RESCOMPILERFLAGS=/D "_UNICODE" /D "UNICODE" /l 0x0409 

wcdresources.res: wcdresources.rc
	$(RC) $(RESCOMPILERFLAGS) /fo$(DIR_INTERMEDIATE)\wcdresources.res wcdresources.rc

# $< apparently gets expanded to .\*.cpp
{$(DIR_SRC)}.cpp{$(DIR_INTERMEDIATE_X86)}.obj ::
	@echo Compiling...
	cl $(ALLCOMPILERFLAGS) /Fo$(DIR_INTERMEDIATE_X86)\ /I$(DIR_INCLUDE) $<

$(EXECUTABLE_NAME) : $(DIR_INTERMEDIATE_X86)\*.obj
	@echo Linking $(EXECUTABLE_NAME)...
	link $(ALLLINKERFLAGS) /out:$(DIR_BIN_X86)\$(EXECUTABLE_NAME) $(DIR_INTERMEDIATE_X86)\*.obj

# build application
wincommondialog: $(EXECUTABLE_NAME)

# create output directories
create_dirs:
 @if not exist $(DIR_BIN_X86) mkdir $(DIR_BIN_X86)
 @if not exist $(DIR_INTERMEDIATE_X86) mkdir $(DIR_INTERMEDIATE_X86)

# delete output directories
clean:
 @if exist $(DIR_BIN_X86)\*.exe del $(DIR_BIN_X86)\*.exe 
 @if exist $(DIR_BIN_X86)\*.pdb del $(DIR_BIN_X86)\*.pdb 
 @if exist $(DIR_BIN_X86)\*.manifest del $(DIR_BIN_X86)\*.manifest 
 @if exist $(DIR_INTERMEDIATE)\*.res del $(DIR_INTERMEDIATE)\*.res
 @if exist $(DIR_INTERMEDIATE_X86)\*.obj del $(DIR_INTERMEDIATE_X86)\*.obj

# create directories and build application
all: clean create_dirs wcdresources.res wincommondialog


