
# shows current keyboard bindings, includes
# commands, languages, user.shortcuts, and menukey changes
# from properties files.
#
# also, performs many checks to see if keyhandling logic has changed
# -- this script intentionally throws errors if keyhandling logic has been updated,
# -- in most cases, the response is just to copy/paste the new code into one of the excerpts below.
#
# this script requires SciTE+Scintilla sources to be present.
# place this script in the /scite/src/scripts directory
# running it will produce the two files
# ../bin/doc/CurrentBindingsGtk.html
# ../bin/doc/CurrentBindingsWin32.html

import os
from ShowBindings import *

def readFromSciTEResMenuEntry(bindings, stack, parts, mapUserDefinedKeys):
	nameAndAccel = parts[0].lstrip('"').rstrip('\t", ')
	name, accel = nameAndAccel.split('\\t') if '\\t' in nameAndAccel else (nameAndAccel, '')
	menupath = '/'.join(stack) + '/' + name
	userDefined = mapUserDefinedKeys.get(normalizeMenuPath(menupath, 'win32'), '')
	name = name.replace('&', '')
	
	if userDefined != '""' and userDefined != 'none':
		accel = userDefined or accel
		if accel:
			priority = 10 if userDefined else 75
			bindings.append(KeyBinding(
				'menu text or user-defined', name, accel, priority=priority, platform='win32'))

def readFromSciTEResMenus(bindings, mapUserDefinedKeys):
	start = '''SciTE MENU'''
	mustContain = '''	MENUITEM "&About SciTE",			IDM_ABOUT'''
	stack = []
	lines = retrieveCodeLines('../win32/SciTERes.rc', start, 'END', mustContain)
	for line in lines:
		line = line.strip()
		if line.startswith('POPUP '):
			stack.append(line.split()[1].strip('"'))
		elif line and line.split()[0] == 'END':
			stack.pop()
		elif line.startswith('MENUITEM ') and not line.startswith('MENUITEM SEPARATOR'):
			line = line[len('MENUITEM '):]
			parts = line.split(',')
			if len(parts) != 2:
				raise RuntimeError('line started with MENUITEM but did not have 2 parts ' + line)
			else:
				readFromSciTEResMenuEntry(bindings, stack, parts, mapUserDefinedKeys)
	
	assert len(stack) == 0

def readNewCommandsFromProperties(results, props):
	for key in props.props:
		matchObj = re.match(r'^customcommand\.([^.]+)\.name', key)
		if matchObj:
			name = props.Expanded(props.GetString(key))
			commandId = matchObj.group(1)
			setShortcutKey = 'customcommand.' + commandId + '.shortcut'
			setShortcutValue = props.Expanded(props.GetString(setShortcutKey))
			if name and setShortcutValue:
				results.append(KeyBinding('properties command', name, setShortcutValue, priority=50, platform='any'))

def getGtkBindings(results, props, mapUserDefinedKeys):
	detectCodeChanges('../gtk/SciTEGTK.cxx', getFragment('SciTEGTK::Key'),
		SciTEGTK_Key_MustInclude)
	
	# --- gint SciTEGTK::Key(GdkEventKey *event) {
	# --- send to extension 			extender->OnKey (priority=20)
	# --- check the "kmap" list 	commandID = kmap[i].msg (priority=30)
	addBindingsManual(results, gtkKmapBindings)
	
	# --- check the language menu	commandID = IDM_LANGUAGE + j (priority=40)
	# --- check the tools menu			MenuCommand(IDM_TOOLS + tool_i) (priority=50)
	# --- check user.shortcuts			shortCutItemList[cut_i].menuCommand (priority=60)
	readFromProperties(results, props)
	readNewCommandsFromProperties(results, props)
	
	# --- check UI strips			findStrip.KeyDown(event), replaceStrip, userStrip (priority=70)
	# --- FindStrip: Alt-initial letter
	# --- ReplaceStrip: Alt-initial letter
	# --- UserStrip: Escape to close, Alt-initial letter of label to hit a button or set focus
	detectCodeChanges('../gtk/SciTEGTK.cxx', getFragment('FindStrip::EscapeSignal'))
	detectCodeChanges('../gtk/SciTEGTK.cxx', getFragment('ReplaceStrip::EscapeSignal'))
	detectCodeChanges('../gtk/SciTEGTK.cxx', getFragment('UserStrip::EscapeSignal'))
	detectCodeChanges('../gtk/SciTEGTK.cxx', getFragment('SciTEGTK::FindIncrementEscapeSignal'))
	detectCodeChanges('../gtk/Widget.cxx', getFragment('gtkStrip::KeyDown'))
	
	# --- check menu items		SciTEItemFactoryEntry menuItems (priority=80)
	readFromSciTEItemFactoryList(results, mapUserDefinedKeys)

def getWindowsBindings(results, props, mapUserDefinedKeys):
	detectCodeChanges('../win32/SciTEWin.cxx', getFragment('SciTEWin::KeyDown'))
	
	# --- LRESULT SciTEWin::KeyDown(WPARAM wParam) {
	# --- send to extension 			extender->OnKey (priority=20)
	# --- check the language menu	commandID = IDM_LANGUAGE + j (priority=40)
	# --- check the tools menu			MenuCommand(IDM_TOOLS + tool_i) (priority=50)
	# --- check user.shortcuts			shortCutItemList[cut_i].menuCommand (priority=60)
	readFromProperties(results, props)
	readNewCommandsFromProperties(results, props)
	
	# --- check UI strips
	# --- FindStrip::KeyDown
	# --- ReplaceStrip::KeyDown
	# --- UserStrip: Escape to close, Alt-initial letter of label to hit a button or set focus
	detectCodeChanges('../win32/SciTEWinDlg.cxx', getFragment('SciTEWin::ModelessHandler'))
	detectCodeChanges('../win32/Strips.cxx', getFragment('win32Strip::KeyDown'))
	
	# --- std::vector<std::pair<int, int>>::iterator itAccels; (priority=75)
	# --- SciteRes.rc gives menu items names like New\tCtrl+N
	# --- previously the \tCtrl+N was purely decorational, but now code in
	# --- SciTEWin::LocaliseMenuAndReadAccelerators parses it out and makes it a real shortcut.
	readFromSciTEResMenus(results, mapUserDefinedKeys)
	
	# --- accelerator table			SciTERes.rc accelerator (priority=80)
	readFromSciTEResAccelTable(results)

def getScintillaBindings(results, props, priority):
	detectCodeChanges('../../scintilla/src/Editor.cxx', getFragment('scintillaKeyHandlerMethodExpectedText'),
		scintillaKeyHandlerMethodExpectedTextMustInclude)
	detectCodeChanges('../src/SciTEProps.cxx', getFragment('callsToAssignKey'))
	detectCodeChanges('../src/SciTEBase.cxx', getFragment('sciteBaseCallAssignKey'))
	checkForNewIfDefsInKeyMap()
	addCallsToAssignKeyBindings(results, props)
	readFromScintillaKeyMap(results, priority)

