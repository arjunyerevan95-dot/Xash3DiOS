/*
vid_sdl.c - SDL vid component
Copyright (C) 2018 a1batross

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
*/

// GL API function pointers, if any, reside in this translation unit
#define APIENTRY_LINKAGE
#include "gl_local.h"
#include "gl_export.h"

#if XASH_GL4ES
#include "gl4es/include/gl4esinit.h"
#endif



static void R_ClearScreen( void )
{
	pglClearColor( 0.0f, 0.0f, 0.0f, 0.0f );
	pglClear( GL_COLOR_BUFFER_BIT );
}

static const byte *R_GetTextureOriginalBuffer( unsigned int idx )
{
	gl_texture_t *glt = R_GetTexture( idx );

	if( !glt || !glt->original || !glt->original->buffer )
		return NULL;

	return glt->original->buffer;
}

/*
=============
CL_FillRGBA

=============
*/
static void CL_FillRGBA( int rendermode, float _x, float _y, float _w, float _h, byte r, byte g, byte b, byte a )
{
	pglDisable( GL_TEXTURE_2D );
	pglEnable( GL_BLEND );
	pglTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE );
	if( rendermode == kRenderTransAdd )
		pglBlendFunc( GL_SRC_ALPHA, GL_ONE );
	else
		pglBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );
	pglColor4ub( r, g, b, a );

	pglBegin( GL_QUADS );
		pglVertex2f( _x, _y );
		pglVertex2f( _x + _w, _y );
		pglVertex2f( _x + _w, _y + _h );
		pglVertex2f( _x, _y + _h );
	pglEnd ();

	pglEnable( GL_TEXTURE_2D );
	pglDisable( GL_BLEND );
}

static qboolean Mod_LooksLikeWaterTexture( const char *name )
{
	if(( name[0] == '*' && Q_stricmp( name, REF_DEFAULT_TEXTURE )) || name[0] == '!' )
		return true;

	if( !FBitSet( gp_host->features, ENGINE_QUAKE_COMPATIBLE ))
	{
		if( !Q_strncmp( name, "water", 5 ) || !Q_strnicmp( name, "laser", 5 ))
			return true;
	}

	return false;
}

static void Mod_BrushUnloadTextures( model_t *mod )
{
	for( int i = 0; i < mod->numtextures; i++ )
	{
		texture_t *tx = mod->textures[i];
		if( !tx )
			continue; // free slot

		if( tx->gl_texturenum != tr.defaultTexture )
			GL_FreeTexture( tx->gl_texturenum ); // main texture

		if( !Mod_LooksLikeWaterTexture( tx->name ))
		{
			GL_FreeTexture( tx->fb_texturenum ); // luma texture
			GL_FreeTexture( tx->dt_texturenum ); // detail texture
		}
	}
}

static void Mod_UnloadTextures( model_t *mod )
{
	Assert( mod != NULL );

	switch( mod->type )
	{
	case mod_studio:
		Mod_StudioUnloadTextures( mod->cache.data );
		break;
	case mod_alias:
		Mod_AliasUnloadTextures( mod->cache.data );
		break;
	case mod_brush:
		Mod_BrushUnloadTextures( mod );
		break;
	case mod_sprite:
		break;
	default:
		Assert( 0 );
		break;
	}
}

static qboolean Mod_ProcessRenderData( model_t *mod, qboolean create, const byte *buf, size_t buffersize )
{
	qboolean loaded = false;

	if( !create )
	{
		if( gEngfuncs.drawFuncs->Mod_ProcessUserData )
			gEngfuncs.drawFuncs->Mod_ProcessUserData( mod, false, buf );
		Mod_UnloadTextures( mod );
		return true;
	}

	switch( mod->type )
	{
	case mod_studio:
	case mod_brush:
		loaded = true;
		break;
	case mod_sprite:
		loaded = true;
		break;
	case mod_alias:
		Mod_LoadAliasModel( mod, buf, &loaded );
		break;
	default:
		gEngfuncs.Host_Error( "%s: unsupported type %d\n", __func__, mod->type );
		return false;
	}

	if( gEngfuncs.drawFuncs->Mod_ProcessUserData )
		gEngfuncs.drawFuncs->Mod_ProcessUserData( mod, true, buf );

	return loaded;
}

