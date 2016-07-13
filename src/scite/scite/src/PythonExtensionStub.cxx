// SciTE Python Extension
// Ben Fisher, 2016

#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "PythonExtensionStub.h"
#include "..\python\include\python.h"

#ifdef _MSC_VER
// allow deprecated stdio, for PyRun_SimpleFileEx
#pragma warning(disable: 4996)

// allow unreferenced parameter, for PyObject methods
#pragma warning(disable: 4100)
#endif

#ifdef _WIN32
#include <windows.h>
#endif

#define ENABLEDEBUGTRACE 1

// Holder for PyObject, to ensure Py_DECREF is called.
class CPyObjectOwned
{
private:
	PyObject* _obj;

public:
	CPyObjectOwned()
	{ 
		_obj = NULL;
	}
	CPyObjectOwned(PyObject* obj)
	{
		_obj = obj;
	}
	void Attach(PyObject* obj)
	{
		_obj = obj;
	}
	~CPyObjectOwned()
	{
		if (_obj)
		{
#pragma warning(push)
#pragma warning(disable: 4127)
			Py_DECREF(_obj);
#pragma warning(pop)
		}
	}
	operator PyObject*()
	{
		return _obj;
	}
};

// Holder for PyObject, when Py_DECREF isn't called, e.g. a borrowed reference.
class CPyObjectPtr
{
private:
	PyObject* _obj;

public:
	CPyObjectPtr(PyObject* obj)
	{
		_obj = obj;
	}
	~CPyObjectPtr()
	{
		// don't need to decref 
	}
	operator PyObject*()
	{
		return _obj;
	}
};

// on startup, import the python module scite_extend.py
static const char* c_PythonModuleName = "scite_extend";
int FindFriendlyNamedIDMConstant(const char* name);
bool GetPaneFromInt(int nPane, ExtensionAPI::Pane* outPane);
bool PullPythonArgument(IFaceType type, CPyObjectPtr pyObjNext, intptr_t* param);
bool PushPythonArgument(IFaceType type, intptr_t param, PyObject** pyValueOut);

void trace(const char* text1, const char* text2 = NULL);
void trace(const char* text1, const char* text2, int n);

bool RunCallback(
	const char* nameOfFunction, int nArgs=0, const char* arg1=0);
bool RunCallbackArgs(
	const char* nameOfFunction, PyObject* pArgsBorrowed);

PythonExtension::PythonExtension()
{
	_host = NULL;
	_pythonInitialized = false;
}

PythonExtension::~PythonExtension()
{
}

bool PythonExtension::FInitialized()
{
	return _pythonInitialized;
}

ExtensionAPI* PythonExtension::GetHost()
{
	return _host;
}

ExtensionAPI* Host()
{
	return PythonExtension::Instance().GetHost();
}

void PythonExtension::InitializePython()
{
	if (!_pythonInitialized)
	{
		// tell python to skip running 'import site'
		Py_NoSiteFlag = 1;
		Py_Initialize();
		SetupPythonNamespace();
		_pythonInitialized = true;
	}
}

PythonExtension& PythonExtension::Instance()
{
	static PythonExtension singleton;
	return singleton;
}

bool PythonExtension::Initialise(ExtensionAPI* host)
{
	WriteLog("log:PythonExtension::Initialise");
	_host = host;

	std::string delayLoadProp = _host->Property("ext.python.delayload");
	bool delayLoad = delayLoadProp.length() > 0 && delayLoadProp[0] != '0';

	if (!delayLoad)
	{
		InitializePython();
		RunCallback("OnStart");

#if 1
		// binary search requires items to be sorted, so verify sort order
		for (unsigned int i = 0; i < PythonExtension::constantsTableLen - 1; i++)
		{
			const char* first = PythonExtension::constantsTable[i].name;
			const char* second = PythonExtension::constantsTable[i + 1].name;
			if (strcmp(first, second) != -1)
			{
				trace("Warning, unsorted.");
				trace(first, second);
			}
		}
#endif
	}
	return true;
}