def processDuplicatesInOutputFile(filepath, adjustForAesthetics):
	newContents = []
	overridden = []
	lastRowCells = []
	for line in readall(filepath).replace('\r\n', '\n').split('\n'):
		if adjustForAesthetics and line in filterLinesFromOutputForAesthetics:
			continue
		
		if line.startswith('<tr><td>'):
			lineCells = line.split('</td><td>')
			if lineCells == lastRowCells:
				# accels and description are the same, so remove the duplicate row
				newContents.append('')
			elif lineCells[0:2] == lastRowCells[0:2] and '*' not in lineCells[3]:
				# accels are the same and it's not scoped to a file type, so move it to overrides.
				overridden.append(line)
			else:
				newContents.append(line)
			lastRowCells = line.split('</td><td>')
		elif overridden and not adjustForAesthetics and line == '</table>':
			newContents.append('<tr><td colspan="4" align="center"><br />Bindings that were overridden<br /><br /></td></tr>')
			for override in overridden:
				newContents.append(override)
			newContents.append(line)
		else:
			newContents.append(line)

	with open(filepath, 'w') as out:
		out.write('\n'.join(newContents))

def mainWithPython(propertiesMain, propertiesUser, adjustForAesthetics, writeMdLocation):
	import sys
	if sys.version_info[0] != 2:
		print('currently, this script is not supported in python 3')
		return
	
	assert os.path.isfile('../src/PythonExtension.cxx'), 'Did not see PythonExtension, please run ShowBindings.py instead.'
	checkForAnyLogicChanges()
	for platform in ('gtk', 'win32'):
		# we've changed SciTE logic for SciTEGlobal.properties, it is now in a subdirectory.
		propertiesMainParent = os.path.split(propertiesMain)[0]
		assert os.path.split(propertiesMainParent)[1] == 'properties', 'Expected SciTEGlobal.properties to be in a directory called properties'
		props = getAllProperties(propertiesMain, propertiesUser, platform, overrideDir=os.path.split(propertiesMainParent)[0])
		
		scintillaPriority = 100
		platformCapitalized = platform[0].upper() + platform[1:]
		outputFile = '../bin/doc/CurrentBindings%s.html' % platformCapitalized
		mapUserDefinedKeys = readUserDefinedKeys(props)
		bindings = []
		getScintillaBindings(bindings, props, scintillaPriority)
		expectedSets = ['SciTEProps.cxx AssignKey', 'properties *language', 'properties user.shortcuts',
			'properties command (implicit)', 'properties command', 'Scintilla keymap']
		if platform == 'gtk':
			getGtkBindings(bindings, props, mapUserDefinedKeys)
			expectedSets.extend(['KeyToCommand kmap[]', 'SciTEItemFactoryEntry or user-defined'])
		else:
			getWindowsBindings(bindings, props, mapUserDefinedKeys)
			expectedSets.extend(['SciTERes accel', 'menu text or user-defined'])
		
		bindings.reverse() # within a priority, generally the binding defined last wins.
		bindings.sort(key=lambda obj: obj.getSortKey())
		writeOutputFile(bindings, outputFile, includeDuplicates=True)
		processDuplicatesInOutputFile(outputFile, adjustForAesthetics)
		setsSeen = {item.setName: 1 for item in bindings}
		if set(expectedSets) != set(key for key in setsSeen):
			warn('''Warning: saw no bindings from expected sets %s, or saw unexpected %s''' %
				(set(expectedSets) - set(key for key in setsSeen),
				set(key for key in setsSeen) - set(expectedSets)))
		makeVersionForMd(outputFile, writeMdLocation)
		print('wrote to ' + outputFile)

def makeVersionForMd(htmlFile, writeMdLocation):
	# pull straight from the .html file, not the bindings list, because we've filtered it via adjustForAesthetics
	assert htmlFile.endswith('.html')
	mdFile = htmlFile.replace('.html', '_worseterms_reference.txt')
	lines = getVersionForMd(htmlFile)
	with open(mdFile, 'w') as f:
		f.write('<a href="index.html" style="color:black; text-decoration:underline">Back</a>\n')
		f.write('\n')
		f.write('''<table>
<thead>
<tr>
<th>Keyboard Shortcut (%os)</th>
<th>Result</th>
</tr>
</thead>
<tbody>'''.replace('%os', ('Linux' if 'Gtk' in htmlFile else 'Windows')))
		f.write('\n'.join(lines))
		f.write('\n</tbody></table>')
		f.write('\n')
		f.write('<p>&nbsp;</p><a href="index.html" style="color:black; text-decoration:underline">Back</a>')
		f.write('\n')

	comparisonShort = 'keyslinux_worseterms_reference.txt' if 'Gtk' in htmlFile else 'keyswin_worseterms_reference.txt'
	mdOutShort = 'keyslinux.mdnotjekyll' if 'Gtk' in htmlFile else 'keyswin.mdnotjekyll'
	comparison = os.path.join(writeMdLocation, comparisonShort)
	allLatest = open(mdFile).read()
	allReference = open(comparison).read()
	if allLatest != allReference:
		print(os.path.abspath(mdFile))
		print('is not the same as')
		print(os.path.abspath(comparison))
		print('please diff these two files and make the corresponding updates to')
		print('BOTH ' + comparisonShort + ' and ' + mdOutShort + '\n\n')

def getVersionForMd(htmlFile):
	lines = []
	htmlLines = open(htmlFile)
	for ln in htmlLines:
		ln = ln.strip()
		if ln.startswith('<tr>') and ln.endswith('</tr>'):
			mark = '@@@@@'
			ln = ln.replace('<tr>', '').replace('</tr>', '').replace('</td><td>', mark).replace('<td>', '').replace('</td>', '')
			cells = ln.split(mark)
			lines.append('<tr>')
			lines.append('<td>' + cells[1] + '</td>')
			lines.append('<td>' + cells[2] + '</td>')
			lines.append('</tr>')

	htmlLines.close()
	return lines

def checkForNewIfDefsInKeyMap():
	start = '''const KeyToCommand KeyMap::MapDefault[] = {'''
	txt = '\n'.join(retrieveCodeLines('../../scintilla/src/KeyMap.cxx', start, '};'))
	txt = txt.replace('''#if OS_X_KEYS
	{SCK_DOWN,		SCI_CTRL,	SCI_DOCUMENTEND},
	{SCK_DOWN,		SCI_CSHIFT,	SCI_DOCUMENTENDEXTEND},
	{SCK_UP,		SCI_CTRL,	SCI_DOCUMENTSTART},
	{SCK_UP,		SCI_CSHIFT,	SCI_DOCUMENTSTARTEXTEND},
	{SCK_LEFT,		SCI_CTRL,	SCI_VCHOME},
	{SCK_LEFT,		SCI_CSHIFT,	SCI_VCHOMEEXTEND},
	{SCK_RIGHT,		SCI_CTRL,	SCI_LINEEND},
	{SCK_RIGHT,		SCI_CSHIFT,	SCI_LINEENDEXTEND},
#endif'''.replace('\r\n', '\n').replace('\n\t', '\n    '), '')
	txt = txt.replace('''#if OS_X_KEYS
	{'Z', 			SCI_CSHIFT,	SCI_REDO},
#else
	{'Y', 			SCI_CTRL,	SCI_REDO},
#endif'''.replace('\r\n', '\n').replace('\n\t', '\n    '), '')
	warnIfTermsSeen('../../scintilla/src/KeyMap.cxx', txt, ['#ifdef', '#else', '#endif'])