static intptr_t GL_RefGetParm( int parm, int arg )
{
	switch( parm )
	{
	case PARM_TEX_WIDTH:
		return R_GetTexture( arg )->width;
	case PARM_TEX_HEIGHT:
		return R_GetTexture( arg )->height;
	case PARM_TEX_SRC_WIDTH:
		return R_GetTexture( arg )->srcWidth;
	case PARM_TEX_SRC_HEIGHT:
		return R_GetTexture( arg )->srcHeight;
	case PARM_TEX_GLFORMAT:
		return R_GetTexture( arg )->format;
	case PARM_TEX_ENCODE:
		return R_GetTexture( arg )->encode;
	case PARM_TEX_MIPCOUNT:
		return R_GetTexture( arg )->numMips;
	case PARM_TEX_DEPTH:
		return R_GetTexture( arg )->depth;
	case PARM_TEX_SKYBOX:
		Assert( arg >= 0 && arg < 6 );
		return tr.skyboxTextures[arg];
	case PARM_TEX_SKYTEXNUM:
		return tr.skytexturenum;
	case PARM_TEX_LIGHTMAP:
		arg = bound( 0, arg, MAX_LIGHTMAPS - 1 );
		return tr.lightmapTextures[arg];
	case PARM_TEX_TARGET:
		return R_GetTexture( arg )->target;
	case PARM_TEX_TEXNUM:
		return R_GetTexture( arg )->texnum;
	case PARM_TEX_FLAGS:
		return R_GetTexture( arg )->flags;
	case PARM_TEX_MEMORY:
		return GL_TexMemory();
	case PARM_ACTIVE_TMU:
		return glState.activeTMU;
	case PARM_LIGHTSTYLEVALUE:
		arg = bound( 0, arg, MAX_LIGHTSTYLES - 1 );
		return g_lightstylevalue[arg];
	case PARM_MAX_IMAGE_UNITS:
		return GL_MaxTextureUnits();
	case PARM_REBUILD_GAMMA:
		return glConfig.softwareGammaUpdate;
	case PARM_GL_CONTEXT_TYPE:
		return glConfig.context;
	case PARM_GLES_WRAPPER:
		return glConfig.wrapper;
	case PARM_STENCIL_ACTIVE:
		return glState.stencilEnabled;
#if XASH_APPLE
	case PARM_DEBUG_FRAMEBUFFER_TRACE:
		R_IOSFramebufferTraceCheckpoint( arg );
		return 0;
#endif
	case PARM_TEX_FILTERING:
		if( arg < 0 )
			return gl_texture_nearest.value == 0.0f;

		return GL_TextureFilteringEnabled( R_GetTexture( arg ));
	case PARM_GET_STUDIO_HDR:
		return (intptr_t)R_StudioGetHeader();
	default:
		return ENGINE_GET_PARM_( parm, arg );
	}
	return 0;
}

static void R_GetDetailScaleForTexture( int texture, float *xScale, float *yScale )
{
	gl_texture_t *glt = R_GetTexture( texture );

	if( xScale ) *xScale = glt->xscale;
	if( yScale ) *yScale = glt->yscale;
}

static void R_SetDetailScaleForTexture( int texture, float xScale, float yScale )
{
	gl_texture_t *glt = R_GetTexture( texture );

	glt->xscale = xScale;
	glt->yscale = yScale;
}

static void R_GetExtraParmsForTexture( int texture, byte *red, byte *green, byte *blue, byte *density )
{
	gl_texture_t *glt = R_GetTexture( texture );

	if( red ) *red = glt->fogParams[0];
	if( green ) *green = glt->fogParams[1];
	if( blue ) *blue = glt->fogParams[2];
	if( density ) *density = glt->fogParams[3];
}


