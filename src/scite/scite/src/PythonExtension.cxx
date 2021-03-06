// SciTE Python Extension
// Ben Fisher, 2016
// Released under the GNU General Public License version 3

#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include <string>
#include <sstream>
#include <vector>
#include <algorithm>
#include <unordered_set>

#ifdef _WIN32
#include <windows.h>
#endif

// for msvc 9 (internally 1500), unordered_set is in the tr1 namespace
#ifdef _MSC_VER

#if (_MSC_VER <= 1500)
#define std_unordered_set std::tr1::unordered_set
#else
#define std_unordered_set std::unordered_set
#endif

#else
#define std_unordered_set std::unordered_set
#endif

#include "SciTE.h"
#include "Scintilla.h"
#include "Extender.h"
#include "SciTEKeys.h"
#include "IFaceTable.h"
#include "PythonExtension.h"

#ifdef _WIN32
#include "..\python\include\Python.h"
#define countof _countof
#else
#include "Python.h"
#define countof(arr) (sizeof(arr) / sizeof((arr)[0]))
#endif

// name of the python module to run on startup
static const char* c_PythonModuleName = "scite_extend_ui";

// from LuaExtension.cxx
inline bool IFaceTypeIsScriptable(IFaceType t, int index) {
	return t < iface_stringresult || (index==1 && t == iface_stringresult);
}

// from LuaExtension.cxx
inline bool IFaceTypeIsNumeric(IFaceType t) {
	return (t > iface_void && t < iface_bool);
}

// from LuaExtension.cxx
inline bool IFaceFunctionIsScriptable(const IFaceFunction &f) {
	return IFaceTypeIsScriptable(f.paramType[0], 0) && IFaceTypeIsScriptable(f.paramType[1], 1);
}

// from LuaExtension.cxx
inline bool IFacePropertyIsScriptable(const IFaceProperty &p) {
	return (((p.valueType > iface_void) && (p.valueType <= iface_stringresult) && (p.valueType != iface_keymod)) &&
	        ((p.paramType < iface_colour) || (p.paramType == iface_string) ||
	                (p.paramType == iface_bool)) && (p.getter || p.setter));
}

// same as SptrFromPointer
inline sptr_t CastPtrToSptr(void *p) {
	return SptrFromPointer(p);
}

// same as SptrFromString
inline sptr_t CastSzToSptr(const char *cp) {
	return SptrFromString(cp);
}

// forward declarations
void verifyConstantsTableOrder();
int FindFriendlyNamedIDMConstant(const char* name);
bool GetPaneFromInt(int nPane, ExtensionAPI::Pane* outPane);
void trace(const char* text, int n);
void trace(const char* text1, const char* text2 = NULL);
void trace_error(const char* text1, const char* text2 = NULL);
void onUpdateUI();
void onChangeCurrentFile();
bool RunCallback(EventNumber eventNumber,
	const char* stringPar = NULL,
	bool useNumericPar1 = false, int numericPar1 = 0,
	bool useNumericPar2 = false, int numericPar2 = 0);

const char* IFaceTypeToString(IFaceType type)
{
	switch(type)
	{
		case iface_void: return "void";
		case iface_int: return "int";
		case iface_length: return "length";
		case iface_position: return "position";
		case iface_colour: return "colour";
		case iface_bool: return "bool";
		case iface_keymod: return "keymod";
		case iface_string: return "string";
		case iface_stringresult: return "stringresult";
		case iface_cells: return "cells";
		case iface_textrange: return "textrange";
		case iface_findtext: return "findtext";
		case iface_formatrange: return "findtext";
		default: return "unknown";
	}
}

const char* EventNumberToString(int i)
{
	switch ((EventNumber) i)
	{
		case EventNumber_OnStart: return "OnStart";
		case EventNumber_OnOpen: return "OnOpen";
		case EventNumber_OnBeforeSave: return "OnBeforeSave";
		case EventNumber_OnSave: return "OnSave";
		case EventNumber_OnSavePointReached: return "OnSavePointReached";
		case EventNumber_OnSavePointLeft: return "OnSavePointLeft";
		case EventNumber_OnDoubleClick: return "OnDoubleClick";
		case EventNumber_OnMarginClick: return "OnMarginClick";
		case EventNumber_OnClose: return "OnClose";
		case EventNumber_OnChar: return "OnChar";
		case EventNumber_OnUserListSelection: return "OnUserListSelection";
		case EventNumber_OnKey: return "OnKey";
		case EventNumber_OnUserStrip: return "OnUserStrip";
		case EventNumber_OnFileChange: return "OnFileChange";
		default: return NULL;
	}
}

bool PythonExtension::OnOpen(const char *filename)
{
	OnFileChange();
	return RunCallback(EventNumber_OnOpen, filename);
}

bool PythonExtension::OnSwitchFile(const char*)
{
	OnFileChange();
	return false;
}

bool PythonExtension::OnBeforeSave(const char *filename)
{
	return RunCallback(EventNumber_OnBeforeSave, filename);
}

bool PythonExtension::OnSave(const char *filename)
{
	OnFileChange();
	return RunCallback(EventNumber_OnSave, filename);
}

bool PythonExtension::OnSavePointReached()
{
	return RunCallback(EventNumber_OnSavePointReached);
}

bool PythonExtension::OnSavePointLeft()
{
	return RunCallback(EventNumber_OnSavePointLeft);
}

bool PythonExtension::OnStyle(unsigned int, int, int, StyleWriter*)
{
	return false;
}

bool PythonExtension::OnDoubleClick()
{
	return RunCallback(EventNumber_OnDoubleClick);
}

bool PythonExtension::OnUpdateUI()
{
	onUpdateUI();
	return false;
}

bool PythonExtension::OnMarginClick()
{
	return RunCallback(EventNumber_OnMarginClick);
}

bool PythonExtension::OnMacro(const char *, const char *)
{
	return false;
}

bool PythonExtension::SendProperty(const char *)
{
	return false;
}

bool PythonExtension::OnDwellStart(int, const char *)
{
	return false;
}

bool PythonExtension::OnClose(const char *filename)
{
	return RunCallback(EventNumber_OnClose, filename);
}

bool PythonExtension::OnChar(char ch)
{
	return RunCallback(EventNumber_OnChar, NULL, true, ch);
}

bool PythonExtension::OnUserListSelection(int type, const char *selection)
{
	return RunCallback(EventNumber_OnUserListSelection, selection, true, type);
}

