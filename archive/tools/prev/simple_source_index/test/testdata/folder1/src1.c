// Wave Persistence
 
#include "bcaudio.h"
#include "wav_persist.h"


// The goal is to use the same code when writing to memory and writing to disk.
// So, we have to use a type of polymorphism, which in C is not very pretty.


typedef struct
{
	bool isFile;
	FILE * f; char* mem;
	size_t position;
	notsourcesearch
} Simplestream;


size_t gfwrite ( const void * ptr, size_t size, size_t count, Simplestream * stream )
{
	if (stream->isFile)
		return fwrite( ptr, size, count, stream->f);
	else
	{
		memcpy(stream->mem + stream->position, ptr,  count*size);
		stream->position += count*size;
		return count*size;
	}
}
int gfputc ( int character, Simplestream * stream )
{
	if (stream->isFile)
		return fputc( character, stream->f);
	else
	{
		stream->mem[stream->position] = (char) character;
		stream->position += 1;
		return 1;
	}
}




errormsg caudiodata_savewavestream(CAudioData* this, Simplestream * f, int bitsPerSample /*=8 or 16*/)
{
	if (bitsPerSample != 8 && bitsPerSample!=16)
		return "NotSupported:Only 8 bit and 16 bit supported.";
	if (this->length==0 || this->data==NULL)
		return "Error:Tried to save empty wave file.";
	
	int nChannels = NUMCHANNELS(this);
	uint thedatasize = (uint)(this->length * (bitsPerSample / 8) * nChannels);
	
	uint thefilesize_minus8 = 4 + (8 + 16) + 8 + thedatasize; //header + fmt chunk + data chunk

	gfputc('R',f); gfputc('I',f); gfputc('F',f); gfputc('F',f);
	gfwrite( &thefilesize_minus8, sizeof(uint), 1, f); // size of data + headers
	
	gfputc('W',f); gfputc('A',f); gfputc('V',f); gfputc('E',f);
	gfputc('f',f); gfputc('m',f); gfputc('t',f); gfputc(' ',f);

	uint tmpuint=16; gfwrite( &tmpuint, sizeof(uint), 1, f); //size is 16 bytes
	ushort tmpushort=1; gfwrite( &tmpushort, sizeof(ushort), 1, f); //format 1
	tmpushort = (ushort)nChannels; gfwrite( &tmpushort, sizeof(ushort), 1, f); //nChannels
	tmpuint = (uint)this->sampleRate; gfwrite( &tmpuint, sizeof(uint), 1, f); //SampleRate
	
	uint byteRate = (uint)((nChannels * bitsPerSample * this->sampleRate)/8); //ByteRate
	gfwrite( &byteRate, sizeof(uint), 1, f);
	
	ushort blockAlign = (ushort)((nChannels * bitsPerSample) / 8); //BlockAlign
	gfwrite( &blockAlign, sizeof(ushort), 1, f);
	
	tmpushort = (ushort)bitsPerSample; gfwrite( &tmpushort, sizeof(ushort), 1, f); //BitsPerSample
	gfputc('d',f); gfputc('a',f); gfputc('t',f); gfputc('a',f);
	gfwrite( &thedatasize, sizeof(uint), 1, f); // Data size
	
	//Question: can we assume that all samples are within -1 to 1? If so we could save time by avoiding cast to int.
	int i;
	if (bitsPerSample==8)
	{
		if (nChannels==1)
		{
			for (i = 0; i < this->length; i++)
			{
				int bvalue = (int)(((this->data[i] / 2.0) + 0.5) * 256);
				if (bvalue > 255) bvalue = 255;
				else if (bvalue < 0) bvalue = 0;
				gfputc((byte) bvalue, f);
			}
		}
		else
		{
			for (i = 0; i < this->length; i++)
			{
				int bvalue = (int)(((this->data[i] / 2.0) + 0.5) * 256);
				if (bvalue > 255) bvalue = 255;
				else if (bvalue < 0) bvalue = 0;
				gfputc((byte) bvalue, f);
				
				bvalue = (int)(((this->data_right[i] / 2.0) + 0.5) * 256);
				if (bvalue > 255) bvalue = 255;
				else if (bvalue < 0) bvalue = 0;
				gfputc((byte) bvalue, f);
			}
		}
	}
	else if (bitsPerSample==16)
	{
		if (nChannels==1)
		{
			for (i = 0; i < this->length; i++)
			{
				double dblvalue = (this->data[i] * SHORT_MAX); // note that this is signed, so range is minval to maxval
				if (dblvalue > SHORT_MAX) dblvalue = SHORT_MAX;
				else if (dblvalue < SHORT_MIN) dblvalue = SHORT_MIN;
				short sh = (short) dblvalue;
				gfputc((byte) (sh & 0x00FF), f);// low byte. index 2*i
				gfputc((byte) (sh >> 8), f);// high byte. index 2*i+1
			}
		}
		else
		{
			for (i = 0; i < this->length; i++)
			{
				double dblvalue = (this->data[i] * SHORT_MAX); // note that this is signed, so range is minval to maxval
				if (dblvalue > SHORT_MAX) dblvalue = SHORT_MAX;
				else if (dblvalue < SHORT_MIN) dblvalue = SHORT_MIN;
				short sh = (short) dblvalue;
				gfputc((byte) (sh & 0x00FF), f);// low byte. index 2*i
				gfputc((byte) (sh >> 8), f);// high byte. index 2*i+1
				
				dblvalue = (this->data_right[i] * SHORT_MAX); // note that this is signed, so range is minval to maxval
				if (dblvalue > SHORT_MAX) dblvalue = SHORT_MAX;
				else if (dblvalue < SHORT_MIN) dblvalue = SHORT_MIN;
				sh = (short) dblvalue;
				gfputc((byte) (sh & 0x00FF), f);// low byte. index 2*i
				gfputc((byte) (sh >> 8), f);// high byte. index 2*i+1
			}
		}
	}
	
	
	return OK;
}

