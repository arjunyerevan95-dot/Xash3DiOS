#!/usr/bin/env python3
"""Validate WO56O's live-context GL4ES provider lifecycle and rejection gates."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import subprocess
import sys


GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
STAGES = [
    "context-create", "context-current", "renderer-entry", "provider-init",
    "native-discovery", "limit-discovery", "essl-discovery", "extension-build",
    "provider-marker", "engine-admission", "diffusion-admission", "teardown-reset",
]


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def revision(path: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}",
         "-C", str(path), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


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


def body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return ""


def validate(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    try:
        contract = json.loads(files["contract"])
    except json.JSONDecodeError as exc:
        return [f"provider lifecycle contract is invalid JSON: {exc}"]

    if (contract.get("schema"), contract.get("workOrder"), contract.get("outcome")) != (1, "56O", "A"):
        failures.append("provider lifecycle contract identity/outcome changed")
    if [row.get("stage") for row in contract.get("lifecycle", [])] != STAGES:
        failures.append("complete provider lifecycle table changed")
    if len(contract.get("allRequiredPredicate", [])) != 9:
        failures.append("complete all-required predicate changed")
    if len(contract.get("rejections", [])) < 14:
        failures.append("provider rejection set is incomplete")
    if contract.get("ordinaryArguments") != "-dev 2 -log -game diffusion -ref gl4es":
        failures.append("ordinary arguments changed")
    if contract.get("deviceQualification") != "not performed or claimed in Phase O":
        failures.append("Phase O claims unauthorized device qualification")

    hardext = files["hardext"]
    hardext_h = files["hardext_h"]
    public_h = files["public_h"]
    getter = files["getter"]
    init = files["init"]
    engine = files["engine"]
    sdl = files["sdl"]
    build = files["build"]

    ordered(sdl, ("SDL_GL_CreateContext", "SDL_GL_MakeCurrent"), "current-context ordering", failures)
    require(sdl, "glw_state.context = SDL_GL_CreateContext", "SDL context creation owner", failures)
    require(sdl, "if( SDL_GL_MakeCurrent", "SDL current-context success gate", failures)
    require(engine, "REF_GL_CONTEXT_MAJOR_VERSION, 3", "iOS ES3 request", failures)
    ordered(engine, (
        "set_getprocaddress( GL4ES_GetProcAddress )",
        "initialize_gl4es();",
        "R_IOSDirectDrawableContextCreated();",
    ), "post-current provider initialization", failures)
    ordered(init, (
        "int gl4es_notest = IsEnvVarTrue(\"LIBGL_NOTEST\")",
        "GetHardwareExtensions(gl4es_notest);",
        "gl_init();",
    ), "provider-before-wrapper-state ordering", failures)
    require(hardext, "if(tested) return;", "singleton discovery guard", failures)
    for token in (
        "const char *Version = (const char *) gles_glGetString(GL_VERSION)",
        'gles_getProcAddress("glTexImage3D")',
        'gles_getProcAddress("glTexSubImage3D")',
        'gles_getProcAddress("glTexStorage3D")',
        "gles_glGetIntegerv(GL_MAX_ARRAY_TEXTURE_LAYERS, &hardext.maxarraylayers)",
        "hardext.maxarraylayers >= 16",
        "static int testGLSL300ES(void)",
        '"#version 300 es\\n"',
        '"layout(location = 0) in vec4 vecPos;\\n"',
        "gles_glShaderSource(shad, 1, &shadTest, NULL)",
        "if(testGLSL300ES())",
    ):
        require(hardext, token, "source-proven provider correction", failures)
    if 'testGLSL("#version 300 es", 0)' in hardext:
        failures.append("malformed generic ESSL 300 probe remains active")
    if not re.search(r"hardext\.texture_array\s*=\s*hardext\.maxarraylayers\s*>=\s*16\s*;", hardext):
        failures.append("native provider accepts zero or insufficient array layers")
    if "#extension require GL_IMG_uniform_buffer_object" not in hardext:
        failures.append("audit discriminator for the rejected generic probe disappeared")

    for token in (
        "texture_array_native_es_major", "texture_array_procs", "texture_array_route",
    ):
        require(hardext_h + hardext, token, "cached provider state", failures)
    require(public_h, "gl4es_get_texture_array_provider_state", "read-only public snapshot", failures)
    snapshot = body(hardext, "void gl4es_get_texture_array_provider_state")
    for token in (
        "hardext.texture_array_native_es_major", "hardext.texture_array_procs",
        "hardext.maxarraylayers", "hardext.glsl300es", "hardext.texture_array_route",
    ):
        require(snapshot, token, "cached snapshot field", failures)
    if re.search(r"\b(gles_|gl4es_gl|glGet|gl4es_texture_array_available)\w*\s*\(", snapshot):
        failures.append("provider marker snapshot performs or drains GL work")

    ordered(getter, (
        "hardext.texture_array && hardext.glsl300es",
        "hardext.maxarraylayers >= 16",
        "gl4es_texture_array_available()",
        'strcat(extensions, "GL_EXT_texture_array ")',
    ), "conditional extension construction", failures)
    require(getter, "if(!glstate->extensions)", "extension cache construction guard", failures)
    ordered(engine, (
        "gl4es_get_texture_array_provider_state",
        "iOS production texture array provider:",
        'GL_CheckExtension( "GL_EXT_texture_array"',
        "GL_MAX_ARRAY_TEXTURE_LAYERS_EXT",
        "iOS production texture array engine:",
    ), "provider-to-engine reporting/admission", failures)
    if not re.search(r"if\(\s*glConfig\.max_2d_texture_layers\s*<\s*16\s*\)", engine):
        failures.append("engine array-layer minimum changed")
    require(engine, "source=live-context", "durable provider marker", failures)
    require(init, "gl4es_texture_array_reset();", "array route teardown", failures)
    require(init, "ResetHardwareExtensions();", "provider teardown", failures)
    require(files["glstate"], "free(state->extensions)", "extension cache teardown", failures)

    for token in (
        "gl4es-wo56-provider-lifecycle-ios.patch",
        "validate-ios-provider-lifecycle.py",
    ):
        require(build, token, "pinned build replay", failures)
    for token in (
        "iOS production texture array provider:",
        "iOS production texture array engine:",
        "iOS production texture array admission:",
    ):
        require(files["verify"], token, "IPA marker gate", failures)
    require(files["launch"], 'ordinaryBootstrapArgs = @"-dev 2 -log -game diffusion -ref gl4es"',
            "ordinary tuple", failures)
    if "-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest" in files["launch"]:
        failures.append("ordinary tuple automatically arms the diagnostic harness")

    combined = "\n".join(files.values())
    for pattern, label in (
        (r"hardext\.maxarraylayers\s*=\s*(16|2048)\s*;", "fabricated layer limit"),
        (r"texture_array_(force|override)|force_texture_array", "force path"),
        (r"terrain[_ -]?(atlas|cpu)[_ -]?fallback", "terrain fallback"),
    ):
        if re.search(pattern, combined, re.IGNORECASE):
            failures.append(f"forbidden {label} detected")
    return failures


def fixtures(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    mutations = (
        ("pre-current discovery", "sdl", "if( SDL_GL_MakeCurrent", "if( SDL_GL_NotCurrent"),
        ("generic malformed ESSL probe", "hardext", "if(testGLSL300ES())", 'if(testGLSL("#version 300 es", 0))'),
        ("forced ESSL", "hardext", "if(testGLSL300ES())\n            hardext.glsl300es = 1;", "hardext.glsl300es = 1;"),
        ("missing image proc", "hardext", 'gles_getProcAddress("glTexImage3D")', "1"),
        ("missing subimage proc", "hardext", 'gles_getProcAddress("glTexSubImage3D")', "1"),
        ("missing storage proc", "hardext", 'gles_getProcAddress("glTexStorage3D")', "1"),
        ("zero layer", "hardext", "hardext.texture_array = hardext.maxarraylayers >= 16;", "hardext.texture_array = hardext.maxarraylayers >= 0;"),
        ("route bypass", "getter", "gl4es_texture_array_available()", "1"),
        ("unconditional token", "getter", "if(hardext.texture_array && hardext.glsl300es &&", "if(1 &&"),
        ("snapshot GL mutation", "hardext", "if(native_es_major) *native_es_major", "glGetError(); if(native_es_major) *native_es_major"),
        ("provider reset lost", "init", "ResetHardwareExtensions();", "/* no provider reset */"),
        ("engine limit weakened", "engine", "glConfig.max_2d_texture_layers < 16", "glConfig.max_2d_texture_layers < 0"),
        ("ordinary selftest", "launch", "-dev 2 -log -game diffusion -ref gl4es", "-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest"),
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=pathlib.Path)
    parser.add_argument("gl4es", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root, gl4es = args.root.resolve(), args.gl4es.resolve()
    if revision(gl4es) != GL4ES_REF:
        print("provider-lifecycle validation failed: wrong pinned GL4ES revision", file=sys.stderr)
        return 1
    files = {
        "contract": read(root / "scripts/ios/wo56o-provider-lifecycle-contract.json"),
        "hardext": read(gl4es / "src/glx/hardext.c"),
        "hardext_h": read(gl4es / "src/glx/hardext.h"),
        "public_h": read(gl4es / "include/gl4esinit.h"),
        "getter": read(gl4es / "src/gl/getter.c"),
        "init": read(gl4es / "src/gl/init.c"),
        "glstate": read(gl4es / "src/gl/glstate.c"),
        "engine": read(root / "ref/gl/gl_opengl.c"),
        "sdl": read(root / "engine/platform/sdl2/vid_sdl2.c"),
        "build": read(root / "scripts/gha/build_ios.sh"),
        "verify": read(root / "scripts/ios/verify_ipa.sh"),
        "launch": read(root / "engine/platform/ios/launchdialog.m"),
    }
    failures = validate(files)
    if args.self_test:
        failures += fixtures(files)
    if failures:
        print("provider-lifecycle validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("provider-lifecycle validation passed: live ESSL 300 admission, cached marker, and rejection fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
