// SciTE Python Extension
// Ben Fisher, 2011

#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "PythonExtension.h"

#ifdef _MSC_VER
// allow deprecated stdio, for PyRun_SimpleFileEx
#pragma warning(disable: 4996)

// allow unreferenced parameter, for PyObject methods
#pragma warning(disable: 4100)
#endif

#ifdef _WIN32
#include <windows.h>
#endif

#define ENABLEDEBUGTRACE 0

// on startup, import the python module scite_extend.py
static const char* c_PythonModuleName = "scite_extend";
int FindFriendlyNamedIDMConstant(const char* name);
bool GetPaneFromInt(int nPane, ExtensionAPI::Pane* outPane);
bool PullPythonArgument(IFaceType type, CPyObjectPtr pyObjNext, intptr_t* param);
bool PushPythonArgument(IFaceType type, intptr_t param, PyObject** pyValueOut);
void trace(const char* text1, const char* text2 = NULL);
void trace(const char* text1, const char* text2, int n);

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

	char* delayLoadProp = _host->Property("ext.python.delayload");
	bool delayLoad = delayLoadProp && delayLoadProp[0] != '\0' &&
		delayLoadProp[0] != '0';

	if (!delayLoad)
	{
		InitializePython();
		RunCallback("OnStart", 0, NULL);

#if _DEBUG
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

bool PythonExtension::OnExecute(const char* s)
{
	InitializePython();

	int result = PyRun_SimpleString(s);
	if (nResult != 0)
	{
		PyErr_Print();
	}
	
	// need to return true even on error
	return true;
}

bool PythonExtension::Finalise()
{
	// _host is no longer valid
	_host = NULL;
	return false;
}

bool PythonExtension::Clear()
{
	WriteLog("log:PythonExtension::Clear");
	return false;
}

bool PythonExtension::Load(const char* fileName)
{
	FILE* f = fopen(fileName, "r");
	if (f)
	{
		// Python will close the file handle
		int result = PyRun_SimpleFileEx(f, fileName, 1);
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

bool PythonExtension::InitBuffer(int index)
{
	WriteLog("log:PythonExtension::InitBuffer");
	return false;
}

bool PythonExtension::ActivateBuffer(int index)
{
	WriteLog("log:PythonExtension::Activatebuffer");
	return false;
}

bool PythonExtension::RemoveBuffer(int index)
{
	WriteLog("log:PythonExtension::removebuffer");
	return false;
}

void PythonExtension::WriteText(const char* text)
{
	trace(text, "\n");
}

bool PythonExtension::WriteError(const char* error)
{
	trace(">Python Error:", error);
	trace("\n");
	return true;
}

bool PythonExtension::WriteError(const char* error, const char* error2)
{
	trace(">Python Error:", error);
	trace(" ", error2);
	trace("\n");
	return true;
}

void PythonExtension::WriteLog(const char* text)
{
#if ENABLEDEBUGTRACE
	trace(text, "\n");
#endif
}

bool PythonExtension::OnOpen(const char *fileName)
{
	return FInitialized() ?
		RunCallback("OnOpen", 1, fileName) : false;
}

bool PythonExtension::OnClose(const char *fileName)
{
	return FInitialized() ?
		RunCallback("OnClose", 1, fileName) : false;
}

bool PythonExtension::OnSwitchFile(const char *fileName)
{
	return FInitialized() ?
		RunCallback("OnSwitchFile", 1, fileName) : false;
}

bool PythonExtension::OnBeforeSave(const char *fileName)
{
	return FInitialized() ?
		RunCallback("OnBeforeSave", 1, fileName) : false;
}

bool PythonExtension::OnSave(const char *fileName)
{
	return FInitialized() ?
		RunCallback("OnSave", 1, fileName) : false;
}

bool PythonExtension::OnSavePointReached()
{
	return FInitialized() ?
		RunCallback("OnSavePointReached", 0, NULL) : false;
}

bool PythonExtension::OnSavePointLeft()
{
	return FInitialized() ?
		RunCallback("OnSavePointLeft", 0, NULL) : false;
}

bool PythonExtension::OnChar(char ch)
{
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

bool PythonExtension::OnKey(int keycode, int modifiers)
{
	if (FInitialized())
	{
		int fShift = (SCMOD_SHIFT & modifiers) != 0 ? 1 : 0;
		int fCtrl = (SCMOD_CTRL & modifiers) != 0 ? 1 : 0;
		int fAlt = (SCMOD_ALT & modifiers) != 0 ? 1 : 0;
		CPyObjectOwned args = Py_BuildValue("(i,i,i,i)",
			(int)keycode, fShift, fCtrl, fAlt);
		return RunCallbackArgs("OnKey", args);
	}
	else
	{
		return false;
	}
}

bool PythonExtension::OnDoubleClick()
{
	return FInitialized() ?
		RunCallback("OnDoubleClick", 0, NULL) : false;
}

bool PythonExtension::OnMarginClick()
{
	return FInitialized() ?
		RunCallback("OnMarginClick", 0, NULL) : false;
}

bool PythonExtension::OnDwellStart(int pos, const char *word)
{
	if (FInitialized())
	{
		if (pos == 0 && word[0] == 0)
		{
			return RunCallback("OnDwellEnd", 0, NULL);
		}
		else
		{
			CPyObjectOwned args = Py_BuildValue("(i,s)", pos, word);
			return RunCallbackArgs("OnDwellStart", args);
		}
	}
	else
	{
		return false;
	}
}

bool PythonExtension::OnUserListSelection(int type, const char* selection)
{
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

bool PythonExtension::RunCallback(
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
		return WriteError(
			"Unexpected: calling RunCallback, only 0/1 args supported.");
	}
}

bool PythonExtension::RunCallbackArgs(
	const char* nameOfFunction, PyObject* pArgsBorrowed)
{
	CPyObjectOwned pName = PyString_FromString(c_PythonModuleName);
	if (!pName)
	{ 
		return WriteError("Unexpected error: could not form string."); 
	}

	CPyObjectOwned pModule = PyImport_Import(pName);
	if (!pModule)
	{
		WriteError("Error importing module.");
		PyErr_Print();
		return false;
	}

	CPyObjectPtr pDict = PyModule_GetDict(pModule);
	if (!pDict)
	{
		return WriteError("Unexpected: could not get module dict.");
	}

	CPyObjectPtr pFn = PyDict_GetItemString(pDict, nameOfFunction);
	if (!pFn)
	{
		// module does not define that callback.
		return false;
	}

	if (!PyCallable_Check(pFn))
	{
		return WriteError("callback not a function", nameOfFunction);
	}

	CPyObjectOwned pResult = PyObject_CallObject(pFn, pArgsBorrowed);
	if (!pResult)
	{
		WriteError("Error in callback ", nameOfFunction);
		PyErr_Print();
		return false;
	}

	// bubble event up by default, unless they explicitly return false.
	bool shouldBubbleUpEvent = !(PyBool_Check(((PyObject*)pResult)) &&
		pResult == Py_False);
	return shouldBubbleUpEvent;
}

PyObject* pyfun_LogStdout(PyObject* self, PyObject* args)
{
	char* msg = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &msg)) 
	{
		Host()->Trace(msg);
		Py_INCREF(Py_None);
		return Py_None;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_MessageBox(PyObject* self, PyObject* args)
{
	char* msg = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &msg))
	{
#ifdef _WIN32
		MessageBoxA(NULL, msg, "SciTEPython", 0);
#endif
		Py_INCREF(Py_None);
		return Py_None;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_SciteOpenFile(PyObject* self, PyObject* args)
{
	char* filename = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &filename) && filename)
	{
		SString cmd = "open:";
		cmd += filename;
		cmd.substitute("\\", "\\\\");
		Host()->Perform(cmd.c_str());
		Py_INCREF(Py_None);
		return Py_None;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_GetProperty(PyObject* self, PyObject* args)
{
	char* propName = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &propName))
	{
		char* value = Host()->Property(propName);
		if (value)
		{
			// give the caller ownership of this object.
			CPyObjectPtr pythonStr = PyString_FromString(value);
			delete[] value;
			return pythonStr;
		}
		else
		{
			Py_INCREF(Py_None);
			return Py_None;
		}
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_SetProperty(PyObject* self, PyObject* args)
{
	char* propName = NULL; // we don't own this.
	char* propValue = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "ss", &propName, &propValue))
	{
		// it looks like SetProperty allocates, it's ok if key and val go out of scope.
		Host()->SetProperty(propName, propValue);
		Py_INCREF(Py_None);
		return Py_None;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_UnsetProperty(PyObject* self, PyObject* args)
{
	char* propName = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &propName))
	{
		Host()->UnsetProperty(propName);
		Py_INCREF(Py_None);
		return Py_None;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_pane_Append(PyObject* self, PyObject* args)
{
	char* text = NULL; // we don't own this.
	int nPane = -1;
	ExtensionAPI::Pane pane;
	if (PyArg_ParseTuple(args, "is", &nPane, &text) &&
		GetPaneFromInt(nPane, &pane))
	{
		Host()->Insert(pane, Host()->Send(pane, SCI_GETLENGTH, 0, 0), text);
		Py_INCREF(Py_None);
		return Py_None;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_pane_Insert(PyObject* self, PyObject* args)
{
	char* text = NULL; // we don't own this.
	int nPane = -1, nPos = -1;
	ExtensionAPI::Pane pane;
	if (PyArg_ParseTuple(args, "iis", &nPane, &nPos, &text) &&
		nPos >= 0 &&
		GetPaneFromInt(nPane, &pane))
	{
		Host()->Insert(pane, nPos, text);
		Py_INCREF(Py_None);
		return Py_None;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_pane_Remove(PyObject* self, PyObject* args)
{
	int nPane = -1, nPosStart = -1, nPosEnd = -1;
	ExtensionAPI::Pane pane;
	if (!PyArg_ParseTuple(args, "iii", &nPane, &nPosStart, &nPosEnd) &&
		!(nPosStart < 0 || nPosEnd < 0) &&
		(GetPaneFromInt(nPane, &pane)))
	{
		Host()->Remove(pane, nPosStart, nPosEnd);
		Py_INCREF(Py_None);
		return Py_None;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_pane_TextRange(PyObject* self, PyObject* args)
{
	int nPane = -1, nPosStart = -1, nPosEnd = -1; ExtensionAPI::Pane pane;
	if (!PyArg_ParseTuple(args, "iii", &nPane, &nPosStart, &nPosEnd)) return NULL;
	if (nPosStart < 0 || nPosEnd < 0) return NULL;
	if (!GetPaneFromInt(nPane, &pane)) return NULL;
	char *value = Host()->Range(pane, nPosStart, nPosEnd);
	if (value)
	{
		// give the caller ownership of this object.
		CPyObjectPtr objRet = PyString_FromString(value);
		delete[] value;
		return objRet;
	}
	else
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
}

PyObject* pyfun_pane_FindText(PyObject* self, PyObject* args) //returns a tuple
{
	char* text = NULL; // we don't own this.
	int nPane = -1, nFlags = 0, nPosStart = 0, nPosEnd = -1;
	ExtensionAPI::Pane pane;
	if (!PyArg_ParseTuple(args, "is|iii", &nPane, &text, &nFlags, &nPosStart, &nPosEnd) &&
		GetPaneFromInt(nPane, &pane))
	{
		if (nPosEnd == -1)
		{
			nPosEnd = Host()->Send(pane, SCI_GETLENGTH, 0, 0);
		}

		if (!(nPosStart < 0 || nPosEnd < 0))
		{
			Sci_TextToFind ft = { {0, 0}, 0, {0, 0} };
			ft.lpstrText = text;
			ft.chrg.cpMin = nPosStart;
			ft.chrg.cpMax = nPosEnd;
			int result = Host()->Send(pane, SCI_FINDTEXT,
				static_cast<uptr_t>(nFlags), reinterpret_cast<sptr_t>(&ft));

			if (result >= 0)
			{
				// give the caller ownership of this object.
				CPyObjectPtr objRet = Py_BuildValue(
					"(i,i)", ft.chrgText.cpMin, ft.chrgText.cpMax);
				return objRet;
			}
			else
			{
				Py_INCREF(Py_None);
				return Py_None;
			}
		}
	}

	return NULL;
}

PyObject* pyfun_pane_SendScintillaFn(PyObject* self, PyObject* args)
{
	// parse arguments
	PyObject* tuplePassedIn; // we don't own this.
	char* commandName = NULL; // we don't own this.
	int nPane = -1;
	ExtensionAPI::Pane pane;
	if (!PyArg_ParseTuple(args, "isO", &nPane, &commandName, &tuplePassedIn) ||
		!GetPaneFromInt(nPane, &pane) ||
		!PyTuple_Check(tuplePassedIn))
	{ 
		PyErr_SetString(PyExc_RuntimeError, "Third arg must be a tuple.");
		return NULL;
	}

	int nFnIndex = IFaceTable::FindFunction(commandName);
	if (nFnIndex == -1)
	{
		PyErr_SetString(PyExc_RuntimeError, "Could not find fn.");
		return NULL;
	}

	intptr_t wParam = 0; // args to be passed to Scite
	intptr_t lParam = 0; // args to be passed to Scite
	IFaceFunction func = IFaceTable::functions[nFnIndex];
	bool isStringResult = func.returnType == iface_int && func.paramType[1] == iface_stringresult;
	size_t nArgCount = PyTuple_GET_SIZE((PyObject*)tuplePassedIn);
	size_t nArgsExpected = isStringResult ? ((func.paramType[0] != iface_void) ? 1 : 0) :
		((func.paramType[1] != iface_void) ? 2 : ((func.paramType[0] != iface_void) ? 1 : 0));
	if (strcmp(commandName, "GetCurLine") == 0)
	{
		nArgsExpected = 0;
		func.paramType[0] = iface_void;
		func.paramType[1] = iface_void;
	}

	if (nArgCount != nArgsExpected)
	{ 
		PyErr_SetString(PyExc_RuntimeError, "Wrong # of args");
		return NULL;
	}

	if (func.paramType[0] != iface_void)
	{
		if (!PullPythonArgument(func.paramType[0], PyTuple_GetItem(tuplePassedIn, 0), &wParam))
		{
			return NULL;
		}
	}
	if (func.paramType[1] != iface_void && !isStringResult)
	{
		if (!PullPythonArgument(func.paramType[1], PyTuple_GetItem(tuplePassedIn, 1), &lParam))
		{
			return NULL;
		}
	}
	else if (isStringResult)
	{ 
		// allocate space for the result
		size_t spaceNeeded = Host()->Send(pane, func.value, wParam, NULL);
		if (strcmp(commandName, "GetCurLine") == 0) // the first param of getCurLine is useless
		{
			wParam = spaceNeeded + 1;
		}

		lParam = (intptr_t) new char[spaceNeeded + 1];
		for (unsigned i = 0; i < spaceNeeded + 1; i++)
		{
			((char*)lParam)[i] = 0;
		}
	}

	intptr_t result = Host()->Send(pane, func.value, wParam, lParam);
	PyObject* pyObjReturn = NULL;
	if (isStringResult)
	{
		if (!lParam)
		{
			// It apparently returned null instead of string
			Py_INCREF(Py_None);
			return Py_None;
		}
		else
		{
			// don't use PyString_FromString because it might not be null-terminated
			if (result == 0)
			{
				pyObjReturn = PyString_FromString("");
			}
			else
			{
				pyObjReturn = PyString_FromStringAndSize((char *)lParam, (size_t)result - 1);
			}

			delete[](char*) lParam;
		}
	}
	else
	{
		// this translates void into None, which makes sense
		if (!PushPythonArgument(func.returnType, result, &pyObjReturn))
		{ 
			return NULL;
		}
	}

	Py_INCREF(pyObjReturn);
	return pyObjReturn;
}

PyObject* pyfun_pane_SendScintillaGet(PyObject* self, PyObject* args)
{
	char* propName = NULL; // we don't own this.
	int nPane = -1;
	ExtensionAPI::Pane pane;
	PyObject* pyObjParam = NULL;
	if (!PyArg_ParseTuple(args, "is|O", &nPane, &propName, &pyObjParam) ||
		!GetPaneFromInt(nPane, &pane))
	{
		return NULL;
	}

	int nFnIndex = IFaceTable::FindProperty(propName);
	if (nFnIndex == -1) 
	{ 
		PyErr_SetString(PyExc_RuntimeError, "Could not find prop."); 
		return NULL; 
	}

	IFaceProperty prop = IFaceTable::properties[nFnIndex];
	if (prop.getter == 0 || strcmp(propName, "Property") == 0 || strcmp(propName, "PropertyInt") == 0)
	{
		PyErr_SetString(PyExc_RuntimeError, "prop can't be get.");
		return NULL;
	}

	intptr_t wParam = 0; // args to be passed to Scite
	intptr_t lParam = 0; // args to be passed to Scite

	if (prop.paramType != iface_void)
	{
		if (pyObjParam == NULL || pyObjParam == Py_None)
		{
			PyErr_SetString(PyExc_RuntimeError, "prop needs param.");
			return NULL;
		}

		if (!PullPythonArgument(prop.paramType, pyObjParam, &wParam))
		{
			return NULL;
		}
	}
	else if (!(pyObjParam == NULL || pyObjParam == Py_None))
	{
		PyErr_SetString(PyExc_RuntimeError, "property does not take params.");
		return NULL;
	}

	intptr_t result = Host()->Send(pane, prop.getter, wParam, lParam);

	// this translates void into None, which makes sense
	PyObject* pyObjReturn = NULL;
	if (PushPythonArgument(prop.valueType, result, &pyObjReturn))
	{
		Py_INCREF(pyObjReturn);
		return pyObjReturn;
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_pane_SendScintillaSet(PyObject* self, PyObject* args)
{
	char* propName = NULL; // we don't own this.
	int nPane = -1;
	ExtensionAPI::Pane pane;
	PyObject* pyObjArg1 = NULL;
	PyObject* pyObjArg2 = NULL;
	if (!PyArg_ParseTuple(args, "isO|O", &nPane, &propName, &pyObjArg1, &pyObjArg2) ||
		!GetPaneFromInt(nPane, &pane))
	{
		return NULL;
	}

	int nFnIndex = IFaceTable::FindProperty(propName);
	if (nFnIndex == -1) { PyErr_SetString(PyExc_RuntimeError, "Could not find prop."); return NULL; }
	IFaceProperty prop = IFaceTable::properties[nFnIndex];
	if (prop.setter == 0) { PyErr_SetString(PyExc_RuntimeError, "prop can't be set."); return NULL; }
	intptr_t wParam = 0; // args to be passed to Scite
	intptr_t lParam = 0; // args to be passed to Scite

	if (prop.paramType == iface_void)
	{
		if (!(pyObjArg2 == NULL || pyObjArg2 == Py_None))
		{
			PyErr_SetString(PyExc_RuntimeError, "property does not take params.");
			return NULL;
		}

		if (!PullPythonArgument(prop.valueType, pyObjArg1, &wParam))
		{
			return NULL;
		}
	}
	else
	{
		// a bit different than expected, but in the docs it says "set void StyleSetBold=2053(int style, bool bold)
		if (pyObjArg2 == NULL || pyObjArg2 == Py_None)
		{
			PyErr_SetString(PyExc_RuntimeError, "prop needs param.");
			return NULL;
		}

		if (!PullPythonArgument(prop.paramType, pyObjArg1, &wParam) ||
			!PullPythonArgument(prop.valueType, pyObjArg2, &lParam))
		{
			return NULL;
		}
	}

	(void)Host()->Send(pane, prop.setter, wParam, lParam);
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* pyfun_app_GetConstant(PyObject* self, PyObject* args)
{
	char* propName = NULL; // we don't own this.
	if (!PyArg_ParseTuple(args, "s", &propName))
	{
		return NULL;
	}

	int nFnIndex = IFaceTable::FindConstant(propName);
	if (nFnIndex == -1)
	{
		PyErr_SetString(PyExc_RuntimeError, "Could not find constant.");
		return NULL;
	}

	IFaceConstant faceConstant = IFaceTable::constants[nFnIndex];
	PyObject* pyValueOut = PyInt_FromLong(faceConstant.value);
	Py_INCREF(pyValueOut);
	return pyValueOut;
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

static PyMethodDef methods_LogStdout[] =
{
	{"LogStdout", pyfun_LogStdout, METH_VARARGS, "Logs stdout"},
	{"app_Trace", pyfun_LogStdout, METH_VARARGS, "(for compat with scite-lua scripts)"},
	{"app_MsgBox", pyfun_MessageBox, METH_VARARGS, ""},
	{"app_OpenFile", pyfun_SciteOpenFile, METH_VARARGS, ""},
	{"app_GetProperty", pyfun_GetProperty, METH_VARARGS, "Get SciTE Property"},
	{"app_SetProperty", pyfun_SetProperty, METH_VARARGS, "Set SciTE Property"},
	{"app_UnsetProperty", pyfun_UnsetProperty, METH_VARARGS, "Unset SciTE Property"},
	{"app_UpdateStatusBar", pyfun_app_UpdateStatusBar, METH_VARARGS, ""},
	{"app_SciteCommand", pyfun_app_SciteCommand, METH_VARARGS, ""},
	{"app_GetConstant", pyfun_app_GetConstant, METH_VARARGS, ""},

	{"pane_Append", pyfun_pane_Append, METH_VARARGS, ""},
	{"pane_Insert", pyfun_pane_Insert, METH_VARARGS, ""},
	{"pane_Remove", pyfun_pane_Remove, METH_VARARGS, ""},
	{"pane_Textrange", pyfun_pane_TextRange, METH_VARARGS, ""},
	{"pane_FindText", pyfun_pane_FindText, METH_VARARGS, ""},
	{"pane_ScintillaFn", pyfun_pane_SendScintillaFn, METH_VARARGS, ""},
	{"pane_ScintillaGet", pyfun_pane_SendScintillaGet, METH_VARARGS, ""},
	{"pane_ScintillaSet", pyfun_pane_SendScintillaSet, METH_VARARGS, ""},
	// the match object, if it's needed at all, can be written in Python.
	{NULL, NULL, 0, NULL}
};

void PythonExtension::SetupPythonNamespace()
{
	CPyObjectPtr module = Py_InitModule("CScite", methods_LogStdout);

	::MessageBoxA(0, "skipping python setup", "skipping", 0);

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
		WriteError("Unexpected: error capturing stdout from Python. make sure python27.zip is present?");
		PyErr_Print(); // if printing isn't set up, will not help, but at least will clear python's error bit
		return;
	}

	// now run setup script to add wrapper classes.
	// use Python's import because PyRun_AnyFile() ran into current-directory issues
	// note that pythonsetup.py modifies the CScite module object
	CPyObjectOwned pName = PyString_FromString("pythonsetup");
	if (!pName)
	{
		WriteError("Unexpected error: could not form string pythonsetup.");
		return;
	}

	CPyObjectOwned pModule = PyImport_Import(pName);
	if (!pModule)
	{
		WriteError("Error importing pythonsetup module.");
		PyErr_Print();
		return;
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

inline bool GetPaneFromInt(int nPane, ExtensionAPI::Pane* outPane)
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

int FindFriendlyNamedIDMConstant(const char *name)
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

static IFaceConstant rgFriendlyNamedIDMConstants[] = 
{
	{"Abbrev", IDM_ABBREV},
	{"About", IDM_ABOUT},
	{"Activate", IDM_ACTIVATE},
	{"BlockComment", IDM_BLOCK_COMMENT},
	{"BookmarkClearall", IDM_BOOKMARK_CLEARALL},
	{"BookmarkNext", IDM_BOOKMARK_NEXT},
	{"BookmarkNextSelect", IDM_BOOKMARK_NEXT_SELECT},
	{"BookmarkPrev", IDM_BOOKMARK_PREV},
	{"BookmarkPrevSelect", IDM_BOOKMARK_PREV_SELECT},
	{"BookmarkToggle", IDM_BOOKMARK_TOGGLE},
	{"BoxComment", IDM_BOX_COMMENT},
	{"Buffer", IDM_BUFFER},
	{"Buffersep", IDM_BUFFERSEP},
	{"Build", IDM_BUILD},
	{"Clear", IDM_CLEAR},
	{"ClearOutput", IDM_CLEAROUTPUT},
	{"Close", IDM_CLOSE},
	{"Closeall", IDM_CLOSEALL},
	{"Compile", IDM_COMPILE},
	{"Complete", IDM_COMPLETE},
	{"CompleteWord", IDM_COMPLETEWORD},
	{"Copy", IDM_COPY},
	{"CopyAsrtf", IDM_COPYASRTF},
	{"CopyPath", IDM_COPYPATH},
	{"Cut", IDM_CUT},
	{"DirectionDown", IDM_DIRECTIONDOWN},
	{"DirectionUp", IDM_DIRECTIONUP},
	{"Duplicate", IDM_DUPLICATE},
	{"Encoding_default", IDM_ENCODING_DEFAULT},
	{"Encoding_ucookie", IDM_ENCODING_UCOOKIE},
	{"Encoding_ucs2be", IDM_ENCODING_UCS2BE},
	{"Encoding_ucs2le", IDM_ENCODING_UCS2LE},
	{"Encoding_utf8", IDM_ENCODING_UTF8},
	{"EnterSelection", IDM_ENTERSELECTION},
	{"Eol_convert", IDM_EOL_CONVERT},
	{"Eol_cr", IDM_EOL_CR},
	{"Eol_crlf", IDM_EOL_CRLF},
	{"Eol_lf", IDM_EOL_LF},
	{"Expand", IDM_EXPAND},
	{"ExpandEnsurechildrenvisible", IDM_EXPAND_ENSURECHILDRENVISIBLE},
	{"Filer", IDM_FILER},
	{"Find", IDM_FIND},
	{"FindInFilesDialog", IDM_FINDINFILES},
	{"FindInFilesStart", IDM_FINDINFILESSTART},
	{"FindNext", IDM_FINDNEXT},
	{"FindNextBack", IDM_FINDNEXTBACK},
	{"FindNextBackSel", IDM_FINDNEXTBACKSEL},
	{"FindNextSel", IDM_FINDNEXTSEL},
	{"FinishedExecute", IDM_FINISHEDEXECUTE},
	{"FoldMargin", IDM_FOLDMARGIN},
	{"Fullscreen", IDM_FULLSCREEN},
	{"Go", IDM_GO},
	{"Goto", IDM_GOTO},
	{"Help", IDM_HELP},
	{"HelpScite", IDM_HELP_SCITE},
	{"Import", IDM_IMPORT},
	{"IncSearch", IDM_INCSEARCH},
	{"InsAbbrev", IDM_INS_ABBREV},
	{"Join", IDM_JOIN},
	{"Language", IDM_LANGUAGE},
	{"LineNumberMargin", IDM_LINENUMBERMARGIN},
	{"LoadSession", IDM_LOADSESSION},
	{"LwrCase", IDM_LWRCASE},
	{"MacroList", IDM_MACROLIST},
	{"MacroPlay", IDM_MACROPLAY},
	{"MacroRecord", IDM_MACRORECORD},
	{"MacroSep", IDM_MACRO_SEP},
	{"MacroStoprecord", IDM_MACROSTOPRECORD},
	{"MatchBrace", IDM_MATCHBRACE},
	{"MatchCase", IDM_MATCHCASE},
	{"MonoFont", IDM_MONOFONT},
	{"MoveTableft", IDM_MOVETABLEFT},
	{"MoveTabright", IDM_MOVETABRIGHT},
	{"MruFile", IDM_MRUFILE},
	{"MruSep", IDM_MRU_SEP},
	{"New", IDM_NEW},
	{"NextFile", IDM_NEXTFILE},
	{"NextFilestack", IDM_NEXTFILESTACK},
	{"NextMatchppc", IDM_NEXTMATCHPPC},
	{"NextMsg", IDM_NEXTMSG},
	{"OnTop", IDM_ONTOP},
	{"Open", IDM_OPEN},
	{"OpenAbbrevproperties", IDM_OPENABBREVPROPERTIES},
	{"OpenDirectoryproperties", IDM_OPENDIRECTORYPROPERTIES},
	{"OpenFileshere", IDM_OPENFILESHERE},
	{"OpenGlobalproperties", IDM_OPENGLOBALPROPERTIES},
	{"OpenLocalproperties", IDM_OPENLOCALPROPERTIES},
	{"OpenLuaexternalfile", IDM_OPENLUAEXTERNALFILE},
	{"OpenSelected", IDM_OPENSELECTED},
	{"OpenUserproperties", IDM_OPENUSERPROPERTIES},
	{"Paste", IDM_PASTE},
	{"PasteAnddown", IDM_PASTEANDDOWN},
	{"PrevFile", IDM_PREVFILE},
	{"PrevFlestack", IDM_PREVFILESTACK},
	{"PrevMatchppc", IDM_PREVMATCHPPC},
	{"PrevMsg", IDM_PREVMSG},
	{"Print", IDM_PRINT},
	{"PrintSetup", IDM_PRINTSETUP},
	{"Quit", IDM_QUIT},
	{"Readonly", IDM_READONLY},
	{"Redo", IDM_REDO},
	{"Regexp", IDM_REGEXP},
	{"Replace", IDM_REPLACE},
	{"Revert", IDM_REVERT},
	{"RunWin", IDM_RUNWIN},
	{"Save", IDM_SAVE},
	{"SaveAcopy", IDM_SAVEACOPY},
	{"SaveAll", IDM_SAVEALL},
	{"SaveAs", IDM_SAVEAS},
	{"SaveAshtml", IDM_SAVEASHTML},
	{"SaveAspdf", IDM_SAVEASPDF},
	{"SaveAsrtf", IDM_SAVEASRTF},
	{"SaveAstex", IDM_SAVEASTEX},
	{"SaveAsxml", IDM_SAVEASXML},
	{"SaveSession", IDM_SAVESESSION},
	{"SelMargin", IDM_SELMARGIN},  // apparently caps first.
	{"SelectAll", IDM_SELECTALL},
	{"SelectToBrace", IDM_SELECTTOBRACE},
	{"SelectToNextmatchppc", IDM_SELECTTONEXTMATCHPPC},
	{"SelectToPrevmatchppc", IDM_SELECTTOPREVMATCHPPC},
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
	{"ToolWin", IDM_TOOLWIN}, // apparently caps first.
	{"Tools", IDM_TOOLS},
	{"Undo", IDM_UNDO},
	{"Unslash", IDM_UNSLASH},
	{"UprCase", IDM_UPRCASE},
	{"ViewEol", IDM_VIEWEOL},
	{"ViewGuides", IDM_VIEWGUIDES},
	{"ViewSpace", IDM_VIEWSPACE},
	{"ViewStatusbar", IDM_VIEWSTATUSBAR},
	{"ViewTabbar", IDM_VIEWTABBAR},
	{"ViewToolbar", IDM_VIEWTOOLBAR},
	{"WholeWord", IDM_WHOLEWORD},
	{"Wrap", IDM_WRAP},
	{"WrapAround", IDM_WRAPAROUND},
	{"WrapOutput", IDM_WRAPOUTPUT},
};

const IFaceConstant * const PythonExtension::constantsTable = rgFriendlyNamedIDMConstants;
const size_t PythonExtension::constantsTableLen = _countof(rgFriendlyNamedIDMConstants);
