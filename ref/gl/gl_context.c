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
typedef struct ios_main_fbo_audit_state_s
{
	uint64_t context;
	uint64_t invocation;
	uint64_t firstActiveInvocation;
	uint64_t lastSDLSignature;
	uint64_t lastOwnerSignature;
	uint64_t lastLifecycleSignature;
	uint32_t menuSamples;
	uint32_t records;
	qboolean activeInvocation;
	qboolean sampleInvocation;
	qboolean terminalPending;
	qboolean terminalPrinted;
	qboolean policyPrinted;
	ref_ios_drawable_bridge_t cachedSDL;
	ref_ios_drawable_bridge_t frame;
	gl4es_drawable_audit_t rendererAudit;
	gl4es_drawable_audit_t presentAudit;
} ios_main_fbo_audit_state_t;

static ios_main_fbo_audit_state_t ios_main_fbo_audit;
static void ( *ios_main_fbo_original_swap )( void );

static qboolean R_IOSMainFBOCanPrint( void )
{
	/* Reserve the final record for the one terminal marker. */
	if( ios_main_fbo_audit.records >= REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS - 1 )
		return false;
	ios_main_fbo_audit.records++;
	return true;
}

static uint64_t R_IOSMainFBOOwnerSignature( const gl4es_drawable_audit_t *audit )
{
	return audit->state_identity ^ ((uint64_t)audit->state_generation << 48 ) ^
		((uint64_t)audit->native_draw_framebuffer << 32 ) ^
		((uint64_t)audit->source.color.object_name << 16 ) ^
		audit->target.color.object_name;
}

static uint64_t R_IOSMainFBOLifecycleSignature( const gl4es_drawable_audit_t *audit )
{
	return ((uint64_t)audit->create_attempts << 48 ) ^
		((uint64_t)audit->create_successes << 32 ) ^
		((uint64_t)audit->resize_count << 16 ) ^ audit->delete_count ^
		((uint64_t)audit->main_framebuffer << 8 );
}

static uint64_t R_IOSMainFBOSDLSignature( const ref_ios_drawable_bridge_t *state )
{
	return state->context ^ ((uint64_t)state->contextGeneration << 56 ) ^
		((uint64_t)state->resizeGeneration << 48 ) ^
		((uint64_t)state->viewFramebuffer << 32 ) ^
		((uint64_t)state->msaaFramebuffer << 16 ) ^ state->viewRenderbuffer;
}

static void R_IOSMainFBOReset( uint64_t context )
{
	memset( &ios_main_fbo_audit, 0, sizeof( ios_main_fbo_audit ));
	ios_main_fbo_audit.context = context;
}

static void R_IOSMainFBOFillEngineState( ref_ios_drawable_bridge_t *state )
{
	const model_t *world = gp_cl ? gp_cl->models[1] : NULL;
	double now = gEngfuncs.pfnTime ? gEngfuncs.pfnTime() : 0.0;
	int clientState = (int)ENGINE_GET_PARM( PARM_CONNSTATE );

	state->invocation = ios_main_fbo_audit.invocation;
	state->timestampUsec = (uint64_t)( now * 1000000.0 );
	state->hostTimeUsec = gp_host ? (uint64_t)( gp_host->realtime * 1000000.0 ) : 0;
	state->clientTimeUsec = gp_cl ? (uint64_t)( gp_cl->time * 1000000.0 ) : 0;
	state->clientState = clientState;
	state->enginePhase = clientState == ca_active ? 2 : 1;
	state->mapName[0] = '\0';
	if( world && world->name[0] )
		Q_strncpy( state->mapName, world->name, sizeof( state->mapName ));
}

static qboolean R_IOSMainFBOScheduledSample( const ref_ios_drawable_bridge_t *state )
{
	static const uint32_t activeGaps[] = { 0, 2, 4, 8, 16, 32, 64 };
	uint64_t relative;
	uint i;

	if( state->enginePhase != 2 )
	{
		if( ios_main_fbo_audit.menuSamples < REF_IOS_DRAWABLE_BRIDGE_MENU_ATTEMPTS )
		{
			ios_main_fbo_audit.menuSamples++;
			return true;
		}
		return false;
	}

	if( !ios_main_fbo_audit.firstActiveInvocation )
		ios_main_fbo_audit.firstActiveInvocation = state->invocation;
	relative = state->invocation - ios_main_fbo_audit.firstActiveInvocation;
	for( i = 0; i < sizeof( activeGaps ) / sizeof( activeGaps[0] ); i++ )
	{
		if( relative == activeGaps[i] )
		{
			if( relative == 64 )
				ios_main_fbo_audit.terminalPending = true;
			return true;
		}
	}
	return false;
}

