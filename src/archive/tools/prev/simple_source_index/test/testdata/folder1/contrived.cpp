wantstring typedef struct
{
	bool isFile; wantstring
	FILE * f; char* mem;
	size_t position;
	int n; CAudioData_donot hit
} Simplestream;


size_t gfwrite ( const void * ptr, size_t size, size_t count, Simplestream * stream )
{
wantstring	if (stream->isFile)
wantstring	if (stream->isFile) same twice wantstring
		return fwrite( ptr, size, count, stream->f); notCAudioData
	else
	a wantstring { also twice wantstring and again wantstring sdf
		memcpy(stream->mem + stream->position, ptr,  count*size);
		stream->position += count*size; notCAudioDatanot
		return count*size;
	}
} wantstring