// SciTE Python Extension
// Ben Fisher, 2011

#include <string>
#include "Scite.h"
#include "Scintilla.h"
#include "Extender.h"

#include "SciTEKeys.h"
#include "IFaceTable.h"

#include "..\python\include\python.h"
#include "IFaceTable.h"

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