static void R_IOSMainFBOPrintPolicyAndState( const ref_ios_drawable_bridge_t *state,
	const gl4es_drawable_audit_t *audit, qboolean lifecycleChanged, qboolean ownerChanged )
{
	if( !ios_main_fbo_audit.policyPrinted && R_IOSMainFBOCanPrint() )
	{
		gEngfuncs.Con_Printf( "iOS main-FBO audit policy: version=%u same_invocation=A-R_EndFrame,B-SDL-entry,C-SDL-post-resolve,D-bridge-entry-return,E-present-entry-return menu_samples=%u active_gaps=0,2,4,8,16,32,64 max_records=%u pixels=five-4x4-regions transfer_policy=unchanged\n",
			REF_IOS_DRAWABLE_BRIDGE_VERSION, REF_IOS_DRAWABLE_BRIDGE_MENU_ATTEMPTS,
			REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS );
		ios_main_fbo_audit.policyPrinted = true;
	}
	if( lifecycleChanged && R_IOSMainFBOCanPrint() )
		gEngfuncs.Con_Printf( "iOS main-FBO lifecycle: inv=%llu gl4es_state=0x%llx generation=%u create_attempts=%u create_success=%u resize=%u delete=%u last_status=0x%04x main=%u/%u/%u/%u size=%ux%u native=%ux%u\n",
			(unsigned long long)state->invocation, audit->state_identity,
			audit->state_generation, audit->create_attempts, audit->create_successes,
			audit->resize_count, audit->delete_count, audit->last_status,
			audit->main_framebuffer, audit->main_texture, audit->main_depth,
			audit->main_stencil, audit->main_width, audit->main_height,
			audit->main_native_width, audit->main_native_height );
	if( ownerChanged && R_IOSMainFBOCanPrint() )
		gEngfuncs.Con_Printf( "iOS main-FBO state: inv=%llu phase=%u map=%s host_us=%llu client_us=%llu gl4es_state=0x%llx generation=%u usefb=%u usefbo=%u logical_fb=%u logical_rb=%u default_fb=%u default_rb=%u native_draw=%u native_read=%u native_rb=%u sdl_context=0x%llx api=%u context_gen=%u resize_gen=%u view=%u/%u msaa=%u/%u depth=%u samples=%u/%u drawable=%ux%u\n",
			(unsigned long long)state->invocation, state->enginePhase,
			state->mapName[0] ? state->mapName : "-",
			(unsigned long long)state->hostTimeUsec,
			(unsigned long long)state->clientTimeUsec, audit->state_identity,
			audit->state_generation, audit->usefb, audit->usefbo,
			audit->logical_framebuffer, audit->logical_renderbuffer,
			audit->default_framebuffer, audit->default_renderbuffer,
			audit->native_draw_framebuffer, audit->native_read_framebuffer,
			audit->native_renderbuffer, (unsigned long long)state->context,
			state->contextAPI, state->contextGeneration, state->resizeGeneration,
			state->viewFramebuffer, state->viewRenderbuffer,
			state->msaaFramebuffer, state->msaaRenderbuffer,
			state->depthRenderbuffer, state->requestedSamples,
			state->effectiveSamples, state->drawableWidth, state->drawableHeight );
}

