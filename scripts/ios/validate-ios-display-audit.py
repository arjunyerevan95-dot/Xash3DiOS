#!/usr/bin/env python3
"""Validate the bounded Work Order 42 iOS display discriminator."""

from __future__ import annotations

import pathlib
import sys


SDL_REF = "5d249570393f7a37e037abf22cd6012a4cc56a71"
POLICY_MARKER = (
    "iOS display audit policy: first_gameplay_frames=3 baseline=pre-world "
    "checksum=5x4x4 sentinel=bars1-3 present=EAGL_BOOL preserve_bindings=1"
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
            "Host_IOSLivenessActive() && frame <= 3",
            "SDL_XASH_IOSDisplayAuditSnapshot",
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
            "validate-ios-display-audit.py",
        ),
        "pinned SDL build",
        failures,
    )
    require(
        sdl_gles,
        ("SDL_XASH_IOSDisplayAuditSnapshot", "xashAuditSnapshotForWindow"),
        "SDL export",
        failures,
    )
    require(
        sdl_view,
        (
            "iOS display audit native:",
            "iOS display audit drawable:",
            "iOS display audit present:",
            "xashDrawableChecksumWithStatus",
            "XASH_AUDIT_SAMPLE_COUNT 5",
            "XASH_AUDIT_SAMPLE_EDGE 4",
            "xashDrawSentinelForFrame",
            "glScissor(sentinelX, sentinelY, 180, 72)",
            "sentinel_bars=%u",
            "BOOL presentResult = [context presentRenderbuffer:GL_RENDERBUFFER]",
            "xashAuditBaselineChecksum",
            "checksumBeforeSentinel",
            "checksumAfterSentinel",
        ),
        "SDL drawable audit",
        failures,
    )

    swap = function(sdl_view, "- (void)swapBuffers", "- (void)layoutSubviews", "SDL swap", failures)
    if swap:
        if swap.find("checksumBeforeSentinel") > swap.find("xashDrawSentinelForFrame"):
            failures.append("SDL swap: checksum must precede the sentinel")
        if swap.find("xashDrawSentinelForFrame") > swap.find("presentRenderbuffer:GL_RENDERBUFFER"):
            failures.append("SDL swap: sentinel must precede presentation")
        if "glBindRenderbuffer(GL_RENDERBUFFER, viewRenderbuffer)" in swap:
            failures.append("SDL swap: diagnostic candidate must not repair the observed renderbuffer binding")
        if "auditFrame > 0 && auditFrame <= 3" not in swap:
            failures.append("SDL swap: drawable work is not bounded to three frames")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print(
        "iOS display audit policy: pinned SDL; three gameplay frames; preserved bindings; "
        "paired native/GL4ES state; drawable checksum; sentinel; EAGL result"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
