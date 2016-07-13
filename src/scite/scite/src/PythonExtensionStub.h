// SciTE Python Extension
// Ben Fisher, 2016

#include <string>
#include "Scite.h"
#include "Scintilla.h"
#include "Extender.h"

#include "SciTEKeys.h"
#include "IFaceTable.h"

#include <vector>
#include <map>

class PythonExtension: public Extension
{
public:
	virtual ~PythonExtension();
	static PythonExtension &Instance();
	void WriteText(const char* text);
	ExtensionAPI* GetHost();
	bool FInitialized();

	virtual bool Initialise(ExtensionAPI* host_);
	virtual bool Finalise();
	virtual bool Clear();
	virtual bool Load(const char* filename);
	virtual bool InitBuffer(int);
	virtual bool ActivateBuffer(int);
	virtual bool RemoveBuffer(int);
	virtual bool OnOpen(const char*);
	virtual bool OnSwitchFile(const char*);
	virtual bool OnBeforeSave(const char*);
	virtual bool OnSave(const char*);
	virtual bool OnChar(char);
	virtual bool OnExecute(const char*);
	virtual bool OnSavePointReached();
	virtual bool OnSavePointLeft();
	virtual bool OnStyle(unsigned int, int, int, StyleWriter*);
	virtual bool OnDoubleClick();
	virtual bool OnUpdateUI();
	virtual bool OnMarginClick();
	virtual bool OnMacro(const char*, const char*);
	virtual bool OnUserListSelection(int, const char*);
	virtual bool SendProperty(const char*);
	virtual bool OnKey(int, int);
	virtual bool OnDwellStart(int, const char*);
	virtual bool OnClose(const char*);
	virtual bool OnUserStrip(int control, int change);
	virtual bool NeedsOnClose();
	
	static void WriteLog(const char* error);
	static bool WriteError(const char* error);
	static bool WriteError(const char* error, const char* error2);

private:
	ExtensionAPI* _host;
	bool _pythonInitialized;

	void InitializePython();
	void SetupPythonNamespace();
	

	// Copying is unsupported.
	PythonExtension();
	PythonExtension(const PythonExtension & copy);
	PythonExtension & operator=(const PythonExtension & copy);
};