static void R_IOSMainFBOPrintCheckpoint( const char *marker, const char *checkpoint,
	const ref_ios_drawable_bridge_t *state, const gl4es_drawable_audit_t *audit,
	const gl4es_drawable_audit_t *before )
{
	if( !R_IOSMainFBOCanPrint() )
		return;
	gEngfuncs.Con_Printf( "%s inv=%llu checkpoint=%s phase=%u map=%s timestamp_us=%llu host_us=%llu client_us=%llu iOS pixel checkpoint: source=%u/0x%04x/%u/0x%08x target=%u/0x%04x/%u/0x%08x before_source=%u/0x%08x before_target=%u/0x%08x native=%u/%u/%u restored=%u/%u/%u logical=%u/%u src_color=%x/%u/%ux%u/0x%x/%u src_depth=%x/%u/%ux%u/0x%x/%u src_stencil=%x/%u/%ux%u/0x%x/%u dst_color=%x/%u/%ux%u/0x%x/%u dst_depth=%x/%u/%ux%u/0x%x/%u dst_stencil=%x/%u/%ux%u/0x%x/%u equals=view:%u,msaa:%u,target_view:%u bridge=attempted:%u,result:%u,preconditions:0x%08x,failure:%u present=attempted:%u,result:%u restore=result:%u,fb:%u,rb:%u,logical:%u query_failure=%u/0x%04x\n",
		marker, (unsigned long long)state->invocation, checkpoint,
		state->enginePhase, state->mapName[0] ? state->mapName : "-",
		(unsigned long long)state->timestampUsec,
		(unsigned long long)state->hostTimeUsec,
		(unsigned long long)state->clientTimeUsec,
		audit->source.framebuffer, audit->source.status,
		audit->source.checksum_valid, audit->source.checksum,
		audit->target.framebuffer, audit->target.status,
		audit->target.checksum_valid, audit->target.checksum,
		before ? before->source.checksum_valid : 0,
		before ? before->source.checksum : 0,
		before ? before->target.checksum_valid : 0,
		before ? before->target.checksum : 0,
		audit->native_draw_framebuffer, audit->native_read_framebuffer,
		audit->native_renderbuffer, audit->restored_draw_framebuffer,
		audit->restored_read_framebuffer, audit->restored_renderbuffer,
		audit->logical_framebuffer, audit->restored_logical_framebuffer,
		audit->source.color.object_type, audit->source.color.object_name,
		audit->source.color.width, audit->source.color.height,
		audit->source.color.internal_format, audit->source.color.samples,
		audit->source.depth.object_type, audit->source.depth.object_name,
		audit->source.depth.width, audit->source.depth.height,
		audit->source.depth.internal_format, audit->source.depth.samples,
		audit->source.stencil.object_type, audit->source.stencil.object_name,
		audit->source.stencil.width, audit->source.stencil.height,
		audit->source.stencil.internal_format, audit->source.stencil.samples,
		audit->target.color.object_type, audit->target.color.object_name,
		audit->target.color.width, audit->target.color.height,
		audit->target.color.internal_format, audit->target.color.samples,
		audit->target.depth.object_type, audit->target.depth.object_name,
		audit->target.depth.width, audit->target.depth.height,
		audit->target.depth.internal_format, audit->target.depth.samples,
		audit->target.stencil.object_type, audit->target.stencil.object_name,
		audit->target.stencil.width, audit->target.stencil.height,
		audit->target.stencil.internal_format, audit->target.stencil.samples,
		audit->source.framebuffer == state->viewFramebuffer,
		audit->source.framebuffer == state->msaaFramebuffer,
		audit->target.framebuffer == state->viewFramebuffer,
		state->transferAttempted, state->transferResult, state->preconditionMask,
		state->failureCode, state->presentAttempted, state->presentResult,
		state->restoreResult, state->restoredFramebuffer,
		state->restoredRenderbuffer, state->restoredLogicalFramebuffer,
		audit->query_failure_operation, audit->query_failure_error );
}

static void R_IOSMainFBOAudit( const ref_ios_drawable_bridge_t *state,
	gl4es_drawable_audit_t *audit, qboolean pixels )
{
	gl4es_drawable_bridge_audit( state->contextAPI, state->viewFramebuffer,
		state->drawableWidth, state->drawableHeight, pixels ? 1 : 0, audit );
}