static void R_SetCurrentEntity( cl_entity_t *ent )
{
	RI.currententity = ent;

	// set model also
	if( RI.currententity != NULL )
	{
		RI.currentmodel = RI.currententity->model;
	}
}

static void R_SetCurrentModel( model_t *mod )
{
	RI.currentmodel = mod;
}

static float R_GetFrameTime( void )
{
	return tr.frametime;
}

static const char *GL_TextureName( unsigned int texnum )
{
	return R_GetTexture( texnum )->name;
}

static const byte *GL_TextureData( unsigned int texnum )
{
	rgbdata_t *pic = R_GetTexture( texnum )->original;

	if( pic != NULL )
		return pic->buffer;
	return NULL;
}

static void R_ProcessEntData( qboolean allocate, cl_entity_t *entities, unsigned int max_entities )
{
	if( !allocate )
	{
		tr.draw_list->num_solid_entities = 0;
		tr.draw_list->num_trans_entities = 0;
		tr.draw_list->num_beam_entities = 0;

		tr.max_entities = 0;
		tr.entities = NULL;
	}
	else
	{
		tr.max_entities = max_entities;
		tr.entities = entities;
	}

	if( gEngfuncs.drawFuncs->R_ProcessEntData )
		gEngfuncs.drawFuncs->R_ProcessEntData( allocate );
}

/*
=============
R_SetSkyCloudsTextures

Quake sky cloud texture was processed by the engine,
remember them for easier access during rendering
==============
*/
static void GAME_EXPORT R_SetSkyCloudsTextures( int solidskyTexture, int alphaskyTexture )
{
	tr.solidskyTexture = solidskyTexture;
	tr.alphaskyTexture = alphaskyTexture;
}

/*
===============
R_SetupSky
===============
*/
static void GAME_EXPORT R_SetupSky( int *skyboxTextures )
{
	R_UnloadSkybox();

	if( !skyboxTextures )
		return;

	for( int i = 0; i < SKYBOX_MAX_SIDES; i++ )
		tr.skyboxTextures[i] = skyboxTextures[i];
}

static qboolean R_SetDisplayTransform( ref_screen_rotation_t rotate, int offset_x, int offset_y, float scale_x, float scale_y )
{
	qboolean ret = true;

	tr.rotation = rotate;

	if( offset_x || offset_y )
	{
		gEngfuncs.Con_Printf("offset transform not supported\n");
		ret = false;
	}

	if( scale_x != 1.0f || scale_y != 1.0f )
	{
		gEngfuncs.Con_Printf("scale transform not supported\n");
		ret = false;
	}

	return ret;
}

static void GAME_EXPORT VGUI_SetupDrawing( qboolean rect )
{
	pglEnable( GL_BLEND );
	pglBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );

	if( rect )
	{
		pglDisable( GL_ALPHA_TEST );
	}
	else
	{
		pglEnable( GL_ALPHA_TEST );
		pglAlphaFunc( GL_GREATER, 0.0f );
		pglTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE );
	}
}

static void GAME_EXPORT R_OverrideTextureSourceSize( unsigned int texnum, uint srcWidth, uint srcHeight )
{
	gl_texture_t *tx = R_GetTexture( texnum );

	tx->srcWidth = srcWidth;
	tx->srcHeight = srcHeight;
}

static void* GAME_EXPORT R_GetProcAddress( const char *name )
{
#if XASH_GL4ES
	return gl4es_GetProcAddress( name );
#else // TODO: other wrappers
	return gEngfuncs.GL_GetProcAddress( name );
#endif
}

static const char *R_GetConfigName( void )
{
	return "opengl";
}

