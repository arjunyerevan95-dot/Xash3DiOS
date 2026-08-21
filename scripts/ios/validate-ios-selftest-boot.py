#!/usr/bin/env python3
"""Validate WO56 Phase G's normal Diffusion-bootstrap iOS self-test route."""

from __future__ import annotations

import argparse
import copy
import pathlib
import subprocess
import sys

BASELINE = "42be8465ec8752182f65005e8419a0cf634faf69"
ALLOWED_PATHS = {
    "engine/common/host.c",
    "engine/platform/ios/launchdialog.m",
    "scripts/ios/validate-ios-renderer-contract.py",
    "scripts/ios/validate-ios-selftest-boot.py",
    "scripts/ios/verify_ipa.sh",
}
LOCKED_ARGS = "-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest"
TERMINAL_FAIL = "iOS texture array selftest terminal: FAIL failures=1 diffusion_started=0"


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


def reject(text: str, token: str, label: str, failures: list[str]) -> None:
    if token in text:
        failures.append(f"{label}: forbidden {token!r}")


def ordered(text: str, tokens: tuple[str, ...], label: str, failures: list[str]) -> None:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            failures.append(f"{label}: missing or out of order {token!r}")
            return


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
    system = files["system"]
    build = files["build"]
    verify = files["verify"]

    host_init = block(host, "static void Host_InitCommon(", "static void Host_FreeCommon", "Host_InitCommon", failures)
    for token in (
        "static qboolean host_ios_texture_array_selftest;",
        'host_ios_texture_array_selftest = Sys_CheckParm( "-gl4es_texture_array_selftest" );',
        "iOS texture array selftest boot: armed",
        "iOS texture array selftest boot: gameinfo-ready game=diffusion",
    ):
        require(host, token, "normal-bootstrap arm", failures)
    reject(host, "filesystem-independent", "withdrawn no-game route", failures)
    reject(host_init, "FI->GameInfo = fake_gameinfo", "fabricated game information", failures)
    reject(host_init, 'title = "Xash3D"', "fallback title", failures)
    ordered(host_init, (
        "Sys_ParseCommandLine( argc, (const char **)argv );",
        'host_ios_texture_array_selftest = Sys_CheckParm( "-gl4es_texture_array_selftest" );',
        "FS_Init();",
        "FS_LoadGameInfo();",
        'Q_stricmp( GI->gamefolder, "diffusion" )',
        "iOS texture array selftest boot: gameinfo-ready game=diffusion",
        "Host_CheckGameLibraries();",
        "Cvar_PostFSInit();",
    ), "normal game-information startup", failures)
    fs_load = host_init.find("FS_LoadGameInfo();")
    if fs_load < 0:
        failures.append("normal game-information startup: FS_LoadGameInfo is absent")
    else:
        before_fs_load = host_init[:fs_load]
        if "iOS texture array selftest boot: gameinfo-ready" in before_fs_load:
            failures.append("gameinfo-ready marker precedes FS_LoadGameInfo")
        flagged_prefix = before_fs_load[before_fs_load.find("FS_Init();") :]
        if "return;" in flagged_prefix:
            failures.append("self-test can return after FS_Init but before FS_LoadGameInfo")
    gameinfo_gate = block(
        host_init,
        "FS_LoadGameInfo();",
        "Host_CheckGameLibraries();",
        "Diffusion game-information gate",
        failures,
    )
    for token in ("GI =", "FI->GameInfo =", "title =", "icon =", '"valve"'):
        reject(gameinfo_gate, token, "fabricated/fallback game information", failures)
    require(gameinfo_gate, TERMINAL_FAIL, "bounded game-information failure", failures)
    require(gameinfo_gate, "Sys_Quit(", "bounded game-information failure", failures)

    host_main = host[host.find("int EXPORT Host_Main") :]
    host_selftest = block(
        host_main,
        "if( host_ios_texture_array_selftest )\n\t{",
        "// init commands and vars",
        "Host_Main self-test route",
        failures,
    )
    for token in ("Host_InitRendererContract( )", "CL_Init();", TERMINAL_FAIL, "Sys_Quit("):
        require(host_selftest, token, "bounded Host_Main dispatch", failures)
    for forbidden in ("Mod_Init();", "NET_Init();", "SV_Init();", "CL_LoadProgs"):
        reject(host_selftest, forbidden, "pre-module Host_Main dispatch", failures)
    ordered(host_main, (
        "if( host_ios_texture_array_selftest )",
        "Host_InitRendererContract( )",
        "CL_Init();",
        "Mod_Init();",
        "SV_Init();",
    ), "self-test before ordinary modules", failures)
    require(host, "&& !host_ios_texture_array_selftest", "self-test config-write bypass", failures)

    for token in (
        "R_IOSTextureArraySelftestMode",
        "if( R_IOSTextureArraySelftestMode() && !success )",
        "iOS texture array selftest boot: renderer-failed",
        "iOS texture array selftest renderer initialization failed",
    ):
        require(renderer_loader, token, "bounded renderer failure", failures)
    ordered(renderer_loader, (
        "R_ValidateIOSTextureArrayRendererContract( )",
        'Sys_GetParmFromCmdLine( "-ref", requested_cmdline )',
        "R_LoadRenderer( requested_cmdline, false )",
        "if( R_IOSTextureArraySelftestMode() && !success )",
        'Sys_Quit( "iOS texture array selftest renderer initialization failed" )',
    ), "renderer contract/load/failure order", failures)
    require(renderer_loader, "if( R_IOSTextureArraySelftestMode( ))\n\t\treturn true;", "minimal self-test renderer init", failures)

    ordered(context, (
        "iOS texture array selftest contract: complete count=57",
        "initialize_gl4es();",
        "iOS texture array selftest boot: renderer-ready",
        "iOS texture array selftest boot: dispatched",
        "R_IOSTextureArraySelftest();",
    ), "post-context pre-module dispatch", failures)
    if context.count("R_IOSTextureArraySelftest();") != 1:
        failures.append("texture-array harness must have exactly one dispatch call")
    require(context, 'if( gEngfuncs.Sys_CheckParm( "-gl4es_texture_array_selftest" ))\n\t\treturn true;', "minimal renderer return", failures)
    require(context, '#if XASH_IOS && XASH_GL4ES\n\tif( !gEngfuncs.Sys_CheckParm( "-gl4es_texture_array_selftest" ))\n\t\tR_ShutdownImages();', "partial-init renderer shutdown", failures)

    for token in (
        "static qboolean dispatched;",
        "if( dispatched )",
        "dispatched = true;",
        "iOS texture array selftest terminal:",
        "diffusion_started=0",
    ):
        require(harness, token, "single dispatch/terminal", failures)
    ordered(harness, ("if( dispatched )", "dispatched = true;", "iOS texture array selftest policy:"), "run-once guard", failures)

    ordered(client, (
        "CL_InitLocal();",
        "VID_Init();",
        'Sys_Quit( "iOS texture array selftest complete" )',
        "CL_LoadProgs( libpath )",
    ), "terminal before client module", failures)
    if client.count('Sys_Quit( "iOS texture array selftest complete" )') != 1:
        failures.append("post-dispatch terminal must occur exactly once")
    require(system, "Host_ShutdownWithReason( reason );\n\tHost_ExitInMain();", "bounded terminal unwind", failures)
    require(host, "if( host.shutdown_issued )\n\t\treturn;", "idempotent host shutdown", failures)

    require(launch, LOCKED_ARGS, "locked launcher arguments", failures)
    reject(launch, "-game valve", "Valve substitution", failures)
    require(launch, "setEnabled:NO", "locked launcher field", failures)
    require(build, "validate-ios-selftest-boot.py", "qualification validator", failures)
    for marker in (
        "iOS texture array selftest boot: armed",
        "iOS texture array selftest boot: gameinfo-ready game=diffusion",
        "iOS texture array selftest contract: complete count=57",
        "iOS texture array selftest boot: renderer-ready",
        "iOS texture array selftest boot: dispatched",
    ):
        require(verify, marker, "IPA marker contract", failures)
    require(verify, "Proprietary game asset is packaged", "IPA game-asset rejection", failures)

    for token in ("FS_LoadGameInfo();", "Mod_Init();", "NET_Init();", "SV_Init();", "SCR_Init();", "CL_LoadProgs( libpath )"):
        require(host + renderer_loader + client, token, "ordinary startup preserved", failures)
    return failures