fragments = []
fragments.append(['SciTEGTK::Key', 'gtk/SciTEGTK.cxx', r'''class KeyToCommand {
public:
	int modifiers;
	unsigned int key;	// For alphabetic keys has to match the shift modifier.
	int msg;
};

enum {
    m__ = 0,
    mS_ = GDK_SHIFT_MASK,
    m_C = GDK_CONTROL_MASK,
    mSC = GDK_SHIFT_MASK | GDK_CONTROL_MASK
};

static KeyToCommand kmap[] = {
                                 {m_C, GKEY_Tab, IDM_NEXTFILESTACK},
                                 {mSC, GKEY_ISO_Left_Tab, IDM_PREVFILESTACK},
                                 {m_C, GKEY_KP_Enter, IDM_COMPLETEWORD},
                                 {GDK_MOD1_MASK, GKEY_F2, IDM_BOOKMARK_NEXT_SELECT},
                                 {GDK_MOD1_MASK|GDK_SHIFT_MASK, GKEY_F2, IDM_BOOKMARK_PREV_SELECT},
                                 {m_C, GKEY_F3, IDM_FINDNEXTSEL},
                                 {mSC, GKEY_F3, IDM_FINDNEXTBACKSEL},
                                 {m_C, GKEY_F4, IDM_CLOSE},
                                 {m_C, 'j', IDM_PREVMATCHPPC},
                                 {mSC, 'J', IDM_SELECTTOPREVMATCHPPC},
                                 {m_C, 'k', IDM_NEXTMATCHPPC},
                                 {mSC, 'K', IDM_SELECTTONEXTMATCHPPC},
                                 {m_C, GKEY_KP_Multiply, IDM_EXPAND},
                                 {0, 0, 0},
                             };

inline bool KeyMatch(const char *menuKey, int keyval, int modifiers) {
	return SciTEKeys::MatchKeyCode(
		SciTEKeys::ParseKeyCode(menuKey), keyval, modifiers);
}

gint SciTEGTK::Key(GdkEventKey *event) {
	//printf("S-key: %d %x %x %x %x\n",event->keyval, event->state, GDK_SHIFT_MASK, GDK_CONTROL_MASK, GDK_F3);
	if (event->type == GDK_KEY_RELEASE) {
		if (event->keyval == GKEY_Control_L || event->keyval == GKEY_Control_R) {
			g_signal_stop_emission_by_name(
			    G_OBJECT(PWidget(wSciTE)), "key-release-event");
			this->EndStackedTabbing();
			return 1;
		} else {
			return 0;
		}
	}

	int modifiers = event->state & (GDK_SHIFT_MASK | GDK_CONTROL_MASK | GDK_MOD1_MASK | GDK_MOD4_MASK);

	int cmodifiers = // modifier mask for Lua extension
		((event->state & GDK_SHIFT_MASK)   ? SCMOD_SHIFT : 0) |
		((event->state & GDK_CONTROL_MASK) ? SCMOD_CTRL  : 0) |
		((event->state & GDK_MOD1_MASK)    ? SCMOD_ALT   : 0);
	if (extender && extender->OnKey(event->keyval, cmodifiers))
		return 1;

	int commandID = 0;
	for (int i = 0; kmap[i].msg; i++) {
		if ((event->keyval == kmap[i].key) && (modifiers == kmap[i].modifiers)) {
			commandID = kmap[i].msg;
		}
	}
	if (!commandID) {
		// Look through language menu
		for (unsigned int j = 0; j < languageMenu.size(); j++) {
			if (KeyMatch(languageMenu[j].menuKey.c_str(), event->keyval, modifiers)) {
				commandID = IDM_LANGUAGE + j;
			}
		}
	}
	if (commandID) {
		Command(commandID);
	}
	if ((commandID == IDM_NEXTFILE) ||
		(commandID == IDM_PREVFILE) ||
		(commandID == IDM_NEXTFILESTACK) ||
		(commandID == IDM_PREVFILESTACK)) {
		// Stop the default key processing from moving the focus
		g_signal_stop_emission_by_name(
		    G_OBJECT(PWidget(wSciTE)), "key_press_event");
	}

	// check tools menu command shortcuts
	for (int tool_i = 0; tool_i < toolMax; ++tool_i) {
		GtkWidget *item = MenuItemFromAction(IDM_TOOLS + tool_i);
		if (item) {
			long keycode = GPOINTER_TO_INT(g_object_get_data(G_OBJECT(item), "key"));
			if (keycode && SciTEKeys::MatchKeyCode(keycode, event->keyval, modifiers)) {
				bool toolRequestedThatEventShouldContinue = false;
				SciTEBase::ToolsMenu(tool_i, &toolRequestedThatEventShouldContinue);
				if (!toolRequestedThatEventShouldContinue) {
					return 1l;
				}
			}
		}
	}

	// check user defined keys
	for (size_t cut_i = 0; cut_i < shortCutItemList.size(); cut_i++) {
		if (KeyMatch(shortCutItemList[cut_i].menuKey.c_str(), event->keyval, modifiers)) {
			int commandNum = SciTEBase::GetMenuCommandAsInt(shortCutItemList[cut_i].menuCommand.c_str());
			if (commandNum != -1) {
				if (commandNum < 2000) {
					SciTEBase::MenuCommand(commandNum);
				} else {
					SciTEBase::CallFocused(commandNum);
				}
				g_signal_stop_emission_by_name(
				    G_OBJECT(PWidget(wSciTE)), "key_press_event");
				return 1;
			}
		}
	}

	if (findStrip.KeyDown(event) || replaceStrip.KeyDown(event) || userStrip.KeyDown(event)) {
		g_signal_stop_emission_by_name(G_OBJECT(PWidget(wSciTE)), "key_press_event");
		return 1;
	}

	return 0;
}'''])
SciTEGTK_Key_MustInclude = r'''	if (findStrip.KeyDown(event) || replaceStrip.KeyDown(event) || userStrip.KeyDown(event)) {'''

