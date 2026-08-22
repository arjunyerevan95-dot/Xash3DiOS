#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "shaderconv.h"
#include "init.h"
#include "../glx/hardext.h"

globals4es_t globals4es = { 0 };
hardext_t hardext = { 0 };
const char *fpeshader_signature = "// FPE_Shader generated\n";

int main( int argc, char **argv )
{
	size_t size = 0;
	size_t capacity = 4096;
	char *input = calloc( capacity, 1 );
	char *output;

	if( !input ) return 1;
	while( !feof( stdin ) )
	{
		size_t count;
		if( size + 2049 > capacity )
		{
			capacity *= 2;
			input = realloc( input, capacity );
			if( !input ) return 1;
		}
		count = fread( input + size, 1, 2048, stdin );
		size += count;
		if( ferror( stdin ) ) return 1;
	}
	input[size] = '\0';

	hardext.highp = 1;
	hardext.derivatives = 1;
	hardext.shaderlod = 1;
	hardext.maxdrawbuffers = 1;
	output = ConvertShader( input, argc > 1 && !strcmp( argv[1], "vertex" ), NULL );
	if( !output ) return 1;
	fputs( output, stdout );

	free( output );
	free( input );
	return 0;
}
