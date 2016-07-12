// SciTE Python Extension
// Ben Fisher, 2011

#include "Scite.h"
#include "Scintilla.h"
#include "Extender.h"
#include "SString.h"
#include "SciTEKeys.h"
#include "IFaceTable.h"

#include "..\python\include\python.h"
#include "IFaceTable.h"

#include <string>
#include <vector>
#include <map>

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
			Py_DECREF(_obj);
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

class PythonExtension : public Extension
{
public:
	static const IFaceConstant* const constantsTable;
	static const size_t constantsTableLen;
	static PythonExtension &Instance();
	void WriteText(const char* text);
	ExtensionAPI* GetHost();
	bool FInitialized();
	virtual ~PythonExtension();

	virtual bool Initialise(ExtensionAPI* host);
	virtual bool Finalise();
	virtual bool Clear();
	virtual bool Load(const char* fileName);
	virtual bool InitBuffer(int index);
	virtual bool ActivateBuffer(int index);
	virtual bool RemoveBuffer(int index);
	virtual bool OnExecute(const char* s);

	// file events
	virtual bool OnOpen(const char* fileName);
	virtual bool OnClose(const char* filename);
	virtual bool OnSwitchFile(const char* fileName);
	virtual bool OnBeforeSave(const char* fileName);
	virtual bool OnSave(const char* fileName);
	virtual bool OnSavePointReached();
	virtual bool OnSavePointLeft();

	// input events
	virtual bool OnChar(char ch);
	virtual bool OnKey(int keycode, int modifiers);
	virtual bool OnDoubleClick();
	virtual bool OnMarginClick();
	virtual bool OnDwellStart(int pos, const char* word);

	// misc events
	virtual bool OnUserListSelection(int type, const char* selection);

private:
	ExtensionAPI* _host;
	bool _pythonInitialized;

	void WriteLog(const char* error);
	bool WriteError(const char* error);
	bool WriteError(const char* error, const char* error2);
	bool RunCallback(const char* nameOfFunction, int nArgs, const char* arg1);
	bool RunCallbackArgs(const char* nameOfFunction, PyObject* pArgsBorrowed);
	void InitializePython();
	void SetupPythonNamespace();

	PythonExtension();
	PythonExtension(const PythonExtension &); // Disable copy ctor
	void operator=(const PythonExtension &); // Disable operator=
};