bool PythonExtension::OnKey(int keyval, int modifiers)
{
	return RunCallback(EventNumber_OnKey,
		NULL, true, keyval, true, modifiers);
}

bool PythonExtension::OnUserStrip(int control, int eventType)
{
	return RunCallback(EventNumber_OnUserStrip,
		NULL, true, control, true, eventType);
}

bool PythonExtension::InitBuffer(int)
{
	OnFileChange();
	return false;
}

bool PythonExtension::ActivateBuffer(int)
{
	OnFileChange();
	return false;
}

bool PythonExtension::RemoveBuffer(int)
{
	OnFileChange();
	return false;
}

bool PythonExtension::OnFileChange()
{
	// the goal is to trigger the callback for all cases when the current buffer's filepath can change.
	// new document. open document. save as. switch buffer.
	onChangeCurrentFile();
	return RunCallback(EventNumber_OnFileChange);
}

inline bool strEqual(const char* s1, const char* s2)
{
	return strcmp(s1, s2) == 0;
}

inline bool strStartsWith(const char* s1, const char* s2)
{
	size_t len1 = strlen(s1);
	size_t len2 = strlen(s2);
	if (len1 < len2)
		return false;
	else
		return memcmp(s1, s2, len2) == 0;
}

inline bool strEndsWith(const char* s1, const char*s2)
{
	size_t len1 = strlen(s1);
	size_t len2 = strlen(s2);
	if (len1 < len2)
		return false;
	else
		return memcmp(s1 + (len1 - len2), s2, len2) == 0;
}

EventNumber eventNumberFromString(const char* eventName)
{
	for (int i = 0; i < EventNumber_LEN; i++)
	{
		if (strEqual(EventNumberToString(i), eventName))
			return (EventNumber)i;
	}
	
	return EventNumber_LEN;
}

// a simple string buffer
class SimpleStringBuffer
{
	std::vector<char> _buffer;
	bool _allocated;
	SimpleStringBuffer (const SimpleStringBuffer& other);
	SimpleStringBuffer& operator= (const SimpleStringBuffer& other);
	
public:
	SimpleStringBuffer() : _allocated(false) {}
	void Allocate(size_t n)
	{
		// the caller is responsible for providing n big enough to contain nul term.
		_buffer.resize(n);
		std::fill(_buffer.begin(), _buffer.end(), 0);
		_allocated = true;
	}
	char* Get()
	{
		return _allocated ? ((char*) &_buffer[0]) : NULL;
	}
	const char* GetConst()
	{
		return _allocated ? ((const char*) &_buffer[0]) : NULL;
	}
};

// holder for a PyObject, to ensure Py_DECREF is called.
class PyObjectOwned
{
private:
	PyObject* _obj;
	PyObjectOwned (const PyObjectOwned& other);
	PyObjectOwned& operator= (const PyObjectOwned& other);

public:
	PyObjectOwned()
	{
		_obj = NULL;
	}
	PyObjectOwned(PyObject* obj)
	{
		_obj = obj;
	}
	void Attach(PyObject* obj)
	{
		_obj = obj;
	}
	void Release()
	{
		if (_obj)
		{
// warning "conditional expression is constant" triggered by Python's code, not our code
#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable: 4127)
#endif
			Py_DECREF(_obj);
#ifdef _MSC_VER
#pragma warning(pop)
#endif
		}
		
		_obj = NULL;
	}
	~PyObjectOwned()
	{
		Release();
	}
	operator PyObject*()
	{
		return _obj;
	}
};

class CachePythonObjects
{
	PyObjectOwned cachedStrings[EventNumber_LEN];
	bool eventEnabled[EventNumber_LEN];
	bool initCompleted;
	bool initSucceeded;
	
	PyObjectOwned stringModuleName;
	PyObjectOwned module;
	PyObjectOwned moduleDict;
	PyObjectOwned functionOnEvent;
	PyObjectOwned classRequestEventPropagate;
	PyObjectOwned runStringGlobals;
	PyObjectOwned runStringLocals;
	std::string pythonHome;
	std::string pythonProgramName;
	
	CachePythonObjects (const CachePythonObjects& other);
	CachePythonObjects& operator= (const CachePythonObjects& other);
	
public:
	CachePythonObjects() : initCompleted(false), initSucceeded(false)
	{
		memset(&eventEnabled[0], 0, sizeof(eventEnabled));
	}
	
	void Initialize()
	{
		initSucceeded = DoInitialize();
		initCompleted = true;
	}
	
	bool DoInitialize()
	{
		for (int i = 0; i < EventNumber_LEN; i++)
		{
			cachedStrings[i].Attach(PyString_FromString(EventNumberToString(i)));
			if (!cachedStrings[i] || !EventNumberToString(i))
			{
				trace_error("Failure building string", EventNumberToString(i));
				return false;
			}
		}
		
		stringModuleName.Attach(PyString_FromString(c_PythonModuleName));
		if (!stringModuleName)
		{
			trace_error("Failure building string", c_PythonModuleName);
			return false;
		}
		
		module.Attach(PyImport_Import(stringModuleName));
		if (!module)
		{
			PyErr_Print();
			trace_error("Failure importing module");
			return false;
		}
		
		moduleDict.Attach(PyModule_GetDict(module));
		if (!moduleDict)
		{
			trace_error("Could not get module dict.");
			return false;
		}
		
		functionOnEvent.Attach(PyDict_GetItemString(moduleDict, "OnEvent"));
		if (!functionOnEvent)
		{
			trace_error("Could not get module's OnEvent function.");
			return false;
		}
		
		if (!PyCallable_Check(functionOnEvent))
		{
			trace_error("OnEvent not a function");
			return false;
		}
		
		classRequestEventPropagate.Attach(PyDict_GetItemString(moduleDict, "RequestThatEventContinuesToPropagate"));
		if (!classRequestEventPropagate)
		{
			trace_error("Could not get module's RequestThatEventContinuesToPropagate class.");
			return false;
		}
		
		PyObjectOwned getBuiltins(PyImport_ImportModule("__builtin__"));
		if (!getBuiltins)
		{
			trace_error("Could not find Python builtins.");
			return false;
		}
		
		runStringLocals.Attach(PyDict_New());
		runStringGlobals.Attach(PyDict_New());
		if (PyDict_SetItemString(runStringGlobals, "__builtins__", getBuiltins) != 0)
		{
			trace_error("Could not add Python builtins to globals.");
			return false;
		}
		
		if (PyDict_SetItemString(runStringGlobals, c_PythonModuleName, module) != 0)
		{
			trace_error("Could not add scite_extend_ui to globals.");
			return false;
		}
		
		return true;
	}
	