def fixtures(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    mutations = (
        ("missing -game diffusion", "launch", LOCKED_ARGS, "-dev 2 -log -ref gl4es -gl4es_texture_array_selftest"),
        ("Valve substitution", "launch", "-game diffusion", "-game valve"),
        ("pre-gameinfo marker", "host", "FS_LoadGameInfo();", 'Con_Printf( "iOS texture array selftest boot: gameinfo-ready game=diffusion\\n" );\n\tFS_LoadGameInfo();'),
        ("pre-gameinfo return", "host", "FS_LoadGameInfo();", "if( host_ios_texture_array_selftest ) return;\n\tFS_LoadGameInfo();"),
        ("fake gameinfo", "host", "FS_LoadGameInfo();", "FI->GameInfo = fake_gameinfo;\n\tFS_LoadGameInfo();"),
        ("fallback title", "host", "FS_LoadGameInfo();", 'title = "Xash3D";\n\tFS_LoadGameInfo();'),
        ("pre-context dispatch", "context", "initialize_gl4es();", "R_IOSTextureArraySelftest();\n\tinitialize_gl4es();"),
        ("duplicate dispatch", "context", "R_IOSTextureArraySelftest();", "R_IOSTextureArraySelftest();\n\t\tR_IOSTextureArraySelftest();"),
        ("post-module terminal", "client", 'Sys_Quit( "iOS texture array selftest complete" );', "/* delayed until after CL_LoadProgs */"),
        ("missing terminal shutdown", "client", 'Sys_Quit( "iOS texture array selftest complete" );', "return;"),
        ("normal launch hijack", "host", "if( host_ios_texture_array_selftest )\n\t{\n\t\tif( !Host_InitRendererContract( ))", "if( true )\n\t{\n\t\tif( !Host_InitRendererContract( ))"),
        ("contract order removed", "context", "iOS texture array selftest contract: complete count=57", "iOS texture array selftest contract: complete count=56"),
        ("packaged asset rejection removed", "verify", "Proprietary game asset is packaged", "Game asset allowed"),
    )
    for label, key, old, new in mutations:
        candidate = copy.deepcopy(files)
        if old not in candidate[key]:
            failures.append(f"fixture {label}: source token absent")
            continue
        candidate[key] = candidate[key].replace(old, new, 1)
        if not validate(candidate):
            failures.append(f"fixture {label}: validator accepted mutation")
    return failures


def changed_paths(root: pathlib.Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", BASELINE, "HEAD", "--"],
        check=True,
        capture_output=True,
        text=True,
    )
    return {path.replace("\\", "/") for path in result.stdout.splitlines() if path}


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
        "system": read(root / "engine/common/system.c"),
        "build": read(root / "scripts/gha/build_ios.sh"),
        "verify": read(root / "scripts/ios/verify_ipa.sh"),
    }
    failures = validate(files)
    unexpected = changed_paths(root) - ALLOWED_PATHS
    if unexpected:
        failures.append(f"Phase G scope changed: {sorted(unexpected)}")
    if args.self_test:
        failures += fixtures(files)
    if failures:
        print("iOS selftest boot validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("iOS selftest boot validation passed: normal Diffusion bootstrap and rejection fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
