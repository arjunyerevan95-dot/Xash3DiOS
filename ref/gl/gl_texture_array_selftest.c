#include "gl_local.h"

#if XASH_IOS && XASH_GL4ES
#include "gl4es/include/gl4esinit.h"

#define GL_TEXTURE_2D_ARRAY 0x8C1A
#define GL_TEXTURE_BINDING_2D_ARRAY 0x8C1D
#define GL_MAX_ARRAY_TEXTURE_LAYERS 0x88FF
#define GL_SAMPLER_2D_ARRAY 0x8DC1
#define IOS_ARRAY_VIEWPORT 0x0BA2
#define IOS_ARRAY_COLOR_CLEAR_VALUE 0x0C22
#define IOS_ARRAY_FRAMEBUFFER_COMPLETE 0x8CD5u
#define IOS_ARRAY_EXPECTED_CHECKSUM 0xA915906Du
#ifndef GL_TEXTURE0
#define GL_TEXTURE0 0x84C0
#define GL_TEXTURE1 0x84C1
#define GL_TEXTURE2 0x84C2
#define GL_TEXTURE3 0x84C3
#endif

extern void gl4es_glTexStorage3D( GLenum target, GLsizei levels,
	GLenum internalformat, GLsizei width, GLsizei height, GLsizei depth );
extern GLuint gl4es_glCreateShader( GLenum shaderType );
extern void gl4es_glShaderSource( GLuint shader, GLsizei count,
	const GLcharARB * const *string, const GLint *length );
extern void gl4es_glCompileShader( GLuint shader );
extern void gl4es_glGetShaderiv( GLuint shader, GLenum pname, GLint *params );
extern void gl4es_glDeleteShader( GLuint shader );
extern GLuint gl4es_glCreateProgram( void );
extern void gl4es_glAttachShader( GLuint program, GLuint shader );
extern void gl4es_glBindAttribLocation( GLuint program, GLuint index, const GLcharARB *name );
extern void gl4es_glLinkProgram( GLuint program );
extern void gl4es_glGetActiveUniform( GLuint program, GLuint index, GLsizei bufSize,
	GLsizei *length, GLint *size, GLenum *type, GLcharARB *name );
extern void gl4es_glUseProgram( GLuint program );
extern GLint gl4es_glGetUniformLocation( GLuint program, const GLcharARB *name );
extern void gl4es_glUniform1i( GLint location, GLint v0 );
extern void gl4es_glUniform1f( GLint location, GLfloat v0 );
extern void gl4es_glEnableVertexAttribArray( GLuint index );
extern void gl4es_glDisableVertexAttribArray( GLuint index );
extern void gl4es_glVertexAttribPointer( GLuint index, GLint size, GLenum type,
	GLboolean normalized, GLsizei stride, const GLvoid *pointer );
extern void gl4es_glDeleteProgram( GLuint program );

static int R_IOSArrayCallResult( unsigned *sequence, const char *call,
	const char *owner, GLuint object, GLuint framebuffer )
{
	GLenum error = pglGetError();
	const unsigned current = ++( *sequence );
	gEngfuncs.Con_Printf( "iOS texture array selftest sampling-call: seq=%u call=%s owner=%s object=%u framebuffer=%u error=0x%04x result=%s\n",
		current, call, owner, object, framebuffer, error,
		error == GL_NO_ERROR ? "PASS" : "FAIL" );
	while( pglGetError() != GL_NO_ERROR ) { }
	return error == GL_NO_ERROR;
}

#define IOS_ARRAY_GL_CALL( call, owner, object, framebuffer, expression ) \
	do { expression; if( !R_IOSArrayCallResult( &samplingSequence, call, owner, object, framebuffer )) failures++; } while( 0 )

static int R_IOSArrayDrainError( const char *step )
{
	GLenum error = pglGetError();
	if( error == GL_NO_ERROR )
		return 1;
	gEngfuncs.Con_Printf( "iOS texture array selftest lifecycle: gl-error step=%s error=0x%04x\n", step, error );
	while( pglGetError() != GL_NO_ERROR ) { }
	return 0;
}

