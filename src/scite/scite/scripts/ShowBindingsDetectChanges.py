
# include excerpts of ScITE code, and alert us when any of this code is updated.

import os
from ShowBindingsReadProps import retrieveCodeLines, addBindingsManual, readall, warn

gtkKeyHandlerMethodExpectedText = r'''class KeyToCommand {
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
				SciTEBase::MenuCommand(IDM_TOOLS + tool_i);
				return 1;
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
}'''
gtkKeyHandlerMethodExpectedTextMustInclude = r'''	if (findStrip.KeyDown(event) || replaceStrip.KeyDown(event) || userStrip.KeyDown(event)) {'''

win32KeyHandlerMethodExpectedText = r'''LRESULT SciTEWin::KeyDown(WPARAM wParam) {
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
				SciTEBase::MenuCommand(IDM_TOOLS+tool_i);
				return 1l;
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

	return 0l;
}'''

gtkSetMenuItem = r'''void SciTEGTK::SetMenuItem(int, int, int itemID, const char *text, const char *mnemonic) {
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
	Substitute(itemText, "Ctrl+Shift+", "Shift+Ctrl+");'''

gtkFindStripEscapeSignal = r'''gboolean FindStrip::EscapeSignal(GtkWidget *w, GdkEventKey *event, FindStrip *pStrip) {
	if (event->keyval == GKEY_Escape) {
		g_signal_stop_emission_by_name(G_OBJECT(w), "key-press-event");
		pStrip->Close();
	}
	return FALSE;
}'''

gtkReplaceStripEscapeSignal = r'''gboolean ReplaceStrip::EscapeSignal(GtkWidget *w, GdkEventKey *event, ReplaceStrip *pStrip) {
	if (event->keyval == GKEY_Escape) {
		g_signal_stop_emission_by_name(G_OBJECT(w), "key-press-event");
		pStrip->Close();
	}
	return FALSE;
}'''

gtkUserStripEscapeSignal = r'''gboolean UserStrip::EscapeSignal(GtkWidget *w, GdkEventKey *event, UserStrip *pStrip) {
	if (event->keyval == GKEY_Escape) {
		g_signal_stop_emission_by_name(G_OBJECT(w), "key-press-event");
		pStrip->Close();
	}
	return FALSE;
}'''

gtkFindIncrementEscapeSignal = r'''gboolean SciTEGTK::FindIncrementEscapeSignal(GtkWidget *w, GdkEventKey *event, SciTEGTK *scitew) {
	if (event->keyval == GKEY_Escape) {
		g_signal_stop_emission_by_name(G_OBJECT(w), "key-press-event");
		gtk_widget_hide(scitew->wIncrementPanel);
		SetFocus(scitew->wEditor);
	}
	return FALSE;
}'''

gtkWidgetCxxKeyDefines = r'''#if GTK_CHECK_VERSION(3,0,0)
#define GKEY_Escape GDK_KEY_Escape
#define GKEY_Void GDK_KEY_VoidSymbol
#else
#define GKEY_Escape GDK_Escape
#define GKEY_Void GDK_VoidSymbol
#endif'''

gtkWidgetCxxStripKeyDown = r'''bool Strip::KeyDown(GdkEventKey *event) {
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
}'''

win32StripKeyDown = r'''bool Strip::KeyDown(WPARAM key) {
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
}'''

win32SomeKeyHandling = r'''#ifndef VK_OEM_2
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
}



LRESULT SciTEWin::KeyUp(WPARAM wParam) {
	if (wParam == VK_CONTROL) {
		EndStackedTabbing();
	}
	return 0l;
}'''

win32KeyPressWhileDraggingTab = r'''	case WM_KEYDOWN: {
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
		break;'''

win32ModelessHandler = r'''bool SciTEWin::ModelessHandler(MSG *pmsg) {
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
}'''

sciteBaseCallAssignKey = r'''void SciTEBase::AssignKey(int key, int mods, int cmd) {
	wEditor.Call(SCI_ASSIGNCMDKEY,
	        LongFromTwoShorts(static_cast<short>(key),
	                static_cast<short>(mods)), cmd);
}'''

scintillaKeyHandlerMethodExpectedText = r'''int Editor::KeyDefault(int, int) {
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
}'''

scintillaKeyHandlerMethodExpectedTextMustInclude = r'''	return KeyDownWithModifiers(key, ModifierFlags(shift, ctrl, alt), consumed);'''

