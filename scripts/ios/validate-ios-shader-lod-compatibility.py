#!/usr/bin/env python3
"""Validate WO56P shader-LOD integration, outputs, and rejection gates."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys


GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
PATCH_PATH = "scripts/ios/gl4es-wo56-shader-lod-compatibility-ios.patch"
PATCH_BYTES = 10564
PATCH_SHA256 = "91AB64B6C392303BEA189BE2D66E409836489DFC6F46F2FC3DFB0BACCFA60FE4"
UPSTREAM_PATHS = ["src/gl/shader.c", "src/gl/shader.h", "src/gl/shaderconv.c"]
FAMILIES = ["BmodelSolid", "StudioSolid", "GrassDlight"]


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def revision(path: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}",
         "-C", str(path), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


def reject(text: str, pattern: str, label: str, failures: list[str]) -> None:
    if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
        failures.append(f"{label}: forbidden pattern {pattern!r}")


def ordered(text: str, tokens: tuple[str, ...], label: str, failures: list[str]) -> None:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            failures.append(f"{label}: missing or out of order {token!r}")
            return


def validate(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    try:
        contract = json.loads(files["contract"])
    except json.JSONDecodeError as exc:
        return [f"shader-LOD contract is invalid JSON: {exc}"]

    if (contract.get("schema"), contract.get("workOrder"), contract.get("checkpoint")) != (
        1, "56P", "production-integration-build-qualification"
    ):
        failures.append("shader-LOD contract identity changed")
    if contract.get("acceptedImplementationCommit") != "d37bf36a5b707273359728a5ae08f81e712bea5d":
        failures.append("accepted implementation commit changed")
    if contract.get("gl4esPin") != GL4ES_REF:
        failures.append("GL4ES pin changed")

    patch_contract = contract.get("patch", {})
    if (
        patch_contract.get("path") != PATCH_PATH
        or patch_contract.get("bytes") != PATCH_BYTES
        or patch_contract.get("sha256") != PATCH_SHA256
        or patch_contract.get("applyAfter") != "scripts/ios/gl4es-wo56-provider-lifecycle-ios.patch"
        or patch_contract.get("upstreamPaths") != UPSTREAM_PATHS
    ):
        failures.append("accepted patch identity, order, or upstream scope changed")
    fixtures = contract.get("representativeFixtures", [])
    if [row.get("family") for row in fixtures] != FAMILIES:
        failures.append("representative family set or order changed")
    if [row.get("coreLodCount") for row in fixtures] != [11, 11, 9]:
        failures.append("representative core-LOD counts changed")
    if len(contract.get("rejections", [])) < 12:
        failures.append("shader-LOD rejection set is incomplete")
    if len(contract.get("crossStageOwner", [])) != 6:
        failures.append("cross-stage owner set is incomplete")

    patch_bytes = files["patch"].encode("utf-8")
    if len(patch_bytes) != PATCH_BYTES:
        failures.append(f"patch byte count changed: {len(patch_bytes)}")
    if digest_bytes(patch_bytes).upper() != PATCH_SHA256:
        failures.append("patch SHA-256 changed")
    patch_paths = re.findall(r"^diff --git a/(\S+) b/(\S+)$", files["patch"], re.MULTILINE)
    if patch_paths != [(path, path) for path in UPSTREAM_PATHS]:
        failures.append(f"patch upstream path set/order changed: {patch_paths}")

    build = files["build"]
    ordered(build, (
        "gl4es-wo56-provider-lifecycle-ios.patch",
        "gl4es-wo56-shader-lod-compatibility-ios.patch",
        "validate-ios-shader-lod-compatibility.py",
    ), "canonical production patch/validator order", failures)
    for token in (
        'apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo56-shader-lod-compatibility-ios.patch"',
        'apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo56-shader-lod-compatibility-ios.patch"',
        'validate-ios-shader-lod-compatibility.py',
        '--self-test',
    ):
        require(build, token, "production integration", failures)

    for token in (
        PATCH_PATH,
        "scripts/ios/validate-ios-shader-lod-compatibility.py",
        "scripts/ios/wo56p-shader-lod-compatibility-contract.json",
    ):
        require(files["renderer"], token, "renderer retained surface", failures)
        require(files["selftest"], token, "self-test retained surface", failures)
    require(files["mobile_shell"], "validate-ios-shader-lod-compatibility.py",
            "representative output gate", failures)
    require(files["mobile_shell"], '--converter "$WORK_DIR/gl4es-shaderconv-dump"',
            "converter binding", failures)
    require(files["verify"], "validate-ios-shader-lod-compatibility.py",
            "IPA qualification surface", failures)

    shader_h = files["shader_h"]
    shader_c = files["shader_c"]
    shaderconv = files["shaderconv"]
    require(shader_h, "int         need_essl300;", "cross-stage need field", failures)
    require(shader_c, "GO(essl300)", "cross-stage need accumulation", failures)
    for token in (
        "int explicit_lod_shader =",
        "hardext.glsl300es && (explicit_lod_shader || need->need_essl300)",
        "need->need_essl300 = 1;",
        "if(!isVertex && !essl300_shader && hardext.shaderlod && explicit_lod_shader)",
        '"texture2DLod", "textureLod"',
        '"texture2DProjLod", "textureProjLod"',
        '"textureCubeLod", "textureLod"',
        '"texture2DLod", "texture2DLodEXT"',
    ):
        require(shaderconv, token, "shared converter owner", failures)

    added = "\n".join(
        line[1:] for line in files["patch"].splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    reject(added, r'hardext\.(?:glsl300es|shaderlod)\s*=\s*1',
           "fabricated capability", failures)
    reject(added, r'"texture(?:2D|Cube)Lod"\s*,\s*"texture(?:2D|Cube)"',
           "implicit sampling", failures)
    reject(added, r'textureLod\s*\([^\n]*,\s*0(?:\.0)?\s*\)',
           "constant LOD", failures)
    reject(added, r'GL_(?:LINK|COMPILE)_STATUS|unlinked|uncompiled',
           "uncompiled/unlinked acceptance", failures)
    reject(added, r'noerrorShim|glGetError|errorGL|suppress',
           "error suppression", failures)
    return failures


def fixtures(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    mutations = (
        ("omitted patch", "build", "gl4es-wo56-shader-lod-compatibility-ios.patch", "omitted.patch"),
        ("reordered patch", "build", "gl4es-wo56-provider-lifecycle-ios.patch", "provider-after-shader.patch"),
        ("cross-stage propagation", "shader_c", "GO(essl300)", "/* missing ESSL 300 propagation */"),
        ("ESSL 300 EXT directive", "shaderconv", "!essl300_shader && hardext.shaderlod", "hardext.shaderlod"),
        ("ESSL 300 EXT intrinsic", "shaderconv", '"texture2DLod", "textureLod"', '"texture2DLod", "texture2DLodEXT"'),
        ("implicit sampling", "patch", '"texture2DLod", "textureLod"', '"texture2DLod", "texture2D"'),
        ("fabricated capability", "patch", "int explicit_lod_shader =", "hardext.glsl300es = 1;\n  int explicit_lod_shader ="),
        ("source-order corruption", "build", "validate-ios-shader-lod-compatibility.py", "validator-before-patch.py"),
        ("unlinked acceptance", "patch", "int explicit_lod_shader =", "GL_LINK_STATUS;\n  int explicit_lod_shader ="),
        ("error suppression", "patch", "int explicit_lod_shader =", "noerrorShim();\n  int explicit_lod_shader ="),
    )
    for label, key, old, new in mutations:
        candidate = copy.deepcopy(files)
        if old not in candidate[key]:
            failures.append(f"fixture {label}: source token absent")
            continue
        candidate[key] = candidate[key].replace(old, new)
        if not validate(candidate):
            failures.append(f"fixture {label}: validator accepted mutation")

    candidate = copy.deepcopy(files)
    contract = json.loads(candidate["contract"])
    contract["representativeFixtures"] = contract["representativeFixtures"][:-1]
    candidate["contract"] = json.dumps(contract)
    if not validate(candidate):
        failures.append("fixture missing family: validator accepted mutation")
    return failures


def load_shader_builder(root: pathlib.Path):
    path = root / "scripts/ios/validate-diffusion-mobile-shaders.py"
    spec = importlib.util.spec_from_file_location("wo56p_mobile_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Diffusion shader source builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_converter(converter: pathlib.Path, stage: str, source: str, mode: str | None = None):
    command = [str(converter), stage]
    if mode:
        command.append(mode)
    return subprocess.run(
        command, input=source.encode("latin-1"), capture_output=True, check=True,
    )


def validate_outputs(
    root: pathlib.Path, diffusion: pathlib.Path, converter: pathlib.Path, contract_text: str
) -> list[str]:
    failures: list[str] = []
    contract = json.loads(contract_text)
    builder = load_shader_builder(root)
    shader_dir = diffusion / "glsl"
    for fixture in contract["representativeFixtures"]:
        for stage, key in (("vertex", "vertex"), ("fragment", "fragment")):
            source = builder.build_source(shader_dir, fixture[key], fixture["defines"])
            expected_source = fixture[f"source{stage.title()}Sha256"]
            if digest_bytes(source.encode("latin-1")) != expected_source:
                failures.append(f"{fixture['family']} {stage}: assembled source fingerprint changed")
                continue
            initial = run_converter(converter, stage, source)
            output = initial.stdout.decode("latin-1")
            if stage == "fragment":
                if not output.startswith("#version 300 es"):
                    failures.append(f"{fixture['family']} fragment: not ESSL 300")
                if output.count("GL_EXT_shader_texture_lod") or output.count("texture2DLodEXT"):
                    failures.append(f"{fixture['family']} fragment: rejected EXT path returned")
                if output.count("textureLod") != fixture["coreLodCount"]:
                    failures.append(f"{fixture['family']} fragment: core LOD count changed")
                if digest_bytes(initial.stdout) != fixture["fragmentOutputSha256"]:
                    failures.append(f"{fixture['family']} fragment: output fingerprint changed")
            else:
                if not output.startswith("#version 100"):
                    failures.append(f"{fixture['family']} vertex: initial conversion is not ESSL 100")
                forced = run_converter(converter, stage, source, "force300")
                reconverted = forced.stdout.decode("latin-1")
                if not reconverted.startswith("#version 300 es"):
                    failures.append(f"{fixture['family']} vertex: reconversion is not ESSL 300")
                if "#define attribute in" not in reconverted or "#define varying out" not in reconverted:
                    failures.append(f"{fixture['family']} vertex: stage mapping changed")
                if b"need_essl300=1" not in forced.stderr:
                    failures.append(f"{fixture['family']} vertex: program need did not propagate")
                if digest_bytes(forced.stdout) != fixture["reconvertedVertexSha256"]:
                    failures.append(f"{fixture['family']} vertex: reconverted fingerprint changed")

    legacy_source = (
        "#version 130\n"
        "uniform sampler2D tex;\n"
        "void main() { gl_FragColor = texture2DLod(tex, vec2(0.25), 1.0); }\n"
    )
    legacy = run_converter(converter, "fragment", legacy_source, "legacy").stdout.decode("latin-1")
    if not legacy.startswith("#version 100"):
        failures.append("legacy control: ESSL 100 changed")
    if legacy.count("GL_EXT_shader_texture_lod") != 1 or legacy.count("texture2DLodEXT") != 1:
        failures.append("legacy control: extension directive/intrinsic changed")
    if "textureLod(" in legacy:
        failures.append("legacy control: incorrectly promoted to core textureLod")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=pathlib.Path)
    parser.add_argument("gl4es", type=pathlib.Path)
    parser.add_argument("diffusion", type=pathlib.Path, nargs="?")
    parser.add_argument("--converter", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root, gl4es = args.root.resolve(), args.gl4es.resolve()
    if revision(gl4es) != GL4ES_REF:
        print("shader-LOD validation failed: wrong pinned GL4ES revision", file=sys.stderr)
        return 1
    files = {
        "contract": read(root / "scripts/ios/wo56p-shader-lod-compatibility-contract.json"),
        "patch": read(root / PATCH_PATH),
        "build": read(root / "scripts/gha/build_ios.sh"),
        "renderer": read(root / "scripts/ios/validate-ios-renderer-contract.py"),
        "selftest": read(root / "scripts/ios/validate-ios-selftest-boot.py"),
        "mobile_shell": read(root / "scripts/ios/validate-diffusion-mobile-shaders.sh"),
        "verify": read(root / "scripts/ios/verify_ipa.sh"),
        "shader_c": read(gl4es / "src/gl/shader.c"),
        "shader_h": read(gl4es / "src/gl/shader.h"),
        "shaderconv": read(gl4es / "src/gl/shaderconv.c"),
    }
    failures = validate(files)
    if args.self_test:
        failures += fixtures(files)
    if args.converter:
        if args.diffusion is None:
            failures.append("converter output validation requires a Diffusion source path")
        else:
            failures += validate_outputs(root, args.diffusion.resolve(), args.converter.resolve(), files["contract"])
    if failures:
        print("shader-LOD validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    output_suffix = " plus representative output fingerprints" if args.converter else ""
    print("shader-LOD validation passed: integration, contract, rejection fixtures" + output_suffix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
