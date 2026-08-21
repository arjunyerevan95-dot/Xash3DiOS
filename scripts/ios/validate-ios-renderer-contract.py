#!/usr/bin/env python3
"""Validate Work Order 56 Phase E's complete pre-renderer contract."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import subprocess
import sys

BASELINE = "5b5cb89f1d9ec9c6b2291003c815c0019d065e1d"
ALLOWED_PATHS = {
    "engine/client/dll_int/ref_common.c",
    "engine/common/host.c",
    "engine/common/model.c",
    "ref/gl/gl_opengl.c",
    "scripts/gha/build_ios.sh",
    "scripts/ios/validate-ios-renderer-contract.py",
    "scripts/ios/validate-ios-selftest-boot.py",
    "scripts/ios/verify_ipa.sh",
    "scripts/ios/wo56e-renderer-contract.json",
}
TERMINAL_FAIL = "iOS texture array selftest terminal: FAIL failures=1 diffusion_started=0"
EXPECTED_COUNTS = {"cvars": 27, "callbacks": 22, "parameters": 5, "globals": 3}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


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
        failures.append(f"{label}: unable to resolve source block")
        return ""
    return text[begin:finish]


def shared_cvars(ref_api: str) -> list[str]:
    macro = block(
        ref_api,
        "#define ENGINE_SHARED_CVAR_LIST( f )",
        "#define DECLARE_ENGINE_SHARED_CVAR_LIST()",
        "engine shared cvar macro",
        [],
    )
    names: list[str] = []
    for line in macro.splitlines():
        named = re.search(r"ENGINE_SHARED_CVAR_NAME\(\s*f\s*,\s*\w+\s*,\s*(\w+)\s*\)", line)
        direct = re.search(r"ENGINE_SHARED_CVAR\(\s*f\s*,\s*(\w+)\s*\)", line)
        if named:
            names.append(named.group(1))
        elif direct:
            names.append(direct.group(1))
    return names


def normalized_flags(expression: str) -> list[str]:
    expression = re.sub(r"\s+", "", expression)
    if expression == "0":
        return []
    return sorted(expression.split("|"))


def validate_cvar_source(
    item: dict[str, object], source: str, all_sources: str, failures: list[str]
) -> None:
    name = str(item.get("name", ""))
    symbol = str(item.get("symbol", ""))
    default = str(item.get("default", ""))
    flags = item.get("flags")
    initializer = str(item.get("normalInitializer", ""))
    if not isinstance(flags, list):
        return

    if initializer not in all_sources:
        failures.append(f"cvar {name}: normal initializer {initializer!r} is absent")

    if symbol.startswith("lookup:"):
        match = re.search(
            rf'Cvar_Get\(\s*"{re.escape(name)}"\s*,\s*"([^"]*)"\s*,\s*([^,]+),',
            source,
        )
    else:
        match = re.search(
            rf'CVAR_DEFINE_AUTO\(\s*{re.escape(symbol)}\s*,\s*"([^"]*)"\s*,\s*([^,]+),',
            source,
        )
        if not match:
            match = re.search(
                rf'CVAR_DEFINE\(\s*{re.escape(symbol)}\s*,\s*"{re.escape(name)}"\s*,\s*"([^"]*)"\s*,\s*([^,]+),',
                source,
            )
    if not match:
        failures.append(f"cvar {name}: source definition is absent from declared owner")
        return
    if match.group(1) != default:
        failures.append(
            f"cvar {name}: default mismatch inventory={default!r} source={match.group(1)!r}"
        )
    source_flags = normalized_flags(match.group(2))
    inventory_flags = sorted(str(flag) for flag in flags)
    if source_flags != inventory_flags:
        failures.append(
            f"cvar {name}: flags mismatch inventory={inventory_flags} source={source_flags}"
        )


def validate(files: dict[str, object]) -> list[str]:
    failures: list[str] = []
    host = str(files["host"])
    model = str(files["model"])
    loader = str(files["loader"])
    context = str(files["context"])
    ref_api = str(files["ref_api"])
    build = str(files["build"])
    verify = str(files["verify"])
    owner_sources = {
        "engine/client/gamma.c": str(files["gamma"]),
        "engine/client/dll_int/ref_common.c": loader,
        "engine/client/cl_main.c": str(files["client"]),
        "engine/common/model.c": model,
        "engine/common/host.c": host,
    }
    all_sources = "\n".join(str(source) for source in owner_sources.values())
    inventory = files["inventory"]
    assert isinstance(inventory, dict)

    for key, expected in EXPECTED_COUNTS.items():
        items = inventory.get(key)
        if not isinstance(items, list) or len(items) != expected:
            failures.append(f"inventory {key}: expected {expected}, got {len(items) if isinstance(items, list) else 'invalid'}")
    total = sum(len(inventory.get(key, [])) for key in EXPECTED_COUNTS)
    if inventory.get("runtimeItemCount") != 57 or total != 57:
        failures.append(f"inventory total: expected 57, got declared={inventory.get('runtimeItemCount')} actual={total}")

    cvar_items = inventory.get("cvars", [])
    cvar_names = [item.get("name") for item in cvar_items if isinstance(item, dict)]
    source_names = shared_cvars(ref_api)
    if cvar_names != source_names:
        failures.append(f"shared cvar inventory differs from engine/ref_api.h: inventory={cvar_names} source={source_names}")

    for item in cvar_items:
        if not isinstance(item, dict):
            failures.append("cvar inventory contains a non-object")
            continue
        for field in ("name", "symbol", "default", "flags", "owner", "normalInitializer", "firstConsumer"):
            if field not in item:
                failures.append(f"cvar {item.get('name')}: missing field {field}")
        if not isinstance(item.get("flags"), list):
            failures.append(f"cvar {item.get('name')}: flags must be a list")
        owner = str(item.get("owner", ""))
        if owner not in owner_sources:
            failures.append(f"cvar {item.get('name')}: unknown owner {owner!r}")
        else:
            validate_cvar_source(item, str(owner_sources[owner]), all_sources, failures)

    callback_names = [item.get("name") for item in inventory.get("callbacks", []) if isinstance(item, dict)]
    parameter_names = [item.get("name") for item in inventory.get("parameters", []) if isinstance(item, dict)]
    global_names = [item.get("name") for item in inventory.get("globals", []) if isinstance(item, dict)]
    for item in inventory.get("callbacks", []) + inventory.get("parameters", []) + inventory.get("globals", []):
        if not isinstance(item, dict) or not item.get("provider") or not item.get("firstConsumer"):
            failures.append(f"non-cvar inventory item lacks provider/consumer: {item}")

    shared_init = block(
        host,
        "static qboolean Host_InitRendererContract( void )",
        "typedef struct feature_message_s",
        "shared contract initializer",
        failures,
    )
    for token in ("&host_allow_materials", "&r_showhull"):
        require(shared_init, token, "shared contract initializer", failures)
    for forbidden in ("FS_LoadGameInfo", "Mod_Init();", "SV_Init();", "CL_Init();"):
        if forbidden in shared_init:
            failures.append(f"shared contract initializer reaches forbidden {forbidden}")
    if model.count("Cvar_RegisterVariable( &r_showhull )") != 0:
        failures.append("r_showhull has duplicate normal registration outside shared initializer")
    if host.count("Host_InitRendererContract(") != 3:
        failures.append("shared initializer must have one definition plus one selftest and one normal call")
    ordered(host, (
        'iOS texture array selftest boot: filesystem-independent',
        "Host_InitRendererContract( )",
        "CL_Init();",
    ), "selftest contract ordering", failures)
    ordered(host, (
        "Host_InitRendererContract();",
        "Mod_Init();",
        "CL_Init();",
    ), "normal contract ordering", failures)
    for token in (
        "iOS texture array selftest contract: begin",
        "iOS texture array selftest contract: missing name=%s reason=ownership",
        TERMINAL_FAIL,
    ):
        require(host, token, "shared initializer failure boundary", failures)

    runtime_cvars = block(loader, "static const char *const cvars[]", "int count = 0;", "runtime cvar inventory", failures)
    for name in cvar_names:
        require(runtime_cvars, f'"{name}"', "runtime cvar inventory", failures)
    if len(re.findall(r'"[a-zA-Z_][a-zA-Z0-9_]*"', runtime_cvars)) != 27:
        failures.append("runtime cvar inventory must contain exactly 27 names")
    for name in callback_names:
        require(loader, f"IOS_REQUIRE_CALLBACK( {name} );", "runtime callback inventory", failures)
    for name in parameter_names[:4]:
        require(loader, f'IOS_REQUIRE_PARM( "{name}", {name} );', "runtime parameter inventory", failures)
    require(loader, 'R_IOSTextureArrayContractItem( "parm.PARM_CONNSTATE", &count );', "scalar parameter inventory", failures)
    require(loader, 'R_IOSTextureArrayContractItem( "global.refState", &count );', "refState inventory", failures)
    require(loader, "IOS_SELFTEST_CONTRACT_ENGINE_ITEMS 55", "engine item count", failures)
    require(loader, "iOS texture array selftest contract: item name=%s source=shared", "runtime contract proof", failures)
    failure_helper = block(
        loader,
        "static qboolean R_IOSTextureArrayContractFailure",
        "static void R_IOSTextureArrayContractItem",
        "runtime contract failure helper",
        failures,
    )
    for token in ("iOS texture array selftest contract: missing name=%s reason=%s", TERMINAL_FAIL, "Sys_Quit("):
        require(failure_helper, token, "runtime contract failure helper", failures)
    ordered(loader, (
        "R_ValidateIOSTextureArrayRendererContract( )",
        'Cbuf_AddText( "exec video.cfg\\n" );',
        'Sys_GetParmFromCmdLine( "-ref", requested_cmdline )',
        "R_LoadRenderer( requested_cmdline, false )",
    ), "contract validation before renderer load", failures)

    for name in global_names[1:]:
        require(context, f"item name=global.{name} source=shared", "renderer field inventory", failures)
        require(context, f"missing name=global.{name}", "renderer field failure", failures)
    ordered(context, (
        "iOS texture array selftest contract: complete count=57",
        "initialize_gl4es();",
        "iOS texture array selftest boot: renderer-ready",
    ), "contract completion before GL4ES dispatch", failures)
    require(context, TERMINAL_FAIL, "renderer field bounded failure", failures)
    if context.count('gEngfuncs.Host_Error( "iOS texture array selftest renderer contract failed') != 2:
        failures.append("renderer field failures must cross the Host_Error boundary exactly twice")

    require(build, "validate-ios-renderer-contract.py", "qualification build", failures)
    for marker in (
        "iOS texture array selftest contract: begin",
        "iOS texture array selftest contract: item name=",
        "iOS texture array selftest contract: complete count=57",
    ):
        require(verify, marker, "IPA contract markers", failures)
    return failures


def fixtures(files: dict[str, object]) -> list[str]:
    failures: list[str] = []
    mutations: list[tuple[str, str, str, str]] = [
        ("r_showhull removed", "host", "Host_RegisterRendererContractCvar( &r_showhull )", "Host_RegisterRendererContractCvar( &host_allow_materials )"),
        ("host_allow_materials removed", "host", "Host_RegisterRendererContractCvar( &host_allow_materials )", "Host_RegisterRendererContractCvar( &r_showhull )"),
        ("duplicate r_showhull", "model", "Cvar_RegisterVariable( &r_wadtextures );", "Cvar_RegisterVariable( &r_wadtextures );\n\tCvar_RegisterVariable( &r_showhull );"),
        ("wrong r_showhull default", "model", 'CVAR_DEFINE_AUTO( r_showhull, "0", 0', 'CVAR_DEFINE_AUTO( r_showhull, "1", 0'),
        ("wrong host flags", "host", "FCVAR_LATCH|FCVAR_ARCHIVE", "FCVAR_ARCHIVE"),
        ("contract after renderer", "loader", "R_ValidateIOSTextureArrayRendererContract( )", "R_ValidateIOSTextureArrayRendererContractAfterLoad( )"),
        ("filesystem leak", "host", "static qboolean Host_InitRendererContract( void )\n{", "static qboolean Host_InitRendererContract( void )\n{\n\tFS_LoadGameInfo();"),
        (
            "missing bounded terminal",
            "loader",
            'Con_Printf( "iOS texture array selftest contract: missing name=%s reason=%s\\n", name, reason );\n\tCon_Printf( "' + TERMINAL_FAIL + '\\n" );',
            'Con_Printf( "iOS texture array selftest contract: missing name=%s reason=%s\\n", name, reason );\n\tCon_Printf( "renderer contract failure\\n" );',
        ),
        ("wrong complete count", "context", "complete count=57", "complete count=56"),
        ("IPA proof removed", "verify", "iOS texture array selftest contract: complete count=57", "contract marker removed"),
    ]
    for label, key, old, new in mutations:
        candidate = copy.deepcopy(files)
        source = str(candidate[key])
        if old not in source:
            failures.append(f"fixture {label}: source token absent")
            continue
        candidate[key] = source.replace(old, new, 1)
        if not validate(candidate):
            failures.append(f"fixture {label}: validator accepted mutation")

    candidate = copy.deepcopy(files)
    assert isinstance(candidate["inventory"], dict)
    candidate["inventory"]["callbacks"] = candidate["inventory"]["callbacks"][:-1]
    if not validate(candidate):
        failures.append("fixture incomplete callback inventory: validator accepted mutation")
    return failures


def changed_paths(root: pathlib.Path) -> set[str]:
    tracked = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", BASELINE, "HEAD", "--"],
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
    files: dict[str, object] = {
        "host": read(root / "engine/common/host.c"),
        "model": read(root / "engine/common/model.c"),
        "loader": read(root / "engine/client/dll_int/ref_common.c"),
        "context": read(root / "ref/gl/gl_opengl.c"),
        "ref_api": read(root / "engine/ref_api.h"),
        "gamma": read(root / "engine/client/gamma.c"),
        "client": read(root / "engine/client/cl_main.c"),
        "build": read(root / "scripts/gha/build_ios.sh"),
        "verify": read(root / "scripts/ios/verify_ipa.sh"),
        "inventory": json.loads(read(root / "scripts/ios/wo56e-renderer-contract.json")),
    }
    failures = validate(files)
    unexpected = changed_paths(root) - ALLOWED_PATHS
    if unexpected:
        failures.append(f"Phase E scope changed: {sorted(unexpected)}")
    if args.self_test:
        failures += fixtures(files)
    if failures:
        print("iOS renderer-contract validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("iOS renderer-contract validation passed: 57-item source and runtime contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