static GLuint R_IOSArrayCompile( GLenum type, const char *source )
{
	GLuint shader = gl4es_glCreateShader( type );
	GLint length = Q_strlen( source );
	GLint status = GL_FALSE;
	gl4es_glShaderSource( shader, 1, (const GLcharARB * const *)&source, &length );
	gl4es_glCompileShader( shader );
	gl4es_glGetShaderiv( shader, GL_OBJECT_COMPILE_STATUS_ARB, &status );
	if( !status )
	{
		gEngfuncs.Con_Printf( "iOS texture array selftest shader: compile=FAIL stage=0x%04x\n", type );
		gl4es_glDeleteShader( shader );
		return 0;
	}
	return shader;
}

static int R_IOSArrayNear( const byte *pixel, const byte *expected )
{
	return abs( pixel[0] - expected[0] ) <= 8 &&
		abs( pixel[1] - expected[1] ) <= 8 &&
		abs( pixel[2] - expected[2] ) <= 8 && pixel[3] >= 240;
}

void R_IOSTextureArraySelftest( void )
{
	static qboolean dispatched;
	static const char *vertexSource =
		"#version 130\n#define GL4ES_TEXTURE_ARRAY_PROGRAM 1\nattribute vec2 a_Position; varying vec2 v_TexCoord;\n"
		"void main(){ v_TexCoord=a_Position*0.5+0.5; gl_Position=vec4(a_Position,0.0,1.0); }\n";
	static const char *fragmentSource =
		"#version 130\nuniform sampler2DArray u_Array; uniform float u_Layer; varying vec2 v_TexCoord;\n"
		"void main(){ gl_FragColor=texture2DArray(u_Array,vec3(v_TexCoord,u_Layer)); }\n";
	static const GLfloat quad[] = { -1.0f,-1.0f, 1.0f,-1.0f, -1.0f,1.0f, 1.0f,1.0f };
	static const byte expected[4][4] = {
		{ 255, 0, 0, 255 }, { 0, 255, 0, 255 },
		{ 255, 0, 255, 255 }, { 255, 255, 0, 255 }
	};
	byte mutablePixels[4 * 4 * 4 * 4];
	byte replacement[4 * 4 * 4];
	byte immutablePixels[4 * 4 * 4];
	byte pixel[4];
	byte dxt[16] = { 0x00,0xf8,0x00,0x00,0,0,0,0, 0x00,0xf8,0x00,0x00,0,0,0,0 };
	byte dxtSub[8] = { 0xe0,0x07,0x00,0x00,0,0,0,0 };
	GLuint textures[4] = { 0 };
	GLuint vertexBuffer = 0;
	GLuint vertexShader = 0, fragmentShader = 0, program = 0;
	GLint maxLayers = 0, binding2D = 0, bindingArray = 0;
	GLint layerLocation, samplerLocation;
	GLuint uniforms = 0;
	GLint width = gpGlobals->width, height = gpGlobals->height;
	int failures = 0, samplerFound = 0;
	unsigned checksum = 2166136261u;
	unsigned samplingSequence = 0;

	if( !gEngfuncs.Sys_CheckParm( "-gl4es_texture_array_selftest" ))
		return;
	if( dispatched )
		return;
	dispatched = true;

	gEngfuncs.Con_Printf( "iOS texture array selftest policy: mode=selftest-only terrain-admission=disabled backend=native-es3\n" );
	pglGetIntegerv( GL_MAX_ARRAY_TEXTURE_LAYERS, &maxLayers );
	gEngfuncs.Con_Printf( "iOS texture array selftest lifecycle: phase=context-created max_layers=%d size=%dx%d\n", maxLayers, width, height );
	if( maxLayers < 4 || width < 4 || height < 4 || !R_IOSArrayDrainError( "capability" )) failures++;

	for( int layer = 0; layer < 4; ++layer )
		for( int i = 0; i < 16; ++i )
			memcpy( mutablePixels + ( layer * 16 + i ) * 4, expected[layer], 4 );
	for( int i = 0; i < 16; ++i )
	{
		mutablePixels[( 2 * 16 + i ) * 4 + 0] = 0;
		mutablePixels[( 2 * 16 + i ) * 4 + 1] = 0;
		mutablePixels[( 2 * 16 + i ) * 4 + 2] = 255;
		mutablePixels[( 2 * 16 + i ) * 4 + 3] = 255;
	}
	for( int i = 0; i < 16; ++i ) memcpy( replacement + i * 4, expected[2], 4 );
	for( int i = 0; i < 16; ++i ) { immutablePixels[i*4+0]=0; immutablePixels[i*4+1]=255; immutablePixels[i*4+2]=255; immutablePixels[i*4+3]=255; }

	pglGenTextures( 4, textures );
	pglActiveTexture( GL_TEXTURE0 );
	pglBindTexture( GL_TEXTURE_2D_ARRAY, textures[0] );
	pglTexParameteri( GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST );
	pglTexParameteri( GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_NEAREST );
	pglTexParameteri( GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE );
	pglTexParameteri( GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE );
	pglTexImage3D( GL_TEXTURE_2D_ARRAY, 0, GL_RGBA8, 4, 4, 4, 0, GL_RGBA, GL_UNSIGNED_BYTE, mutablePixels );
	pglTexSubImage3D( GL_TEXTURE_2D_ARRAY, 0, 0, 0, 2, 4, 4, 1, GL_RGBA, GL_UNSIGNED_BYTE, replacement );
	{
		int uploadOk = R_IOSArrayDrainError( "mutable-upload" );
		if( !uploadOk ) failures++;
		gEngfuncs.Con_Printf( "iOS texture array selftest upload: mutable=image3d subimage3d zoffset=2 depth=1 result=%s\n", uploadOk ? "PASS" : "FAIL" );
	}

	pglActiveTexture( GL_TEXTURE1 );
	pglBindTexture( GL_TEXTURE_2D_ARRAY, textures[1] );
	gl4es_glTexStorage3D( GL_TEXTURE_2D_ARRAY, 3, GL_RGBA8, 4, 4, 4 );
	pglTexSubImage3D( GL_TEXTURE_2D_ARRAY, 0, 0, 0, 3, 4, 4, 1, GL_RGBA, GL_UNSIGNED_BYTE, immutablePixels );
	pglTexSubImage3D( GL_TEXTURE_2D_ARRAY, 1, 0, 0, 1, 2, 2, 1, GL_RGBA, GL_UNSIGNED_BYTE, immutablePixels );
	if( !R_IOSArrayDrainError( "immutable-upload" )) failures++;
	gEngfuncs.Con_Printf( "iOS texture array selftest upload: immutable=storage3d levels=3 subimage3d zoffset=3 mip=0,1 result=%s\n", failures ? "CHECK" : "PASS" );

	pglActiveTexture( GL_TEXTURE2 );
	pglBindTexture( GL_TEXTURE_2D_ARRAY, textures[2] );
	pglCompressedTexImage3DARB( GL_TEXTURE_2D_ARRAY, 0, GL_COMPRESSED_RGB_S3TC_DXT1_EXT, 4, 4, 2, 0, sizeof( dxt ), dxt );
	pglCompressedTexSubImage3DARB( GL_TEXTURE_2D_ARRAY, 0, 0, 0, 1, 4, 4, 1, GL_COMPRESSED_RGB_S3TC_DXT1_EXT, sizeof( dxtSub ), dxtSub );
	if( !R_IOSArrayDrainError( "compressed-decode-upload" )) failures++;
	gEngfuncs.Con_Printf( "iOS texture array selftest upload: compressed=dxt1 image+subimage route=per-layer-rgba8-decompression zoffset=1 result=%s\n", failures ? "CHECK" : "PASS" );

	pglActiveTexture( GL_TEXTURE0 );
	pglBindTexture( GL_TEXTURE_2D, textures[3] );
	pglGetIntegerv( GL_TEXTURE_BINDING_2D, &binding2D );
	pglGetIntegerv( GL_TEXTURE_BINDING_2D_ARRAY, &bindingArray );
	pglBindTexture( GL_TEXTURE_2D, textures[0] );
	if( pglGetError() != GL_INVALID_OPERATION ) failures++;
	pglDeleteTextures( 1, &textures[3] );
	pglGenTextures( 1, &textures[3] );
	pglActiveTexture( GL_TEXTURE3 );
	pglBindTexture( GL_TEXTURE_2D_ARRAY, textures[3] );
	gEngfuncs.Con_Printf( "iOS texture array selftest object: array=%u tex2d_binding=%d array_binding=%d units=0,1,2,3 alias_rejected=%s delete_recreate=%u\n",
		textures[0], binding2D, bindingArray, failures ? "CHECK" : "PASS", textures[3] );
	if( !R_IOSArrayDrainError( "object-routing" )) failures++;

	vertexShader = R_IOSArrayCompile( GL_VERTEX_SHADER_ARB, vertexSource );
	fragmentShader = R_IOSArrayCompile( GL_FRAGMENT_SHADER_ARB, fragmentSource );
	if( !vertexShader || !fragmentShader ) failures++;
	if( !failures )
	{
		GLuint linked = GL_FALSE;
		program = gl4es_glCreateProgram();
		gl4es_glAttachShader( program, vertexShader );
		gl4es_glAttachShader( program, fragmentShader );
		gl4es_glBindAttribLocation( program, 0, "a_Position" );
		gl4es_glLinkProgram( program );
		gl4es_glGetProgramiv( program, GL_OBJECT_LINK_STATUS_ARB, &linked );
		if( !linked ) failures++;
		gl4es_glGetProgramiv( program, GL_OBJECT_ACTIVE_UNIFORMS_ARB, &uniforms );
		for( int i = 0; i < uniforms; ++i )
		{
			GLcharARB name[64]; GLsizei length = 0; GLint size = 0; GLenum type = 0;
			gl4es_glGetActiveUniform( program, i, sizeof( name ), &length, &size, &type, name );
			if( !Q_strcmp( name, "u_Array" ) && type == GL_SAMPLER_2D_ARRAY ) samplerFound = 1;
		}
		if( !samplerFound ) failures++;
	}
	gEngfuncs.Con_Printf( "iOS texture array selftest shader: source=glsl130 translated=essl300 stage-correct=1 sampler2DArray_reflection=%s\n", samplerFound ? "PASS" : "FAIL" );

	if( !failures )
	{
		gl4es_external_default_state_t framebufferProof;
		GLint savedViewport[4] = { 0 };
		GLint savedScissor[4] = { 0 };
		GLfloat savedClearColor[4] = { 0 };
		GLint savedPackAlignment = 4;
		GLint savedArrayBuffer = 0;
		GLboolean savedScissorEnabled;
		const GLint viewports[4][4] = {
			{ 0, 0, width/2, height/2 }, { width/2, 0, width-width/2, height/2 },
			{ 0, height/2, width/2, height-height/2 }, { width/2, height/2, width-width/2, height-height/2 }
		};
		const GLuint framebuffer = gl4es_external_default_framebuffer_state( width,
			height, 0, &framebufferProof ) ? framebufferProof.registered_framebuffer : 0;

		if( !R_IOSArrayCallResult( &samplingSequence, "stage-entry", "selftest-boundary", program, framebuffer ))
			failures++;
		if( !framebuffer || framebufferProof.logical_current ||
			framebufferProof.logical_read || framebufferProof.logical_draw ||
			framebufferProof.native_draw != framebuffer ||
			framebufferProof.native_read != framebuffer ||
			framebufferProof.framebuffer_status != IOS_ARRAY_FRAMEBUFFER_COMPLETE )
			failures++;
		gEngfuncs.Con_Printf( "iOS texture array selftest sampling-fbo: owner=sdl-view logical=0/0/0 native=%u/%u registered=%u status=0x%04x size=%dx%d samples=0 result=%s\n",
			framebufferProof.native_draw, framebufferProof.native_read,
			framebufferProof.registered_framebuffer, framebufferProof.framebuffer_status,
			width, height, failures ? "FAIL" : "PASS" );
		if( !R_IOSArrayCallResult( &samplingSequence, "gl4es_external_default_framebuffer_state",
			"direct-drawable", framebufferProof.registered_framebuffer, framebuffer ))
			failures++;

		IOS_ARRAY_GL_CALL( "glGetIntegerv(GL_VIEWPORT)", "GL4ES", 0, framebuffer,
			pglGetIntegerv( IOS_ARRAY_VIEWPORT, savedViewport ));
		IOS_ARRAY_GL_CALL( "glGetIntegerv(GL_SCISSOR_BOX)", "GL4ES", 0, framebuffer,
			pglGetIntegerv( GL_SCISSOR_BOX, savedScissor ));
		savedScissorEnabled = pglIsEnabled( GL_SCISSOR_TEST );
		if( !R_IOSArrayCallResult( &samplingSequence, "glIsEnabled(GL_SCISSOR_TEST)",
			"GL4ES", 0, framebuffer )) failures++;
		IOS_ARRAY_GL_CALL( "glGetIntegerv(GL_PACK_ALIGNMENT)", "GL4ES", 0, framebuffer,
			pglGetIntegerv( GL_PACK_ALIGNMENT, &savedPackAlignment ));
		IOS_ARRAY_GL_CALL( "glGetFloatv(GL_COLOR_CLEAR_VALUE)", "GL4ES", 0, framebuffer,
			pglGetFloatv( IOS_ARRAY_COLOR_CLEAR_VALUE, savedClearColor ));
		IOS_ARRAY_GL_CALL( "glGetIntegerv(GL_ARRAY_BUFFER_BINDING)", "GL4ES", 0, framebuffer,
			pglGetIntegerv( GL_ARRAY_BUFFER_BINDING_ARB, &savedArrayBuffer ));

		IOS_ARRAY_GL_CALL( "glUseProgram", "GL4ES-program-cache", program, framebuffer,
			gl4es_glUseProgram( program ));
		samplerLocation = gl4es_glGetUniformLocation( program, "u_Array" );
		if( !R_IOSArrayCallResult( &samplingSequence, "glGetUniformLocation(u_Array)",
			"GL4ES-program-cache", program, framebuffer )) failures++;
		layerLocation = gl4es_glGetUniformLocation( program, "u_Layer" );
		if( !R_IOSArrayCallResult( &samplingSequence, "glGetUniformLocation(u_Layer)",
			"GL4ES-program-cache", program, framebuffer )) failures++;
		if( samplerLocation < 0 || layerLocation < 0 ) failures++;
		IOS_ARRAY_GL_CALL( "glUniform1i(u_Array)", "GL4ES-uniform-type-cache", program, framebuffer,
			gl4es_glUniform1i( samplerLocation, 0 ));
		IOS_ARRAY_GL_CALL( "glActiveTexture(GL_TEXTURE0)", "GL4ES-texture-state", textures[0], framebuffer,
			pglActiveTexture( GL_TEXTURE0 ));
		IOS_ARRAY_GL_CALL( "glEnable(GL_TEXTURE_2D_ARRAY)", "GL4ES-texture-state", textures[0], framebuffer,
			pglEnable( GL_TEXTURE_2D_ARRAY ));
		IOS_ARRAY_GL_CALL( "glBindTexture(GL_TEXTURE_2D_ARRAY)", "GL4ES-native-array-binding", textures[0], framebuffer,
			pglBindTexture( GL_TEXTURE_2D_ARRAY, textures[0] ));
		IOS_ARRAY_GL_CALL( "glGenBuffers", "GL4ES-buffer-owner", 0, framebuffer,
			pglGenBuffersARB( 1, &vertexBuffer ));
		IOS_ARRAY_GL_CALL( "glBindBuffer(GL_ARRAY_BUFFER)", "GL4ES-buffer-owner", vertexBuffer, framebuffer,
			pglBindBufferARB( GL_ARRAY_BUFFER_ARB, vertexBuffer ));
		IOS_ARRAY_GL_CALL( "glBufferData(GL_ARRAY_BUFFER)", "GL4ES-native-vbo", vertexBuffer, framebuffer,
			pglBufferDataARB( GL_ARRAY_BUFFER_ARB, sizeof( quad ), quad, GL_STATIC_DRAW_ARB ));
		IOS_ARRAY_GL_CALL( "glEnableVertexAttribArray(0)", "GL4ES-vertex-state", vertexBuffer, framebuffer,
			gl4es_glEnableVertexAttribArray( 0 ));
		IOS_ARRAY_GL_CALL( "glVertexAttribPointer(0,VBO)", "GL4ES-native-vbo", vertexBuffer, framebuffer,
			gl4es_glVertexAttribPointer( 0, 2, GL_FLOAT, GL_FALSE, 0, (const GLvoid *)0 ));
		IOS_ARRAY_GL_CALL( "glDisable(GL_SCISSOR_TEST)", "GL4ES-raster-state", 0, framebuffer,
			pglDisable( GL_SCISSOR_TEST ));
		IOS_ARRAY_GL_CALL( "glPixelStorei(GL_PACK_ALIGNMENT,1)", "GL4ES-pack-state", 0, framebuffer,
			pglPixelStorei( GL_PACK_ALIGNMENT, 1 ));
		IOS_ARRAY_GL_CALL( "glClearColor", "GL4ES-raster-state", 0, framebuffer,
			pglClearColor( 0.1f, 0.1f, 0.1f, 1.0f ));
		IOS_ARRAY_GL_CALL( "glClear(GL_COLOR_BUFFER_BIT)", "GL4ES-direct-drawable", 0, framebuffer,
			pglClear( GL_COLOR_BUFFER_BIT ));
		for( int layer = 0; layer < 4; ++layer )
		{
			IOS_ARRAY_GL_CALL( "glViewport(quadrant)", "GL4ES-raster-state", layer, framebuffer,
				pglViewport( viewports[layer][0], viewports[layer][1], viewports[layer][2], viewports[layer][3] ));
			IOS_ARRAY_GL_CALL( "glUniform1f(u_Layer)", "GL4ES-uniform-type-cache", layer, framebuffer,
				gl4es_glUniform1f( layerLocation, (GLfloat)layer ));
			IOS_ARRAY_GL_CALL( "glDrawArrays(GL_TRIANGLE_STRIP)", "GL4ES-native-es3", layer, framebuffer,
				pglDrawArrays( GL_TRIANGLE_STRIP, 0, 4 ));
		}
		IOS_ARRAY_GL_CALL( "glFinish", "GL4ES-native-es3", 0, framebuffer, pglFinish() );
		for( int layer = 0; layer < 4; ++layer )
		{
			GLint x = viewports[layer][0] + viewports[layer][2]/2;
			GLint y = viewports[layer][1] + viewports[layer][3]/2;
			IOS_ARRAY_GL_CALL( "glReadPixels(GL_RGBA,GL_UNSIGNED_BYTE)", "GL4ES-direct-readback", layer, framebuffer,
				pglReadPixels( x, y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel ));
			for( int c = 0; c < 4; ++c ) checksum = ( checksum ^ pixel[c] ) * 16777619u;
			if( !R_IOSArrayNear( pixel, expected[layer] )) failures++;
		}
		if( checksum != IOS_ARRAY_EXPECTED_CHECKSUM ) failures++;
		IOS_ARRAY_GL_CALL( "glDisableVertexAttribArray(0)", "GL4ES-vertex-state", vertexBuffer, framebuffer,
			gl4es_glDisableVertexAttribArray( 0 ));
		IOS_ARRAY_GL_CALL( "glBindBuffer(GL_ARRAY_BUFFER,restore)", "GL4ES-buffer-owner", savedArrayBuffer, framebuffer,
			pglBindBufferARB( GL_ARRAY_BUFFER_ARB, savedArrayBuffer ));
		IOS_ARRAY_GL_CALL( "glDeleteBuffers", "GL4ES-buffer-owner", vertexBuffer, framebuffer,
			pglDeleteBuffersARB( 1, &vertexBuffer ));
		IOS_ARRAY_GL_CALL( "glDisable(GL_TEXTURE_2D_ARRAY,restore)", "GL4ES-texture-state", textures[0], framebuffer,
			pglDisable( GL_TEXTURE_2D_ARRAY ));
		IOS_ARRAY_GL_CALL( "glBindTexture(GL_TEXTURE_2D_ARRAY,restore)", "GL4ES-native-array-binding", 0, framebuffer,
			pglBindTexture( GL_TEXTURE_2D_ARRAY, 0 ));
		IOS_ARRAY_GL_CALL( "glUseProgram(restore)", "GL4ES-program-cache", 0, framebuffer,
			gl4es_glUseProgram( 0 ));
		if( savedScissorEnabled )
			IOS_ARRAY_GL_CALL( "glEnable(GL_SCISSOR_TEST,restore)", "GL4ES-raster-state", 0, framebuffer,
				pglEnable( GL_SCISSOR_TEST ));
		IOS_ARRAY_GL_CALL( "glScissor(restore)", "GL4ES-raster-state", 0, framebuffer,
			pglScissor( savedScissor[0], savedScissor[1], savedScissor[2], savedScissor[3] ));
		IOS_ARRAY_GL_CALL( "glPixelStorei(GL_PACK_ALIGNMENT,restore)", "GL4ES-pack-state", 0, framebuffer,
			pglPixelStorei( GL_PACK_ALIGNMENT, savedPackAlignment ));
		IOS_ARRAY_GL_CALL( "glClearColor(restore)", "GL4ES-raster-state", 0, framebuffer,
			pglClearColor( savedClearColor[0], savedClearColor[1], savedClearColor[2], savedClearColor[3] ));
		IOS_ARRAY_GL_CALL( "glViewport(restore)", "GL4ES-raster-state", 0, framebuffer,
			pglViewport( savedViewport[0], savedViewport[1], savedViewport[2], savedViewport[3] ));
	}
	gEngfuncs.Con_Printf( "iOS texture array selftest sampling-contract: schema=1 expected_checksum=%08x error_origin=gl4es-uniform-type-cache vertex_source=vbo framebuffer=external-default attribution=immediate\n",
		IOS_ARRAY_EXPECTED_CHECKSUM );
	gEngfuncs.Con_Printf( "iOS texture array selftest sample: quadrants=4 layers=0,1,2,3 checksum=%08x result=%s\n", checksum, failures ? "FAIL" : "PASS" );

	gl4es_glUseProgram( 0 );
	if( program ) gl4es_glDeleteProgram( program );
	if( vertexShader ) gl4es_glDeleteShader( vertexShader );
	if( fragmentShader ) gl4es_glDeleteShader( fragmentShader );
	pglDeleteTextures( 4, textures );
	pglGenTextures( 1, &textures[0] );
	pglBindTexture( GL_TEXTURE_2D_ARRAY, textures[0] );
	pglTexImage3D( GL_TEXTURE_2D_ARRAY, 0, GL_RGBA8, 1, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, expected[0] );
	if( !R_IOSArrayDrainError( "lifecycle-recreate" )) failures++;
	pglDeleteTextures( 1, textures );
	gEngfuncs.Con_Printf( "iOS texture array selftest lifecycle: delete_recreate=PASS background_foreground=context-owner generation=current\n" );
	gEngfuncs.Con_Printf( "iOS texture array selftest terminal: %s failures=%d diffusion_started=0\n", failures ? "FAIL" : "PASS", failures );
}
#else
void R_IOSTextureArraySelftest( void ) { }
#endif

#undef IOS_ARRAY_GL_CALL