fragments.append(['SciTEWin::KeyDown', 'win32/SciTEWin.cxx', r'''LRESULT SciTEWin::KeyDown(WPARAM wParam) {
	// Look through lexer menu
	int modifiers =
	    (IsKeyDown(VK_SHIFT) ? SCMOD_SHIFT : 0) |
	    (IsKeyDown(VK_CONTROL) ? SCMOD_CTRL : 0) |
	    (IsKeyDown(VK_MENU) ? SCMOD_ALT : 0);

	if (extender && extender->OnKey(static_cast<int>(wParam), modifiers))
		return 1l;

	for (unsigned int j = 0; j < languageMenu.size(); j++) {
		if (KeyMatch(languageMenu[j].menuKey, static_cast<int>(wParam), modifiers)) {
			SciTEBase::MenuCommand(IDM_LANGUAGE + j);
			return 1l;
		}
	}

	// loop through the Tools menu's active commands.
	HMENU hMenu = ::GetMenu(MainHWND());
	HMENU hToolsMenu = ::GetSubMenu(hMenu, menuTools);
	for (int tool_i = 0; tool_i < toolMax; ++tool_i) {
		MENUITEMINFO mii;
		mii.cbSize = sizeof(MENUITEMINFO);
		mii.fMask = MIIM_DATA;
		if (::GetMenuItemInfo(hToolsMenu, IDM_TOOLS+tool_i, FALSE, &mii) && mii.dwItemData) {
			if (SciTEKeys::MatchKeyCode(static_cast<long>(mii.dwItemData), static_cast<int>(wParam), modifiers)) {
				bool toolRequestedThatEventShouldContinue = false;
				SciTEBase::ToolsMenu(tool_i, &toolRequestedThatEventShouldContinue);
				if (!toolRequestedThatEventShouldContinue) {
					return 1l;
				}
			}
		}
	}

	// loop through the keyboard short cuts defined by user.. if found
	// exec it the command defined
	for (size_t cut_i = 0; cut_i < shortCutItemList.size(); cut_i++) {
		if (KeyMatch(shortCutItemList[cut_i].menuKey, static_cast<int>(wParam), modifiers)) {
			int commandNum = SciTEBase::GetMenuCommandAsInt(shortCutItemList[cut_i].menuCommand.c_str());
			if (commandNum != -1) {
				// its possible that the command is for scintilla directly
				// all scintilla commands are larger then 2000
				if (commandNum < 2000) {
					SciTEBase::MenuCommand(commandNum);
				} else {
					SciTEBase::CallFocused(commandNum);
				}
				return 1l;
			}
		}
	}
	
	std::vector<std::pair<int, int>>::iterator itAccels;
	for (itAccels = acceleratorKeys.begin(); itAccels != acceleratorKeys.end(); ++itAccels) {
		int parsedKeys = itAccels->first;
		int command = itAccels->second;
		if (SciTEKeys::MatchKeyCode(parsedKeys, static_cast<int>(wParam), modifiers)) {
			SciTEBase::MenuCommand(command);
			return 1l;
		}
	}

	return 0l;
}'''])

fragments.append(['SciTEGTK::SetMenuItem', 'gtk/SciTEGTK.cxx', r'''void SciTEGTK::SetMenuItem(int, int, int itemID, const char *text, const char *mnemonic) {
	DestroyMenuItem(0, itemID);

	// On GTK+ the menuNumber and position are ignored as the menu item already exists and is in the right
	// place so only needs to be shown and have its text set.

	std::string itemText = GtkFromWinCaption(text);

	long keycode = 0;
	if (mnemonic && *mnemonic) {
		keycode = SciTEKeys::ParseKeyCode(mnemonic);
		if (keycode) {
			itemText += " ";
			itemText += mnemonic;
		}
		// the keycode could be used to make a custom accelerator table
		// but for now, the menu's item data is used instead for command
		// tools, and for other menu entries it is just discarded.
	}

	// Reorder shift and ctrl indicators for compatibility with other menus
	Substitute(itemText, "Ctrl+Shift+", "Shift+Ctrl+");'''])

fragments.append(['FindStrip::EscapeSignal', 'gtk/SciTEGTK.cxx', r'''gboolean FindStrip::EscapeSignal(GtkWidget *w, GdkEventKey *event, FindStrip *pStrip) {
	if (event->keyval == GKEY_Escape) {
		g_signal_stop_emission_by_name(G_OBJECT(w), "key-press-event");
		pStrip->Close();
	}
	return FALSE;
}'''])

fragments.append(['ReplaceStrip::EscapeSignal', 'gtk/SciTEGTK.cxx', r'''gboolean ReplaceStrip::EscapeSignal(GtkWidget *w, GdkEventKey *event, ReplaceStrip *pStrip) {
	if (event->keyval == GKEY_Escape) {
		g_signal_stop_emission_by_name(G_OBJECT(w), "key-press-event");
		pStrip->Close();
	}
	return FALSE;
}'''])

fragments.append(['UserStrip::EscapeSignal', 'gtk/SciTEGTK.cxx', r'''gboolean UserStrip::EscapeSignal(GtkWidget *w, GdkEventKey *event, UserStrip *pStrip) {
	if (event->keyval == GKEY_Escape) {
		g_signal_stop_emission_by_name(G_OBJECT(w), "key-press-event");
		pStrip->Close();
	}
	return FALSE;
}'''])

fragments.append(['SciTEGTK::FindIncrementEscapeSignal', 'gtk/SciTEGTK.cxx', r'''gboolean SciTEGTK::FindIncrementEscapeSignal(GtkWidget *w, GdkEventKey *event, SciTEGTK *scitew) {
	if (event->keyval == GKEY_Escape) {
		g_signal_stop_emission_by_name(G_OBJECT(w), "key-press-event");
		gtk_widget_hide(scitew->wIncrementPanel);
		SetFocus(scitew->wEditor);
	}
	return FALSE;
}'''])

fragments.append(['Gtk key defines', 'gtk/Widget.cxx', r'''#if GTK_CHECK_VERSION(3,0,0)
#define GKEY_Escape GDK_KEY_Escape
#define GKEY_Void GDK_KEY_VoidSymbol
#else
#define GKEY_Escape GDK_Escape
#define GKEY_Void GDK_VoidSymbol
#endif'''])

