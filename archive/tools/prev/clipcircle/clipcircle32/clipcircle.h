
#include <stdlib.h>
const int g_nItems = 8;
class ClipCircle
{
private:
	WCHAR* m_items[g_nItems];
	int m_ptr;
public:
	ClipCircle()
	{
		// set everything to a space character
		for (int i=0; i<_countof(m_items); i++)
		{
			m_items[i] = (WCHAR*) calloc(2, sizeof(WCHAR));
			m_items[i][0] = L' ';
		}
		m_ptr = 0;
	}
	~ClipCircle()
	{
		for (int i=0; i<_countof(m_items);i++)
			free(m_items[i]);
	}
	void OnClipChange(const WCHAR* s)
	{
		if (!s || !s[0])
			return;
		// is it equal to anything already cached?
		for (int i=0; i<_countof(m_items);i++)
			if (wcscmp(s, m_items[i])==0)
				return;

		// push it onto the ring
		m_ptr++;
		if (m_ptr >= g_nItems) m_ptr=0;
		free(m_items[m_ptr]);
		m_items[m_ptr] = _wcsdup(s);
		PrintDebug();
	}
	void PasteAndCycle()
	{
		SetClipboardString(m_items[m_ptr]);
		sendinput_ctrlv(wcslen(m_items[m_ptr]));
		m_ptr--;
		if (m_ptr < 0) m_ptr= g_nItems-1;
		PrintDebug();
	}


	void PrintDebug()
	{
		FILE* f = fopen("C:\\pydev\\pyaudio_here\\progs\\clipcircle\\clipcircle32\\dbgout.txt", "w");
		for (int i=0; i<g_nItems; i++)
		{
			const WCHAR* fmt = (i==m_ptr ? L"(%d):%s\n" : L"%d:%s\n");
			fwprintf(f, fmt, i, m_items[i]);
		}
		fclose(f);
	}

};