static void R_IOSMainFBOSwap( void )
{
	uint64_t ownerSignature, lifecycleSignature;
	qboolean ownerChanged, lifecycleChanged;
	ref_ios_drawable_bridge_t *state = &ios_main_fbo_audit.frame;

	if( ios_main_fbo_audit.terminalPrinted || !ios_main_fbo_original_swap )
	{
		if( ios_main_fbo_original_swap )
			ios_main_fbo_original_swap();
		return;
	}

	ios_main_fbo_audit.invocation++;
	ios_main_fbo_audit.activeInvocation = true;
	*state = ios_main_fbo_audit.cachedSDL;
	R_IOSMainFBOFillEngineState( state );
	state->checkpoint = REF_IOS_DRAWABLE_BRIDGE_RENDERER_HANDOFF;
	ios_main_fbo_audit.sampleInvocation = R_IOSMainFBOScheduledSample( state );
	R_IOSMainFBOAudit( state, &ios_main_fbo_audit.rendererAudit,
		ios_main_fbo_audit.sampleInvocation );
	ownerSignature = R_IOSMainFBOOwnerSignature( &ios_main_fbo_audit.rendererAudit );
	lifecycleSignature = R_IOSMainFBOLifecycleSignature( &ios_main_fbo_audit.rendererAudit );
	ownerChanged = ownerSignature != ios_main_fbo_audit.lastOwnerSignature;
	lifecycleChanged = lifecycleSignature != ios_main_fbo_audit.lastLifecycleSignature;
	if( ownerChanged || lifecycleChanged )
	{
		if( !ios_main_fbo_audit.sampleInvocation )
			R_IOSMainFBOAudit( state, &ios_main_fbo_audit.rendererAudit, true );
		ios_main_fbo_audit.sampleInvocation = true;
	}
	state->auditSample = ios_main_fbo_audit.sampleInvocation;
	R_IOSMainFBOPrintPolicyAndState( state, &ios_main_fbo_audit.rendererAudit,
		lifecycleChanged, ownerChanged );
	if( ios_main_fbo_audit.sampleInvocation )
		R_IOSMainFBOPrintCheckpoint( "iOS presentation pipeline:", "A-renderer-handoff",
			state, &ios_main_fbo_audit.rendererAudit, NULL );
	ios_main_fbo_audit.lastOwnerSignature = ownerSignature;
	ios_main_fbo_audit.lastLifecycleSignature = lifecycleSignature;
	ios_main_fbo_original_swap();
	ios_main_fbo_audit.activeInvocation = false;
}

static void R_IOSMainFBOCopyFrameState( ref_ios_drawable_bridge_t *state )
{
	state->invocation = ios_main_fbo_audit.frame.invocation;
	state->timestampUsec = ios_main_fbo_audit.frame.timestampUsec;
	state->hostTimeUsec = ios_main_fbo_audit.frame.hostTimeUsec;
	state->clientTimeUsec = ios_main_fbo_audit.frame.clientTimeUsec;
	state->enginePhase = ios_main_fbo_audit.frame.enginePhase;
	state->clientState = ios_main_fbo_audit.frame.clientState;
	state->auditSample = ios_main_fbo_audit.sampleInvocation;
	Q_strncpy( state->mapName, ios_main_fbo_audit.frame.mapName, sizeof( state->mapName ));
}