fragments.append(['gtkStrip::KeyDown', 'gtk/Widget.cxx', r'''bool Strip::KeyDown(GdkEventKey *event) {
	bool retVal = false;

	if (visible) {
		if (event->keyval == GKEY_Escape) {
			Close();
			return true;
		}

		if (event->state & GDK_MOD1_MASK) {
			GList *childWidgets = gtk_container_get_children(GTK_CONTAINER(GetID()));
			for (GList *child = g_list_first(childWidgets); child; child = g_list_next(child)) {
				GtkWidget **w = (GtkWidget **)child;
				std::string name = gtk_widget_get_name(*w);
				std::string label;
				if (name == "GtkButton" || name == "GtkCheckButton") {
					label = gtk_button_get_label(GTK_BUTTON(*w));
				} else if (name == "GtkLabel") {
					label = gtk_label_get_label(GTK_LABEL(*w));
				}
				char key = KeyFromLabel(label);
				if (static_cast<unsigned int>(key) == event->keyval) {
					//fprintf(stderr, "%p %s %s %c\n", *w, name.c_str(), label.c_str(), key);
					if (name == "GtkButton" || name == "GtkCheckButton") {
						gtk_button_clicked(GTK_BUTTON(*w));
					} else if (name == "GtkLabel") {
						// Only ever use labels to label ComboBoxEntry
						GtkWidget *pwidgetSelect = gtk_label_get_mnemonic_widget(GTK_LABEL(*w));
						if (pwidgetSelect) {
							gtk_widget_grab_focus(pwidgetSelect);
						}
					}
					retVal = true;
					break;
				}
			}
			g_list_free(childWidgets);
		}
	}
	return retVal;
}'''])

fragments.append(['win32Strip::KeyDown', 'win32/Strips.cxx', r'''bool Strip::KeyDown(WPARAM key) {
	if (!visible)
		return false;
	switch (key) {
	case VK_MENU:
		::SendMessage(Hwnd(), WM_UPDATEUISTATE, (UISF_HIDEACCEL|UISF_HIDEFOCUS) << 16 | UIS_CLEAR, 0);
		return false;
	case VK_TAB:
		if (IsChild(Hwnd(), ::GetFocus())) {
			::SendMessage(Hwnd(), WM_UPDATEUISTATE, (UISF_HIDEACCEL|UISF_HIDEFOCUS) << 16 | UIS_CLEAR, 0);
			Tab((::GetKeyState(VK_SHIFT) & 0x80000000) == 0);
			return true;
		} else {
			return false;
		}
	case VK_ESCAPE:
		Close();
		return true;
	default:
		if ((::GetKeyState(VK_MENU) & 0x80000000) != 0) {
			HWND wChild = ::GetWindow(Hwnd(), GW_CHILD);
			while (wChild) {
				enum { capSize = 2000 };
				GUI::gui_char className[capSize];
				::GetClassName(wChild, className, capSize);
				if ((wcscmp(className, TEXT("Button")) == 0) ||
					(wcscmp(className, TEXT("Static")) == 0)) {
					GUI::gui_char caption[capSize];
					::GetWindowText(wChild, caption, capSize);
					for (int i=0; caption[i]; i++) {
						if ((caption[i] == L'&') && (toupper(caption[i+1]) == static_cast<int>(key))) {
							if (wcscmp(className, TEXT("Button")) == 0) {
								::SendMessage(wChild, BM_CLICK, 0, 0);
							} else {	// Static caption
								wChild = ::GetWindow(wChild, GW_HWNDNEXT);
								::SetFocus(wChild);
							}
							return true;
						}
					}
				}
				wChild = ::GetWindow(wChild, GW_HWNDNEXT);
			};
		}
	}
	return false;
}'''])

fragments.append(['bool KeyMatch', 'win32/SciTEWin.cxx', r'''#ifndef VK_OEM_2
static const int VK_OEM_2=0xbf;
static const int VK_OEM_3=0xc0;
static const int VK_OEM_4=0xdb;
static const int VK_OEM_5=0xdc;
static const int VK_OEM_6=0xdd;
#endif
#ifndef VK_OEM_PLUS
static const int VK_OEM_PLUS=0xbb;
#endif

inline bool KeyMatch(const std::string &sKey, int keyval, int modifiers) {
	return SciTEKeys::MatchKeyCode(
		SciTEKeys::ParseKeyCode(sKey.c_str()), keyval, modifiers);
}'''])


fragments.append(['SciTEWin::KeyUp', 'win32/SciTEWin.cxx', r'''LRESULT SciTEWin::KeyUp(WPARAM wParam) {
	if (wParam == VK_CONTROL) {
		EndStackedTabbing();
	}
	return 0l;
}'''])

fragments.append(['key while dragging tab', 'win32/SciTEWinBar.cxx', r'''	case WM_KEYDOWN: {
			if (wParam == VK_ESCAPE) {
				if (st_bDragBegin == TRUE) {
					if (st_hwndLastFocus != NULL) ::SetFocus(st_hwndLastFocus);
					::ReleaseCapture();
					::SetCursor(::LoadCursor(NULL, IDC_ARROW));
					st_bDragBegin = FALSE;
					st_iDraggingTab = -1;
					st_iLastClickTab = -1;
					::InvalidateRect(hWnd, NULL, FALSE);
				}
			}
		}
		break;'''])

fragments.append(['SciTEWin::ModelessHandler', 'win32/SciTEWinDlg.cxx', r'''bool SciTEWin::ModelessHandler(MSG *pmsg) {
	if (DialogHandled(wFindReplace.GetID(), pmsg)) {
		return true;
	}
	if (DialogHandled(wFindInFiles.GetID(), pmsg)) {
		return true;
	}
	if (wParameters.GetID()) {
		// Allow commands, such as Ctrl+1 to be active while the Parameters dialog is
		// visible so that a group of commands can be easily run with differing parameters.
		bool menuKey = (pmsg->message == WM_KEYDOWN) &&
		               (pmsg->wParam != VK_TAB) &&
		               (pmsg->wParam != VK_ESCAPE) &&
		               (pmsg->wParam != VK_RETURN) &&
		               (pmsg->wParam < 'A' || pmsg->wParam > 'Z') &&
		               (IsKeyDown(VK_CONTROL) || !IsKeyDown(VK_MENU));
		if (!menuKey && DialogHandled(wParameters.GetID(), pmsg))
			return true;
	}
	if ((pmsg->message == WM_KEYDOWN) || (pmsg->message == WM_SYSKEYDOWN)) {
		if (searchStrip.KeyDown(pmsg->wParam))
			return true;
		if (findStrip.KeyDown(pmsg->wParam))
			return true;
		if (replaceStrip.KeyDown(pmsg->wParam))
			return true;
		if (userStrip.KeyDown(pmsg->wParam))
			return true;
	}
	if (pmsg->message == WM_KEYDOWN || pmsg->message == WM_SYSKEYDOWN) {
		if (KeyDown(pmsg->wParam))
			return true;
	} else if (pmsg->message == WM_KEYUP) {
		if (KeyUp(pmsg->wParam))
			return true;
	}

	return false;
}'''])

fragments.append(['sciteBaseCallAssignKey', 'src/SciTEBase.cxx', r'''void SciTEBase::AssignKey(int key, int mods, int cmd) {
	wEditor.Call(SCI_ASSIGNCMDKEY,
	        LongFromTwoShorts(static_cast<short>(key),
	                static_cast<short>(mods)), cmd);
}'''])

