

void SetClipboardString(const WCHAR* s)
{
 if (OpenClipboard(NULL))
  {
   // Empty the Clipboard. This also has the effect
   // of allowing Windows to free the memory associated
   // with any data that is in the Clipboard
   EmptyClipboard();

   HGLOBAL hClipboardData;
   hClipboardData = GlobalAlloc(GMEM_DDESHARE, 
                               sizeof(WCHAR) * (wcslen(s)+1));
    WCHAR* pchData;
	pchData = (WCHAR*)GlobalLock(hClipboardData);
    wcscpy(pchData, s);
		  
   // Once done, I unlock the memory - remember you 
   // don't call GlobalFree because Windows will free the 
   // memory automatically when EmptyClipboard is next 
   // called. 

   GlobalUnlock(hClipboardData);
		  
   // Now, set the Clipboard data by specifying that 
   // unicode text is being used and passing the handle to
   // the global memory.
   SetClipboardData(CF_UNICODETEXT, hClipboardData);
		  
   // Finally, when finished I simply close the Clipboard
   // which has the effect of unlocking it so that other
   // applications can examine or modify its contents.
   CloseClipboard();
	}
}