static int R_IOSDrawableBridge( int action, void *opaqueState, size_t stateSize )
{
	ref_ios_drawable_bridge_t *state = (ref_ios_drawable_bridge_t *)opaqueState;
	gl4es_drawable_audit_t before, after;
	uint64_t sdlSignature;
	int result = 0;

	if( !state || stateSize < sizeof( *state ) ||
		state->version != REF_IOS_DRAWABLE_BRIDGE_VERSION || state->size < sizeof( *state ) )
		return 0;

	if( !ios_main_fbo_original_swap )
	{
		ios_main_fbo_original_swap = gEngfuncs.GL_SwapBuffers;
		gEngfuncs.GL_SwapBuffers = R_IOSMainFBOSwap;
		R_IOSMainFBOReset( state->context );
		ios_main_fbo_audit.cachedSDL = *state;
		ios_main_fbo_audit.lastSDLSignature = R_IOSMainFBOSDLSignature( state );
		return 0;
	}

	if( ios_main_fbo_audit.context != state->context )
	{
		R_IOSMainFBOReset( state->context );
		ios_main_fbo_audit.cachedSDL = *state;
		ios_main_fbo_audit.lastSDLSignature = R_IOSMainFBOSDLSignature( state );
		return 0;
	}
	if( !ios_main_fbo_audit.activeInvocation || ios_main_fbo_audit.terminalPrinted )
		return 0;

	R_IOSMainFBOCopyFrameState( state );
	if( action == REF_IOS_DRAWABLE_BRIDGE_SDL_SWAP_ENTRY )
	{
		sdlSignature = R_IOSMainFBOSDLSignature( state );
		if( sdlSignature != ios_main_fbo_audit.lastSDLSignature &&
			!ios_main_fbo_audit.sampleInvocation )
		{
			ios_main_fbo_audit.sampleInvocation = true;
			state->auditSample = 1;
			R_IOSMainFBOAudit( state, &ios_main_fbo_audit.rendererAudit, true );
			R_IOSMainFBOPrintCheckpoint( "iOS presentation pipeline:", "A-renderer-handoff",
				state, &ios_main_fbo_audit.rendererAudit, NULL );
		}
		ios_main_fbo_audit.lastSDLSignature = sdlSignature;
		ios_main_fbo_audit.cachedSDL = *state;
		if( ios_main_fbo_audit.sampleInvocation )
		{
			R_IOSMainFBOAudit( state, &after, true );
			R_IOSMainFBOPrintCheckpoint( "iOS native attachment:", "B-SDL-swap-entry",
				state, &after, NULL );
		}
		return 1;
	}

	if( action == REF_IOS_DRAWABLE_BRIDGE_SDL_POST_RESOLVE )
	{
		if( ios_main_fbo_audit.sampleInvocation )
		{
			R_IOSMainFBOAudit( state, &after, true );
			R_IOSMainFBOPrintCheckpoint( "iOS presentation pipeline:", "C-SDL-post-resolve",
				state, &after, NULL );
		}
		return 1;
	}

	if( action == REF_IOS_DRAWABLE_BRIDGE_PRE_PRESENT )
	{
		if( ios_main_fbo_audit.sampleInvocation )
			R_IOSMainFBOAudit( state, &before, true );
		state->transferAttempted = 0;
		state->transferResult = 0;
		state->failureCode = 0;
		state->preconditionMask = 0;
		if( !state->context || !state->currentContext || !state->contextMatches )
			state->failureCode = 2;
		else if( !state->targetFramebuffer || !state->targetRenderbuffer ||
			!state->drawableWidth || !state->drawableHeight )
			state->failureCode = 3;
		else
		{
			state->transferAttempted = 1;
			result = gl4es_drawable_bridge_pre( state->targetFramebuffer,
				state->drawableWidth, state->drawableHeight,
				&state->sourceFramebuffer, &state->sourceTexture,
				&state->sourceRenderbuffer, &state->logicalFramebuffer,
				&state->targetStatus, &state->preconditionMask );
			state->transferResult = result ? 1 : 0;
			if( !result ) state->failureCode = 4;
		}
		if( ios_main_fbo_audit.sampleInvocation )
		{
			R_IOSMainFBOAudit( state, &after, true );
			R_IOSMainFBOPrintCheckpoint( "iOS drawable bridge attempt:", "D-bridge-entry-return",
				state, &after, &before );
		}
		return result;
	}

	if( action == REF_IOS_DRAWABLE_BRIDGE_PRESENT_BEFORE )
	{
		if( ios_main_fbo_audit.sampleInvocation )
			R_IOSMainFBOAudit( state, &ios_main_fbo_audit.presentAudit, true );
		return 1;
	}

	if( action != REF_IOS_DRAWABLE_BRIDGE_POST_PRESENT )
		return 0;

	result = gl4es_drawable_bridge_post( state->sourceFramebuffer,
		state->sourceRenderbuffer, &state->restoredFramebuffer,
		&state->restoredRenderbuffer, &state->restoredLogicalFramebuffer );
	state->restoreResult = result ? 1 : 0;
	if( !result && !state->failureCode ) state->failureCode = 5;
	if( ios_main_fbo_audit.sampleInvocation )
	{
		R_IOSMainFBOAudit( state, &after, true );
		R_IOSMainFBOPrintCheckpoint( "iOS drawable bridge present: iOS drawable bridge restore:",
			"E-present-entry-return", state, &after, &ios_main_fbo_audit.presentAudit );
	}
	if( ios_main_fbo_audit.terminalPending ||
		ios_main_fbo_audit.records >= REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS - 1 )
	{
		if( ios_main_fbo_audit.records < REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS )
		{
			ios_main_fbo_audit.records++;
			gEngfuncs.Con_Printf( "iOS main-FBO audit terminal: result=bounded-stop invocations=%llu records=%u max_records=%u phase=%u map=%s no_renderer_conclusion=1\n",
				(unsigned long long)ios_main_fbo_audit.invocation,
				ios_main_fbo_audit.records, REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS,
				state->enginePhase, state->mapName[0] ? state->mapName : "-" );
		}
		ios_main_fbo_audit.terminalPrinted = true;
	}
	return result;
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
