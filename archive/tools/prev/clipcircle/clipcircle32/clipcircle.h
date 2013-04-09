
#include <stdlib.h>

const int g_nItems = 8;

// This class maintains a ring buffer of clipboard items.
class ClipCircle
{
public:
	ClipCircle()
	{
		// initialize all strings to " " (a single space)
		for (int i=0; i<_countof(m_items); i++)
			m_items[i] = _wcsdup(L" ");

		m_ptr = 0;
	}
	~ClipCircle()
	{
		for (int i=0; i<_countof(m_items);i++)
			free(m_items[i]);
	}

	// Push onto the buffer.
	void OnClipChange(const WCHAR* wz)
	{
		if (!wz || !wz[0])
			return;

		// ignore if it is equal to the current one.
		if (wcscmp(wz, m_items[m_ptr])==0)
			return;

		// push it onto the ring
		m_ptr++;
		if (m_ptr >= g_nItems) m_ptr=0;
		free(m_items[m_ptr]);
		m_items[m_ptr] = _wcsdup(wz);
	}

	// Pop from the buffer. Output the string to the current window.
	void PasteAndCycle()
	{
		SetClipboardString(m_items[m_ptr]);
		SendKeyboardInputToWindow(m_items[m_ptr]);
		m_ptr--;
		if (m_ptr < 0) m_ptr = g_nItems-1;
	}

private:
	WCHAR* m_items[g_nItems];
	int m_ptr;
};

