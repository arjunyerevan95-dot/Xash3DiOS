#!/usr/bin/env python3
"""Validate the bounded iOS GL4ES-to-SDL drawable ownership bridge."""

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
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


def reject(text: str, pattern: str, label: str, failures: list[str]) -> None:
    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
        failures.append(f"{label}: forbidden pattern {pattern!r}")


def function(text: str, name: str, next_name: str) -> str:
    start = text.find(name)
    end = text.find(next_name, start + len(name))
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
        "REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS 64",
        "REF_IOS_DRAWABLE_BRIDGE_PROOF_TRANSFERS 3",
        "R_IOSDrawableBridge",
    ):
        require(api, token, "engine ABI", failures)

    require(engine, "SDL_XASH_IOSSetDrawableBridgeCallback", "engine-to-SDL registration", failures)
    require(engine, "ref.dllFuncs.R_IOSDrawableBridge", "engine-to-SDL registration", failures)
    require(renderer, "#if XASH_IOS && XASH_GL4ES", "renderer scope", failures)
    require(renderer, "gl4es_drawable_bridge_pre", "renderer pre-present callback", failures)
    require(renderer, "gl4es_drawable_bridge_post", "renderer post-present callback", failures)
    require(renderer, "state->sourceRenderbuffer", "renderer renderbuffer restore contract", failures)
    require(renderer, "iOS drawable bridge policy:", "bounded policy marker", failures)
    require(renderer, "iOS drawable bridge terminal:", "bounded terminal marker", failures)
    require(renderer, "R_IOSDrawableBridge,\n#else\n\tNULL,", "non-GL4ES no-op", failures)

    require(sdl_header, "SDL_XASH_IOSDrawableBridgeState", "SDL bridge contract", failures)
    for token in (
        "bridge.context = (Uint64)(uintptr_t)context;",
        "bridge.currentContext = (Uint64)(uintptr_t)[EAGLContext currentContext];",
        "bridge.targetFramebuffer = viewFramebuffer;",
        "bridge.targetRenderbuffer = viewRenderbuffer;",
        "bridge.drawableWidth = backingWidth;",
        "bridge.drawableHeight = backingHeight;",
    ):
        require(sdl_view, token, "live SDL drawable state", failures)

    pre = sdl_view.find("SDL_XASH_IOS_DRAWABLE_BRIDGE_PRE_PRESENT")
    present_bind = sdl_view.find("glBindRenderbuffer(GL_RENDERBUFFER, viewRenderbuffer);", pre)
    present = sdl_view.find("presentRenderbuffer:GL_RENDERBUFFER", present_bind)
    post = sdl_view.find("SDL_XASH_IOS_DRAWABLE_BRIDGE_POST_PRESENT", present)
    if not (0 <= pre < present_bind < present < post):
        failures.append("SDL swap order: expected pre-transfer, view renderbuffer bind, present, post-restore")
    require(sdl_view, "xashBridgeTransfers < XASH_BRIDGE_PROOF_TRANSFERS", "bounded checksum proof", failures)
    require(sdl_view, "XASH_BRIDGE_PROOF_TRANSFERS 3", "bounded checksum proof", failures)

    for field in ("targetFramebuffer", "targetRenderbuffer", "drawableWidth", "drawableHeight"):
        reject(sdl_view, rf"bridge\.{field}\s*=\s*[1-9][0-9]*\s*;", "hard-coded SDL target", failures)
    reject(sdl_view, r"sentinel|yellow[_ -]?bar|SDL_Log", "SDL diagnostic policy", failures)

    require(gl4es_api, "gl4es_drawable_bridge_pre", "GL4ES public bridge API", failures)
    require(gl4es_api, "gl4es_drawable_bridge_post", "GL4ES public bridge API", failures)
    pre_function = function(gl4es_main, "int gl4es_drawable_bridge_pre", "int gl4es_drawable_bridge_post")
    post_function = function(gl4es_main, "int gl4es_drawable_bridge_post", "#if defined(AMIGAOS4)")
    require(pre_function, "gl4es_flush()", "GL4ES flush boundary", failures)
    require(pre_function, "bitmap_flush()", "GL4ES bitmap flush boundary", failures)
    require(pre_function, "blitMainFBOTo(target_framebuffer", "target-aware GL4ES route", failures)
    require(post_function, "restoreMainFBOAfterPresent", "post-present restore", failures)
    reject(pre_function + post_function, r"gl4es_(pre|post)_swap", "stock framebuffer-zero route", failures)

    blit = function(gl4es_fbo, "int blitMainFBOTo", "int restoreMainFBOAfterPresent")
    restore = function(gl4es_fbo, "int restoreMainFBOAfterPresent", "void bindMainFBO")
    for token in (
        "gles_glBindFramebuffer(GL_FRAMEBUFFER, target);",
        "gles_glCheckFramebufferStatus(GL_FRAMEBUFFER)",
        "gles_glGetIntegerv(GL_FRAMEBUFFER_BINDING, &native_source)",
        "gles_glGetIntegerv(GL_RENDERBUFFER_BINDING, &native_renderbuffer)",
        "gl4es_blitTexture(glstate->fbo.mainfbo_tex",
        "glstate->fbo.current_fb->id != 0",
    ):
        require(blit, token, "explicit GL4ES target transfer", failures)
    require(restore, "gles_glBindFramebuffer(GL_FRAMEBUFFER, glstate->fbo.mainfbo_fbo);",
            "GL4ES native framebuffer restore", failures)
    require(restore, "gles_glBindRenderbuffer(GL_RENDERBUFFER, expected_renderbuffer);",
            "GL4ES native renderbuffer restore", failures)
    require(restore, "gles_glGetIntegerv(GL_FRAMEBUFFER_BINDING, &native_framebuffer)",
            "GL4ES framebuffer restore proof", failures)
    require(restore, "gles_glGetIntegerv(GL_RENDERBUFFER_BINDING, &native_renderbuffer)",
            "GL4ES renderbuffer restore proof", failures)
    require(restore, "expected_renderbuffer != glstate->fbo.current_rb->renderbuffer",
            "GL4ES renderbuffer identity invariant", failures)
    require(restore, "glstate->fbo.current_fb->id != 0", "GL4ES logical-zero invariant", failures)
    reject(blit, r"glBindFramebuffer\s*\([^\n]*,\s*0\s*\)", "stock framebuffer-zero target", failures)

    require(deps, f"SDL_REF=${{SDL_REF:-{SDL_REF}}}", "SDL pin", failures)
    require(deps, "sdl2-drawable-bridge-ios.patch", "SDL patch route", failures)
    for obsolete in ("sdl2-display-audit-ios.patch", "sdl2-wo43-diagnostics-ios.patch",
                     "sdl2-wo43-phase-b-correction-ios.patch"):
        reject(deps, re.escape(obsolete), "obsolete SDL diagnostic route", failures)
    require(build, f"GL4ES_REF=${{GL4ES_REF:-{GL4ES_REF}}}", "GL4ES pin", failures)
    require(build, "gl4es-drawable-bridge-ios.patch", "GL4ES patch route", failures)
    require(build, "validate-ios-drawable-bridge.py", "bridge policy validation route", failures)
    for obsolete in ("diffusion-ios-liveness.patch", "diffusion-wo43-diagnostics-ios.patch",
                     "diffusion-wo43-phase-b-correction-ios.patch"):
        reject(diffusion_build, re.escape(obsolete), "obsolete Diffusion diagnostic route", failures)

    active = "\n".join((engine, renderer, deps, build, diffusion_build))
    reject(active, r"WO43|sentinel_bars|liveness frame|GL_INVALID_OPERATION audit",
           "removed high-volume diagnostic", failures)
    return failures


def self_test(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    cases = (
        ("hard-coded target", "sdl_view", "bridge.targetFramebuffer = viewFramebuffer;",
         "bridge.targetFramebuffer = 7;"),
        ("hard-coded geometry", "sdl_view", "bridge.drawableWidth = backingWidth;",
         "bridge.drawableWidth = 1024;"),
        ("stock pre-swap", "gl4es_main", "if (glstate->list.active) gl4es_flush();",
         "gl4es_pre_swap();\n    if (glstate->list.active) gl4es_flush();"),
        ("sentinel", "sdl_view", "- (void)swapBuffers", "void xashDrawSentinel(void);\n- (void)swapBuffers"),
        ("missing restore", "gl4es_main", "return restoreMainFBOAfterPresent(", "return missingRestore("),
        ("unbounded record policy", "api", "REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS 64",
         "REF_IOS_DRAWABLE_BRIDGE_MAX_RECORDS 0"),
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

    print("iOS drawable bridge policy: live SDL target, GL4ES transfer/restore, bounded proof")
    if len(sys.argv) == 5:
        print("iOS drawable bridge rejection tests: all forbidden mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