static void R_NewMap( void )
{
	tr.worldmodel = gp_cl->models[1];

	R_ClearDecals(); // clear all level decals

	R_StudioResetPlayerModels();

	// clear out efrags in case the level hasn't been reloaded
	for( int i = 0; i < WORLDMODEL->numleafs; i++ )
		WORLDMODEL->leafs[i+1].efrags = NULL;

	glState.isFogEnabled = false;
	tr.skytexturenum = -1;
	pglDisable( GL_FOG );

	// clearing texture chains
	for( int i = 0; i < WORLDMODEL->numtextures; i++ )
	{
		if( !WORLDMODEL->textures[i] )
			continue;

		texture_t *tx = WORLDMODEL->textures[i];

		if( !Q_strncmp( tx->name, "sky", 3 ) && tx->width == ( tx->height * 2 ))
			tr.skytexturenum = i;

		tx->texturechain = NULL;
	}

	GL_BuildLightmaps ();

	R_ClearVBO();
	if( R_HasEnabledVBO( ))
		R_GenerateVBO();
	R_ResetRipples();

	if( gEngfuncs.drawFuncs->R_NewMap != NULL )
		gEngfuncs.drawFuncs->R_NewMap();
}

static void R_FillRenderAPI( render_api_t *api )
{
	api->GetExtraParmsForTexture  = R_GetExtraParmsForTexture;
	api->GetFrameTime             = R_GetFrameTime;
	api->R_SetCurrentEntity       = R_SetCurrentEntity;
	api->R_SetCurrentModel        = R_SetCurrentModel;
	api->GL_CreateTexture         = GL_CreateTexture;
	api->GL_LoadTextureArray      = GL_LoadTextureArray;
	api->GL_CreateTextureArray    = GL_CreateTextureArray;
	api->DrawSingleDecal          = DrawSingleDecal;
	api->R_DecalSetupVerts        = R_DecalSetupVerts;
	api->R_EntityRemoveDecals     = R_EntityRemoveDecals;
	api->GL_SelectTexture         = GL_SelectTexture;
	api->GL_LoadTextureMatrix     = GL_LoadTexMatrixExt;
	api->GL_TexMatrixIdentity     = GL_LoadIdentityTexMatrix;
	api->GL_CleanUpTextureUnits   = GL_CleanUpTextureUnits;
	api->GL_TexGen                = GL_TexGen;
	api->GL_TextureTarget         = GL_TextureTarget;
	api->GL_TexCoordArrayMode     = GL_SetTexCoordArrayMode;
	api->GL_UpdateTexSize         = GL_UpdateTexSize;
	api->GL_DrawParticles         = CL_DrawParticlesExternal;
	api->LightVec                 = R_LightVec;
	api->StudioGetTexture         = R_StudioGetTexture;
	api->GL_GetProcAddress        = R_GetProcAddress;
}

static void R_FillTriAPI( triangleapi_t *api )
{
	api->TexCoord2f    = TriTexCoord2f;
	api->Fog           = TriFog;
	api->ScreenToWorld = R_ScreenToWorld;
	api->GetMatrix     = TriGetMatrix;
	api->FogParams     = TriFogParams;
}

#if XASH_IOS && XASH_GL4ES
#define IOS_GL_FRAMEBUFFER_COMPLETE 0x8CD5u

typedef struct ios_direct_drawable_state_s
{
	ref_ios_direct_drawable_t drawable;
	uint64_t invocation;
	uint64_t context;
	uint32_t contextGeneration;
	uint32_t resizeGeneration;
	uint32_t registeredFramebuffer;
	uint32_t menuSamples;
	uint32_t activeSamples;
	uint32_t presentSamples;
	uint32_t records;
	uint32_t menuChecksum;
	qboolean menuChecksumValid;
	qboolean policyPrinted;
	qboolean proofPrinted;
} ios_direct_drawable_state_t;

static ios_direct_drawable_state_t ios_direct_drawable;
static void ( *ios_direct_drawable_original_swap )( void );

static qboolean R_IOSDirectDrawableCanPrint( void )
{
	if( ios_direct_drawable.records >= REF_IOS_DIRECT_DRAWABLE_MAX_RECORDS )
		return false;
	ios_direct_drawable.records++;
	return true;
}

