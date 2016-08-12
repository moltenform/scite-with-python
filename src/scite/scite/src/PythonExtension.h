// SciTE Python Extension
// Ben Fisher, 2016

struct IFaceConstant;

enum EventNumber
{
	EventNumber_OnStart = 0,
	EventNumber_OnOpen,
	EventNumber_OnBeforeSave,
	EventNumber_OnSave,
	EventNumber_OnSavePointReached,
	EventNumber_OnSavePointLeft,
	EventNumber_OnDoubleClick,
	EventNumber_OnMarginClick,
	EventNumber_OnClose,
	EventNumber_OnChar,
	EventNumber_OnUserListSelection,
	EventNumber_OnKey,
	EventNumber_OnUserStrip,
	EventNumber_OnFileChange,
	EventNumber_LEN
};

class PythonExtension : public Extension
{
public:
	virtual ~PythonExtension();
	static PythonExtension &Instance();
	void WriteText(const char* text);
	ExtensionAPI* GetHost();

	virtual bool Initialise(ExtensionAPI*);
	virtual bool Finalise();
	virtual bool Clear();
	virtual bool Load(const char*);
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
	virtual bool OnUserStrip(int, int);
	virtual bool NeedsOnClose();
	bool OnFileChange();

	static const IFaceConstant* const constantsTable;
	static const size_t constantsTableLen;

private:
	ExtensionAPI* _host;

	void InitializePython();
	void SetupPythonNamespace();

	// Copying is unsupported.
	PythonExtension();
	PythonExtension(const PythonExtension & copy);
	PythonExtension & operator=(const PythonExtension & copy);
};


