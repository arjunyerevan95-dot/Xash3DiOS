#!/usr/bin/env python3
"""Validate Work Order 45 Phase B's diagnostics-only iOS main-FBO audit."""

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
    renderer = files["renderer"]
    sdl_header = files["sdl_header"]
    sdl_view = files["sdl_view"]
    gl4es_api = files["gl4es_api"]
    gl4es_fbo = files["gl4es_fbo"]
    gl4es_main = files["gl4es_main"]
    deps = files["deps"]
    build = files["build"]
    diffusion_build = files["diffusion_build"]

    for token in (
        "#define REF_API_VERSION 18",
        "#define REF_IOS_DRAWABLE_BRIDGE_VERSION 2",
        "REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS 64",
        "REF_IOS_DRAWABLE_BRIDGE_MENU_ATTEMPTS 3",
        "REF_IOS_DRAWABLE_BRIDGE_MAP_GAPS 6",
        "REF_IOS_DRAWABLE_BRIDGE_RENDERER_HANDOFF",
        "REF_IOS_DRAWABLE_BRIDGE_SDL_SWAP_ENTRY",
        "REF_IOS_DRAWABLE_BRIDGE_SDL_POST_RESOLVE",
        "REF_IOS_DRAWABLE_BRIDGE_PRE_PRESENT",
        "REF_IOS_DRAWABLE_BRIDGE_PRESENT_BEFORE",
        "REF_IOS_DRAWABLE_BRIDGE_POST_PRESENT",
        "contextGeneration",
        "resizeGeneration",
        "requestedSamples",
        "effectiveSamples",
        "preconditionMask",
    ):
        require(api, token, "engine audit ABI", failures)

    require(engine, "SDL_XASH_IOSSetDrawableBridgeCallback", "engine-to-SDL registration", failures)
    require(engine, "ref.dllFuncs.R_IOSDrawableBridge", "engine-to-SDL registration", failures)
    require(renderer, "gEngfuncs.GL_SwapBuffers = R_IOSMainFBOSwap", "renderer-handoff hook", failures)
    require(renderer, "R_IOSMainFBOPrintCheckpoint( \"iOS presentation pipeline:\", \"A-renderer-handoff\"",
            "renderer checkpoint A", failures)
    for marker in (
        "iOS main-FBO audit policy:",
        "iOS main-FBO lifecycle:",
        "iOS main-FBO state:",
        "iOS native attachment:",
        "iOS presentation pipeline:",
        "iOS pixel checkpoint:",
        "iOS drawable bridge attempt:",
        "iOS drawable bridge present:",
        "iOS drawable bridge restore:",
        "iOS main-FBO audit terminal:",
    ):
        require(renderer, marker, "required bounded marker", failures)
    for token in (
        "static const uint32_t activeGaps[] = { 0, 2, 4, 8, 16, 32, 64 }",
        "ios_main_fbo_audit.records >= REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS - 1",
        "gl4es_drawable_bridge_audit(",
        "state->preconditionMask",
        "R_IOSDrawableBridge,\n#else\n\tNULL,",
    ):
        require(renderer, token, "bounded renderer audit", failures)

    for token in (
        "#define SDL_XASH_IOS_DRAWABLE_BRIDGE_VERSION 2",
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_SDL_SWAP_ENTRY 2",
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_SDL_POST_RESOLVE 3",
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_PRE_PRESENT 4",
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_PRESENT_BEFORE 5",
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_POST_PRESENT 6",
        "Uint32 contextGeneration",
        "Uint32 resizeGeneration",
        "Uint32 viewFramebuffer",
        "Uint32 msaaFramebuffer",
        "Uint32 depthRenderbuffer",
        "Uint32 requestedSamples",
        "Uint32 effectiveSamples",
    ):
        require(sdl_header, token, "SDL audit ABI", failures)
    for token in (
        "requestedSamples = multisamples;",
        "samples = multisamples;",
        "samples = SDL_min(samples, maxsamples);",
        "bridge.contextAPI = (Uint32)context.API;",
        "bridge.contextGeneration = xashContextGeneration;",
        "bridge.resizeGeneration = xashResizeGeneration;",
        "bridge.viewFramebuffer = viewFramebuffer;",
        "bridge.viewRenderbuffer = viewRenderbuffer;",
        "bridge.msaaFramebuffer = msaaFramebuffer;",
        "bridge.msaaRenderbuffer = msaaRenderbuffer;",
        "bridge.depthRenderbuffer = depthRenderbuffer;",
        "bridge.requestedSamples = (Uint32)SDL_max(0, requestedSamples);",
        "bridge.effectiveSamples = (Uint32)SDL_max(0, samples);",
    ):
        require(sdl_view, token, "live SDL drawable state", failures)

    swap = between(sdl_view, "- (void)swapBuffers", "- (void)layoutSubviews")
    order = [swap.find(token) for token in (
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_SDL_SWAP_ENTRY",
        "if (msaaFramebuffer)",
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_SDL_POST_RESOLVE",
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_PRE_PRESENT",
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_PRESENT_BEFORE",
        "presentRenderbuffer:GL_RENDERBUFFER",
        "SDL_XASH_IOS_DRAWABLE_BRIDGE_POST_PRESENT",
    )]
    if any(position < 0 for position in order) or order != sorted(order):
        failures.append("SDL swap order: checkpoints B/C/D/E do not surround the ordinary resolve/present path")
    if swap.count("glBlitFramebuffer(") != 1 or swap.count("glResolveMultisampleFramebufferAPPLE(") != 1:
        failures.append("SDL swap policy: ordinary resolve count changed")
    for field in ("targetFramebuffer", "targetRenderbuffer", "viewFramebuffer",
                  "viewRenderbuffer", "msaaFramebuffer", "msaaRenderbuffer",
                  "depthRenderbuffer", "drawableWidth", "drawableHeight"):
        reject(sdl_view, rf"bridge\.{field}\s*=\s*[1-9][0-9]*\s*;", "hard-coded SDL identity", failures)
    reject(sdl_view, r"sentinel|yellow[_ -]?bar|SDL_Log", "SDL diagnostics-only policy", failures)

    for token in (
        "GL4ES_DRAWABLE_AUDIT_VERSION 1",
        "GL4ES_DRAWABLE_PRE_NO_USEFBO",
        "GL4ES_DRAWABLE_PRE_NO_MAIN_FBO",
        "GL4ES_DRAWABLE_PRE_NO_MAIN_TEXTURE",
        "GL4ES_DRAWABLE_PRE_NO_CURRENT_FBO",
        "GL4ES_DRAWABLE_PRE_LOGICAL_NOT_ZERO",
        "GL4ES_DRAWABLE_PRE_NO_TARGET",
        "GL4ES_DRAWABLE_PRE_SOURCE_MISMATCH",
        "GL4ES_DRAWABLE_PRE_TARGET_IS_SOURCE",
        "GL4ES_DRAWABLE_PRE_INVALID_SIZE",
        "GL4ES_DRAWABLE_PRE_TARGET_INCOMPLETE",
        "gl4es_drawable_attachment_audit_t",
        "gl4es_drawable_fbo_audit_t",
        "gl4es_drawable_audit_t",
        "gl4es_drawable_bridge_audit",
    ):
        require(gl4es_api, token, "GL4ES audit ABI", failures)

    bridge = between(gl4es_fbo, "int blitMainFBOTo", "int restoreMainFBOAfterPresent")
    restore = between(gl4es_fbo, "int restoreMainFBOAfterPresent", "#define NATIVE_DRAW_FRAMEBUFFER")
    audit = between(gl4es_fbo, "#define NATIVE_DRAW_FRAMEBUFFER", "void bindMainFBO")
    for token in (
        "mask |= GL4ES_DRAWABLE_PRE_NO_USEFBO",
        "mask |= GL4ES_DRAWABLE_PRE_NO_MAIN_FBO",
        "mask |= GL4ES_DRAWABLE_PRE_SOURCE_MISMATCH",
        "mask |= GL4ES_DRAWABLE_PRE_TARGET_INCOMPLETE",
        "glstate->fbo.current_fb->id != 0",
        "gl4es_blitTexture(glstate->fbo.mainfbo_tex",
    ):
        require(bridge, token, "unchanged named bridge guard", failures)
    for token in (
        "gles_glBindFramebuffer(GL_FRAMEBUFFER, glstate->fbo.mainfbo_fbo);",
        "gles_glBindRenderbuffer(GL_RENDERBUFFER, expected_renderbuffer);",
        "expected_renderbuffer != glstate->fbo.current_rb->renderbuffer",
    ):
        require(restore, token, "existing bridge restore", failures)
    for token in (
        "NATIVE_DRAW_FRAMEBUFFER_BINDING 0x8CA6",
        "NATIVE_READ_FRAMEBUFFER_BINDING 0x8CAA",
        "gles_glGetFramebufferAttachmentParameteriv",
        "GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE",
        "GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME",
        "GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL",
        "gles_glGetRenderbufferParameteriv",
        "GL_RENDERBUFFER_WIDTH",
        "GL_RENDERBUFFER_HEIGHT",
        "GL_RENDERBUFFER_INTERNAL_FORMAT",
        "GL_RENDERBUFFER_SAMPLES",
        "gles_glReadPixels",
        "GL4ES_DRAWABLE_QUERY_PRIOR_ERROR",
        "GL4ES_DRAWABLE_QUERY_RESTORE",
        "GL4ES_DRAWABLE_QUERY_REQUERY",
        "gles_glBindFramebuffer(NATIVE_DRAW_FRAMEBUFFER, draw);",
        "gles_glBindFramebuffer(NATIVE_READ_FRAMEBUFFER, read);",
        "gles_glBindRenderbuffer(GL_RENDERBUFFER, renderbuffer);",
        "audit->restored_draw_framebuffer",
        "audit->restored_read_framebuffer",
        "audit->restored_renderbuffer",
        "audit->restored_logical_framebuffer",
    ):
        require(audit, token, "native interrogation and exact restore", failures)
    reject(audit, r"gl4es_blitTexture|glBlitFramebuffer|glResolve|glCopy|glFramebuffer(Texture|Renderbuffer)|glGen(Framebuffers|Renderbuffers|Textures)|glDelete(Framebuffers|Renderbuffers|Textures)|glClear\s*\(",
           "audit must be read-only", failures)
    if gl4es_fbo.count("void createMainFBO(") != 1:
        failures.append("main-FBO creation policy: audit changed the number of creator definitions")
    reject(renderer + gl4es_main, r"\bcreateMainFBO\s*\(", "main-FBO creation remains unauthorized", failures)

    main_pre = between(gl4es_main, "int gl4es_drawable_bridge_pre", "int gl4es_drawable_bridge_post")
    main_audit = between(gl4es_main, "int gl4es_drawable_bridge_audit", "#if defined(AMIGAOS4)")
    require(main_pre, "blitMainFBOTo(target_framebuffer", "existing bridge route", failures)
    require(main_pre, "precondition_mask", "named bridge preconditions", failures)
    require(main_audit, "auditDrawableBridge", "audit wrapper", failures)

    require(deps, f"SDL_REF=${{SDL_REF:-{SDL_REF}}}", "SDL pin", failures)
    require(deps, "sdl2-drawable-bridge-ios.patch", "SDL patch route", failures)
    require(build, f"GL4ES_REF=${{GL4ES_REF:-{GL4ES_REF}}}", "GL4ES pin", failures)
    require(build, "gl4es-drawable-bridge-ios.patch", "GL4ES patch route", failures)
    require(build, "validate-ios-drawable-bridge.py", "audit validation route", failures)
    for obsolete in ("sdl2-display-audit-ios.patch", "sdl2-wo43-diagnostics-ios.patch",
                     "sdl2-wo43-phase-b-correction-ios.patch",
                     "diffusion-ios-liveness.patch", "diffusion-wo43-diagnostics-ios.patch",
                     "diffusion-wo43-phase-b-correction-ios.patch"):
        reject(deps + build + diffusion_build, re.escape(obsolete), "obsolete diagnostic route", failures)

    active = "\n".join((engine, renderer, sdl_view, gl4es_main, deps, build, diffusion_build))
    reject(active, r"LIBGL_FB\s*=|setenv\s*\(\s*[\"']LIBGL_FB", "LIBGL_FB policy change", failures)
    reject(active, r"sentinel_bars|yellow[_ -]?sentinel|normal-scene proof", "sentinel policy", failures)
    return failures