# instead of writing code to parse a few lines, write the bindings manually here,
# and verify in ShowKeyboardBindingsDetectCodeChange.py that the table hasn't changed.
gtkKmapBindings = r'''Control+Tab|IDM_NEXTFILESTACK|30|gtk|KeyToCommand kmap[]
Shift+Control+Tab|IDM_PREVFILESTACK|30|gtk|KeyToCommand kmap[]
Control+Enter|IDM_COMPLETEWORD|30|gtk|KeyToCommand kmap[]
Alt+F2|IDM_BOOKMARK_NEXT_SELECT|30|gtk|KeyToCommand kmap[]
Alt+Shift+F2|IDM_BOOKMARK_PREV_SELECT|30|gtk|KeyToCommand kmap[]
Control+F3|IDM_FINDNEXTSEL|30|gtk|KeyToCommand kmap[]
Control+Shift+F3|IDM_FINDNEXTBACKSEL|30|gtk|KeyToCommand kmap[]
Control+F4|IDM_CLOSE|30|gtk|KeyToCommand kmap[]
Control+J|IDM_PREVMATCHPPC|30|gtk|KeyToCommand kmap[]
Control+Shift+J|IDM_SELECTTOPREVMATCHPPC|30|gtk|KeyToCommand kmap[]
Control+K|IDM_NEXTMATCHPPC|30|gtk|KeyToCommand kmap[]
Control+Shift+K|IDM_SELECTTONEXTMATCHPPC|30|gtk|KeyToCommand kmap[]
Control+*|IDM_EXPAND|30|gtk|KeyToCommand kmap[]'''

# instead of writing code to parse a few lines, write the bindings manually here,
# and verify in ShowKeyboardBindingsDetectCodeChange.py that the table hasn't changed.
def addCallsToAssignKeyBindings(props, allBindings):
	bindings = '''Control+Shift+L|SCI_LINEDELETE|1|any|SciTEProps.cxx AssignKey\n'''
	if props.GetInt("os.x.home.end.keys"):
		bindings += '''Home|SCI_SCROLLTOSTART|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_NULL|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_NULL|1|any|SciTEProps.cxx AssignKey
End|SCI_SCROLLTOEND|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_NULL|1|any|SciTEProps.cxx AssignKey'''
	else:
		if props.GetInt("wrap.aware.home.end.keys", 0):
			if props.GetInt("vc.home.key", 1):
				bindings += '''Home|SCI_VCHOMEWRAP|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_VCHOMEWRAPEXTEND|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_VCHOMERECTEXTEND|1|any|SciTEProps.cxx AssignKey
End|SCI_LINEENDWRAP|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_LINEENDWRAPEXTEND|1|any|SciTEProps.cxx AssignKey'''
			else:
				bindings += '''Home|SCI_HOMEWRAP|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_HOMEWRAPEXTEND|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_HOMERECTEXTEND|1|any|SciTEProps.cxx AssignKey
End|SCI_LINEENDWRAP|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_LINEENDWRAPEXTEND|1|any|SciTEProps.cxx AssignKey'''
		else:
			if props.GetInt("vc.home.key", 1):
				bindings += '''Home|SCI_VCHOME|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_VCHOMEEXTEND|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_VCHOMERECTEXTEND|1|any|SciTEProps.cxx AssignKey
End|SCI_LINEEND|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_LINEENDEXTEND|1|any|SciTEProps.cxx AssignKey'''
			else:
				bindings += '''Home|SCI_HOME|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_HOMEEXTEND|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_HOMERECTEXTEND|1|any|SciTEProps.cxx AssignKey
End|SCI_LINEEND|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_LINEENDEXTEND|1|any|SciTEProps.cxx AssignKey'''
	addBindingsManual(allBindings, bindings)

callsToAssignKey = r'''	if (props.GetInt("os.x.home.end.keys")) {
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


	scrollOutput = props.GetInt("output.scroll", 1);'''


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

def checkForAnyLogicChangesFile(path, watchFor, acceptedCode):
	if not (path.endswith('.cxx') or path.endswith('.c') or path.endswith('.cpp') or path.endswith('.h')):
		return
		
	if os.path.split(path)[1] == 'IFaceTable.cxx':
		return
	
	codeFound = readall(path, 'rb').replace('\r\n', '\n')
	for codeExcerpt in acceptedCode:
		codeFound = codeFound.replace(codeExcerpt, '')
	
	for term in watchFor:
		if term in codeFound:
			index = codeFound.find(term)
			context = codeFound[index - 200:index + 200]
			message = '''Warning: the keyboard shortcut-related term %s was newly seen in file \n%s\n
We're checking for new key-handling logic.
This is likely a false positive, though, in which case you can add a line acceptedCode.append to %s.
Context: %s''' % (term, path, __file__, context)
			warn(message)