	bool IsInitialized()
	{
		return initCompleted;
	}
	
	void Release()
	{
		for (int i = 0; i < EventNumber_LEN; i++)
		{
			cachedStrings[i].Release();
		}
		
		stringModuleName.Release();
		module.Release();
		moduleDict.Release();
		functionOnEvent.Release();
		classRequestEventPropagate.Release();
		runStringGlobals.Release();
		runStringLocals.Release();
	}
	
	void BuildPythonArgs(PyObjectOwned& args, EventNumber eventNumber, const char* stringPar,
		bool useNumericPar1, int numericPar1,
		bool useNumericPar2, int numericPar2)
	{
		if (eventNumber == EventNumber_OnKey)
		{
			PyObject* shift = (SCMOD_SHIFT & numericPar2) != 0 ? Py_True : Py_False;
			PyObject* ctrl = (SCMOD_CTRL & numericPar2) != 0 ? Py_True : Py_False;
			PyObject* alt = (SCMOD_ALT & numericPar2) != 0 ? Py_True : Py_False;
			args.Attach(Py_BuildValue("iOOO", numericPar1, shift, ctrl, alt));
		}
		else if (stringPar && useNumericPar1 && useNumericPar2)
		{
			args.Attach(Py_BuildValue("sii", stringPar, numericPar1, numericPar2));
		}
		else if (stringPar && useNumericPar1 && !useNumericPar2)
		{
			args.Attach(Py_BuildValue("si", stringPar, numericPar1));
		}
		else if (stringPar && !useNumericPar1 && !useNumericPar2)
		{
			args.Attach(Py_BuildValue("(s)", stringPar));
		}
		else if (!stringPar && useNumericPar1 && !useNumericPar2)
		{
			args.Attach(Py_BuildValue("(i)", numericPar1));
		}
		else if (!stringPar && useNumericPar1 && useNumericPar2)
		{
			args.Attach(Py_BuildValue("ii", numericPar1, numericPar2));
		}
		else
		{
			Py_INCREF(Py_None);
			args.Attach(Py_None);
		}
	}
	
	bool NeedsNotification(EventNumber eventNumber)
	{
		if (eventNumber < 0 || eventNumber >= EventNumber_LEN)
		{
			trace_error("Unrecognized event number");
			return false;
		}
		
		return eventEnabled[eventNumber];
	}
	
	bool RunString(const char* cmd)
	{
		if (!initSucceeded)
		{
			return true;
		}
		
		PyObjectOwned result(PyRun_String(cmd, Py_file_input, runStringGlobals, runStringLocals));
		if (PyErr_Occurred() && PyErr_ExceptionMatches(classRequestEventPropagate))
		{
			// this special exception means we should say that the event was not handled.
			PyErr_Clear();
			return false;
		}
		else if (PyErr_Occurred())
		{
			// for this case we want to return true, we want to indicate the event as handled.
			// return true even on error
			PyErr_Print();
			PyErr_Clear();
			return true;
		}
		else
		{
			return true;
		}
	}
	
	bool RunCallback(EventNumber eventNumber,
		const char* stringPar = NULL,
		bool useNumericPar1 = false, int numericPar1 = 0,
		bool useNumericPar2 = false, int numericPar2 = 0)
	{
		// returning true can prevent the event from being propagated, so be careful about return value here.
		if (!initCompleted || !initSucceeded)
		{
			return false;
		}
		
		if (!NeedsNotification(eventNumber))
		{
			return false;
		}
		
		PyObjectOwned args;
		BuildPythonArgs(args, eventNumber, stringPar,
			useNumericPar1, numericPar1, useNumericPar2, numericPar2);
		if (!args)
		{
			trace_error("Error building args.");
			return false;
		}
		
		PyObject* eventName = cachedStrings[eventNumber];
		PyObjectOwned fullArgs(Py_BuildValue("OO", eventName, (PyObject*)args));
		if (!fullArgs)
		{
			trace_error("Error building full args.");
			return false;
		}
		
		PyObjectOwned result(PyObject_CallObject(functionOnEvent, fullArgs));
		if (!result)
		{
			trace_error("Error in callback.", EventNumberToString(eventNumber));
			PyErr_Print();
			return false;
		}
		
		// only prevent propagation if the special string StopEventPropagation is returned.
		if (PyString_Check(result))
		{
			const char* string = PyString_AsString(result); // we don't own this
			if (strEqual("StopEventPropagation", string))
			{
				return true;
			}
		}
		
		return false;
	}
	
	void EnableNotification(const char* eventName, bool enabled)
	{
		EventNumber number = eventNumberFromString(eventName);
		if (number >= 0 && number < EventNumber_LEN)
		{
			eventEnabled[number] = enabled;
		}
	}
	
	void setPythonHomeAndProgramName(const char* home, const char* progname)
	{
		pythonHome = home;
		pythonProgramName = progname;
		Py_SetPythonHome((char*) pythonHome.c_str());
		Py_SetProgramName((char*) pythonProgramName.c_str());
	}
} cachePythonObjects;

PythonExtension& PythonExtension::Instance()
{
	static PythonExtension singleton;
	return singleton;
}

PythonExtension::PythonExtension() : 
	_host(NULL)
{
}

PythonExtension::~PythonExtension()
{
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
	if (!cachePythonObjects.IsInitialized())
	{
		SetupPythonNamespace();
		cachePythonObjects.Initialize();
	}
}

bool PythonExtension::Initialise(ExtensionAPI* host)
{
	_host = host;
	std::string delayLoadProp = _host->Property("ext.python.delayload");
	bool delayLoad = delayLoadProp.length() > 0 && delayLoadProp[0] != '0';

	if (!delayLoad)
	{
		verifyConstantsTableOrder();
		InitializePython();
		RunCallback(EventNumber_OnStart);
	}
	
	return false;
}

bool PythonExtension::Finalise()
{
	cachePythonObjects.Release();
	Py_Finalize();
	_host = NULL;
	return false;
}

bool PythonExtension::Clear()
{
	return false;
}

bool PythonExtension::Load(const char *filename)
{
	// only run files with a .py extension
	if (strEndsWith(filename, ".py"))
	{
		FILE* f = fopen(filename, "r");
		if (f)
		{
			// Python will close the file handle
			int result = PyRun_SimpleFileEx(f, filename, 1);
			if (result != 0)
			{
				PyErr_Print();
			}
		}
		else
		{
			_host->Trace(">Python: could not open file.\n");
		}
	}
	
	return false;
}

