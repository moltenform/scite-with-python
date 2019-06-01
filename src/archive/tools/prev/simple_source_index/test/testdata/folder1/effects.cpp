#include "bcaudio.h"
#include "effects.h"

bool effect_checksame(CAudioData* w1, CAudioData* w2, bool lengthmatters)
{
	if (lengthmatters==1)
		if (w1->length != w2->length) return 0;
	if ((w1->data_right==NULL) ^ (w2->data_right==NULL)) return 0; //xor checks if they are they Different.
	if (w1->sampleRate != w2->sampleRate) return 0;
	return 1;
}

double effect_interpolate(double* data, int length, double sampleIndex)
{
	if (sampleIndex > length-1) sampleIndex = length-1;
	else if (sampleIndex < 0+1) sampleIndex=0;
	
	// Uses linear interpolation to find, say, the 4.15th element of an array of doubles.
        // In the future maybe consider better interpolation methods, like cubic, polynomial, or sinc
	double proportion = sampleIndex - trunc(sampleIndex);
	double v1 = data[(int)trunc(sampleIndex)];
	double v2 = data[(int)ceil(sampleIndex)];
	return v2 * proportion + v1 * (1 - proportion);
}


void effect_mix_impl(int length, double* out, double* d1,double* d2, double s1, double s2)
{
	if (d1==NULL || d2==NULL || out==NULL) return;
	int i; for (i=0; i<length;i++)
	{
		out[i] = d1[i]*s1 + d2[i]*s2;
		if (out[i]>1.0) out[i]=1.0;
		else if (out[i]<-1.0) out[i] = -1.0;
	}
}
// Caller responsible for freeing! You must call caudiodata_dispose!
errormsg effect_mix(CAudioData**out, CAudioData* w1, CAudioData* w2, double s1, double s2)
{
	CAudioData* audio;
	audio = *out = caudiodata_new(); //use audio as an alias for the output, *out.
	if (!effect_checksame(w1,w2,1)) return "Inputs must have same length, same sample rate and # of channels";

	errormsg msg = caudiodata_allocate(audio, w1->length, NUMCHANNELS(w1), w1->sampleRate);
	if (msg!=OK) return msg;
	effect_mix_impl(w1->length,audio->data,w1->data, w2->data,s1, s2);
	effect_mix_impl(w1->length,audio->data_right,w1->data_right, w2->data_right,s1, s2);

	return OK;
}

void effect_modulate_impl(int length, double* out, double* d1,double* d2, double a1, double a2)
{
	if (d1==NULL || d2==NULL || out==NULL) return;
	int i; for (i=0; i<length;i++)
	{
		out[i] = (a1+d1[i]) * (a2+d2[i]);
		if (out[i]>1.0) out[i]=1.0;
		else if (out[i]<-1.0) out[i] = -1.0;
	}
}
// Caller responsible for freeing! You must call caudiodata_dispose!
errormsg effect_modulate(CAudioData**out, CAudioData* w1, CAudioData* w2, double a1, double a2)
{
	CAudioData* audio;
	audio = *out = caudiodata_new(); //use audio as an alias for the output, *out.
	if (!effect_checksame(w1,w2,1)) return "Inputs must have same length, same sample rate and # of channels";

	errormsg msg = caudiodata_allocate(audio, w1->length, NUMCHANNELS(w1), w1->sampleRate);
	if (msg!=OK) return msg;
	effect_modulate_impl(w1->length,audio->data,w1->data, w2->data,a1, a2);
	effect_modulate_impl(w1->length,audio->data_right,w1->data_right, w2->data_right,a1, a2);

	return OK;
}

// Caller responsible for freeing! You must call caudiodata_dispose!
errormsg effect_append(CAudioData**out, CAudioData* w1, CAudioData* w2)
{
	CAudioData* audio;
	audio = *out = caudiodata_new(); //use audio as an alias for the output, *out.
	if (!effect_checksame(w1,w2,0)) return "Inputs must have same sample rate and # of channels";

	errormsg msg = caudiodata_allocate(audio, w1->length+w2->length, NUMCHANNELS(w1), w1->sampleRate);
	if (msg!=OK) return msg;
		
	memcpy( audio->data, w1->data, w1->length*sizeof(double) ); //copy over first clip
	memcpy( audio->data + w1->length, w2->data, w2->length*sizeof(double)); // copy over second clip.
	
	if (w1->data_right==NULL) return OK;
	memcpy( audio->data_right, w1->data_right, w1->length*sizeof(double)); //copy over first clip
	memcpy( audio->data_right + w1->length, w2->data_right, w2->length*sizeof(double)); // copy over second clip.

	return OK;
}

// the factor is the rate we walk through the file. if factor is 2.0, then we walk twice as fast
void effect_scale_pitch_duration_impl(int newLength, double* out, int oldLength, double* d1, double factor)
{
	if (d1==NULL || out==NULL) return;
	double currentPosition = 0.0;
	int i; for (i= 0; i < newLength; i++)
	{
	out[i] = effect_interpolate(d1, oldLength, currentPosition);
	currentPosition += factor;
	}
}
// Caller responsible for freeing! You must call caudiodata_dispose!
errormsg effect_scale_pitch_duration(CAudioData**out, CAudioData* w1, double factor)
{
	CAudioData* audio;
	audio = *out = caudiodata_new(); //use audio as an alias for the output, *out.

	if (factor<=0) return "Invalid factor.";
	int newLength = (int)(w1->length / factor); // find new length
	
	errormsg msg = caudiodata_allocate(audio, newLength, NUMCHANNELS(w1), w1->sampleRate);
	if (msg!=OK) return msg;
	effect_scale_pitch_duration_impl(audio->length,audio->data,w1->length, w1->data,factor);
	effect_scale_pitch_duration_impl(audio->length,audio->data_right,w1->length,w1->data_right,factor);
	return OK;
}

 // walk through the file at varying speeds
void effect_vibrato_impl(int length, double* out, double* d1, double vibratoFreqScale, double width)
{
	if (d1==NULL || out==NULL) return;
	double currentPosition = 0.0;
	
	int i; for (i = 0; i < length; i++)
	{
		out[i] = effect_interpolate(d1, length, currentPosition);
		currentPosition += 1.0 + width *sin(i * vibratoFreqScale);
	}
}
// Caller responsible for freeing! You must call caudiodata_dispose!
//common values: 0.1, 2.0. freq is in Hz, width is strength of the effect
errormsg effect_vibrato(CAudioData**out, CAudioData* w1, double freq, double width)
{
	CAudioData* audio;
	audio = *out = caudiodata_new(); //use audio as an alias for the output, *out.

	errormsg msg = caudiodata_allocate(audio, w1->length, NUMCHANNELS(w1), w1->sampleRate);
	if (msg!=OK) return msg;
	double vibratoFreqScale = 2.0 * PI * freq / (double)w1->sampleRate;
	effect_vibrato_impl(audio->length,audio->data, w1->data,vibratoFreqScale,width);
	effect_vibrato_impl(audio->length,audio->data_right,w1->data_right,vibratoFreqScale,width);
	return OK;
}

