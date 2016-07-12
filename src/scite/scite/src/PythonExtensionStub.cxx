// SciTE Python Extension
// Ben Fisher, 2011

#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "PythonExtensionStub.h"

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


PyObject* pyfun_LogStdout(PyObject* self, PyObject* args)
{
	char* msg = NULL; // we don't own this.
	if (PyArg_ParseTuple(args, "s", &msg)) 
	{
		MessageBoxA(0, msg, "from python", 0);
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

const char* demoProgram = "f = open(r'C:\\b\\documents\\test.txt', 'w') \nf.write('test') \nf.close()";

void runPythonTest()
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
	
	ret = PyRun_SimpleString(demoProgram);

	if (ret != 0)
	{
		MessageBoxA(0, "PyRun_SimpleString returned failure", "", 0);
		PyErr_Print();
	}
	else
	{
		MessageBoxA(0, "PyRun_SimpleString returned success", "", 0);
	}
}
