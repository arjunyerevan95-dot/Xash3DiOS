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
	shaderconv_need_t need = { 0 };

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
	hardext.glsl300es = argc > 2 && !strcmp( argv[2], "legacy" ) ? 0 : 1;
	hardext.maxdrawbuffers = 1;
	need.need_texcoord = -1;
	need.need_essl300 = argc > 2 && !strcmp( argv[2], "force300" );
	output = ConvertShader( input, argc > 1 && !strcmp( argv[1], "vertex" ), &need );
	if( !output ) return 1;
	fprintf( stderr, "need_essl300=%d\n", need.need_essl300 );
	fputs( output, stdout );

	free( output );
	free( input );
	return 0;
}
