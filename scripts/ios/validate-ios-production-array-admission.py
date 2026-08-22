#!/usr/bin/env python3
"""Validate WO56K's conditional provider-to-terrain texture-array admission."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import subprocess
import sys


GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
DIFFUSION_REF = "14d156bf3a6993c172697fac83a937836c3b5561"
MIN_LAYERS = 16


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


def reject(text: str, pattern: str, label: str, failures: list[str]) -> None:
    if re.search(pattern, text, re.IGNORECASE):
        failures.append(f"{label}: forbidden pattern {pattern!r}")


def validate(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    try:
        contract = json.loads(files["contract"])
    except json.JSONDecodeError as exc:
        failures.append(f"production admission contract is invalid JSON: {exc}")
        contract = {}

    if contract.get("schema") != 1 or contract.get("workOrder") != "56K":
        failures.append("production admission contract identity changed")
    if contract.get("outcome") != "A" or contract.get("minimumLandscapeLayers") != MIN_LAYERS:
        failures.append("Outcome A or 16-layer contract changed")
    predicate = contract.get("capabilityPredicate", {})
    if predicate.get("allRequired") is not True or len(predicate.get("conditions", [])) != 8:
        failures.append("complete all-required capability predicate is missing")
    if len(contract.get("provenance", [])) != 7 or len(contract.get("gl4esOperations", [])) != 9:
        failures.append("end-to-end provenance or operation table is incomplete")
    stages = [row.get("stage") for row in contract.get("provenance", [])]
    if stages != [
        "native-provider", "gl4es-extension-provider", "engine-gate",
        "engine-loader-export", "diffusion-gate", "terrain-loader", "terrain-shader",
    ]:
        failures.append("provenance stage order changed")
    units = contract.get("terrainMaterialContract", {}).get("samplerUnits", {})
    if units != {
        "solidDiffuseArray": 0, "solidNormalArray": 4, "solidWeightArray": 5,
        "dlightDiffuseArray": 0, "dlightWeightArray": 5, "dlightNormalArray": 6,
    }:
        failures.append("terrain sampler-unit contract changed")
    if contract.get("ordinaryStartup", {}).get("terrainRuntimeQualification") != "not performed or claimed in Phase K":
        failures.append("Phase K claims unauthorized terrain runtime qualification")

    hardext = files["hardext"]
    getter = files["getter"]
    array = files["array"]
    for token in (
        "native_es_major>=3", 'gles_getProcAddress("glTexImage3D")',
        'gles_getProcAddress("glTexSubImage3D")', 'gles_getProcAddress("glTexStorage3D")',
        "GL_MAX_ARRAY_TEXTURE_LAYERS", "hardext.maxarraylayers >= 16",
        "hardext.glsl300es", "iOS production texture array provider:",
    ):
        require(hardext, token, "native provider predicate", failures)
    require(hardext, "if(native_es_major>=3 && texture_array_procs)",
            "native ES3 provider gate", failures)
    for token in (
        "hardext.texture_array && hardext.glsl300es", "hardext.maxarraylayers >= 16",
        "gl4es_texture_array_available()", 'strcat(extensions, "GL_EXT_texture_array ")',
    ):
        require(getter, token, "conditional GL4ES advertisement", failures)
    if getter.count('"GL_EXT_texture_array "') != 1:
        failures.append("GL_EXT_texture_array must have exactly one conditional provider")
    if not re.search(
        r"if\(hardext\.texture_array\s*&&\s*hardext\.glsl300es\s*&&\s*"
        r"hardext\.maxarraylayers\s*>=\s*16\s*&&\s*gl4es_texture_array_available\(\)\)",
        getter, re.DOTALL,
    ):
        failures.append("extension token is not dominated by the complete provider predicate")
    for token in (
        "native_teximage3d", "native_texsubimage3d", "native_texstorage3d",
        "glstate->actual_texarray", "GL_TEXTURE_2D_ARRAY", "GL_INVALID_OPERATION",
    ):
        require(array, token, "qualified GL4ES array implementation", failures)

    engine = files["engine"]
    engine_image = files["engine_image"]
    engine_export = files["engine_export"]
    for token in (
        "texturearrayfuncs", "glTexImage3D", "glTexSubImage3D",
        "glCompressedTexImage3DARB", "glCompressedTexSubImage3DARB",
        'GL_CheckExtension( "GL_EXT_texture_array", texturearrayfuncs',
        "GL_MAX_ARRAY_TEXTURE_LAYERS_EXT", "glConfig.max_2d_texture_layers < 16",
        "GL_SetExtension( GL_TEXTURE_ARRAY_EXT, false )",
        "iOS production texture array engine:",
    ):
        require(engine, token, "engine capability gate", failures)
    for token in (
        "GL_TEXTURE_ARRAY_EXT", "IMAGE_MULTILAYER", "GL_TEXTURE_2D_ARRAY_EXT",
        "GL_CreateTextureArray", "GL_LoadTextureArray",
        "pglCompressedTexImage3DARB", "pglCompressedTexSubImage3DARB",
    ):
        require(engine_image, token, "engine array target/loader", failures)
    require(engine_image, "tex->target = GL_TEXTURE_2D_ARRAY_EXT;",
            "engine multilayer target", failures)
    for token in ("GL_LoadTextureArray", "GL_CreateTextureArray"):
        require(engine_export, token, "engine render callback export", failures)

    diffusion_gl = files["diffusion_gl"]
    terrain = files["terrain"]
    shader = files["shader"]
    shader_sources = files["shader_sources"]
    for token in (
        'GL_CheckExtension( "GL_EXT_texture_array"',
        "#ifndef GL_MAX_ARRAY_TEXTURE_LAYERS_EXT",
        "#define GL_MAX_ARRAY_TEXTURE_LAYERS_EXT 0x88FF",
        "gRenderfuncs.GL_LoadTextureArray != NULL",
        "gRenderfuncs.GL_CreateTextureArray != NULL",
        "GL_MAX_ARRAY_TEXTURE_LAYERS_EXT", "MAX_LANDSCAPE_LAYERS",
        "GL_SetExtension( R_TEXTURE_ARRAY_EXT, false )",
        "iOS production texture array admission:",
    ):
        require(diffusion_gl, token, "Diffusion agreement gate", failures)
    require(diffusion_gl,
            "const bool callbacks = gRenderfuncs.GL_LoadTextureArray != NULL && gRenderfuncs.GL_CreateTextureArray != NULL;",
            "Diffusion callback agreement", failures)
    for token in (
        "if( !GL_Support( R_TEXTURE_ARRAY_EXT ))", "return tex != 0;",
        "LOAD_TEXTURE_ARRAY( (const char**)texnames, 0 )",
        "LOAD_TEXTURE_ARRAY( (const char **)normalmaps, TF_NORMALMAP )",
        "CREATE_TEXTURE_ARRAY( im->name", "terra->valid = LoadTerrainLayers",
        "FREE_TEXTURE( lm->gl_diffuse_id )", "FREE_TEXTURE( terra->indexmap.gl_heightmap_id )",
    ):
        require(terrain, token, "terrain loader/ownership", failures)
    for token in (
        "#define GLSL_ALLOW_TEXTURE_ARRAY", "terrainShader",
        "GL_AddTerrainShaderDirective", "TERRAIN_NUM_LAYERS",
        "BMODEL_MULTI_LAYERS", "BMODEL_BUMP", "BMODEL_SPECULAR", "BMODEL_EMBOSS",
        "u_ColorMap, GL_TEXTURE0", "u_NormalMap, GL_TEXTURE4",
        "u_LayerMap, GL_TEXTURE5", "u_NormalMap, GL_TEXTURE6",
    ):
        require(shader, token, "terrain shader/material admission", failures)
    if shader.count('out->Printf( "#define GLSL_ALLOW_TEXTURE_ARRAY 1\\n" );') != 2:
        failures.append("both Diffusion texture-array capability branches must emit GLSL_ALLOW_TEXTURE_ARRAY")
    if shader.count('GL_AddTerrainShaderDirective( options, "BMODEL_MULTI_LAYERS" )') != 2:
        failures.append("both solid and dlight terrain cache keys must retain BMODEL_MULTI_LAYERS")
    if shader.count("u_LayerMap, GL_TEXTURE5") != 2:
        failures.append("solid and dlight terrain weight samplers must both use texture unit 5")
    for token in ("sampler2DArray", "texture2DArray", "BMODEL_MULTI_LAYERS", "TERRAIN_NUM_LAYERS"):
        require(shader_sources, token, "pinned production terrain GLSL", failures)
    if not re.search(r"!terrainShader\s*&&.*MULTI_LAYERS.*EMBOSS.*SPECULAR.*BUMP", shader, re.DOTALL):
        failures.append("iOS filter does not preserve the full terrain feature family")

    for token in (
        "gl4es-wo56-production-array-admission-ios.patch",
        "diffusion-wo56-production-array-admission-ios.patch",
        "validate-ios-production-array-admission.py",
    ):
        require(files["build"], token, "pinned build replay", failures)
    for token in (
        "TEXTURE_ARRAY_JOBS", "GLSL_ALLOW_TEXTURE_ARRAY", "BMODEL_MULTI_LAYERS",
        "BMODEL_BUMP", "BMODEL_SPECULAR", "BMODEL_EMBOSS",
    ):
        require(files["shader_gate"], token, "full terrain shader gate", failures)
    for marker in contract.get("markers", []):
        require(files["verify"], marker, "IPA marker inspection", failures)
    require(
        files["verify"],
        "grep -q 'iOS production texture array engine:' \"$GL4ES_RENDERER_STRINGS\"",
        "engine gate marker owner",
        failures,
    )
    for token in (
        "cmake --build build --target install", "./scripts/ios/builddiffusion.sh",
        "client_arm64.dylib", "server_arm64.dylib", "menu_arm64.dylib",
        "Proprietary game asset is packaged in the IPA",
    ):
        require(files["build"] + files["verify"], token, "ordinary build/package contract", failures)
    require(files["launch"], 'ordinaryBootstrapArgs = @"-dev 2 -log -game diffusion -ref gl4es"',
            "locked ordinary bootstrap", failures)
    if "-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest" in files["launch"]:
        failures.append("ordinary bootstrap still automatically arms the selftest")

    phase_sources = files["provider_patch"] + files["diffusion_patch"] + engine
    reject(phase_sources, r"terrain[_ -]?(atlas|cpu)[_ -]?fallback", "fallback policy", failures)
    if re.search(r"GL_TEXTURE_2D(?!_ARRAY)", files["diffusion_patch"]):
        failures.append("Diffusion admission patch introduces an ordinary 2-D fallback")
    for token in ("force_texture_array", "texture_array_override", "-enable_terrain"):
        if token in phase_sources:
            failures.append(f"forbidden force-enable path introduced: {token}")
    return failures


def fixtures(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    mutations = (
        ("unconditional exposure", "getter", "if(hardext.texture_array && hardext.glsl300es &&", "if(1 &&"),
        ("unsupported context", "hardext", "if(native_es_major>=3 && texture_array_procs)", "if(native_es_major>=2 && texture_array_procs)"),
        ("missing image proc", "hardext", 'gles_getProcAddress("glTexImage3D")', "1"),
        ("missing subimage proc", "hardext", 'gles_getProcAddress("glTexSubImage3D")', "1"),
        ("missing storage proc", "hardext", 'gles_getProcAddress("glTexStorage3D")', "1"),
        ("zero-layer admission", "hardext", "hardext.maxarraylayers >= 16", "hardext.maxarraylayers >= 0"),
        ("engine limit disagreement", "engine", "glConfig.max_2d_texture_layers < 16", "glConfig.max_2d_texture_layers < 0"),
        ("absent callbacks accepted", "diffusion_gl", "const bool callbacks = gRenderfuncs.GL_LoadTextureArray != NULL && gRenderfuncs.GL_CreateTextureArray != NULL;", "const bool callbacks = true;"),
        ("wrong texture target", "engine_image", "tex->target = GL_TEXTURE_2D_ARRAY_EXT;", "tex->target = GL_TEXTURE_2D;"),
        ("lost GLSL allow", "shader", "#define GLSL_ALLOW_TEXTURE_ARRAY", "#define ARRAY_DISABLED"),
        ("stripped multi layers", "shader", 'GL_AddTerrainShaderDirective( options, "BMODEL_MULTI_LAYERS" )', 'GL_AddShaderDirective( options, "BMODEL_MULTI_LAYERS" )'),
        ("bypassed loader", "terrain", "terra->valid = LoadTerrainLayers", "terra->valid = true /* bypass */; LoadTerrainLayers"),
        ("missing diffuse array", "terrain", "LOAD_TEXTURE_ARRAY( (const char**)texnames, 0 )", "LOAD_TEXTURE( texnames[0], NULL, 0, 0 )"),
        ("missing normal array", "terrain", "LOAD_TEXTURE_ARRAY( (const char **)normalmaps, TF_NORMALMAP )", "LOAD_TEXTURE( normalmaps[0], NULL, 0, TF_NORMALMAP )"),
        ("sampler unit mismatch", "shader", "u_LayerMap, GL_TEXTURE5", "u_LayerMap, GL_TEXTURE4"),
        ("engine marker wrong binary", "verify", "grep -q 'iOS production texture array engine:' \"$GL4ES_RENDERER_STRINGS\"", "grep -q 'iOS production texture array engine:' \"$ENGINE_STRINGS\""),
        ("ordinary startup changed", "launch", "-dev 2 -log -game diffusion -ref gl4es", "-dev 2 -game diffusion -enable_terrain"),
    )
    for label, key, old, new in mutations:
        candidate = copy.deepcopy(files)
        if old not in candidate[key]:
            failures.append(f"fixture {label}: source token absent")
            continue
        candidate[key] = candidate[key].replace(old, new, 1)
        if not validate(candidate):
            failures.append(f"fixture {label}: validator accepted mutation")

    for label, payload in (
        ("atlas fallback", "terrain_atlas_fallback"),
        ("CPU fallback", "terrain_cpu_fallback"),
    ):
        candidate = copy.deepcopy(files)
        candidate["diffusion_patch"] += "\n" + payload
        if not validate(candidate):
            failures.append(f"fixture {label}: validator accepted mutation")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=pathlib.Path)
    parser.add_argument("gl4es", type=pathlib.Path)
    parser.add_argument("diffusion", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root, gl4es, diffusion = args.root.resolve(), args.gl4es.resolve(), args.diffusion.resolve()
    if revision(gl4es) != GL4ES_REF or revision(diffusion) != DIFFUSION_REF:
        print("production-array validation failed: wrong pinned source revision", file=sys.stderr)
        return 1
    files = {
        "contract": read(root / "scripts/ios/wo56k-production-array-admission-contract.json"),
        "provider_patch": read(root / "scripts/ios/gl4es-wo56-production-array-admission-ios.patch"),
        "diffusion_patch": read(root / "scripts/ios/diffusion-wo56-production-array-admission-ios.patch"),
        "hardext": read(gl4es / "src/glx/hardext.c"),
        "getter": read(gl4es / "src/gl/getter.c"),
        "array": read(gl4es / "src/gl/texture_array.c") + read(gl4es / "src/gl/texture_params.c"),
        "engine": read(root / "ref/gl/gl_opengl.c"),
        "engine_image": read(root / "ref/gl/gl_image.c"),
        "engine_export": read(root / "ref/gl/gl_context.c"),
        "diffusion_gl": read(diffusion / "client/render/r_opengl.cpp"),
        "terrain": read(diffusion / "client/render/r_misc.cpp"),
        "shader": read(diffusion / "client/render/r_shader.cpp"),
        "shader_sources": "\n".join(
            path.read_bytes().decode("latin-1")
            for path in sorted((diffusion / "glsl").iterdir()) if path.is_file()
        ),
        "shader_gate": read(root / "scripts/ios/validate-diffusion-mobile-shaders.py"),
        "build": read(root / "scripts/gha/build_ios.sh") + read(root / "scripts/ios/builddiffusion.sh"),
        "verify": read(root / "scripts/ios/verify_ipa.sh"),
        "launch": read(root / "engine/platform/ios/launchdialog.m"),
    }
    failures = validate(files)
    if args.self_test:
        failures += fixtures(files)
    if failures:
        print("production-array validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("production-array validation passed: conditional provider-to-terrain route and rejection fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