fragments.append(['scintillaKeyHandlerMethodExpectedText', '../scintilla/src/Editor.cxx', r'''int Editor::KeyDefault(int, int) {
	return 0;
}

int Editor::KeyDownWithModifiers(int key, int modifiers, bool *consumed) {
	DwellEnd(false);
	int msg = kmap.Find(key, modifiers);
	if (msg) {
		if (consumed)
			*consumed = true;
		return static_cast<int>(WndProc(msg, 0, 0));
	} else {
		if (consumed)
			*consumed = false;
		return KeyDefault(key, modifiers);
	}
}

int Editor::KeyDown(int key, bool shift, bool ctrl, bool alt, bool *consumed) {
	return KeyDownWithModifiers(key, ModifierFlags(shift, ctrl, alt), consumed);
}'''])

scintillaKeyHandlerMethodExpectedTextMustInclude = r'''	return KeyDownWithModifiers(key, ModifierFlags(shift, ctrl, alt), consumed);'''

fragments.append(['accelStringWindowsToGtkIfNeeded', 'gtk/SciTEGTK.cxx', r'''static void AccelStringWindowsToGtkIfNeeded(std::string &accelKey) {
	Substitute(accelKey, "Ctrl+", "<control>");
	Substitute(accelKey, "Shift+", "<shift>");
	Substitute(accelKey, "Alt+", "<alt>");
	Substitute(accelKey, "Super+", "<super>");
}'''])

fragments.append(['accelStringGtkToWindowsIfNeeded', 'win32/SciTEWinBar.cxx', r'''static void AccelStringGtkToWindowsIfNeeded(std::string &accelKey) {
	Substitute(accelKey, "<control>", "Ctrl+");
	Substitute(accelKey, "<shift>", "Shift+");
	Substitute(accelKey, "<alt>", "Alt+");
}'''])

fragments.append(['sciteWinRegisterAccelerator', 'win32/SciTEWinBar.cxx', r'''void SciTEWin::RegisterAccelerator(const GUI::gui_char *accel, int id) {
	if (accel && accel[0]) {
		std::string keys(GUI::UTF8FromString(accel));
		long parsedKeys = SciTEKeys::ParseKeyCode(keys.c_str());
		if (parsedKeys) {
			acceleratorKeys.push_back(std::pair<int, int>(parsedKeys, id));
		}
	}
}'''])

fragments.append(['callsToAssignKey', 'src/SciTEProps.cxx', r'''	if (props.GetInt("os.x.home.end.keys")) {
		AssignKey(SCK_HOME, 0, SCI_SCROLLTOSTART);
		AssignKey(SCK_HOME, SCMOD_SHIFT, SCI_NULL);
		AssignKey(SCK_HOME, SCMOD_SHIFT | SCMOD_ALT, SCI_NULL);
		AssignKey(SCK_END, 0, SCI_SCROLLTOEND);
		AssignKey(SCK_END, SCMOD_SHIFT, SCI_NULL);
	} else {
		if (props.GetInt("wrap.aware.home.end.keys",0)) {
			if (props.GetInt("vc.home.key", 1)) {
				AssignKey(SCK_HOME, 0, SCI_VCHOMEWRAP);
				AssignKey(SCK_HOME, SCMOD_SHIFT, SCI_VCHOMEWRAPEXTEND);
				AssignKey(SCK_HOME, SCMOD_SHIFT | SCMOD_ALT, SCI_VCHOMERECTEXTEND);
			} else {
				AssignKey(SCK_HOME, 0, SCI_HOMEWRAP);
				AssignKey(SCK_HOME, SCMOD_SHIFT, SCI_HOMEWRAPEXTEND);
				AssignKey(SCK_HOME, SCMOD_SHIFT | SCMOD_ALT, SCI_HOMERECTEXTEND);
			}
			AssignKey(SCK_END, 0, SCI_LINEENDWRAP);
			AssignKey(SCK_END, SCMOD_SHIFT, SCI_LINEENDWRAPEXTEND);
		} else {
			if (props.GetInt("vc.home.key", 1)) {
				AssignKey(SCK_HOME, 0, SCI_VCHOME);
				AssignKey(SCK_HOME, SCMOD_SHIFT, SCI_VCHOMEEXTEND);
				AssignKey(SCK_HOME, SCMOD_SHIFT | SCMOD_ALT, SCI_VCHOMERECTEXTEND);
			} else {
				AssignKey(SCK_HOME, 0, SCI_HOME);
				AssignKey(SCK_HOME, SCMOD_SHIFT, SCI_HOMEEXTEND);
				AssignKey(SCK_HOME, SCMOD_SHIFT | SCMOD_ALT, SCI_HOMERECTEXTEND);
			}
			AssignKey(SCK_END, 0, SCI_LINEEND);
			AssignKey(SCK_END, SCMOD_SHIFT, SCI_LINEENDEXTEND);
		}
	}

	AssignKey('L', SCMOD_SHIFT | SCMOD_CTRL, SCI_LINEDELETE);


	scrollOutput = props.GetInt("output.scroll", 1);'''])

