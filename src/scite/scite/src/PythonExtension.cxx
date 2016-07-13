



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



static PyMethodDef methods_LogStdout[] =
{
	{"LogStdout", pyfun_LogStdout, METH_VARARGS, "Logs stdout"},
	{"app_Trace", pyfun_LogStdout, METH_VARARGS, "(for compat with scite-lua scripts)"},
	{"app_MsgBox", pyfun_MessageBox, METH_VARARGS, ""},
	{"app_OpenFile", pyfun_SciteOpenFile, METH_VARARGS, ""},
	{"app_GetProperty", pyfun_GetProperty, METH_VARARGS, "Get SciTE Property"},
	{"app_SetProperty", pyfun_SetProperty, METH_VARARGS, "Set SciTE Property"},
	{"app_UnsetProperty", pyfun_UnsetProperty, METH_VARARGS, "Unset SciTE Property"},
	
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