errormsg caudiodata_savewave(CAudioData* this, char* filename, int bitsPerSample /*=8 or 16*/)
{
	FILE * f = fopen(filename,"wb");
	if (!f) return "Could not open file for writing.";
	Simplestream obj; obj.position = 0;
	obj.isFile = 1;
	obj.f = f;
	
	errormsg msg = caudiodata_savewavestream(this,&obj,bitsPerSample);
	fclose(f);
	return msg;
}
//user is responsible for freeing!
errormsg caudiodata_savewavemem(char** out, uint*outLengthInBytes, CAudioData* this, int bitsPerSample /*=8 or 16*/)
{
	//allocate memory
	uint thedatasize = (uint)(this->length * (bitsPerSample / 8) * NUMCHANNELS(this));
	uint thefilesize =8+ 4 + (8 + 16) + 8 + thedatasize; //"riffwave" + header + fmt chunk + data chunk
	void * mem;
	mem = *out = (char*) malloc(thefilesize);
	if (!mem) return "Not enough memory.";
	*outLengthInBytes = thefilesize;
	
	Simplestream obj; obj.position = 0;
	obj.isFile = 0;
	obj.mem = mem;
	
	errormsg msg = caudiodata_savewavestream(this,&obj,bitsPerSample);
	return msg;
}


bool strfromfile(FILE*f, char c1, char c2, char c3, char c4)
{
	// we must read 4 characters regardless.
	bool b1 = (fgetc(f)==c1);
	bool b2 = (fgetc(f)==c2);
	bool b3 = (fgetc(f)==c3);
	bool b4 = (fgetc(f)==c4);
	return (b1 && b2 && b3 && b4);
}