filterLinesFromOutputForAesthetics = {r'''<tr><td>0</td><td>Ctrl+0</td><td>Lint</td><td>only *.pl;*.pm;*.pod</td></tr>''': 0,
r'''<tr><td>0</td><td>Ctrl+0</td><td>Link</td><td>only *.asm</td></tr>''': 0,
r'''<tr><td>0</td><td>Ctrl+0</td><td>Debug compile</td><td>only *.pas</td></tr>''': 0,
r'''<tr><td>0</td><td>Ctrl+0</td><td>Execute selection</td><td>only *.bat</td></tr>''': 0,
r'''<tr><td>0</td><td>Ctrl+0</td><td>Indent</td><td>only *.c;*.cc;*.cpp;*.cxx;*.h;*.hh;*.hpp;*.hxx;*.ipp;*.m;*.mm;*.sma</td></tr>''': 0,
r'''<tr><td>2</td><td>Ctrl+2</td><td>Code profiler</td><td>only *.pl;*.pm;*.pod</td></tr>''': 0,
r'''<tr><td>2</td><td>Ctrl+2</td><td>Bibtex</td><td>only *.tex;*.sty</td></tr>''': 0,
r'''<tr><td>2</td><td>Ctrl+2</td><td>Gdb</td><td>only *.pas</td></tr>''': 0,
r'''<tr><td>2</td><td>Ctrl+2</td><td>Bibtex</td><td>only *.tex;*.sty;*.aux;*.toc;*.idx</td></tr>''': 0,
r'''<tr><td>2</td><td>Ctrl+2</td><td>Bibtex</td><td>only *.tex;*.tui;*.tuo;*.sty</td></tr>''': 0,
r'''<tr><td>3</td><td>Ctrl+3</td><td>Profiler parser</td><td>only *.pl;*.pm;*.pod</td></tr>''': 0,
r'''<tr><td>9</td><td>Ctrl+9</td><td>Debug build</td><td>only *.pas</td></tr>''': 0,
r'''<tr><td>9</td><td>Ctrl+9</td><td>Nmake</td><td>only *.mak</td></tr>''': 0,
r'''<tr><td>9</td><td>Ctrl+9</td><td>Check syntax</td><td>only *.pl;*.pm;*.pod</td></tr>''': 0,
r'''<tr><td>2</td><td>Ctrl+2</td><td>Code profiler</td><td>only *.rb</td></tr>''': 0,
r'''<tr><td>3</td><td>Ctrl+3</td><td>Ddd</td><td>only *.pas</td></tr>''': 0,
r'''<tr><td>F9</td><td>F9</td><td>Macroplay</td><td></td></tr>''': 0,
r'''<tr><td>F9</td><td>Shift+F9</td><td>List macros</td><td></td></tr>''': 0,
r'''<tr><td>F9</td><td>Ctrl+F9</td><td>Macrorecord</td><td></td></tr>''': 0,
r'''<tr><td>F9</td><td>Ctrl+Shift+F9</td><td>Macrostoprecord</td><td></td></tr>''': 0,
r'''<tr><td>0</td><td>Alt+0</td><td>Open tab 10</td><td></td></tr>''': 0,
r'''<tr><td>X</td><td>Ctrl+X</td><td>Line cut if no selection</td><td>from properties</td></tr>''': 0,
r'''<tr><td>C</td><td>Ctrl+C</td><td>Line copy if no selection</td><td>from properties</td></tr>''': 0,
r'''<tr><td>V</td><td>Ctrl+V</td><td>Line paste if clipboard has entire line</td><td>from properties</td></tr>''': 0,
r'''<tr><td>M</td><td>Ctrl+Shift+M</td><td>Null</td><td>from properties</td></tr>''': 0,
r'''<tr><td>Delete</td><td>Delete</td><td>Clear</td><td></td></tr>''': 0,
r'''<tr><td>9</td><td>Ctrl+9</td><td>Check syntax</td><td>only *.rb</td></tr>''': 0,
r'''<tr><td>9</td><td>Ctrl+9</td><td>Syntax check</td><td>only *.py;*.pyw</td></tr>''': 0,
r'''<tr><td>9</td><td>Ctrl+9</td><td>Lint</td><td>only *.cc;*.cpp;*.cxx</td></tr>''': 0,
}

def getFragment(fragmentName):
	for arr in fragments:
		if arr[0] == fragmentName:
			return arr[2]
	assert False, 'not found ' + fragmentName

def detectCodeChanges(filename, expectedText, mustInclude=None):
	expectedLines = expectedText.replace('\r\n', '\n').split('\n')
	first, last = expectedLines[0], expectedLines[-1]
	linesGot = retrieveCodeLines(filename, first, last, mustInclude)
	
	if expectedLines != linesGot:
		import difflib
		diff = difflib.context_diff(expectedLines, linesGot)
		message = '''The code in %s beginning with \n%s\n has changed.
This could just mean a comment has been altered, in which case no work is needed
besides updating %s. Changed logic, though, might require updating ShowKeyboardBindings.py.
Here's a diff of the changes: \n%s''' % (filename, first, __file__, '\n'.join(list(diff)))
		warn(message)

def checkForAnyLogicChangesFile(allFragments, watchFor, path):
	if not (path.endswith('.cxx') or path.endswith('.c') or path.endswith('.cpp') or path.endswith('.h')):
		return
		
	if os.path.split(path)[1] == 'IFaceTable.cxx':
		return
	
	contents = readall(path, 'rb').replace('\r\n', '\n')
	for fragment in allFragments:
		fragmentFilename = fragment[1]
		if path.lower().replace('\\', '/').endswith('/' + fragmentFilename.lower()):
			contentsLenBefore = len(contents)
			contents = contents.replace(fragment[2], '')
			if len(contents) == contentsLenBefore:
				warn('Warning: in the file %s expected to see the code %s'%(path, fragment[2]))
	
	warnIfTermsSeen(path, contents, watchFor)
	
def warnIfTermsSeen(path, codeFound, watchFor):
	for term in watchFor:
		if term in codeFound:
			index = codeFound.find(term)
			context = codeFound[index - 200 : index + 200]
			message = '''Warning: the keyboard shortcut-related term %s was newly seen in file \n%s\n
We're checking for new key-handling logic.
This is likely a false positive, though, in which case you can add a line acceptedCode.append to %s.
Context: %s''' % (term, path, __file__, context)
			warn(message)

