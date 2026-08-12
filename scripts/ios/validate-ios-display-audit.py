#!/usr/bin/env python3
"""Validate the bounded Work Order 43 Phase B iOS diagnostics contract."""

from __future__ import annotations

import pathlib
import sys


SDL_REF = "5d249570393f7a37e037abf22cd6012a4cc56a71"
POLICY_MARKER = (
    "iOS display audit policy: gameplay_frames=12 baseline=pre-world "
    "checksum=5x4x4 sentinel=disabled present=EAGL_BOOL preserve_bindings=1"
)


def require(source: str, tokens: tuple[str, ...], label: str, failures: list[str]) -> None:
    for token in tokens:
        if token not in source:
            failures.append(f"{label}: missing {token!r}")


def function(source: str, start: str, end: str, label: str, failures: list[str]) -> str:
    first = source.find(start)
    last = source.find(end, first + len(start))
    if first < 0 or last < 0:
        failures.append(f"{label}: could not resolve source boundary")
        return ""
    return source[first:last]


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {pathlib.Path(sys.argv[0]).name} REPOSITORY SDL_SOURCE", file=sys.stderr)
        return 2

    root = pathlib.Path(sys.argv[1])
    sdl = pathlib.Path(sys.argv[2])
    failures: list[str] = []

    host = (root / "engine/common/host.c").read_text(encoding="utf-8")
    view = (root / "engine/client/cl_view.c").read_text(encoding="utf-8")
    fade = (root / "engine/client/dll_int/cl_game.c").read_text(encoding="utf-8")
    platform = (root / "engine/platform/sdl2/vid_sdl2.c").read_text(encoding="utf-8")
    renderer = (root / "ref/gl/gl_rmain.c").read_text(encoding="utf-8")
    deps = (root / "scripts/gha/deps_ios.sh").read_text(encoding="utf-8")
    sdl_view = (sdl / "src/video/uikit/SDL_uikitopenglview.m").read_text(encoding="utf-8")
    sdl_gles = (sdl / "src/video/uikit/SDL_uikitopengles.m").read_text(encoding="utf-8")

    require(
        host,
        (POLICY_MARKER, 'GL_IOSDisplayAuditSnapshot( "next-host-frame-entry"'),
        "host",
        failures,
    )
    require(
        view,
        (
            'GL_IOSDisplayAuditSnapshot( "engine-frame-entry"',
            'GL_IOSDisplayAuditSnapshot( "before-renderer-dispatch"',
            'GL_IOSDisplayAuditSnapshot( "after-renderer-dispatch"',
            'GL_IOSDisplayAuditSnapshot( "after-2d-hud-menu-touch"',
        ),
        "engine display boundaries",
        failures,
    )
    require(
        platform,
        (
            'GL_IOSDisplayAuditSnapshot( "immediately-before-presentation"',
            'GL_IOSDisplayAuditSnapshot( "immediately-after-presentation"',
            "Host_IOSLivenessActive() && frame <= 12",
            "SDL_XASH_IOSDisplayAuditSnapshot",
            "WO43 native presentation:",
            "WO43 normal-scene proof:",
            "presentResult",
            "prePresentChecksum",
        ),
        "platform presentation boundary",
        failures,
    )
    require(
        renderer,
        (
            "iOS display audit GL4ES:",
            "IOS_GL_FRAMEBUFFER_BINDING",
            "IOS_GL_RENDERBUFFER_BINDING",
            "errors_before=%s errors_after_query=%s",
            "ios_renderer_calls > 3",
        ),
        "GL4ES-side audit",
        failures,
    )
    require(
        fade,
        (
            "iOS display audit ScreenFade: frame=%u stage=entry",
            "stage=return action=alpha-zero",
            "stage=return action=existing-diffusion-suppression",
            "stage=return action=drawn",
            'if( !Q_stricmp( GI->gamefolder, "diffusion" ))',
        ),
        "ScreenFade pairing",
        failures,
    )
    require(
        deps,
        (
            f"SDL_REF=${{SDL_REF:-{SDL_REF}}}",
            "sdl2-display-audit-ios.patch",
            "sdl2-wo43-diagnostics-ios.patch",
            "validate-ios-display-audit.py",
        ),
        "pinned SDL build",
        failures,
    )
    require(
        sdl_gles,
        (
            "SDL_XASH_IOSDisplayAuditSnapshot",
            "xashAuditSnapshotForWindow",
            "void *result",
            "resultSize",
        ),
        "SDL export",
        failures,
    )
    require(
        sdl_view,
        (
            "xashDrawableChecksumWithStatus",
            "XASH_AUDIT_SAMPLE_COUNT 5",
            "XASH_AUDIT_SAMPLE_EDGE 4",
            "BOOL presentResult = [context presentRenderbuffer:GL_RENDERBUFFER]",
            "xashAuditBaselineChecksum",
            "xashAuditPrePresentChecksum",
            "xashAuditPresentResult",
            "result->eaglCurrent",
            "result->expectedPresentFramebuffer",
        ),
        "SDL drawable audit",
        failures,
    )

    swap = function(sdl_view, "- (void)swapBuffers", "- (void)layoutSubviews", "SDL swap", failures)
    if swap:
        if "glBindRenderbuffer(GL_RENDERBUFFER, viewRenderbuffer)" in swap:
            failures.append("SDL swap: diagnostic candidate must not repair the observed renderbuffer binding")
        if "auditFrame > 0 && auditFrame <= 12" not in swap:
            failures.append("SDL swap: drawable work is not bounded to twelve frames")
        if "xashDrawSentinelForFrame" in swap or "sentinel" in swap.lower():
            failures.append("SDL swap: Phase B must not draw a colored sentinel")

    if "SDL_Log(" in sdl_view or "iOS display audit native:" in sdl_view:
        failures.append("SDL audit: native evidence must return to engine Con_Printf, not SDL_Log")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print(
        "WO43 Phase B diagnostics: pinned SDL; twelve gameplay frames; engine-routed POD; "
        "preserved bindings; drawable checksum; no sentinel; EAGL result"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
