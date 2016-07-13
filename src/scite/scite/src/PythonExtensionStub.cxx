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

	//char* delayLoadProp = _host->Property("ext.python.delayload");
	//bool delayLoad = delayLoadProp && delayLoadProp[0] != '\0' &&
	//	delayLoadProp[0] != '0';
	bool delayLoad = false;

	if (!delayLoad)
	{
		InitializePython();
		RunCallback("OnStart");

//#if _DEBUG
//		// binary search requires items to be sorted, so verify sort order
//		for (unsigned int i = 0; i < PythonExtension::constantsTableLen - 1; i++)
//		{
//			const char* first = PythonExtension::constantsTable[i].name;
//			const char* second = PythonExtension::constantsTable[i + 1].name;
//			if (strcmp(first, second) != -1)
//			{
//				trace("Warning, unsorted.");
//				trace(first, second);
//			}
//		}
//#endif
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
	return FInitialized() ?
		RunCallback("OnLoad", 1, filename) : false;
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
	WriteLog("log:PythonExtension::OnExecute");
	return false;
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

static PyMethodDef methods_LogStdout[] =
{
	{"LogStdout", pyfun_LogStdout, METH_VARARGS, "Logs stdout"},
	
	// the match object, if it's needed at all, can be written in Python.
	{NULL, NULL, 0, NULL}
};

void PythonExtension::SetupPythonNamespace()
{
	MessageBoxA(0, "attach", "", 0);
	
	// tell python to skip running 'import site'
	Py_NoSiteFlag = 1;
	Py_Initialize();
	
	CPyObjectPtr module = Py_InitModule("CScite", methods_LogStdout);

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
		return;
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