bool PythonExtension::Finalise() {
	_host = NULL;
	return false;
}

bool PythonExtension::Clear() {
	WriteLog("log:PythonExtension::Clear");
	return false;
}

bool PythonExtension::Load(const char *filename)
{
	FILE* f = fopen(filename, "r");
	if (f)
	{
		// Python will close the file handle
		int result = PyRun_SimpleFileEx(f, filename, 1);
		if (result == 0)
		{ 
			return true;
		}
		else 
		{
			PyErr_Print();
			return false; 
		}
	}
	else
	{
		_host->Trace(">Python: could not open file.\n");
		return false;
	}
}

bool PythonExtension::InitBuffer(int index) {
	WriteLog("log:PythonExtension::InitBuffer");
	return false;
}

bool PythonExtension::ActivateBuffer(int index) {
	WriteLog("log:PythonExtension::ActivateBuffer");
	return false;
}

bool PythonExtension::RemoveBuffer(int index) {
	WriteLog("log:PythonExtension::RemoveBuffer");
	return false;
}

bool PythonExtension::OnOpen(const char *filename) {
	return FInitialized() ?
		RunCallback("OnOpen", 1, filename) : false;
}

bool PythonExtension::OnSwitchFile(const char *filename) {
	return FInitialized() ?
		RunCallback("OnSwitchFile", 1, filename) : false;
}

bool PythonExtension::OnBeforeSave(const char *filename) {
	return FInitialized() ?
		RunCallback("OnBeforeSave", 1, filename) : false;
}

bool PythonExtension::OnSave(const char *filename) {
	return FInitialized() ?
		RunCallback("OnSave", 1, filename) : false;
}

bool PythonExtension::OnChar(char ch) {
	if (FInitialized())
	{
		CPyObjectOwned args = Py_BuildValue("(i)", (int)ch);
		return RunCallbackArgs("OnChar", args);
	}
	else
	{
		return false;
	}
}

bool PythonExtension::OnExecute(const char *cmd) {
	InitializePython();

	int result = PyRun_SimpleString(cmd);
	if (result != 0)
	{
		PyErr_Print();
	}
	
	// need to return true even on error
	return true;
}

bool PythonExtension::OnSavePointReached() {
	return FInitialized() ?
		RunCallback("OnSavePointReached") : false;
}

bool PythonExtension::OnSavePointLeft() {
	return FInitialized() ?
		RunCallback("OnSavePointLeft") : false;
}

bool PythonExtension::OnStyle(unsigned int p, int q, int r, StyleWriter *s) {
	WriteLog("log:PythonExtension::OnStyle");
	return false;
}

bool PythonExtension::OnDoubleClick() {
	return FInitialized() ?
		RunCallback("OnDoubleClick") : false;
}

bool PythonExtension::OnUpdateUI() {
	return false;
}

bool PythonExtension::OnMarginClick() {
	return FInitialized() ?
		RunCallback("OnMarginClick") : false;
}

bool PythonExtension::OnMacro(const char *, const char *) {
	WriteLog("log:PythonExtension::OnMacro");
	return false;
}

bool PythonExtension::OnUserListSelection(int type, const char *selection) {
	if (FInitialized())
	{
		CPyObjectOwned args = Py_BuildValue("(i,s)", type, selection);
		return RunCallbackArgs("OnUserListSelection", args);
	}
	else
	{
		return false;
	}
}

bool PythonExtension::SendProperty(const char *) {
	WriteLog("log:PythonExtension::SendProperty");
	return false;
}

bool PythonExtension::OnKey(int keyval, int modifiers) {
	if (FInitialized())
	{
		int fShift = (SCMOD_SHIFT & modifiers) != 0 ? 1 : 0;
		int fCtrl = (SCMOD_CTRL & modifiers) != 0 ? 1 : 0;
		int fAlt = (SCMOD_ALT & modifiers) != 0 ? 1 : 0;
		CPyObjectOwned args = Py_BuildValue("(i,i,i,i)",
			(int)keyval, fShift, fCtrl, fAlt);
		return RunCallbackArgs("OnKey", args);
	}
	else
	{
		return false;
	}
}

