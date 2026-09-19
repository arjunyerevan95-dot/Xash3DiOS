#!/usr/bin/env python3
"""Validate WO56M's locked ordinary iOS bootstrap and dormant self-test."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import sys

ORDINARY = "-dev 2 -log -game diffusion -ref gl4es"
COMBINED = ORDINARY + " -gl4es_texture_array_selftest"


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


def validate(files: dict[str, str], blobs: dict[str, bytes]) -> list[str]:
    failures: list[str] = []
    try:
        contract = json.loads(files["contract"])
    except json.JSONDecodeError as exc:
        return [f"ordinary-bootstrap contract is invalid JSON: {exc}"]

    if contract.get("schema") != 1 or contract.get("workOrder") != "56M":
        failures.append("ordinary-bootstrap contract identity changed")
    if contract.get("outcomeGate") != "A":
        failures.append("ordinary-bootstrap Outcome A gate changed")
    if contract.get("defaultArguments") != ORDINARY:
        failures.append("contract ordinary arguments changed")
    if contract.get("forbiddenCombinedDefault") != COMBINED:
        failures.append("contract combined-default discriminator changed")
    if [row.get("stage") for row in contract.get("argumentOwnership", [])] != [
        "locked-source-value", "tokenization", "argument-export", "host-admission"
    ]:
        failures.append("argument ownership table is incomplete or reordered")
    dormancy = contract.get("diagnosticDormancy", {})
    if dormancy.get("flag") != "-gl4es_texture_array_selftest" or dormancy.get("automaticDefault") is not False:
        failures.append("explicit-flag dormancy contract changed")
    if dormancy.get("harnessOwner") != "R_IOSTextureArraySelftest":
        failures.append("diagnostic harness ownership changed")
    if contract.get("runtimeQualification") != "not performed or claimed in Phase M":
        failures.append("Phase M claims unauthorized runtime qualification")

    launch = files["launch"]
    require(launch, f'static NSString *const ordinaryBootstrapArgs = @"{ORDINARY}";', "exact ordinary source tuple", failures)
    if launch.count(f'@"{ORDINARY}"') != 1:
        failures.append("ordinary launch tuple must have exactly one source owner")
    reject(launch, COMBINED, "combined automatic selftest tuple", failures)
    reject(launch, "textureArraySelftestArgs", "diagnostic default constant", failures)
    require(launch, "[textField setText:ordinaryBootstrapArgs];", "sole field value", failures)
    require(launch, "[textField setEnabled:NO];", "immutable field", failures)
    ordered(launch, (
        "[textField setText:ordinaryBootstrapArgs];",
        "[textField setEnabled:NO];",
        'componentsSeparatedByString:@" "',
        "szArgv = calloc",
        "szArgc = count + 1;",
    ), "locked field to argv", failures)
    for forbidden in ("setEnabled:YES", "getenv(", "NSUserDefaults", "settings.launch", "fallbackArgs", "overrideArgs"):
        reject(launch, forbidden, "argument override/fallback", failures)

    launcher = files["launcher"]
    ordered(launcher, (
        "IOS_LaunchDialog();",
        "szArgc = IOS_GetArgs( &szArgv );",
        "return Host_Main( szArgc, szArgv, XASH_GAMEDIR, 0, Sys_ChangeGame );",
    ), "IOS launch-to-host ownership", failures)

    combined_runtime = files["host"] + files["client"] + files["loader"] + files["context"] + files["harness"]
    for token in (
        'Sys_CheckParm( "-gl4es_texture_array_selftest" )',
        "host_ios_texture_array_selftest",
        "R_IOSTextureArraySelftest();",
        'Sys_Quit( "iOS texture array selftest complete" )',
        "iOS texture array selftest boot: armed",
        "iOS texture array selftest terminal:",
    ):
        require(combined_runtime, token, "retained explicit diagnostic machinery", failures)
    require(files["host"], 'host_ios_texture_array_selftest = Sys_CheckParm( "-gl4es_texture_array_selftest" );', "explicit flag parser", failures)
    require(files["host"], "if( host_ios_texture_array_selftest )\n\t{\n\t\tif( !Host_InitRendererContract( ))", "conditional host dispatch", failures)
    require(files["context"], 'if( gEngfuncs.Sys_CheckParm( "-gl4es_texture_array_selftest" ))', "conditional renderer dispatch", failures)
    require(files["harness"], "iOS texture array selftest terminal:", "harness terminal marker", failures)
    reject(files["host"], "if( true )\n\t{\n\t\tif( !Host_InitRendererContract( ))", "unconditional host dispatch", failures)

    verify = files["verify"]
    require(verify, f"grep -Fxq -- '{ORDINARY}' \"$ENGINE_STRINGS\"", "exact packaged ordinary discriminator", failures)
    require(verify, f"grep -Fxq -- '{COMBINED}' \"$ENGINE_STRINGS\"", "exact packaged combined rejection", failures)
    require(verify, "if ! grep -q -- '-gl4es_texture_array_selftest' \"$ENGINE_STRINGS\"", "packaged dormant flag", failures)
    for marker in contract.get("productionAdmissionMarkers", []):
        require(verify, marker, "retained production marker verifier", failures)
    require(files["build"], "validate-ios-ordinary-bootstrap.py", "build qualification hook", failures)

    expected_hashes = contract.get("lockedProductionSha256", {})
    if set(expected_hashes) != set(blobs):
        failures.append("locked production file set changed")
    for path, payload in blobs.items():
        actual = hashlib.sha256(payload).hexdigest()
        if expected_hashes.get(path) != actual:
            failures.append(f"Phase K production owner changed: {path} expected={expected_hashes.get(path)} actual={actual}")
    return failures


def fixtures(files: dict[str, str], blobs: dict[str, bytes]) -> list[str]:
    failures: list[str] = []
    mutations = (
        ("tuple inequality", "launch", ORDINARY, "-dev 2 -game diffusion -ref gl4es"),
        ("automatic selftest", "launch", f'@"{ORDINARY}"', f'@"{COMBINED}"'),
        ("Valve substitution", "launch", "-game diffusion", "-game valve"),
        ("editable field", "launch", "setEnabled:NO", "setEnabled:YES"),
        ("field authority removed", "launch", "setText:ordinaryBootstrapArgs", "setText:settingsArgs"),
        ("launcher order", "launcher", "IOS_LaunchDialog();", "/* IOS_LaunchDialog removed */"),
        ("host argv bypass", "launcher", "Host_Main( szArgc, szArgv", "Host_Main( argc, argv"),
        ("flag parser removed", "host", 'Sys_CheckParm( "-gl4es_texture_array_selftest" )', "false"),
        ("unconditional dispatch", "host", "if( host_ios_texture_array_selftest )\n\t{\n\t\tif( !Host_InitRendererContract( ))", "if( true )\n\t{\n\t\tif( !Host_InitRendererContract( ))"),
        ("harness removed", "context", "R_IOSTextureArraySelftest();", "/* harness removed */"),
        ("terminal removed", "client", 'Sys_Quit( "iOS texture array selftest complete" )', "return"),
        ("marker removed", "harness", "iOS texture array selftest terminal:", "terminal marker removed"),
        ("substring false positive", "verify", "grep -Fxq -- '-dev 2 -log -game diffusion -ref gl4es'", "grep -Fq -- '-dev 2 -log -game diffusion -ref gl4es'"),
        ("combined rejection weakened", "verify", f"grep -Fxq -- '{COMBINED}'", f"grep -Fq -- '{COMBINED}'"),
        ("argument fallback", "launch", "(void)ret;", "(void)ret;\n\tNSString *fallbackArgs = settings.launch;"),
    )
    for label, key, old, new in mutations:
        candidate = copy.deepcopy(files)
        if old not in candidate[key]:
            failures.append(f"fixture {label}: source token absent")
            continue
        candidate[key] = candidate[key].replace(old, new, 1)
        if not validate(candidate, blobs):
            failures.append(f"fixture {label}: validator accepted mutation")

    for path in sorted(blobs):
        candidate_blobs = dict(blobs)
        candidate_blobs[path] = blobs[path] + b"\nmutation"
        if not validate(files, candidate_blobs):
            failures.append(f"fixture production predicate change: validator accepted {path}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    files = {
        "contract": read(root / "scripts/ios/wo56m-ordinary-bootstrap-contract.json"),
        "launch": read(root / "engine/platform/ios/launchdialog.m"),
        "launcher": read(root / "engine/common/launcher.c"),
        "host": read(root / "engine/common/host.c"),
        "client": read(root / "engine/client/cl_main.c"),
        "loader": read(root / "engine/client/dll_int/ref_common.c"),
        "context": read(root / "ref/gl/gl_opengl.c"),
        "harness": read(root / "ref/gl/gl_texture_array_selftest.c"),
        "verify": read(root / "scripts/ios/verify_ipa.sh"),
        "build": read(root / "scripts/gha/build_ios.sh"),
    }
    locked_paths = json.loads(files["contract"]).get("lockedProductionSha256", {})
    blobs = {path: (root / path).read_bytes() for path in locked_paths}
    failures = validate(files, blobs)
    if args.self_test:
        failures += fixtures(files, blobs)
    if failures:
        print("ordinary-bootstrap validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("ordinary-bootstrap validation passed: exact locked tuple, dormant diagnostics, and rejection fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
