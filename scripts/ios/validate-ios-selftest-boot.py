#!/usr/bin/env python3
"""Validate Work Order 56 Phase C's filesystem-independent iOS self-test boot."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

BASELINE = "9cf4cf1fea8e1aa8e83b9f110452582302b3877f"
ALLOWED_PATHS = {
    "engine/common/host.c",
    "engine/client/dll_int/ref_common.c",
    "ref/gl/gl_opengl.c",
    "ref/gl/gl_texture_array_selftest.c",
    "scripts/gha/build_ios.sh",
    "scripts/ios/validate-ios-selftest-boot.py",
    "scripts/ios/verify_ipa.sh",
}
LOCKED_ARGS = '-dev 2 -log -ref gl4es -gl4es_texture_array_selftest'
TERMINAL_FAIL = "iOS texture array selftest terminal: FAIL failures=1 diffusion_started=0"


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


def ordered(text: str, tokens: tuple[str, ...], label: str, failures: list[str]) -> None:
    cursor = -1
    for token in tokens:
        position = text.find(token, cursor + 1)
        if position < 0:
            failures.append(f"{label}: missing or out of order {token!r}")
            return
        cursor = position


def block(text: str, start: str, end: str, label: str, failures: list[str]) -> str:
    begin = text.find(start)
    finish = text.find(end, begin + len(start)) if begin >= 0 else -1
    if begin < 0 or finish < 0:
        failures.append(f"{label}: unable to resolve bounded source block")
        return ""
    return text[begin:finish]


def validate(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    host = files["host"]
    renderer_loader = files["renderer_loader"]
    context = files["context"]
    harness = files["harness"]
    client = files["client"]
    launch = files["launch"]
    build = files["build"]
    verify = files["verify"]

    for token in (
        "static qboolean host_ios_texture_array_selftest;",
        'host_ios_texture_array_selftest = Sys_CheckParm( "-gl4es_texture_array_selftest" );',
        'iOS texture array selftest boot: armed',
        'iOS texture array selftest boot: filesystem-independent',
    ):
        require(host, token, "early arm/filesystem bypass", failures)
    require(host, "&& !host_ios_texture_array_selftest", "selftest shutdown config bypass", failures)
    ordered(host, (
        "Sys_ParseCommandLine( argc, (const char **)argv );",
        'host_ios_texture_array_selftest = Sys_CheckParm( "-gl4es_texture_array_selftest" );',
        "FS_Init();",
        "Image_Init();",
        "Sound_Init();",
        'Con_Printf( "iOS texture array selftest boot: filesystem-independent\\n" );',
        "return;",
        "FS_LoadGameInfo();",
    ), "host initialization boundary", failures)
    filesystem_marker = host.find("iOS texture array selftest boot: filesystem-independent")
    filesystem_branch = host.rfind("if( host_ios_texture_array_selftest )", 0, filesystem_marker)
    filesystem_end = host.find("#endif", filesystem_marker)
    if filesystem_marker < 0 or filesystem_branch < 0 or filesystem_end < 0:
        failures.append("filesystem-independent branch is not bounded")
    elif "FS_LoadGameInfo" in host[filesystem_branch:filesystem_end]:
        failures.append("filesystem-independent branch calls FS_LoadGameInfo")

    host_selftest = block(
        host,
        "if( host_ios_texture_array_selftest )\n\t{\n\t\tCL_Init();",
        "// init commands and vars",
        "Host_Main selftest route",
        failures,
    )
    for token in ("CL_Init();", TERMINAL_FAIL, "Sys_Quit("):
        require(host_selftest, token, "bounded Host_Main dispatch", failures)
    for forbidden in ("Mod_Init();", "NET_Init();", "SV_Init();", "FS_LoadGameInfo();"):
        if forbidden in host_selftest:
            failures.append(f"bounded Host_Main dispatch reaches forbidden {forbidden}")
    if host.find("if( host_ios_texture_array_selftest )", host.find("Host_Main(")) > host.find("Mod_Init();"):
        failures.append("Host_Main selftest dispatch occurs after normal subsystem initialization")

    for token in (
        "R_IOSTextureArraySelftestMode",
        "if( R_IOSTextureArraySelftestMode() && !success )",
        "iOS texture array selftest boot: renderer-failed",
        TERMINAL_FAIL,
        "iOS texture array selftest renderer initialization failed",
    ):
        require(renderer_loader, token, "bounded renderer failure", failures)
    ordered(renderer_loader, (
        'Sys_GetParmFromCmdLine( "-ref", requested_cmdline )',
        "R_LoadRenderer( requested_cmdline, false )",
        "if( R_IOSTextureArraySelftestMode() && !success )",
        "Sys_Quit( \"iOS texture array selftest renderer initialization failed\" )",
        "if( !success && !COM_StringEmptyOrNULL( r_refdll.string )",
    ), "renderer failure before fallback", failures)
    for token in (
        "if( R_IOSTextureArraySelftestMode( ))\n\t\treturn true;",
        "R_CreateBuiltinTextures();",
        "CL_FillTriAPI( &gTriApi );",
        "SCR_Init();",
    ):
        require(renderer_loader, token, "selftest/ordinary renderer split", failures)

    ordered(context, (
        "initialize_gl4es();",
        'iOS texture array selftest boot: renderer-ready',
        'iOS texture array selftest boot: dispatched',
        "R_IOSTextureArraySelftest();",
    ), "current-context dispatch", failures)
    require(context, 'if( gEngfuncs.Sys_CheckParm( "-gl4es_texture_array_selftest" ))\n\t\treturn true;', "minimal renderer init", failures)
    require(context, '#if XASH_IOS && XASH_GL4ES\n\tif( !gEngfuncs.Sys_CheckParm( "-gl4es_texture_array_selftest" ))\n\t\tR_ShutdownImages();\n#else\n\tR_ShutdownImages();\n#endif', "partial-init shutdown", failures)
    for token in (
        "static qboolean dispatched;",
        "if( dispatched )",
        "dispatched = true;",
        "iOS texture array selftest terminal:",
        "diffusion_started=0",
    ):
        require(harness, token, "single dispatch/terminal", failures)
    ordered(harness, ("if( dispatched )", "dispatched = true;", "iOS texture array selftest policy:"), "run-once guard", failures)

    require(client, 'Sys_Quit( "iOS texture array selftest complete" )', "post-dispatch clean exit", failures)
    require(launch, LOCKED_ARGS, "locked launcher arguments", failures)
    require(launch, "setEnabled:NO", "locked launcher field", failures)
    require(build, "validate-ios-selftest-boot.py", "qualification validator", failures)
    for marker in (
        "iOS texture array selftest boot: armed",
        "iOS texture array selftest boot: filesystem-independent",
        "iOS texture array selftest boot: renderer-ready",
        "iOS texture array selftest boot: dispatched",
    ):
        require(verify, marker, "IPA boot marker contract", failures)

    for token in (
        "FS_LoadGameInfo();", "Host_CheckGameLibraries();", "Cvar_PostFSInit();",
        "Mod_Init();", "NET_Init();", "SV_Init();", "SCR_Init();",
    ):
        require(host + renderer_loader, token, "ordinary launch preserved", failures)
    return failures


def fixtures(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    mutations = (
        ("arm removed", "host", "host_ios_texture_array_selftest = Sys_CheckParm", "host_ios_texture_array_selftest = false && Sys_CheckParm"),
        ("filesystem bypass removed", "host", "iOS texture array selftest boot: filesystem-independent", "selftest filesystem bypass removed"),
        ("config write restored", "host", "&& !host_ios_texture_array_selftest", "&& true"),
        ("game-info leak", "host", 'Con_Printf( "iOS texture array selftest boot: filesystem-independent\\n" );', 'FS_LoadGameInfo(); Con_Printf( "iOS texture array selftest boot: filesystem-independent\\n" );'),
        ("normal launch hijack", "host", "if( host_ios_texture_array_selftest )\n\t{\n\t\tCL_Init();", "if( true )\n\t{\n\t\tCL_Init();"),
        ("renderer fallback", "renderer_loader", "if( R_IOSTextureArraySelftestMode() && !success )", "if( false && R_IOSTextureArraySelftestMode() && !success )"),
        ("missing failure terminal", "renderer_loader", TERMINAL_FAIL, "selftest renderer failure"),
        ("dispatch removed", "context", "R_IOSTextureArraySelftest();", "/* selftest dispatch removed */"),
        ("run-once removed", "harness", "if( dispatched )", "if( false && dispatched )"),
        ("launcher changed", "launch", LOCKED_ARGS, "-dev 2 -log -ref gl4es -game diffusion"),
        ("IPA marker removed", "verify", "iOS texture array selftest boot: dispatched", "selftest dispatched marker removed"),
    )
    for label, key, old, new in mutations:
        candidate = dict(files)
        if old not in candidate[key]:
            failures.append(f"fixture {label}: source token absent")
            continue
        candidate[key] = candidate[key].replace(old, new, 1)
        if not validate(candidate):
            failures.append(f"fixture {label}: validator accepted mutation")
    return failures


def changed_paths(root: pathlib.Path) -> set[str]:
    tracked = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", BASELINE, "--"],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    return {path.replace("\\", "/") for path in tracked + untracked if path}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    files = {
        "host": read(root / "engine/common/host.c"),
        "renderer_loader": read(root / "engine/client/dll_int/ref_common.c"),
        "context": read(root / "ref/gl/gl_opengl.c"),
        "harness": read(root / "ref/gl/gl_texture_array_selftest.c"),
        "client": read(root / "engine/client/cl_main.c"),
        "launch": read(root / "engine/platform/ios/launchdialog.m"),
        "build": read(root / "scripts/gha/build_ios.sh"),
        "verify": read(root / "scripts/ios/verify_ipa.sh"),
    }
    failures = validate(files)
    unexpected = changed_paths(root) - ALLOWED_PATHS
    if unexpected:
        failures.append(f"Phase C scope changed: {sorted(unexpected)}")
    if args.self_test:
        failures += fixtures(files)
    if failures:
        print("iOS selftest boot validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("iOS selftest boot validation passed: filesystem-independent route and rejection fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