static void R_IOSDirectDrawableFillEngineState( ref_ios_direct_drawable_t *state )
{
	const model_t *world = gp_cl ? gp_cl->models[1] : NULL;
	int clientState = (int)ENGINE_GET_PARM( PARM_CONNSTATE );

	state->invocation = ios_direct_drawable.invocation;
	state->clientState = clientState;
	state->enginePhase = clientState == ca_active ? 2 : 1;
	state->mapName[0] = '\0';
	if( world && world->name[0] )
		Q_strncpy( state->mapName, world->name, sizeof( state->mapName ));
}

static qboolean R_IOSDirectDrawableQuery( ref_ios_direct_drawable_t *state )
{
	if( !gEngfuncs.GL_GetDrawableInfo ||
		!gEngfuncs.GL_GetDrawableInfo( state, sizeof( *state ) ) )
		return false;
	R_IOSDirectDrawableFillEngineState( state );
	return state->version == REF_IOS_DIRECT_DRAWABLE_VERSION &&
		state->size >= sizeof( *state );
}

static qboolean R_IOSDirectDrawableRegister( ref_ios_direct_drawable_t *state,
	const char *reason, qboolean printLifecycle )
{
	gl4es_external_default_state_t proof;
	qboolean valid, printRegister;

	printRegister = printLifecycle || !Q_strcmp( reason, "context-created" );

	valid = state && state->context && state->currentContext &&
		state->contextMatches && state->viewFramebuffer && state->viewRenderbuffer &&
		state->drawableWidth && state->drawableHeight &&
		state->requestedSamples == 0 && state->effectiveSamples == 0;
	if( !valid || !set_external_default_framebuffer( state->viewFramebuffer ) )
	{
		if( R_IOSDirectDrawableCanPrint() )
			gEngfuncs.Con_Printf( "iOS direct drawable register: result=failed reason=%s context=0x%llx current=0x%llx match=%u view=%u/%u size=%ux%u samples=%u/%u\n",
				reason, (unsigned long long)( state ? state->context : 0 ),
				(unsigned long long)( state ? state->currentContext : 0 ),
				state ? state->contextMatches : 0, state ? state->viewFramebuffer : 0,
				state ? state->viewRenderbuffer : 0, state ? state->drawableWidth : 0,
				state ? state->drawableHeight : 0, state ? state->requestedSamples : 0,
				state ? state->effectiveSamples : 0 );
		return false;
	}

	valid = gl4es_external_default_framebuffer_state( state->drawableWidth,
		state->drawableHeight, 0, &proof ) != 0;
	if( printRegister && R_IOSDirectDrawableCanPrint() )
		gEngfuncs.Con_Printf( "iOS direct drawable register: result=%s reason=%s context=0x%llx context_gen=%u resize_gen=%u view=%u/%u size=%ux%u samples=%u/%u external_gen=%u logical=%u/%u/%u native=%u/%u status=0x%04x\n",
			valid ? "ok" : "failed", reason, (unsigned long long)state->context,
			state->contextGeneration, state->resizeGeneration,
			state->viewFramebuffer, state->viewRenderbuffer,
			state->drawableWidth, state->drawableHeight,
			state->requestedSamples, state->effectiveSamples, proof.generation,
			proof.logical_current, proof.logical_read, proof.logical_draw,
			proof.native_draw, proof.native_read, proof.framebuffer_status );
	if( printLifecycle && R_IOSDirectDrawableCanPrint() )
		gEngfuncs.Con_Printf( "iOS direct drawable lifecycle: reason=%s context=0x%llx context_gen=%u resize_gen=%u view=%u/%u reasserted=%u complete=%u\n",
			reason, (unsigned long long)state->context, state->contextGeneration,
			state->resizeGeneration, state->viewFramebuffer, state->viewRenderbuffer,
			valid ? 1 : 0, valid && proof.framebuffer_status == IOS_GL_FRAMEBUFFER_COMPLETE );
	if( !valid )
		return false;

	ios_direct_drawable.drawable = *state;
	ios_direct_drawable.context = state->context;
	ios_direct_drawable.contextGeneration = state->contextGeneration;
	ios_direct_drawable.resizeGeneration = state->resizeGeneration;
	ios_direct_drawable.registeredFramebuffer = state->viewFramebuffer;
	return true;
}

