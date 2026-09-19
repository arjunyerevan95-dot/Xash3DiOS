#!/usr/bin/env python3
"""Validate Work Order 46 Phase B's direct iOS drawable ownership contract."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys


SDL_REF = "5d249570393f7a37e037abf22cd6012a4cc56a71"
GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def revision(path: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}", "-C", str(path),
         "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


def reject(text: str, pattern: str, label: str, failures: list[str]) -> None:
    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
        failures.append(f"{label}: forbidden pattern {pattern!r}")


def between(text: str, start_token: str, end_token: str) -> str:
    start = text.find(start_token)
    end = text.find(end_token, start + len(start_token))
    if start < 0 or end < 0:
        return ""
    return text[start:end]


def validate(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    api = files["api"]
    engine = files["engine"]
    platform = files["platform"]
    ref_common = files["ref_common"]
    renderer = files["renderer"]
    opengl = files["opengl"]
    sdl_header = files["sdl_header"]
    sdl_view = files["sdl_view"]
    sdl_gles = files["sdl_gles"]
    gl4es_api = files["gl4es_api"]
    gl4es_fbo = files["gl4es_fbo"]
    gl4es_fpe = files["gl4es_fpe"]
    gl4es_state = files["gl4es_state"]
    deps = files["deps"]
    build = files["build"]
    diffusion_build = files["diffusion_build"]

    for token in (
        "#define REF_API_VERSION 19",
        "#define REF_IOS_DIRECT_DRAWABLE_VERSION 3",
        "REF_IOS_DIRECT_DRAWABLE_MAX_RECORDS 32",
        "REF_IOS_DIRECT_DRAWABLE_MENU_SAMPLES 2",
        "REF_IOS_DIRECT_DRAWABLE_ACTIVE_SAMPLES 3",
        "REF_IOS_DIRECT_DRAWABLE_CONTEXT_RESTORED",
        "REF_IOS_DIRECT_DRAWABLE_RESIZED",
        "REF_IOS_DIRECT_DRAWABLE_DESTROYING",
        "GL_GetDrawableInfo",
    ):
        require(api, token, "direct-drawable ABI", failures)

    for token in (
        "SDL_XASH_IOSSetDirectDrawableCallback",
        "SDL_GetWindowWMInfo( host.hWnd, &info )",
        "info.subsystem != SDL_SYSWM_UIKIT",
        "info.info.uikit.framebuffer",
        "info.info.uikit.colorbuffer",
        "SDL_GL_GetCurrentContext()",
        "SDL_GL_GetDrawableSize",
        "ios_direct_drawable_context_generation++",
        "ios_direct_drawable_resize_generation++",
        "SDL_XASH_IOSSetDirectDrawableCallback( NULL )",
    ):
        require(engine, token, "live SDL drawable query/lifecycle", failures)
    require(platform, "int GL_GetDrawableInfo( ref_ios_direct_drawable_t *state",
            "engine platform ABI", failures)
    require(ref_common, "GL_GetDrawableInfo,", "renderer API initializer", failures)

    setup = between(opengl, "void GL_SetupAttributes", "void wes_init")
    for token in (
        "#if XASH_IOS && XASH_GL4ES",
        "/* SDL's CAEAGLLayer view FBO is the one presented drawable. */\n\t\tsamples = 0;",
        "REF_GL_MULTISAMPLEBUFFERS, 0",
        "REF_GL_MULTISAMPLESAMPLES, 0",
    ):
        require(setup, token, "iOS GL4ES samples-zero policy", failures)
    created = between(opengl, "void GL_OnContextCreated", "}")
    require(opengl, "initialize_gl4es();\n#if XASH_IOS\n\tR_IOSDirectDrawableContextCreated();",
            "registration before renderer GL", failures)
    require(opengl, "R_IOSDirectDrawableContextDestroying();\n#endif\n\tclose_gl4es();",
            "clear before GL4ES destruction", failures)

    for marker in (
        "iOS direct drawable policy:",
        "iOS direct drawable register:",
        "iOS direct drawable logical-zero:",
        "iOS direct drawable present:",
        "iOS direct drawable lifecycle:",
        "iOS direct drawable proof:",
    ):
        require(renderer, marker, "required bounded marker", failures)
    for token in (
        "gEngfuncs.GL_SwapBuffers = R_IOSDirectDrawableSwap",
        "set_external_default_framebuffer( state->viewFramebuffer )",
        "set_external_default_framebuffer( 0 )",
        "gl4es_external_default_framebuffer_state(",
        "state.contextGeneration != ios_direct_drawable.contextGeneration",
        "state.resizeGeneration != ios_direct_drawable.resizeGeneration",
        "state.viewFramebuffer != ios_direct_drawable.registeredFramebuffer",
        "action == REF_IOS_DIRECT_DRAWABLE_CONTEXT_RESTORED",
        "action == REF_IOS_DIRECT_DRAWABLE_RESIZED",
        "ios_direct_drawable.records >= REF_IOS_DIRECT_DRAWABLE_MAX_RECORDS",
        "checksum_changed=%u",
    ):
        require(renderer, token, "renderer registration/proof path", failures)
    reject(renderer, r"gl4es_drawable_bridge_(pre|post)|blitMainFBOTo|restoreMainFBOAfterPresent|transferAttempted|PRE_PRESENT",
           "failed transfer bridge removal", failures)

    for token in (
        "#define SDL_XASH_IOS_DIRECT_DRAWABLE_VERSION 3",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_CONTEXT_RESTORED 1",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_RESIZED 2",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_SWAP_ENTRY 3",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_PRESENT_BEFORE 4",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_POST_PRESENT 5",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_DESTROYING 6",
        "SDL_XASH_IOSSetDirectDrawableCallback",
    ):
        require(sdl_header, token, "SDL lifecycle ABI", failures)
    for token in (
        "state->viewFramebuffer = viewFramebuffer;",
        "state->viewRenderbuffer = viewRenderbuffer;",
        "state->contextGeneration = xashContextGeneration;",
        "state->resizeGeneration = xashResizeGeneration;",
        "state->requestedSamples = (Uint32)SDL_max(0, requestedSamples);",
        "state->effectiveSamples = (Uint32)SDL_max(0, samples);",
        "glBindRenderbuffer(GL_RENDERBUFFER, viewRenderbuffer);",
        "state.presentResult = [context presentRenderbuffer:GL_RENDERBUFFER];",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_RESIZED",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_DESTROYING",
    ):
        require(sdl_view, token, "SDL live drawable ownership", failures)
    require(sdl_gles, "SDL_XASH_IOS_DIRECT_DRAWABLE_CONTEXT_RESTORED",
            "foreground context reassertion", failures)
    swap = between(sdl_view, "- (void)swapBuffers", "- (void)layoutSubviews")
    order = [swap.find(token) for token in (
        "SDL_XASH_IOS_DIRECT_DRAWABLE_SWAP_ENTRY",
        "glBindRenderbuffer(GL_RENDERBUFFER, viewRenderbuffer);",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_PRESENT_BEFORE",
        "presentRenderbuffer:GL_RENDERBUFFER",
        "SDL_XASH_IOS_DIRECT_DRAWABLE_POST_PRESENT",
    )]
    if any(position < 0 for position in order) or order != sorted(order):
        failures.append("SDL present path: live drawable callbacks do not surround one normal present")
    if swap.count("presentRenderbuffer:GL_RENDERBUFFER") != 1:
        failures.append("SDL present path: expected exactly one presentRenderbuffer call")
    for field in ("viewFramebuffer", "viewRenderbuffer"):
        reject(sdl_view, rf"state->{field}\s*=\s*[1-9][0-9]*\s*;",
               "hard-coded SDL drawable identity", failures)

    for token in (
        "GL4ES_EXTERNAL_DEFAULT_STATE_VERSION 1",
        "registered_framebuffer",
        "logical_current",
        "logical_read",
        "logical_draw",
        "native_draw",
        "native_read",
        "framebuffer_status",
        "set_external_default_framebuffer",
        "gl4es_external_default_framebuffer_state",
    ):
        require(gl4es_api, token, "GL4ES external-default ABI", failures)
    for token in (
        "external_default_fbo",
        "external_default_generation",
        "external_default_active",
    ):
        require(gl4es_state, token, "context-scoped GL4ES state", failures)
    for token in (
        "static GLuint gl4es_defaultFramebuffer(void)",
        "static GLuint gl4es_nativeFramebuffer(const glframebuffer_t *framebuffer)",
        "GLuint gl4es_getDefaultFBO(void)",
        "int set_external_default_framebuffer(GLuint framebuffer)",
        "glstate->fbo.external_default_active = GL_FALSE",
        "glstate->fbo.external_default_active = GL_TRUE",
        "glstate->fbo.current_fb = glstate->fbo.fbo_0",
        "gl4es_nativeFramebuffer(glstate->fbo.fbo_read)",
        "gl4es_nativeFramebuffer(glstate->fbo.fbo_draw)",
        "gl4es_nativeFramebuffer(glstate->fbo.current_fb)",
        "framebuffer = gl4es_defaultFramebuffer();",
        "gl4es_external_default_framebuffer_state",
        "state->logical_current || state->logical_read || state->logical_draw",
        "state->native_draw != state->registered_framebuffer",
        "state->native_read != state->registered_framebuffer",
        "state->framebuffer_status != GL_FRAMEBUFFER_COMPLETE",
    ):
        require(gl4es_fbo, token, "central GL4ES logical-zero mapping", failures)
    if gl4es_fbo.count("gl4es_nativeFramebuffer(") < 10:
        failures.append("central GL4ES logical-zero mapping: helper coverage is incomplete")
    require(gl4es_fpe, "gles_glBindFramebuffer(GL_FRAMEBUFFER, gl4es_getDefaultFBO());",
            "fixed-pipeline temporary unbind mapping", failures)
    reject(gl4es_fbo + gl4es_fpe, r"gles_glBindFramebuffer\s*\([^\n,]+,\s*0\s*\)",
           "logical zero must not reach native framebuffer zero", failures)
    reject(gl4es_fbo, r"gl4es_drawable_bridge_(pre|post)|blitMainFBOTo|restoreMainFBOAfterPresent",
           "Bundle 60 transfer bridge", failures)

    require(deps, f"SDL_REF=${{SDL_REF:-{SDL_REF}}}", "SDL pin", failures)
    require(deps, "sdl2-drawable-bridge-ios.patch", "SDL patch route", failures)
    require(build, f"GL4ES_REF=${{GL4ES_REF:-{GL4ES_REF}}}", "GL4ES pin", failures)
    require(build, "gl4es-drawable-bridge-ios.patch", "GL4ES patch route", failures)
    require(build, "validate-ios-drawable-bridge.py", "policy validation route", failures)

    active = "\n".join((api, engine, renderer, opengl, sdl_header, sdl_view, sdl_gles,
                         gl4es_api, gl4es_fbo, gl4es_fpe, deps, build, diffusion_build))
    reject(active, r"LIBGL_FB\s*=|setenv\s*\(\s*[\"']LIBGL_FB", "LIBGL_FB/main-FBO route", failures)
    reject(active, r"sentinel_bars|yellow[_ -]?sentinel|normal-scene proof|menu_bypass",
           "sentinel/menu bypass", failures)
    reject(active, r"REF_IOS_DRAWABLE_BRIDGE_VERSION|SDL_XASH_IOS_DRAWABLE_BRIDGE_VERSION|iOS main-FBO audit",
           "obsolete Bundle 60/64 contract", failures)
    return failures


def self_test(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    cases = (
        ("hard-coded FBO", "sdl_view", "state->viewFramebuffer = viewFramebuffer;", "state->viewFramebuffer = 7;"),
        ("MSAA greater than zero", "opengl", "/* SDL's CAEAGLLayer view FBO is the one presented drawable. */\n\t\tsamples = 0;", "/* invalid active MSAA */\n\t\tsamples = 4;"),
        ("active transfer", "renderer", "static int R_IOSDrawableBridge", "int gl4es_drawable_bridge_pre(void);\nstatic int R_IOSDrawableBridge"),
        ("LIBGL_FB", "engine", "void GL_SwapBuffers( void )", "const char *policy = \"LIBGL_FB=2\";\nvoid GL_SwapBuffers( void )"),
        ("public-bind-only", "gl4es_fbo", "static GLuint gl4es_nativeFramebuffer(const glframebuffer_t *framebuffer)", "static GLuint publicBindOnly(const glframebuffer_t *framebuffer)"),
        ("native zero", "gl4es_fbo", "void readfboBegin()", "void bad(void){ gles_glBindFramebuffer(GL_FRAMEBUFFER, 0); }\nvoid readfboBegin()"),
        ("missing clear", "opengl", "R_IOSDirectDrawableContextDestroying();", "missingDirectDrawableClear();"),
        ("missing foreground re-register", "sdl_gles", "SDL_XASH_IOS_DIRECT_DRAWABLE_CONTEXT_RESTORED", "SDL_XASH_IOS_DIRECT_DRAWABLE_SWAP_ENTRY"),
        ("stale context generation", "renderer", "state.contextGeneration != ios_direct_drawable.contextGeneration", "false"),
        ("Bundle 60 bridge", "gl4es_fbo", "void readfboBegin()", "int blitMainFBOTo(void);\nvoid readfboBegin()"),
        ("sentinel", "sdl_view", "- (void)swapBuffers", "void yellow_sentinel(void);\n- (void)swapBuffers"),
        ("unbounded diagnostics", "api", "REF_IOS_DIRECT_DRAWABLE_MAX_RECORDS 32", "REF_IOS_DIRECT_DRAWABLE_MAX_RECORDS 0"),
        ("menu bypass", "renderer", "static int R_IOSDrawableBridge", "void menu_bypass(void);\nstatic int R_IOSDrawableBridge"),
    )
    for label, key, old, new in cases:
        mutated = dict(files)
        if old not in mutated[key]:
            failures.append(f"self-test setup failed for {label}")
            continue
        mutated[key] = mutated[key].replace(old, new, 1)
        if not validate(mutated):
            failures.append(f"self-test accepted forbidden case: {label}")
    return failures


def main() -> int:
    if len(sys.argv) not in (4, 5) or (len(sys.argv) == 5 and sys.argv[4] != "--self-test"):
        print(f"usage: {pathlib.Path(sys.argv[0]).name} REPOSITORY SDL_SOURCE GL4ES_SOURCE [--self-test]",
              file=sys.stderr)
        return 2

    repository = pathlib.Path(sys.argv[1]).resolve()
    sdl = pathlib.Path(sys.argv[2]).resolve()
    gl4es = pathlib.Path(sys.argv[3]).resolve()
    failures: list[str] = []
    try:
        if revision(sdl) != SDL_REF:
            failures.append(f"SDL revision is not pinned to {SDL_REF}")
        if revision(gl4es) != GL4ES_REF:
            failures.append(f"GL4ES revision is not pinned to {GL4ES_REF}")
    except (OSError, subprocess.CalledProcessError) as error:
        failures.append(f"could not verify pinned revisions: {error}")

    files = {
        "api": read(repository / "engine/ref_api.h"),
        "engine": read(repository / "engine/platform/sdl2/vid_sdl2.c"),
        "platform": read(repository / "engine/platform/platform.h"),
        "ref_common": read(repository / "engine/client/dll_int/ref_common.c"),
        "renderer": read(repository / "ref/gl/gl_context.c"),
        "opengl": read(repository / "ref/gl/gl_opengl.c"),
        "sdl_header": read(sdl / "src/video/uikit/SDL_uikitopengles.h"),
        "sdl_view": read(sdl / "src/video/uikit/SDL_uikitopenglview.m"),
        "sdl_gles": read(sdl / "src/video/uikit/SDL_uikitopengles.m"),
        "gl4es_api": read(gl4es / "include/gl4esinit.h"),
        "gl4es_fbo": read(gl4es / "src/gl/framebuffers.c"),
        "gl4es_fpe": read(gl4es / "src/gl/fpe.c"),
        "gl4es_state": read(gl4es / "src/gl/state.h"),
        "deps": read(repository / "scripts/gha/deps_ios.sh"),
        "build": read(repository / "scripts/gha/build_ios.sh"),
        "diffusion_build": read(repository / "scripts/ios/builddiffusion.sh"),
    }
    failures.extend(validate(files))
    if len(sys.argv) == 5:
        failures.extend(self_test(files))
    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1
    print("iOS direct drawable policy: SDL-owned no-MSAA drawable, central GL4ES logical-zero mapping, one present")
    if len(sys.argv) == 5:
        print("iOS direct drawable rejection tests: identity, MSAA, transfer, environment, mapping, lifecycle, generations, sentinel, bounds, and menu bypass rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