bool PythonExtension::OnExecute(const char* cmd)
{
	if (strStartsWith(cmd, "py:"))
	{
		cmd += strlen("py:");
		InitializePython();
		
		return cachePythonObjects.RunString(cmd);
	}
	else
	{
		// this wasn't sent to us, maybe it's a lua string
		return false;
	}
}

bool PythonExtension::NeedsOnClose()
{
	return cachePythonObjects.NeedsNotification(EventNumber_OnClose);
}

bool RunCallback(EventNumber eventNumber,
	const char* stringParam,
	bool useNumericPar1, int numericPar1,
	bool useNumericPar2, int numericPar2)
{
	return cachePythonObjects.RunCallback(eventNumber, stringParam,
		useNumericPar1, numericPar1, useNumericPar2, numericPar2);
}

inline PyObject* IncrefAndReturnNone()
{
	// None is a reference-counted object like any other object,
	// it should be incref'd when returned. 
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject* pyfun_LogStdout(PyObject*, PyObject* args)
{
	const char* msg = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &msg) && msg)
	{
		if (Host())
		{
			trace(msg);
		}

		return IncrefAndReturnNone();
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_MessageBox(PyObject*, PyObject* args)
{
	const char* msg = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &msg) && msg)
	{
#ifdef _WIN32
		::MessageBoxA(NULL, msg, "SciTE", 0);
#endif
		return IncrefAndReturnNone();
	}
	else
	{
		return NULL;
	}
}

void SciteOpenFile(const char* filename)
{
	std::string cmd = "open:";
	for (unsigned int i = 0; i < strlen(filename); i++)
	{
		if (filename[i] == '\\')
		{
			cmd += "\\\\";
		}
		else
		{
			cmd += filename[i];
		}
	}

	Host()->Perform(cmd.c_str());
}