static qboolean R_IOSDirectDrawableSampleScheduled( const ref_ios_direct_drawable_t *state )
{
	if( state->enginePhase == 2 && Q_strstr( state->mapName, "ch1map0" ) )
	{
		if( ios_direct_drawable.activeSamples < REF_IOS_DIRECT_DRAWABLE_ACTIVE_SAMPLES )
		{
			ios_direct_drawable.activeSamples++;
			return true;
		}
		return false;
	}
	if( state->enginePhase != 2 &&
		ios_direct_drawable.menuSamples < REF_IOS_DIRECT_DRAWABLE_MENU_SAMPLES )
	{
		ios_direct_drawable.menuSamples++;
		return true;
	}
	return false;
}

static void R_IOSDirectDrawablePrintProof( const ref_ios_direct_drawable_t *state,
	const gl4es_external_default_state_t *proof )
{
	qboolean active = state->enginePhase == 2 && Q_strstr( state->mapName, "ch1map0" );
	qboolean changed = false;

	if( !active && proof->checksum_valid && !ios_direct_drawable.menuChecksumValid )
	{
		ios_direct_drawable.menuChecksum = proof->checksum;
		ios_direct_drawable.menuChecksumValid = true;
	}
	if( active && proof->checksum_valid && ios_direct_drawable.menuChecksumValid )
		changed = proof->checksum != ios_direct_drawable.menuChecksum;

	if( R_IOSDirectDrawableCanPrint() )
		gEngfuncs.Con_Printf( "iOS direct drawable logical-zero: inv=%llu phase=%u map=%s registered=%u external_gen=%u logical=%u/%u/%u native=%u/%u status=0x%04x checksum=%u/0x%08x\n",
			(unsigned long long)state->invocation, state->enginePhase,
			state->mapName[0] ? state->mapName : "-", proof->registered_framebuffer,
			proof->generation, proof->logical_current, proof->logical_read,
			proof->logical_draw, proof->native_draw, proof->native_read,
			proof->framebuffer_status, proof->checksum_valid, proof->checksum );

	if( active && !ios_direct_drawable.proofPrinted && R_IOSDirectDrawableCanPrint() )
	{
		gEngfuncs.Con_Printf( "iOS direct drawable proof: inv=%llu map=%s view=%u logical_native_agree=%u complete=%u checksum_valid=%u menu_checksum_valid=%u checksum_changed=%u checksum=0x%08x menu_checksum=0x%08x\n",
			(unsigned long long)state->invocation,
			state->mapName[0] ? state->mapName : "-", state->viewFramebuffer,
			proof->logical_current == 0 && proof->logical_read == 0 &&
			proof->logical_draw == 0 && proof->native_draw == state->viewFramebuffer &&
			proof->native_read == state->viewFramebuffer,
			proof->framebuffer_status == IOS_GL_FRAMEBUFFER_COMPLETE,
			proof->checksum_valid, ios_direct_drawable.menuChecksumValid,
			changed, proof->checksum, ios_direct_drawable.menuChecksum );
		if( changed )
			ios_direct_drawable.proofPrinted = true;
	}
}

