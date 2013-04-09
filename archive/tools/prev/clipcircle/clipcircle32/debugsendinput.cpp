
void PrintDebugsendinput(int nLen, INPUT* arinput, int nStart, int nAll, int nw)
{
	char buf[256];
	sprintf(buf, "C:\\pydev\\pyaudio_here\\progs\\clipcircle\\clipcircle32\\dbgoutsendinput%d.txt", nw);
	FILE* f = fopen(buf, "w");
	for (int i=0; i<nAll; i++)
	{
		if (i==nStart) fprintf(f, "--start--\n");
		if (i==nStart+nLen) fprintf(f, "--end--\n");
		const char* sname= "unknown";
		if (arinput[i].ki.wVk == 0) sname = "0";
		else if (arinput[i].ki.wVk == VK_LCONTROL) sname = "VK_LCONTROL";
		else if (arinput[i].ki.wVk == 'V') sname = "'V'";
		else if (arinput[i].ki.wVk == VK_LSHIFT) sname = "VK_LSHIFT";
		else if (arinput[i].ki.wVk == VK_LEFT) sname = "VK_LEFT";
		const char* snamen = (arinput[i].ki.dwFlags & KEYEVENTF_KEYUP) ? "(up)" : "";
		fprintf(f, "%d) %s %s\n", i, sname, snamen);
	}
	fclose(f);
}