def checkForAnyLogicChanges():
	watchFor = ['GDK_KEY', 'GKEY_', 'GDK_CONTROL_MASK', 'MatchKeyCode', 'ParseKeyCode', 'KeyMatch', 'KeyDown',
		'VK_', 'SCK_', 'AssignKey', 'WM_KEYDOWN', 'kmap', 'AssignCmdKey', 'SCI_ASSIGNCMDKEY', '<control>']
	acceptedCode = []
	acceptedCode.append('''	static long ParseKeyCode(const char *mnemonic);''')
	acceptedCode.append('''	static bool MatchKeyCode(long parsedKeyCode, int key, int modifiers);''')
	acceptedCode.append('''void AssignKey(int key, int mods, int cmd);''')
	acceptedCode.append('''bool SciTEKeys::MatchKeyCode(long parsedKeyCode, int keyval, int modifiers) {''')
	acceptedCode.append('''virtual bool KeyDown(GdkEventKey *event);''')
	acceptedCode.append('''	static gboolean KeyDown(GtkWidget *widget, GdkEventKey *event, WCheckDraw *pcd);''')
	acceptedCode.append('''	return gtk_label_get_mnemonic_keyval(GTK_LABEL(Pointer())) != GKEY_Void;''')
	acceptedCode.append('''	g_signal_connect(G_OBJECT(da), "key-press-event", G_CALLBACK(KeyDown), this);''')
	acceptedCode.append('''gboolean WCheckDraw::KeyDown(GtkWidget */*widget*/, GdkEventKey *event, WCheckDraw *pcd) {''')
	acceptedCode.append('''case WM_KEYDOWN:\n			return KeyDown(wParam);''')
	acceptedCode.append('''	LRESULT KeyDown(WPARAM wParam);''')
	acceptedCode.append('''inline bool IsKeyDown(int key) {''')
	acceptedCode.append('''// code) as KeyMatch uses in SciTEWin.cxx.''')
	acceptedCode.append('''FindNext(reverseFind ^ IsKeyDown(VK_SHIFT));''')
	acceptedCode.append('''return HandleReplaceCommand(ControlIDOfWParam(wParam), IsKeyDown(VK_SHIFT));''')
	acceptedCode.append('''	virtual bool KeyDown(WPARAM key);''')
	acceptedCode.append(gtkSetMenuItem.replace('\r\n', '\n'))
	acceptedCode.append(gtkWidgetCxxKeyDefines.replace('\r\n', '\n'))
	acceptedCode.append(gtkWidgetCxxStripKeyDown.replace('\r\n', '\n'))
	acceptedCode.append(sciteBaseCallAssignKey.replace('\r\n', '\n'))
	acceptedCode.append(gtkKeyHandlerMethodExpectedText.replace('\r\n', '\n'))
	acceptedCode.append(win32KeyHandlerMethodExpectedText.replace('\r\n', '\n'))
	acceptedCode.append(win32SomeKeyHandling.replace('\r\n', '\n'))
	acceptedCode.append(win32KeyPressWhileDraggingTab.replace('\r\n', '\n'))
	acceptedCode.append(win32ModelessHandler.replace('\r\n', '\n'))
	acceptedCode.append(win32StripKeyDown.replace('\r\n', '\n'))
	acceptedCode.append(scintillaKeyHandlerMethodExpectedText.replace('\r\n', '\n'))
	acceptedCode.append(callsToAssignKey.replace('\r\n', '\n'))
	acceptedCode.append(gtkFindStripEscapeSignal.replace('\r\n', '\n'))
	acceptedCode.append(gtkReplaceStripEscapeSignal.replace('\r\n', '\n'))
	acceptedCode.append(gtkUserStripEscapeSignal.replace('\r\n', '\n'))
	acceptedCode.append(gtkFindIncrementEscapeSignal.replace('\r\n', '\n'))
	
	start = '''void SciTEGTK::CreateMenu() {'''
	end = '''	gtk_window_add_accel_group(GTK_WINDOW(PWidget(wSciTE)), accelGroup);'''
	acceptedCode.append('\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, end)))
	start = '''#define GKEY_Escape GDK_KEY_Escape'''
	end = '''#define GKEY_F4 GDK_F4'''
	acceptedCode.append('\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, end)))
	
	start = '''const KeyToCommand KeyMap::MapDefault[] = {'''
	acceptedCode.append('\n'.join(retrieveCodeLines('../../scintilla/src/KeyMap.cxx', start, '};')))
	start = '''static gint messageBoxKey(GtkWidget *w, GdkEventKey *event, gpointer p) {'''
	acceptedCode.append('\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, '}')))
	start = '''long SciTEKeys::ParseKeyCode(const char *mnemonic) {'''
	acceptedCode.append('\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, '}')))
	start = '''long SciTEKeys::ParseKeyCode(const char *mnemonic) {'''
	acceptedCode.append('\n'.join(retrieveCodeLines('../win32/SciTEWin.cxx', start, '}')))
	start = '''void SciTEWin::SetMenuItem(int menuNumber, int position, int itemID,'''
	acceptedCode.append('\n'.join(retrieveCodeLines('../win32/SciTEWinBar.cxx', start, '}')))
	
	for stripType in ('FindStrip', 'ReplaceStrip', 'UserStrip'):
		start = '''bool %s::KeyDown(GdkEventKey *event) {''' % stripType
		acceptedCode.append('\n'.join(retrieveCodeLines('../gtk/SciTEGTK.cxx', start, '}')))
		
	for stripType in ('BackgroundStrip', 'SearchStrip', 'FindStrip', 'ReplaceStrip', 'UserStrip'):
		start = '''bool %s::KeyDown(WPARAM key) {''' % stripType
		acceptedCode.append('\n'.join(retrieveCodeLines('../win32/Strips.cxx', start, '}')))
	
	for (path, dirs, files) in os.walk('..'):
		for file in files:
			full = os.path.join(path, file)
			checkForAnyLogicChangesFile(full, watchFor, acceptedCode)

if __name__ == '__main__':
	checkForAnyLogicChanges()