PyObject* pyfun_SciteOpenFile(PyObject*, PyObject* args)
{
	const char* filename = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &filename) && filename)
	{
		SciteOpenFile(filename);
		return IncrefAndReturnNone();
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_GetProperty(PyObject*, PyObject* args)
{
	const char* propName = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &propName) && propName)
	{
		std::string value = Host()->Property(propName);
		
		// follow properties file behavior: a missing property returns empty string, not null
		const char* sz = value.length() > 0 ? value.c_str() : "";
		
		// give the caller ownership of this object.
		return PyString_FromString(sz);
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_SetProperty(PyObject*, PyObject* args)
{
	const char* propName = NULL; // we don't own this.
	const char* propValue = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "ss", &propName, &propValue) && propName && propValue)
	{
		// it looks like SetProperty allocates, it's ok if key and val go out of scope.
		Host()->SetProperty(propName, propValue);
		return IncrefAndReturnNone();
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_UnsetProperty(PyObject*, PyObject* args)
{
	const char* propName = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &propName) && propName)
	{
		Host()->UnsetProperty(propName);
		return IncrefAndReturnNone();
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_pane_Append(PyObject*, PyObject* args)
{
	const char* text = NULL; // we don't own this.
	int nPane = -1;
	ExtensionAPI::Pane pane;
	if (PyArg_ParseTuple(args, "is", &nPane, &text) &&
		text &&
		GetPaneFromInt(nPane, &pane))
	{
		Host()->Insert(pane, Host()->Send(pane, SCI_GETLENGTH, 0, 0), text);
		return IncrefAndReturnNone();
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_pane_Insert(PyObject*, PyObject* args)
{
	const char* text = NULL; // we don't own this.
	int nPane = -1, nPos = -1;
	ExtensionAPI::Pane pane;
	if (PyArg_ParseTuple(args, "iis", &nPane, &nPos, &text) &&
		nPos >= 0 &&
		text &&
		GetPaneFromInt(nPane, &pane))
	{
		Host()->Insert(pane, nPos, text);
		return IncrefAndReturnNone();
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_pane_Remove(PyObject*, PyObject* args)
{
	int nPane = -1, nPosStart = -1, nPosEnd = -1;
	ExtensionAPI::Pane pane;
	
	if (PyArg_ParseTuple(args, "iii", &nPane, &nPosStart, &nPosEnd) &&
		(nPosStart >=0 && nPosEnd >= 0) &&
		(GetPaneFromInt(nPane, &pane)))
	{
		Host()->Remove(pane, nPosStart, nPosEnd);
		return IncrefAndReturnNone();
	}
	else
	{
		return NULL;
	}
}

PyObject* pyfun_pane_TextRange(PyObject*, PyObject* args)
{
	int nPane = -1, nPosStart = -1, nPosEnd = -1;
	ExtensionAPI::Pane pane;
	
	if (PyArg_ParseTuple(args, "iii", &nPane, &nPosStart, &nPosEnd) &&
	(nPosStart >=0 && nPosEnd >= 0) &&
	(GetPaneFromInt(nPane, &pane)))
	{
		char *value = Host()->Range(pane, nPosStart, nPosEnd);
		if (value)
		{
			// give the caller ownership of this object.
			PyObject* objRet = PyString_FromString(value);
			delete[] value;
			return objRet;
		}
		else
		{
			return IncrefAndReturnNone();
		}
	}
	else
	{
	return NULL;
	}
}

PyObject* pyfun_pane_FindText(PyObject*, PyObject* args) // returns a tuple
{
	const char* text = NULL; // we don't own this.
	int nPane = -1, nFlags = 0, nPosStart = 0, nPosEnd = -1;
	ExtensionAPI::Pane pane;
	if (PyArg_ParseTuple(args, "is|iii", &nPane, &text, &nFlags, &nPosStart, &nPosEnd) &&
		text &&
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
				return Py_BuildValue(
					"(i,i)", ft.chrgText.cpMin, ft.chrgText.cpMax);
			}
			else
			{
				return IncrefAndReturnNone();
			}
		}
	}

	return NULL;
}

int GetPythonInt(PyObject *arg, bool optional=false)
{
	if (!arg || !PyInt_Check(arg))
	{
		if (!arg && optional)
		{
			return 0;
		}
		else
		{
			PyErr_SetString(PyExc_RuntimeError, "expected int param.");
			return 0;
		}
	}
	else
	{
		return PyInt_AsLong(arg);
	}
}

bool GetPythonBool(PyObject *arg, bool optional=false)
{
	if (!arg || !PyBool_Check(arg))
	{
		if (!arg && optional)
		{
			return false;
		}
		else
		{
			PyErr_SetString(PyExc_RuntimeError, "expected boolean param.");
			return false;
		}
	}
	else
	{
		return !!PyObject_IsTrue(arg);
	}
}

void GetPythonString(PyObject* arg, const char** str, size_t* len, bool optional=false)
{
	if (!arg || !PyString_Check(arg))
	{
		if (!arg && optional)
		{
			*str = "";
			*len = 0;
		}
		else
		{
			*str = NULL;
			*len = 0;
			PyErr_SetString(PyExc_RuntimeError, "expected string param.");
		}
	}
	else
	{
		*str = PyString_AsString(arg);
		*len = PyString_Size(arg);
	}
}

IFaceFunction SearchForFunction(const char* name, std::string& nameFound)
{
	// first, look for a function. Some functions begin with the string "Get", but aren't a property.
	IFaceFunction empty = IFaceFunction();
	int index = IFaceTable::FindFunction(name);
	if (index >= 0)
	{
		if (!IFaceFunctionIsScriptable(IFaceTable::functions[index])) {
			PyErr_SetString(PyExc_RuntimeError, "function is not scriptable");
			return empty;
		} else if (!strEqual(name, IFaceTable::functions[index].name)) {
			PyErr_SetString(PyExc_RuntimeError, "IFaceTable::FindFunction returned incorrect name");
			return empty;
		} else {
			nameFound = IFaceTable::functions[index].name;
			return IFaceTable::functions[index];
		}
	}
	
	// then, if the name begins with "Get" or "Set", look for a property.
	bool isGet = strStartsWith(name, "Get");
	bool isSet = strStartsWith(name, "Set");
	if (isGet || isSet)
	{
		const char* potentialPropertyName = name + 
			(isGet ? strlen("Get") : strlen("Set"));
		
		index = IFaceTable::FindProperty(potentialPropertyName);
		if (index > 0)
		{
			if (!IFacePropertyIsScriptable(IFaceTable::properties[index])) {
				PyErr_SetString(PyExc_RuntimeError, "property is not scriptable");
				return empty;
			} else if (!strEqual(potentialPropertyName, IFaceTable::properties[index].name)) {
				PyErr_SetString(PyExc_RuntimeError, "IFaceTable::FindProperty returned incorrect name");
				return empty;
			} else if (isGet && !IFaceTable::properties[index].getter) {
				PyErr_SetString(PyExc_RuntimeError, "Cannot read from a write-only property");
				return empty;
			} else if (isSet && !IFaceTable::properties[index].setter) {
				PyErr_SetString(PyExc_RuntimeError, "Cannot write to a read-only property");
				return empty;
			} else if (isGet) {
				nameFound = IFaceTable::properties[index].name;
				nameFound += " (getter)";
				return IFaceTable::properties[index].GetterFunction();
			} else if (isSet) {
				nameFound = IFaceTable::properties[index].name;
				nameFound += " (setter)";
				return IFaceTable::properties[index].SetterFunction();
			}
		}
	}
	
	return empty;
}

PyObject* CallPaneFunction(ExtensionAPI::Pane pane, const IFaceFunction& functionInfo,
	const char* name, PyObject* arg1, PyObject* arg2)
{
	// the logic here follows iface_function_helper
	sptr_t paramsToSend[2] = {0,0};
	int arg = 0;
	PyObject* args[] = {arg1, arg2};
	SimpleStringBuffer stringResult;
	bool needStringResult = false;
	int loopParamCount = 2;
	
	if (functionInfo.paramType[0] == iface_length && functionInfo.paramType[1] == iface_string)
	{
		// for caller's convenience, we shouldn't ask for both string and length, we can just get the string's length here.
		// we require a valid string here, which is more strict than the Lua extension
		const char* str;
		size_t len;
		GetPythonString(args[arg], &str, &len);
		if (PyErr_Occurred())
		{
			return NULL;
		}
		
		paramsToSend[0] = len;
		paramsToSend[1] = CastSzToSptr(str);
		loopParamCount = 0;
	}
	else if ((functionInfo.paramType[1] == iface_stringresult) || (functionInfo.returnType == iface_stringresult))
	{
		// get ready for a string result. the buffer will be allocated later.
		needStringResult = true;
		if (functionInfo.paramType[0] == iface_length)
		{
			// Python shouldn't provide this parameter, it's used as part of the stringresult.
			loopParamCount = 0;
		}
		else
		{
			loopParamCount = 1;
		}
	}
	
	// loop through and pick up remaining parameters
	for (int i = 0; i < loopParamCount; ++i)
	{
		if (functionInfo.paramType[i] == iface_string)
		{
			const char* str;
			size_t len;
			GetPythonString(args[arg++], &str, &len);
			paramsToSend[i] = CastSzToSptr(str);
		}
		else if (functionInfo.paramType[i] == iface_bool)
		{
			bool b = GetPythonBool(args[arg++]);
			paramsToSend[i] = b ? 1 : 0;
		}
		else if (IFaceTypeIsNumeric(functionInfo.paramType[i]) || functionInfo.paramType[i] == iface_keymod)
		{
			// lua extension has special logic for iface_keymod, there's no real need,
			// we can build a keymod ourselves via my ScConst.MakeKeymod helper
			int n = GetPythonInt(args[arg++]);
			paramsToSend[i] = static_cast<long>(n);
		}
		else if (functionInfo.paramType[i] != iface_void)
		{
			trace("Warning: parameter expected, but unhandled type, in function ", name);
		}
		
		if (PyErr_Occurred())
		{
			// user passed the wrong type in one of the conversions above.
			return NULL; 
		}
	}
	
	// nitpick, there were too many params.
	for (int i = arg; i < loopParamCount; i++)
	{
		if (args[i] != NULL)
			trace("Warning: too many parameter(s) passed to function ", name);
	}
	
	if (needStringResult)
	{
		// sending with 0 means we are asking for the length of buffer.
		sptr_t stringResultLen = Host()->Send(pane, functionInfo.value, paramsToSend[0], 0);
		
		if (stringResultLen == 0)
		{
			// LuaExtension.cxx iface_function_helper says this is an error, but it can be reached with GetProperty('nonexistant')
			// let's cause an empty string to be returned
			stringResultLen = 1;
		}
		
		// not all string result methods are guaranteed to add a null terminator
		stringResult.Allocate(stringResultLen + 1);
		paramsToSend[1] = CastPtrToSptr(stringResult.Get());
		
		if (functionInfo.paramType[0] == iface_length)
		{
			paramsToSend[0] = stringResultLen;
		}
	}
	
	sptr_t result = Host()->Send(pane, functionInfo.value, paramsToSend[0], paramsToSend[1]);

	// we'll give ownership of this object to the caller.
	PyObject* returnedString = stringResult.Get() ? PyString_FromString(stringResult.Get()) : NULL;
	if (functionInfo.returnType == iface_bool)
	{
		// return either (string, bool) or bool.
		if (returnedString)
			return Py_BuildValue("NO", (PyObject*)returnedString, (result ? Py_True : Py_False));
		else
			return Py_BuildValue("O", (result ? Py_True : Py_False));
	}
	else if (IFaceTypeIsNumeric(functionInfo.returnType) || functionInfo.returnType == iface_keymod)
	{
		// return either (string, int) or int.
		if (returnedString)
			return Py_BuildValue("Ni", (PyObject*)returnedString, (int)result);
		else
			return Py_BuildValue("i", (int)result);
	}
	else
	{
		// return either string or None.
		if (returnedString)
			return returnedString;
		else
			return Py_BuildValue("");
	}
}

PyObject* pyfun_pane_SendScintilla(PyObject*, PyObject* args)
{
	const char* functionName = NULL; // we don't own this.
	int nPane = -1;
	ExtensionAPI::Pane pane;
	PyObject *arg1=NULL, *arg2=NULL;
	if (!PyArg_ParseTuple(args, "is|OO", &nPane, &functionName, &arg1, &arg2) ||
		!functionName ||
		!GetPaneFromInt(nPane, &pane))
	{
		return NULL;
	}
	
	std::string nameFound;
	IFaceFunction functionInfo = SearchForFunction(functionName, nameFound);
	if (PyErr_Occurred())
	{
		return NULL;
	}
	else if (!functionInfo.name)
	{
		PyErr_SetString(PyExc_RuntimeError, "Function or property not found");
		return NULL;
	}
	else
	{
		return CallPaneFunction(pane, functionInfo, nameFound.c_str(), arg1, arg2);
	}
}

PyObject* pyfun_app_GetConstant(PyObject*, PyObject* args)
{
	const char* propName = NULL; // we don't own this.
	if (!PyArg_ParseTuple(args, "s", &propName) || !propName)
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
	return pyValueOut;
}

PyObject* pyfun_app_EnableNotification(PyObject*, PyObject* args)
{
	const char* eventName = NULL; // we don't own this.
	int value = 0;
	if (!PyArg_ParseTuple(args, "si", &eventName, &value) || !eventName)
	{
		return NULL;
	}
	
	cachePythonObjects.EnableNotification(eventName, !!value);
	return IncrefAndReturnNone();
}

PyObject* pyfun_app_SciteCommand(PyObject*, PyObject* args)
{
	const char* propName = NULL; // we don't own this.
	if (!PyArg_ParseTuple(args, "s", &propName) || !propName)
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
	return IncrefAndReturnNone();
}

PyObject* pyfun_app_UpdateStatusBar(PyObject*, PyObject* args)
{
	PyObject * pyObjBoolUpdate = NULL;
	if (!PyArg_ParseTuple(args, "O", &pyObjBoolUpdate))
	{
		return NULL;
	}

	bool bUpdateSlowData = pyObjBoolUpdate == Py_True;
	Host()->UpdateStatusBar(bUpdateSlowData);
	return IncrefAndReturnNone();
}

PyObject* pyfun_app_UserStripShow(PyObject*, PyObject* args)
{
	const char* s = NULL; // we don't own this.
	if (!PyArg_ParseTuple(args, "s", &s) || !s)
	{
		return NULL;
	}
	
	Host()->UserStripShow(s);
	return IncrefAndReturnNone();
}

PyObject* pyfun_app_UserStripSet(PyObject*, PyObject* args)
{
	int control = 0;
	const char* value = NULL; // we don't own this.
	if (!PyArg_ParseTuple(args, "is", &control, &value) || !value)
	{
		return NULL;
	}
	
	Host()->UserStripSet(control, value);
	return IncrefAndReturnNone();
}

PyObject* pyfun_app_UserStripSetList(PyObject*, PyObject* args)
{
	int control = 0;
	const char* value = NULL; // we don't own this.
	if (!PyArg_ParseTuple(args, "is", &control, &value) || !value)
	{
		return NULL;
	}
	
	Host()->UserStripSetList(control, value);
	return IncrefAndReturnNone();
}

PyObject* pyfun_app_UserStripGetValue(PyObject*, PyObject* args)
{
	int control = 0;
	if (!PyArg_ParseTuple(args, "i", &control))
	{
		return NULL;
	}
	
	const char *value = Host()->UserStripValue(control);
	if (value)
	{
		// give the caller ownership of this object.
		return PyString_FromString(value);
	}
	else
	{
		return IncrefAndReturnNone();
	}
}

// when recording location, the same filename will appear very often.
// let's save memory usage by using a set to de-dupe strings.
// references to elements in the unordered_set container remain valid in all cases, even after a rehash.
// if an actual pool is needed, see http://llvm.org/docs/doxygen/html/StringPool_8h_source.html
class SimpleStringPool
{
	std_unordered_set<std::string> _set;
	SimpleStringPool (const SimpleStringPool& other);
	SimpleStringPool& operator= (const SimpleStringPool& other);
	
public:
	SimpleStringPool() {}
	const std::string* Get(const char* s)
	{
		std_unordered_set<std::string>::iterator it = _set.find(s);
		if (it == _set.end())
		{
			it = _set.insert(s).first;
		}
		
		const std::string& ref = *it;
		return &ref;
	}
};

template <class T>
class UndoStack
{
	std::vector<T> _list;
	int _position;
	UndoStack (const UndoStack& other);
	UndoStack& operator= (const UndoStack& other);
	static const int MAXSIZE = UINT_MAX/8;

public:
	UndoStack() : _position(-1) {}
	void Add(T current)
	{
		if (_list.size() > MAXSIZE)
		{
			// we've reached the maximum size.
			return;
		}
		
		// if we are here after having called undo,
		// invalidate items higher on the stack
		int howManyToUndo = (_list.size() - _position) - 1;
		int first = _position + 1;
		_list.erase(_list.begin() + first, _list.begin() + first + howManyToUndo);

		// add to stack
		_list.push_back(current);
		_position = _list.size() - 1;
	}

	T PeekUndo()
	{
		if (_position >= 0)
			return _list[_position];
		else
			return T();
	}

	void Undo()
	{
		if (_position >= 0)
			--_position;
	}

	T PeekRedo()
	{
		// cast to signed int ok because of maximum size check in Add()
		if (_position + 1 <= (int)(_list.size()) - 1)
			return _list[_position + 1];
		else
			return T();
	}

	void Redo()
	{
		// cast to signed int ok because of maximum size check in Add()
		if (_position + 1 <= (int)(_list.size()) - 1)
			++_position;
	}
};

struct SavedLocation
{
	const std::string* filename;
	int lineNumber;
	SavedLocation() : filename(NULL), lineNumber(INT_MIN) {}
};

// saved location.
// tracks current file and caret location, so that the user can navigate back to the lines they were editing previously.
// implemented in C++ for performance; there is no onCaretChange event and the onUpdateUI event is quite chatty.
// possible future improvements:
// 	track location in untitled documents through buffer number
// 	track file save-as changes, possibly through buffer number
// 	use circular buffer with maximum size
// 	use Scintilla markers to save the correct locations even when preceding lines of text are added.
class SavedLocationManager
{
	SimpleStringPool _stringpool;
	UndoStack<SavedLocation> _stack;
	int _prevPos;
	int _prevLine;
	const std::string* _currentFile;
	int _lineWeJustSet;
	const std::string* _fileWeJustSet;
	SavedLocationManager (const SavedLocationManager& other);
	SavedLocationManager& operator= (const SavedLocationManager& other);

	bool isTooCloseToExisting(int line)
	{
		// if the user only moved one line away, don't need to record a new entry.
		SavedLocation lastLocation = _stack.PeekUndo();
		bool ret = (lastLocation.filename == _currentFile) && (lastLocation.lineNumber == line - 1 ||
			lastLocation.lineNumber == line ||lastLocation.lineNumber == line + 1);
		return ret;
	}
	
	bool isOneWeJustSet(int line)
	{
		// is this "move" the result of the move we just sent to SciTE? if so, don't add to the stack.
		bool ret = (_currentFile && _currentFile == _fileWeJustSet && line == _lineWeJustSet);
		return ret;
	}
	
	void addToStack(int line)
	{
		if (!isOneWeJustSet(line) && !isTooCloseToExisting(line))
		{
			SavedLocation location;
			location.filename = _currentFile;
			location.lineNumber = line;
			_stack.Add(location);
		}
	}
	
public:
	SavedLocationManager() : _prevPos(INT_MIN), _prevLine(INT_MIN), _currentFile(NULL),
		_lineWeJustSet(INT_MIN), _fileWeJustSet(NULL)
	{
	}
	
	void goPrevLocation(const std::string* &file, int& line)
	{
		SavedLocation lastLocation = _stack.PeekUndo();
		if (lastLocation.filename)
		{
			file = _fileWeJustSet = lastLocation.filename;
			line = _lineWeJustSet = lastLocation.lineNumber;
			goLocation(file, line);
			_stack.Undo();
		}
	}
	
	void goNextLocation(const std::string* &file, int& line)
	{
		SavedLocation nextLocation = _stack.PeekRedo();
		if (nextLocation.filename)
		{
			file = _fileWeJustSet = nextLocation.filename;
			line = _lineWeJustSet = nextLocation.lineNumber;
			goLocation(file, line);
			_stack.Redo();
		}
	}
	
	void goLocation(const std::string* file, int line)
	{
		if (file != _currentFile)
		{
			SciteOpenFile(file->c_str());
		}
		
		const ExtensionAPI::Pane pane = ExtensionAPI::paneEditor;
		Host()->Send(pane, SCI_GOTOLINE, line, 0);
	}
	
	void onChangeCurrentFile()
	{
		if (Host())
		{
			// both path and name must be set, because sometimes an untitled document has a non-empty path.
			std::string filepath = Host()->Property("FilePath");
			std::string filename = Host()->Property("FileNameExt");
			if (filepath.length() && filename.length())
			{
				_currentFile = _stringpool.Get(filepath.c_str());
			}
			else
			{
				// we can't track location in untitled documents
				_currentFile = NULL;
			}
		}
	}	
	
	void onUpdateUI()
	{
		if (Host() && _currentFile)
		{
			// if it's the same position, or the same line, don't add a new entry.
			const ExtensionAPI::Pane pane = ExtensionAPI::paneEditor;
			int pos = Host()->Send(pane, SCI_GETSELECTIONSTART, 0, 0);
			if (pos != _prevPos)
			{
				int line = Host()->Send(pane, SCI_LINEFROMPOSITION, pos, 0);
				if (line != _prevLine)
				{
					addToStack(line);
					_prevLine = line;
				}
				
				_prevPos = pos;
			}
		}
	}
} savedLocationManager;

void onUpdateUI()
{
	savedLocationManager.onUpdateUI();
}

void onChangeCurrentFile()
{
	savedLocationManager.onChangeCurrentFile();
}

PyObject* pyfun_app_GetNextOrPreviousLocation(PyObject*, PyObject* args)
{
	const std::string* file = NULL;
	int line = 0;
	int isNext = 0;
	if (!PyArg_ParseTuple(args, "i", &isNext))
	{
		return NULL;
	}
	
	if (isNext)
		savedLocationManager.goNextLocation(file, line);
	else
		savedLocationManager.goPrevLocation(file, line);
	
	if (file)
		return Py_BuildValue("si", file->c_str(), line);
	else
		return Py_BuildValue("OO", Py_None, Py_None);
}

static PyMethodDef methodsExportedToPython[] =
{
	{"LogStdout", pyfun_LogStdout, METH_VARARGS, "Redirects stdout to output pane"},
	{"app_Trace", pyfun_LogStdout, METH_VARARGS, ""},
	{"app_MsgBox", pyfun_MessageBox, METH_VARARGS, ""},
	{"app_OpenFile", pyfun_SciteOpenFile, METH_VARARGS, ""},
	{"app_GetProperty", pyfun_GetProperty, METH_VARARGS, "Get SciTE Property"},
	{"app_SetProperty", pyfun_SetProperty, METH_VARARGS, "Set SciTE Property"},
	{"app_UnsetProperty", pyfun_UnsetProperty, METH_VARARGS, "Unset SciTE Property"},
	{"app_GetConstant", pyfun_app_GetConstant, METH_VARARGS, ""},
	{"app_EnableNotification", pyfun_app_EnableNotification, METH_VARARGS, ""},
	{"app_UpdateStatusBar", pyfun_app_UpdateStatusBar, METH_VARARGS, ""},
	{"app_UserStripShow", pyfun_app_UserStripShow, METH_VARARGS, ""},
	{"app_UserStripSet", pyfun_app_UserStripSet, METH_VARARGS, ""},
	{"app_UserStripSetList", pyfun_app_UserStripSetList, METH_VARARGS, ""},
	{"app_UserStripGetValue", pyfun_app_UserStripGetValue, METH_VARARGS, ""},
	{"app_GetNextOrPreviousLocation", pyfun_app_GetNextOrPreviousLocation, METH_VARARGS, ""},
	{"app_SciteCommand", pyfun_app_SciteCommand, METH_VARARGS, ""},
	{"pane_Append", pyfun_pane_Append, METH_VARARGS, ""},
	{"pane_Insert", pyfun_pane_Insert, METH_VARARGS, ""},
	{"pane_Remove", pyfun_pane_Remove, METH_VARARGS, ""},
	{"pane_Textrange", pyfun_pane_TextRange, METH_VARARGS, ""},
	{"pane_FindText", pyfun_pane_FindText, METH_VARARGS, ""},
	{"pane_SendScintilla", pyfun_pane_SendScintilla, METH_VARARGS, ""},
	{NULL, NULL, 0, NULL}
};

void runPythonString(const char* s)
{
	if (PyRun_SimpleString(s) != 0)
	{
		trace_error("Python extension encountered error while initializing, \n", s);
		PyErr_Print();
	}
}

void PythonExtension::SetupPythonNamespace()
{
#ifdef _WIN32
	std::string SciTEHome(_host->Property("SciteDefaultHome"));
	const char* pythonHome = SciTEHome.c_str();
	const char* dirSep = "\\";
	const char* binaryName = "SciTE.exe";
#else
	const char* pythonHome = SYSCONF_PATH;
	const char* dirSep = "/";
	const char* binaryName = "SciTE_with_python";
#endif
	
	// tell python to skip running 'import site'
	Py_NoSiteFlag = 1;
	
	// set home and argv[0]
	std::string programName = pythonHome;
	programName += dirSep;
	programName += binaryName;
	cachePythonObjects.setPythonHomeAndProgramName(pythonHome, programName.c_str());
	
	// initialize without signal handling
	Py_InitializeEx(0);
	
	// add our C module
	Py_InitModule("SciTEModule", methodsExportedToPython);
	
	// add to system path. 'sys' is built-in, no worry of importing the wrong sys
	std::string pathToImport = "import sys; sys.path.insert(0, \"";
	pathToImport += pythonHome;
	pathToImport += "\");";
	runPythonString(pathToImport.c_str());
	pathToImport = "import sys; sys.path.insert(0, \"";
	pathToImport += pythonHome;
	pathToImport += dirSep;
	pathToImport += "python27.zip\");";
	runPythonString(pathToImport.c_str());
	
#ifndef _WIN32
	// without this, warning seen "no codec search functions registered"
	runPythonString("import codecs; import encodings");
#endif

	runPythonString(
		"import SciTEModule\n"
		"import sys\n"
		"class StdoutCatcher:\n"
		"    def write(self, s):\n"
		"        SciTEModule.LogStdout(s)\n"
		"sys.stdout = StdoutCatcher()\n"
		"sys.stderr = StdoutCatcher()\n"
	);
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

void trace(const char* text1, const char* text2)
{
	if (Host())
	{
		if (text1)
			Host()->Trace(text1);
		
		if (text2)
			Host()->Trace(text2);
	}
}

void trace_error(const char* text1, const char* text2)
{
	trace(">Error in Python extension.");
	trace(text1, text2);
	trace("\n.");
}

void trace(const char* text, int n)
{
	std::ostringstream stm;
	stm << text << n;
	trace(stm.str().c_str());
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

void assertEq(int expected, int received)
{
	if (expected != received)
	{
		trace("\nassertion failed, expected ", expected);
		trace(" got ", received);
	}
}

void verifyConstantsTableOrder()
{
	// binary search requires items to be sorted, so verify sort order
	for (unsigned int i = 0; i < PythonExtension::constantsTableLen - 1; i++)
	{
		const char* first = PythonExtension::constantsTable[i].name;
		const char* second = PythonExtension::constantsTable[i + 1].name;
		if (!(strcmp(first, second) < 0))
		{
			trace("Warning, unsorted.");
			trace(first, second);
		}
	}
	
	// test undo stack.
	UndoStack<int> stack;
	assertEq(0, stack.PeekUndo());
	assertEq(0, stack.PeekRedo());
	stack.Add(1);
	assertEq(1, stack.PeekUndo());
	stack.Add(2);
	assertEq(2, stack.PeekUndo());
	stack.Add(3);
	assertEq(3, stack.PeekUndo());
	stack.Add(4);
	assertEq(4, stack.PeekUndo());
	stack.Undo();
	assertEq(3, stack.PeekUndo());
	stack.Undo();
	assertEq(2, stack.PeekUndo());
	stack.Undo();
	assertEq(1, stack.PeekUndo());
	stack.Redo();
	assertEq(2, stack.PeekUndo());
	stack.Redo();
	assertEq(3, stack.PeekUndo());
	stack.Add(40); // not at the top of stack, will overwrite other values
	assertEq(40, stack.PeekUndo());
	stack.Add(50);
	assertEq(50, stack.PeekUndo());
	stack.Undo();
	assertEq(40, stack.PeekUndo());
	stack.Undo();
	assertEq(3, stack.PeekUndo());
	stack.Undo();
	assertEq(2, stack.PeekUndo());
	stack.Undo();
	assertEq(1, stack.PeekUndo());
	stack.Undo();
	assertEq(0, stack.PeekUndo());
	stack.Undo();
	assertEq(0, stack.PeekUndo());
}

static IFaceConstant rgFriendlyNamedIDMConstants[] =
{
	//++Autogenerated -- run src/scite/scite/scripts/PythonExtensionGenTable.py and paste the results here
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
	{"OpenSelectedPlaceholder", IDM_OPENSELECTED_PLACEHOLDER},
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
const size_t PythonExtension::constantsTableLen = countof(rgFriendlyNamedIDMConstants);