static void R_IOSDirectDrawableSwap( void )
{
	ref_ios_direct_drawable_t state;
	gl4es_external_default_state_t proof;
	qboolean lifecycleChanged, sample;

	if( !ios_direct_drawable_original_swap )
		return;
	ios_direct_drawable.invocation++;
	if( !R_IOSDirectDrawableQuery( &state ) )
	{
		if( R_IOSDirectDrawableCanPrint() )
			gEngfuncs.Con_Printf( "iOS direct drawable lifecycle: reason=query-failed inv=%llu\n",
				(unsigned long long)ios_direct_drawable.invocation );
		ios_direct_drawable_original_swap();
		return;
	}

	lifecycleChanged = state.context != ios_direct_drawable.context ||
		state.contextGeneration != ios_direct_drawable.contextGeneration ||
		state.resizeGeneration != ios_direct_drawable.resizeGeneration ||
		state.viewFramebuffer != ios_direct_drawable.registeredFramebuffer;
	if( !R_IOSDirectDrawableRegister( &state,
		lifecycleChanged ? "swap-lifecycle-change" : "swap-reassert", lifecycleChanged ) )
	{
		ios_direct_drawable_original_swap();
		return;
	}

	if( !ios_direct_drawable.policyPrinted && R_IOSDirectDrawableCanPrint() )
	{
		gEngfuncs.Con_Printf( "iOS direct drawable policy: version=%u requested_samples=0 effective_samples=0 msaa_objects=0 resolve=disabled transfer=none logical_zero=live-sdl-view samples=menu:%u,active:%u max_records=%u\n",
			REF_IOS_DIRECT_DRAWABLE_VERSION, REF_IOS_DIRECT_DRAWABLE_MENU_SAMPLES,
			REF_IOS_DIRECT_DRAWABLE_ACTIVE_SAMPLES, REF_IOS_DIRECT_DRAWABLE_MAX_RECORDS );
		ios_direct_drawable.policyPrinted = true;
	}

	sample = R_IOSDirectDrawableSampleScheduled( &state );
	if( sample && gl4es_external_default_framebuffer_state( state.drawableWidth,
		state.drawableHeight, 1, &proof ) )
		R_IOSDirectDrawablePrintProof( &state, &proof );
	ios_direct_drawable.drawable = state;
	ios_direct_drawable_original_swap();
}

void R_IOSDirectDrawableContextCreated( void )
{
	ref_ios_direct_drawable_t state;

	memset( &ios_direct_drawable, 0, sizeof( ios_direct_drawable ) );
	if( !ios_direct_drawable_original_swap )
		ios_direct_drawable_original_swap = gEngfuncs.GL_SwapBuffers;
	gEngfuncs.GL_SwapBuffers = R_IOSDirectDrawableSwap;
	if( R_IOSDirectDrawableQuery( &state ) )
		R_IOSDirectDrawableRegister( &state, "context-created", true );
}

void R_IOSDirectDrawableContextDestroying( void )
{
	set_external_default_framebuffer( 0 );
	if( R_IOSDirectDrawableCanPrint() )
		gEngfuncs.Con_Printf( "iOS direct drawable lifecycle: reason=context-destroying context=0x%llx cleared=1\n",
			(unsigned long long)ios_direct_drawable.context );
	if( ios_direct_drawable_original_swap )
		gEngfuncs.GL_SwapBuffers = ios_direct_drawable_original_swap;
}