//Caller is responsible for freeing object by calling dispose.
#define READUINT(varname) fread(&varname, sizeof(uint),1,f)
#define READUSHORT(varname) fread(&varname, sizeof(ushort),1,f)
errormsg caudiodata_loadwavestream(CAudioData**out, FILE * f)
{
	CAudioData* audio;
	audio = *out = caudiodata_new(); //we'll use audio as an alias for the output, *out.
	if (!strfromfile(f,'R','I','F','F')) return "No RIFF tag, probably invalid wav file.";
	
	uint length; READUINT(length); // (length of file in bytes) - 8
	if (!strfromfile(f,'W','A','V','E')) return "No WAVE tag, probably invalid wav file.";
	if (!strfromfile(f,'f','m','t',' ')) return "No fmt  tag.";
	
	uint size; READUINT(size); // header size
	if (size!=16) return "Size of fmt header != 16.";
	
	ushort audioformat; READUSHORT(audioformat); // audio format. 1 refers to uncompressed PCM
	if (audioformat != 1) return "Only audio format 1 is supported";
	
	ushort nChannels; READUSHORT(nChannels);
	uint nSampleRate; READUINT(nSampleRate);
	uint byteRate; READUINT(byteRate);
	ushort blockAlignTmp; READUSHORT(blockAlignTmp); //unused
	ushort nBitsPerSample; READUSHORT(nBitsPerSample);
	
	
	
	if (nChannels != 1 && nChannels!=2) return "Unsupported number of channels. Currently only support 1 or 2.";
	if (nBitsPerSample != 8 && nBitsPerSample!=16) return "Unsupported bitrate, Currently supports 8bit and 16 bit audio.";
	
	uint dataSize = 0;
	int MAXTRIES = 100, nTry = 0; bool found = 0;
	for (nTry = 0; nTry < MAXTRIES; nTry++)
	{
		bool rightTag = strfromfile(f, 'd','a','t','a');
		READUINT(dataSize);
		if (dataSize > INT_MAX) return "Data size too large.";
			
		if (rightTag)
		{
			found = 1;
			break;
		}
		else
		{
			// look ahead by dataSize bytes, effectively skipping over the current chunk
			uint z; for (z=0; z<dataSize; z++) fgetc(f);
		}
	}
	if (!found)
		return "Could not find data tag";
	
	
	uint rawdatalength = dataSize;
	//we could move datasize chars into memory, but that'd involve another malloc. The data from file should be in cache anyways.
	
	int nSamples = ((8 * rawdatalength) / (nBitsPerSample * nChannels));
	
	//allocate memory.
	errormsg msg = caudiodata_allocate(audio, nSamples, nChannels, nSampleRate);
	if (msg!=OK) return msg;
	
	// The next step is to convert data to doubles...this is probably lossless because the precision of doubles is pretty high
	int i;
	if (nBitsPerSample == 8)
	{
		if (nChannels == 1)
		{
			for (i = 0; i < rawdatalength; i += 1)
				audio->data[i] = (fgetc(f) / 256.0) * 2.0 - 1.0;   //note: stored as unsigned.
		}
		else
		{
			for (i = 0; i < rawdatalength; i += 2)
			{
				audio->data[i/2] = (fgetc(f) / 256.0) * 2.0 - 1.0;
				audio->data_right[i/2] = (fgetc(f) / 256.0) * 2.0 - 1.0;
			}
		}
	}
	else if (nBitsPerSample == 16) //note: signed
	{
		if (nChannels == 1)
		{
			for (i = 0; i < rawdatalength; i += 2)
			{
				short sh1 = fgetc(f); // assumes intel byte order
				short sh2 = (short)(((short)fgetc(f)) << 8);
				short sh = (short)(sh1 + sh2);
				audio->data[i/2] = sh / ((double)SHORT_MAX);
			}
		}
		else
		{
			for (i = 0; i < rawdatalength; i += 4)
			{
				short sh1 = fgetc(f); // assumes intel byte order
				short sh2 = (short)(((short)fgetc(f)) << 8);
				short sh = (short)(sh1 + sh2);
				audio->data[i/4] = sh / ((double)SHORT_MAX);
				
				sh1 = fgetc(f); // assumes intel byte order
				sh2 = (short)(((short)fgetc(f)) << 8);
				sh = (short)(sh1 + sh2);
				audio->data_right[i/4] = sh / ((double)SHORT_MAX);
			}
		}
	}
	else return "Only 8 or 16 bit supported currently.";
		
	return OK;
}

errormsg caudiodata_loadwave(CAudioData** waveout, char* filename)
{
	FILE * f = fopen(filename,"rb");
	if (!f) return "Could not open file for reading.";
	errormsg msg = caudiodata_loadwavestream(waveout,f);
	fclose(f);
	return msg;
}