bool PythonExtension::OnDwellStart(int, const char *) {
	WriteLog("log:PythonExtension::OnDwellStart");
	return false;
}

bool PythonExtension::OnClose(const char *filename) {
	return FInitialized() ?
		RunCallback("OnClose", 1, filename) : false;
}

bool PythonExtension::OnUserStrip(int control, int change) {
	//for (int i = 0; i < extensionCount; ++i)
	//	extensions[i]->OnUserStrip(control, change);
	return false;
}

bool PythonExtension::NeedsOnClose()
{
	return false;
}

/*static*/ void PythonExtension::WriteText(const char* text)
{
	trace(text, "\n");
}

/*static*/ bool PythonExtension::WriteError(const char* error)
{
	trace(">Python Error:", error);
	trace("\n");
	return true;
}

/*static*/ bool PythonExtension::WriteError(const char* error, const char* error2)
{
	trace(">Python Error:", error);
	trace(" ", error2);
	trace("\n");
	return true;
}

/*static*/ void PythonExtension::WriteLog(const char* text)
{
#if ENABLEDEBUGTRACE
	trace(text, "\n");
#endif
}

void trace(const char* text1, const char* text2 /*=NULL*/)
{
	if (Host() && text1)
	{
		Host()->Trace(text1);
	}

	if (Host() && text2)
	{
		Host()->Trace(text2);
	}
}

void trace(const char* text1, const char* text2, int n)
{
	trace(text1, text2);
	char buf[256] = { 0 };
	int count = snprintf(buf, sizeof(buf), "%d", n);
	if (!(count > sizeof(buf) || count < 0))
	{
		Host()->Trace(buf);
	}
}