static int R_IOSDrawableBridge( int action, void *opaqueState, size_t stateSize )
{
	ref_ios_direct_drawable_t *state = (ref_ios_direct_drawable_t *)opaqueState;
	gl4es_external_default_state_t proof;
	qboolean lifecycleAction;

	if( !state || stateSize < sizeof( *state ) ||
		state->version != REF_IOS_DIRECT_DRAWABLE_VERSION || state->size < sizeof( *state ) )
		return 0;
	R_IOSDirectDrawableFillEngineState( state );
	lifecycleAction = action == REF_IOS_DIRECT_DRAWABLE_CONTEXT_RESTORED ||
		action == REF_IOS_DIRECT_DRAWABLE_RESIZED;

	if( action == REF_IOS_DIRECT_DRAWABLE_DESTROYING )
	{
		set_external_default_framebuffer( 0 );
		if( R_IOSDirectDrawableCanPrint() )
			gEngfuncs.Con_Printf( "iOS direct drawable lifecycle: reason=sdl-destroying context=0x%llx cleared=1\n",
				(unsigned long long)state->context );
		return 1;
	}
	if( lifecycleAction )
		return R_IOSDirectDrawableRegister( state,
			action == REF_IOS_DIRECT_DRAWABLE_CONTEXT_RESTORED ? "context-restored" : "resized",
			true );
	if( action == REF_IOS_DIRECT_DRAWABLE_SWAP_ENTRY )
		return R_IOSDirectDrawableRegister( state, "sdl-swap-entry", false );
	if( action == REF_IOS_DIRECT_DRAWABLE_PRESENT_BEFORE )
	{
		if( !R_IOSDirectDrawableRegister( state, "present-reassert", false ) )
			return 0;
		return gl4es_external_default_framebuffer_state( state->drawableWidth,
			state->drawableHeight, 0, &proof );
	}
	if( action == REF_IOS_DIRECT_DRAWABLE_POST_PRESENT )
	{
		qboolean printPresent = state->invocation <= 1;
		if( state->enginePhase == 2 &&
			ios_direct_drawable.presentSamples < ios_direct_drawable.activeSamples )
		{
			ios_direct_drawable.presentSamples++;
			printPresent = true;
		}
		if( printPresent &&
			R_IOSDirectDrawableCanPrint() )
			gEngfuncs.Con_Printf( "iOS direct drawable present: inv=%llu phase=%u map=%s view=%u/%u attempted=%u result=%u resolve=0 transfer=0 one_present=1\n",
				(unsigned long long)state->invocation, state->enginePhase,
				state->mapName[0] ? state->mapName : "-", state->viewFramebuffer,
				state->viewRenderbuffer, state->presentAttempted, state->presentResult );
		return state->presentAttempted && state->presentResult;
	}
	return 1;
}
#endif

const ref_interface_t gReffuncs =
{
	R_Init,
	R_Shutdown,
	R_GetConfigName,
	R_SetDisplayTransform,

	GL_SetupAttributes,
	GL_InitExtensions,
	GL_ClearExtensions,

	R_GammaChanged,
	R_BeginFrame,
	R_RenderScene,
	R_EndFrame,
	R_PushScene,
	R_PopScene,
	GL_BackendStartFrame,
	GL_BackendEndFrame,

	R_ClearScreen,
	R_AllowFog,
	GL_SetRenderMode,

	R_AddEntity,
	R_ProcessEntData,

	R_ShowTextures,

	R_GetTextureOriginalBuffer,
	GL_LoadTextureFromBuffer,
	GL_ProcessTexture,
	R_SetupSky,

	R_Set2DMode,
	R_DrawStretchPic,
	CL_FillRGBA,
	R_WorldToScreen,

	VID_ScreenShot,
	VID_CubemapShot,

	R_LightPoint,

	R_DecalShoot,
	R_DecalRemoveAll,
	R_CreateDecalList,
	R_ClearAllDecals,

	R_StudioEstimateFrame,
	R_StudioLerpMovement,
	R_StudioFillAPI,
	R_StudioSetDrawInterface,

	R_SetSkyCloudsTextures,
	GL_SubdivideSurface,
	CL_RunLightStyles,


	Mod_ProcessRenderData,
	Mod_StudioLoadTextures,

	CL_DrawParticles,
	CL_DrawTracers,
	CL_DrawBeams,

	GL_RefGetParm,

	R_GetDetailScaleForTexture,
	R_SetDetailScaleForTexture,

	GL_CreateTexture,
	GL_FindTexture,
	GL_TextureName,
	GL_TextureData,
	GL_LoadTexture,
	GL_FreeTexture,
	R_OverrideTextureSourceSize,

	GL_UpdateTexture,

	GL_Bind,

	R_RenderFrame,
	Mod_SetOrthoBounds,
	R_SpeedsMessage,
	Mod_GetCurrentVis,
	R_NewMap,
	R_ClearScene,

	TriRenderMode,
	TriBegin,
	TriEnd,
	_TriColor4f,
	_TriColor4ub,
	TriVertex3fv,
	TriVertex3f,
	TriCullFace,

	R_FillRenderAPI,
	R_FillTriAPI,

	VGUI_SetupDrawing,

#if XASH_IOS && XASH_GL4ES
	R_IOSDrawableBridge,
#else
	NULL,
#endif
};