def checkForAnyLogicChanges():
	watchFor = ['GDK_KEY', 'GKEY_', 'GDK_CONTROL_MASK', 'MatchKeyCode', 'ParseKeyCode', 'KeyMatch', 'KeyDown',
		'VK_', 'SCK_', 'AssignKey', 'WM_KEYDOWN', 'kmap', 'AssignCmdKey', 'SCI_ASSIGNCMDKEY', '<control>']

	allFragments = list(fragments)
	allFragments.append(['', 'src/SciTEKeys.h', r'''	static long ParseKeyCode(const char *mnemonic);'''])
	allFragments.append(['', 'src/SciTEKeys.h', r'''	static bool MatchKeyCode(long parsedKeyCode, int key, int modifiers);'''])
	allFragments.append(['', 'src/SciTEBase.h', r'''void AssignKey(int key, int mods, int cmd);'''])
	allFragments.append(['', 'win32/SciTEWin.cxx', r'''bool SciTEKeys::MatchKeyCode(long parsedKeyCode, int keyval, int modifiers) {'''])
	allFragments.append(['', 'gtk/SciTEGTK.cxx', r'''bool SciTEKeys::MatchKeyCode(long parsedKeyCode, int keyval, int modifiers) {'''])
	allFragments.append(['', 'gtk/Widget.h', r'''virtual bool KeyDown(GdkEventKey *event);'''])
	allFragments.append(['', 'gtk/SciTEGTK.cxx', r'''virtual bool KeyDown(GdkEventKey *event);'''])
	allFragments.append(['', 'gtk/Widget.h', r'''	static gboolean KeyDown(GtkWidget *widget, GdkEventKey *event, WCheckDraw *pcd);'''])
	allFragments.append(['', 'gtk/Widget.cxx', r'''	return gtk_label_get_mnemonic_keyval(GTK_LABEL(Pointer())) != GKEY_Void;'''])
	allFragments.append(['', 'gtk/Widget.cxx', r'''	g_signal_connect(G_OBJECT(da), "key-press-event", G_CALLBACK(KeyDown), this);'''])
	allFragments.append(['', 'gtk/Widget.cxx', r'''gboolean WCheckDraw::KeyDown(GtkWidget */*widget*/, GdkEventKey *event, WCheckDraw *pcd) {'''])
	allFragments.append(['', 'win32/SciTEWin.cxx', '''case WM_KEYDOWN:\n			return KeyDown(wParam);'''])
	allFragments.append(['', 'win32/SciTEWin.h', r'''	LRESULT KeyDown(WPARAM wParam);'''])
	allFragments.append(['', 'win32/SciTEWin.h', r'''inline bool IsKeyDown(int key) {'''])
	allFragments.append(['', 'win32/SciTEWinBar.cxx', r'''// code) as KeyMatch uses in SciTEWin.cxx.'''])
	allFragments.append(['', 'win32/SciTEWinDlg.cxx', r'''FindNext(reverseFind ^ IsKeyDown(VK_SHIFT));'''])
	allFragments.append(['', 'win32/SciTEWinDlg.cxx', r'''return HandleReplaceCommand(ControlIDOfWParam(wParam), IsKeyDown(VK_SHIFT));'''])
	allFragments.append(['', 'win32/Strips.h', r'''	virtual bool KeyDown(WPARAM key);'''])

	start = '''void SciTEGTK::CreateMenu() {'''
	end = '''	gtk_window_add_accel_group(GTK_WINDOW(PWidget(wSciTE)), accelGroup);'''
	allFragments.append(['', 'gtk/SciTEGTK.cxx', '\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, end))])
	start = '''#define GKEY_Escape GDK_KEY_Escape'''
	end = '''#define GKEY_F4 GDK_F4'''
	allFragments.append(['', 'gtk/SciTEGTK.cxx', '\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, end))])
	start = '''const KeyToCommand KeyMap::MapDefault[] = {'''
	allFragments.append(['', '../scintilla/src/KeyMap.cxx', '\n'.join(retrieveCodeLines('../../scintilla/src/KeyMap.cxx', start, '};'))])
	start = '''static gint messageBoxKey(GtkWidget *w, GdkEventKey *event, gpointer p) {'''
	allFragments.append(['', 'gtk/SciTEGTK.cxx', '\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, '}'))])
	start = '''long SciTEKeys::ParseKeyCode(const char *mnemonic) {'''
	allFragments.append(['', 'gtk/SciTEGTK.cxx', '\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, '}'))])
	start = '''long SciTEKeys::ParseKeyCode(const char *mnemonic) {'''
	allFragments.append(['', 'win32/SciTEWin.cxx', '\n'.join(retrieveCodeLines('../win32/SciTEWin.cxx', start, '}'))])
	start = '''void SciTEWin::SetMenuItem(int menuNumber, int position, int itemID,'''
	allFragments.append(['', 'win32/SciTEWinBar.cxx', '\n'.join(retrieveCodeLines('../win32/SciTEWinBar.cxx', start, '}'))])
	
	for stripType in ('FindStrip', 'ReplaceStrip', 'UserStrip'):
		start = '''bool %s::KeyDown(GdkEventKey *event) {''' % stripType
		allFragments.append(['', 'gtk/SciTEGTK.cxx', '\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, '}'))])
		
	for stripType in ('BackgroundStrip', 'SearchStrip', 'FindStrip', 'ReplaceStrip', 'UserStrip'):
		start = '''bool %s::KeyDown(WPARAM key) {''' % stripType
		allFragments.append(['', 'win32/Strips.cxx', '\n'.join(retrieveCodeLines('../win32/Strips.cxx', start, '}'))])

	for arr in fragments:
		assert os.path.isfile(os.path.join('..', arr[1]))
	
	for (path, dirs, files) in os.walk('..'):
		for file in files:
			full = os.path.join(path, file)
			checkForAnyLogicChangesFile(allFragments, watchFor, full)

def tests():
	entriesRead = []
	line = '''{"/Edit/Make Selection _Lowercase", "<control>U", menuSig, IDM_LWRCASE, 0},'''
	readFromSciTEItemFactoryEntry(line.split(','), entriesRead, dict())
	line = '''{"/View/_Parameters", NULL, menuSig, IDM_TOGGLEPARAMETERS, "<CheckItem>"},'''
	readFromSciTEItemFactoryEntry(line.split(','), entriesRead, dict())
	line = '''{"/Edit/S_how Calltip", "<control><shift>space", menuSig, IDM_SHOWCALLTIP, 0},'''
	readFromSciTEItemFactoryEntry(line.split(','), entriesRead, dict())
	line = '''	"N", IDM_NEW,   VIRTKEY, CONTROL'''
	readFromSciTEResAccelTableEntry(line.split(',', 2), entriesRead)
	line = '''	VK_F8, IDM_TOGGLEOUTPUT, VIRTKEY'''
	readFromSciTEResAccelTableEntry(line.split(',', 2), entriesRead)
	line = r'''    VK_SPACE, IDM_SHOWCALLTIP, VIRTKEY, CONTROL, SHIFT'''
	readFromSciTEResAccelTableEntry(line.split(',', 2), entriesRead)
	line = r'''{'[',			SCI_CSHIFT,	SCI_PARAUPEXTEND},'''
	readFromScintillaKeyMapEntry(line.split(','), entriesRead, 100)
	line = r'''{SCK_UP,			SCI_CTRL_META,	SCI_LINESCROLLUP},'''
	readFromScintillaKeyMapEntry(line.split(','), entriesRead, 100)
	line = r'''{SCK_LEFT,		SCI_NORM,	SCI_CHARLEFT},'''
	readFromScintillaKeyMapEntry(line.split(','), entriesRead, 100)
	expected = '''Ctrl+U|Make Selection Lowercase|80|gtk|SciTEItemFactoryEntry or user-defined
Ctrl+Shift+Space|Show Calltip|80|gtk|SciTEItemFactoryEntry or user-defined
Ctrl+N|IDM_NEW|80|win32|SciTERes accel
F8|IDM_TOGGLEOUTPUT|80|win32|SciTERes accel
Ctrl+Shift+Space|IDM_SHOWCALLTIP|80|win32|SciTERes accel
Ctrl+Shift+[|SCI_PARAUPEXTEND|100|any|Scintilla keymap
Ctrl+Up|SCI_LINESCROLLUP|100|any|Scintilla keymap
Left|SCI_CHARLEFT|100|any|Scintilla keymap'''
	expectedArr = []
	addBindingsManual(expectedArr, expected)
	assertEqArray(expectedArr, entriesRead)


if __name__ == '__main__':
	tests()
	propertiesMain = '../bin/properties/SciTEGlobal.properties'
	propertiesUser = None
	adjustForAesthetics = True
	
	writeMdLocation = '../../../../../../../../devarchive/moltenform/static/page/scite-with-python/doc'
	if writeMdLocation and not os.path.exists(writeMdLocation):
		raise Exception('path does not exist ' + os.path.abspath(writeMdLocation))
	
	msg = 'keymap.cxx not found, please download both the scintilla and scite sources and place this script in the /scite/src/scripts directory'
	if not os.path.isfile('../../scintilla/src/KeyMap.cxx'):
		print(msg)
	elif not os.path.isfile('../gtk/SciTEGTK.cxx'	):
		print(msg)
	else:
		mainWithPython(propertiesMain, propertiesUser, adjustForAesthetics, writeMdLocation)