PyObject* pyfun_LogStdout(PyObject* self, PyObject* args)
{
	char* msg = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &msg)) 
	{
		if (Host())
		{
			trace(msg);
		}

		Py_INCREF(Py_None);
		return Py_None;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_app_SciteCommand(PyObject* self, PyObject* args)
{
	char* propName = NULL; // we don't own this.
	if (!PyArg_ParseTuple(args, "s", &propName))
	{
		return NULL;
	}

	int nFnIndex = FindFriendlyNamedIDMConstant(propName);
	if (nFnIndex == -1)
	{
		PyErr_SetString(PyExc_RuntimeError, "Could not find command.");
		return NULL;
	}

	IFaceConstant faceConstant = PythonExtension::constantsTable[nFnIndex];
	Host()->DoMenuCommand(faceConstant.value);
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* pyfun_app_UpdateStatusBar(PyObject* self, PyObject* args)
{
	PyObject * pyObjBoolUpdate = NULL;
	if (!PyArg_ParseTuple(args, "|O", &pyObjBoolUpdate))
	{
		return NULL;
	}

	bool bUpdateSlowData = pyObjBoolUpdate == Py_True;
	Host()->UpdateStatusBar(bUpdateSlowData);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef methodsExportedToPython[] =
{
	{"LogStdout", pyfun_LogStdout, METH_VARARGS, "Logs stdout"},
	{"app_UpdateStatusBar", pyfun_app_UpdateStatusBar, METH_VARARGS, ""},
	{"app_SciteCommand", pyfun_app_SciteCommand, METH_VARARGS, ""},
	
	// the match object, if it's needed at all, can be written in Python.
	{NULL, NULL, 0, NULL}
};

void PythonExtension::SetupPythonNamespace()
{
	// tell python to skip running 'import site'
	Py_NoSiteFlag = 1;
	Py_Initialize();
	
	CPyObjectPtr module = Py_InitModule("CScite", methodsExportedToPython);

	// PyRun_SimpleString does not handle errors well,
	// check return value and not ErrorsOccurred() or it might leave python in a weird state.
	int ret = PyRun_SimpleString(
		"import CScite\n"
		"import sys\n"
		"class StdoutCatcher:\n"
		"    def write(self, str):\n"
		"        CScite.LogStdout(str)\n"
		"sys.stdout = StdoutCatcher()\n"
		"sys.stderr = StdoutCatcher()\n"
	);

	if (ret != 0)
	{
		MessageBoxA(0, "Unexpected: error capturing stdout from Python. make sure python27.zip is present?", "", 0);
		PyErr_Print(); // if printing isn't set up, will not help, but at least will clear python's error bit
	}
}

bool PullPythonArgument(IFaceType type, CPyObjectPtr pyObjNext, intptr_t* param)
{
	if (!pyObjNext)
	{
		PyErr_SetString(PyExc_RuntimeError, "Unexpected: could not get next item.");
		return false;
	}

	switch (type) {
	case iface_void:
		break;
	case iface_int:
	case iface_length:
	case iface_position:
	case iface_colour:
	case iface_keymod:  
		// no urgent need to make keymods in c++, because AssignCmdKey / ClearCmdKey
		// are only ones using this... see py's makeKeyMod
		if (!PyInt_Check((PyObject*)pyObjNext))
		{
			PyErr_SetString(PyExc_RuntimeError, "Int expected.");
			return false;
		}

		*param = (intptr_t)PyInt_AsLong(pyObjNext);
		break;
	case iface_bool:
		if (!PyBool_Check((PyObject*)pyObjNext))
		{
			PyErr_SetString(PyExc_RuntimeError, "Bool expected.");
			return false;
		}
		*param = (pyObjNext == Py_True) ? 1 : 0;
		break;
	case iface_string:
	case iface_cells:
		if (!PyString_Check((PyObject*)pyObjNext))
		{
			PyErr_SetString(PyExc_RuntimeError, "String expected.");
			return false;
		}
		*param = (intptr_t)PyString_AsString(pyObjNext);
		break;
	case iface_textrange:
		PyErr_SetString(PyExc_RuntimeError,
			"raw textrange unsupported, but you can use CScite.Editor.Textrange(s,e)");
		return false;
		break;
	default:
		PyErr_SetString(PyExc_RuntimeError, "Unexpected: receiving unknown scintilla type.");
		return false;
	}
	return true;
}

// note: caller must incref pyValueOut.
bool PushPythonArgument(IFaceType type, intptr_t param, PyObject** pyValueOut)
{
	switch (type) {
	case iface_void:
		*pyValueOut = Py_None;
		break;
	case iface_int:
	case iface_length:
	case iface_position:
	case iface_colour:
		*pyValueOut = PyInt_FromLong((long)param);
		break;
	case iface_bool:
		*pyValueOut = param ? Py_True : Py_False;
		break;
	default:
		PyErr_SetString(PyExc_RuntimeError, "Unexpected: returning unknown scintilla type.");
		return false;
	}
	return true;
}

bool GetPaneFromInt(int nPane, ExtensionAPI::Pane* outPane)
{
	if (nPane == 0)
	{
		*outPane = ExtensionAPI::paneEditor;
		return true;
	}
	else if (nPane == 1)
	{
		*outPane = ExtensionAPI::paneOutput;
		return true;
	}
	else
	{
		PyErr_SetString(PyExc_RuntimeError, "Invalid pane, must be 0 or 1.");
		return false;
	}
}

bool RunCallback(
	const char* nameOfFunction, int nArgs, const char* arg1)
{
	if (nArgs == 0)
	{
		return RunCallbackArgs(nameOfFunction, NULL);
	}
	else if (nArgs == 1)
	{
		CPyObjectOwned args = Py_BuildValue("(s)", arg1);
		return RunCallbackArgs(nameOfFunction, args);
	}
	else
	{
		return PythonExtension::WriteError(
			"Unexpected: calling RunCallback, only 0/1 args supported.");
	}
}

bool RunCallbackArgs(
	const char* nameOfFunction, PyObject* pArgsBorrowed)
{
	CPyObjectOwned pName = PyString_FromString(c_PythonModuleName);
	if (!pName)
	{ 
		return PythonExtension::WriteError("Unexpected error: could not form string."); 
	}

	CPyObjectOwned pModule = PyImport_Import(pName);
	if (!pModule)
	{
		PythonExtension::WriteError("Error importing module.");
		PyErr_Print();
		return false;
	}

	CPyObjectPtr pDict = PyModule_GetDict(pModule);
	if (!pDict)
	{
		return PythonExtension::WriteError("Unexpected: could not get module dict.");
	}

	CPyObjectPtr pFn = PyDict_GetItemString(pDict, nameOfFunction);
	if (!pFn)
	{
		// module does not define that callback.
		return false;
	}

	if (!PyCallable_Check(pFn))
	{
		return PythonExtension::WriteError("callback not a function", nameOfFunction);
	}

	CPyObjectOwned pResult = PyObject_CallObject(pFn, pArgsBorrowed);
	if (!pResult)
	{
		PythonExtension::WriteError("Error in callback ", nameOfFunction);
		PyErr_Print();
		return false;
	}

	// bubble event up by default, unless they explicitly return false.
	bool shouldBubbleUpEvent = !(PyBool_Check(((PyObject*)pResult)) &&
		pResult == Py_False);
	return shouldBubbleUpEvent;
}

int FindFriendlyNamedIDMConstant(const char* name)
{
	// pattern from IFaceTable.cxx
	int lo = 0;
	int hi = PythonExtension::constantsTableLen - 1;
	do
	{
		int idx = (lo + hi) / 2;
		int cmp = strcmp(name, PythonExtension::constantsTable[idx].name);
		if (cmp > 0)
		{
			lo = idx + 1;
		}
		else if (cmp < 0)
		{
			hi = idx - 1;
		}
		else
		{
			return idx;
		}
	} while (lo <= hi);
	return -1;
}

static IFaceConstant rgFriendlyNamedIDMConstants[] = 
{
//++Autogenerated -- when new SciTE version is released, run archive/generate/constantsTable.py and paste the results here
	{"Abbrev", IDM_ABBREV},
	{"About", IDM_ABOUT},
	{"Activate", IDM_ACTIVATE},
	{"AllowAccess", IDM_ALLOWACCESS},
	{"BlockComment", IDM_BLOCK_COMMENT},
	{"BookmarkClearAll", IDM_BOOKMARK_CLEARALL},
	{"BookmarkNext", IDM_BOOKMARK_NEXT},
	{"BookmarkNextSelect", IDM_BOOKMARK_NEXT_SELECT},
	{"BookmarkPrev", IDM_BOOKMARK_PREV},
	{"BookmarkPrevSelect", IDM_BOOKMARK_PREV_SELECT},
	{"BookmarkToggle", IDM_BOOKMARK_TOGGLE},
	{"BoxComment", IDM_BOX_COMMENT},
	{"Buffer", IDM_BUFFER},
	{"BufferSep", IDM_BUFFERSEP},
	{"Build", IDM_BUILD},
	{"Clean", IDM_CLEAN},
	{"Clear", IDM_CLEAR},
	{"ClearOutput", IDM_CLEAROUTPUT},
	{"Close", IDM_CLOSE},
	{"CloseAll", IDM_CLOSEALL},
	{"Compile", IDM_COMPILE},
	{"Complete", IDM_COMPLETE},
	{"CompleteWord", IDM_COMPLETEWORD},
	{"Copy", IDM_COPY},
	{"CopyAsRtf", IDM_COPYASRTF},
	{"CopyPath", IDM_COPYPATH},
	{"Cut", IDM_CUT},
	{"DirectionDown", IDM_DIRECTIONDOWN},
	{"DirectionUp", IDM_DIRECTIONUP},
	{"Duplicate", IDM_DUPLICATE},
	{"EncodingDefault", IDM_ENCODING_DEFAULT},
	{"EncodingUCookie", IDM_ENCODING_UCOOKIE},
	{"EncodingUcs2be", IDM_ENCODING_UCS2BE},
	{"EncodingUcs2le", IDM_ENCODING_UCS2LE},
	{"EncodingUtf8", IDM_ENCODING_UTF8},
	{"EnterSelection", IDM_ENTERSELECTION},
	{"EolConvert", IDM_EOL_CONVERT},
	{"EolCr", IDM_EOL_CR},
	{"EolCrlf", IDM_EOL_CRLF},
	{"EolLf", IDM_EOL_LF},
	{"Expand", IDM_EXPAND},
	{"ExpandEnsureChildrenVisible", IDM_EXPAND_ENSURECHILDRENVISIBLE},
	{"Filer", IDM_FILER},
	{"Find", IDM_FIND},
	{"FindInFiles", IDM_FINDINFILES},
	{"FindNext", IDM_FINDNEXT},
	{"FindNextBack", IDM_FINDNEXTBACK},
	{"FindNextBackSel", IDM_FINDNEXTBACKSEL},
	{"FindNextSel", IDM_FINDNEXTSEL},
	{"FinishedExecute", IDM_FINISHEDEXECUTE},
	{"FoldMargin", IDM_FOLDMARGIN},
	{"FullScreen", IDM_FULLSCREEN},
	{"Go", IDM_GO},
	{"Goto", IDM_GOTO},
	{"Help", IDM_HELP},
	{"HelpScite", IDM_HELP_SCITE},
	{"Import", IDM_IMPORT},
	{"IncrementalSearch", IDM_INCSEARCH},
	{"InsAbbrev", IDM_INS_ABBREV},
	{"Join", IDM_JOIN},
	{"Language", IDM_LANGUAGE},
	{"LineNumberMargin", IDM_LINENUMBERMARGIN},
	{"LoadSession", IDM_LOADSESSION},
	{"LowerCase", IDM_LWRCASE},
	{"MacroList", IDM_MACROLIST},
	{"MacroPlay", IDM_MACROPLAY},
	{"MacroRecord", IDM_MACRORECORD},
	{"MacroSep", IDM_MACRO_SEP},
	{"MacroStopRecord", IDM_MACROSTOPRECORD},
	{"MatchBrace", IDM_MATCHBRACE},
	{"MatchCase", IDM_MATCHCASE},
	{"MonoFont", IDM_MONOFONT},
	{"MoveTabLeft", IDM_MOVETABLEFT},
	{"MoveTabRight", IDM_MOVETABRIGHT},
	{"MruFile", IDM_MRUFILE},
	{"MruSep", IDM_MRU_SEP},
	{"MruSub", IDM_MRU_SUB},
	{"New", IDM_NEW},
	{"NextFile", IDM_NEXTFILE},
	{"NextFileStack", IDM_NEXTFILESTACK},
	{"NextMatchPpc", IDM_NEXTMATCHPPC},
	{"NextMsg", IDM_NEXTMSG},
	{"OnTop", IDM_ONTOP},
	{"Open", IDM_OPEN},
	{"OpenAbbrevProperties", IDM_OPENABBREVPROPERTIES},
	{"OpenDirectoryProperties", IDM_OPENDIRECTORYPROPERTIES},
	{"OpenFilesHere", IDM_OPENFILESHERE},
	{"OpenGlobalProperties", IDM_OPENGLOBALPROPERTIES},
	{"OpenLocalProperties", IDM_OPENLOCALPROPERTIES},
	{"OpenLuaExternalfile", IDM_OPENLUAEXTERNALFILE},
	{"OpenSelected", IDM_OPENSELECTED},
	{"OpenUserProperties", IDM_OPENUSERPROPERTIES},
	{"Paste", IDM_PASTE},
	{"PasteAndDown", IDM_PASTEANDDOWN},
	{"PrevFile", IDM_PREVFILE},
	{"PrevFileStack", IDM_PREVFILESTACK},
	{"PrevMatchPpc", IDM_PREVMATCHPPC},
	{"PrevMsg", IDM_PREVMSG},
	{"Print", IDM_PRINT},
	{"PrintSetup", IDM_PRINTSETUP},
	{"Quit", IDM_QUIT},
	{"ReadOnly", IDM_READONLY},
	{"Redo", IDM_REDO},
	{"Regexp", IDM_REGEXP},
	{"Replace", IDM_REPLACE},
	{"Revert", IDM_REVERT},
	{"RunWin", IDM_RUNWIN},
	{"Save", IDM_SAVE},
	{"SaveACopy", IDM_SAVEACOPY},
	{"SaveAll", IDM_SAVEALL},
	{"SaveAs", IDM_SAVEAS},
	{"SaveAsHtml", IDM_SAVEASHTML},
	{"SaveAsPdf", IDM_SAVEASPDF},
	{"SaveAsRtf", IDM_SAVEASRTF},
	{"SaveAsTex", IDM_SAVEASTEX},
	{"SaveAsXml", IDM_SAVEASXML},
	{"SaveSession", IDM_SAVESESSION},
	{"SelMargin", IDM_SELMARGIN},
	{"SelectAll", IDM_SELECTALL},
	{"SelectToBrace", IDM_SELECTTOBRACE},
	{"SelectToNextMatchPpc", IDM_SELECTTONEXTMATCHPPC},
	{"SelectToPrevMatchPpc", IDM_SELECTTOPREVMATCHPPC},
	{"SelectionAddEach", IDM_SELECTIONADDEACH},
	{"SelectionAddNext", IDM_SELECTIONADDNEXT},
	{"SelectionForFind", IDM_SELECTION_FOR_FIND},
	{"ShowCalltip", IDM_SHOWCALLTIP},
	{"Split", IDM_SPLIT},
	{"SplitVertical", IDM_SPLITVERTICAL},
	{"SrcWin", IDM_SRCWIN},
	{"StatusWin", IDM_STATUSWIN},
	{"StopExecute", IDM_STOPEXECUTE},
	{"StreamComment", IDM_STREAM_COMMENT},
	{"SwitchPane", IDM_SWITCHPANE},
	{"TabSize", IDM_TABSIZE},
	{"TabWin", IDM_TABWIN},
	{"ToggleFoldAll", IDM_TOGGLE_FOLDALL},
	{"ToggleFoldRecursive", IDM_TOGGLE_FOLDRECURSIVE},
	{"ToggleOutput", IDM_TOGGLEOUTPUT},
	{"ToggleParameters", IDM_TOGGLEPARAMETERS},
	{"ToolWin", IDM_TOOLWIN},
	{"Tools", IDM_TOOLS},
	{"Undo", IDM_UNDO},
	{"Unslash", IDM_UNSLASH},
	{"UpperCase", IDM_UPRCASE},
	{"ViewEol", IDM_VIEWEOL},
	{"ViewGuides", IDM_VIEWGUIDES},
	{"ViewSpace", IDM_VIEWSPACE},
	{"ViewStatusBar", IDM_VIEWSTATUSBAR},
	{"ViewTabBar", IDM_VIEWTABBAR},
	{"ViewToolbar", IDM_VIEWTOOLBAR},
	{"WholeWord", IDM_WHOLEWORD},
	{"Wrap", IDM_WRAP},
	{"WrapAround", IDM_WRAPAROUND},
	{"WrapOutput", IDM_WRAPOUTPUT},
//--Autogenerated -- end of automatically generated section
};

const IFaceConstant* const PythonExtension::constantsTable = rgFriendlyNamedIDMConstants;
const size_t PythonExtension::constantsTableLen = _countof(rgFriendlyNamedIDMConstants);