def self_test(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    cases = (
        ("main-FBO creation", "renderer", "static void R_IOSMainFBOSwap( void )",
         "static void R_IOSMainFBOSwap( void )\n{ createMainFBO(640, 480); }"),
        ("LIBGL_FB injection", "engine", "void GL_SwapBuffers( void )",
         "const char *x = \"LIBGL_FB=2\";\nvoid GL_SwapBuffers( void )"),
        ("MSAA policy change", "sdl_view", "samples = multisamples;", "samples = 0;"),
        ("hard-coded FBO", "sdl_view", "bridge.viewFramebuffer = viewFramebuffer;",
         "bridge.viewFramebuffer = 7;"),
        ("new transfer", "gl4es_fbo", "#define NATIVE_DRAW_FRAMEBUFFER 0x8CA9",
         "#define NATIVE_DRAW_FRAMEBUFFER 0x8CA9\nvoid auditTransfer(void) { gl4es_blitTexture(1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, BLIT_OPAQUE); }"),
        ("persistent target mutation", "gl4es_fbo", "#define NATIVE_DRAW_FRAMEBUFFER 0x8CA9",
         "#define NATIVE_DRAW_FRAMEBUFFER 0x8CA9\nvoid auditAttach(void) { glFramebufferTexture2D(0, 0, 0, 0, 0); }"),
        ("sentinel", "sdl_view", "- (void)swapBuffers", "void yellow_sentinel(void);\n- (void)swapBuffers"),
        ("unbounded records", "api", "REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS 64",
         "REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS 0"),
        ("missing native restore", "gl4es_fbo", "gles_glBindFramebuffer(NATIVE_DRAW_FRAMEBUFFER, draw);",
         "missingNativeDrawRestore(draw);"),
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
        "renderer": read(repository / "ref/gl/gl_context.c"),
        "sdl_header": read(sdl / "src/video/uikit/SDL_uikitopengles.h"),
        "sdl_view": read(sdl / "src/video/uikit/SDL_uikitopenglview.m"),
        "gl4es_api": read(gl4es / "include/gl4esinit.h"),
        "gl4es_fbo": read(gl4es / "src/gl/framebuffers.c"),
        "gl4es_main": read(gl4es / "src/gl/gl4es.c"),
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
    print("iOS main-FBO audit policy: diagnostics-only checkpoints A-E, bounded checksums, exact restore")
    if len(sys.argv) == 5:
        print("iOS main-FBO audit rejection tests: creation, environment, MSAA, identity, transfer, mutation, sentinel, bounds, and restore rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
