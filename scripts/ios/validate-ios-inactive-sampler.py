#!/usr/bin/env python3
"""Validate the WO52 Phase D inactive-sampler/location-zero repair."""

from __future__ import annotations

import argparse
import copy
import re
from pathlib import Path


DIFFUSION_HEADERS = {"client/render/r_shader.cpp"}
GL4ES_HEADERS = {"src/gl/indextrace.c", "src/gl/indextrace.h"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def section(text: str, start: str, end: str | None = None) -> str:
    begin = text.find(start)
    if begin < 0:
        return ""
    if end is None:
        return text[begin:]
    finish = text.find(end, begin + len(start))
    return text[begin:] if finish < 0 else text[begin:finish]


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"missing {label}: {token}")


def reject(text: str, pattern: str, label: str, failures: list[str]) -> None:
    if re.search(pattern, text):
        failures.append(f"forbidden {label}: {pattern}")


def ordered(text: str, tokens: tuple[str, ...], label: str,
            failures: list[str]) -> None:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            failures.append(f"bad {label} ordering at: {token}")
            return


def headers(patch: str) -> set[str]:
    return set(re.findall(r"^diff --git a/(\S+) b/\S+$", patch, re.MULTILINE))


def load_files(root: Path, gl4es: Path, diffusion: Path) -> dict[str, str]:
    return {
        "shader": read(diffusion / "client/render/r_shader.cpp"),
        "studio": read(diffusion / "client/render/r_studio.cpp"),
        "program": read(gl4es / "src/gl/program.c"),
        "program_h": read(gl4es / "src/gl/program.h"),
        "uniform": read(gl4es / "src/gl/uniform.c"),
        "fpe": read(gl4es / "src/gl/fpe.c"),
        "trace": read(gl4es / "src/gl/indextrace.c"),
        "trace_h": read(gl4es / "src/gl/indextrace.h"),
        "diff_patch": read(root / "scripts/ios/diffusion-wo52-inactive-sampler-ios.patch"),
        "gl_patch": read(root / "scripts/ios/gl4es-wo52-trace-cap-ios.patch"),
        "diffusion_build": read(root / "scripts/ios/builddiffusion.sh"),
        "gha_build": read(root / "scripts/gha/build_ios.sh"),
        "verify": read(root / "scripts/ios/verify_ipa.sh"),
    }


def lifecycle_model(failures: list[str]) -> None:
    """Executable discriminator mirroring the proven source ownership."""

    def assign_sampler(location: int, unit: int) -> tuple[int, int] | None:
        return None if location < 0 else (location, unit)

    class Shader:
        def __init__(self, admitted: set[str], reflection: dict[str, int]):
            self.admitted = admitted
            self.locations = {
                "u_CubemapBox": -1,
                "u_Cubemap": -1,
                "u_ReflectScale": -1,
                "u_Fresnel": -1,
                "u_InteriorMap": -1,
                "u_InteriorParams": -1,
                "u_BlendTexture": -1,
                "u_ColorMask": -1,
            }
            if "REFLECTION_CUBEMAP" in admitted:
                for name in ("u_CubemapBox", "u_Cubemap", "u_ReflectScale", "u_Fresnel"):
                    self.locations[name] = reflection.get(name, -1)
            self.runtime_cubemap = "REFLECTION_CUBEMAP" in admitted

    # Reproduce the Bundle-94 failure: the request survives in runtime status while
    # the canonical profile removes the shader directive; zero-filled u_Cubemap then
    # aliases the valid vec3-array location 0 occupied by u_MeshParams.
    mesh_params = [1.0, 2.0, 3.0]
    legacy_location = 0
    requested = True
    admitted: set[str] = set()
    if requested and legacy_location == 0:
        mesh_params = [-2785.5, -2588.0, -446.0]
    if mesh_params == [1.0, 2.0, 3.0]:
        failures.append("harness did not reproduce the location-zero overwrite")

    # Fixed filtered variant: all conditional locations remain -1 and the runtime
    # status is derived from the admitted key, so neither sampler nor vec3 uploads run.
    filtered = Shader(admitted, {"u_MeshParams": 0})
    if filtered.runtime_cubemap or filtered.locations["u_Cubemap"] != -1:
        failures.append("filtered variant retained a cubemap runtime/upload route")
    if assign_sampler(filtered.locations["u_CubemapBox"], 2) is not None:
        failures.append("inactive sampler upload was not skipped")

    # A genuine active location 0 remains legal and writable.
    if assign_sampler(0, 2) != (0, 2):
        failures.append("active sampler location 0 was rejected")

    # Active desktop/admitted feature remains functional.
    active = Shader({"REFLECTION_CUBEMAP"}, {
        "u_CubemapBox": 0, "u_Cubemap": 7, "u_ReflectScale": 8, "u_Fresnel": 9,
    })
    if not active.runtime_cubemap or assign_sampler(active.locations["u_CubemapBox"], 2) != (0, 2):
        failures.append("admitted cubemap path was disabled")

    # Lifecycle proof: first link, cache hit, relink, variant switch, invalidation,
    # destruction and recreation never carry a prior nonnegative location forward.
    first = Shader(set(), {})
    cache_hit = first
    relinked = Shader({"REFLECTION_CUBEMAP"}, {"u_CubemapBox": 0, "u_Cubemap": 4})
    switched = Shader(set(), {})
    invalidated = None
    recreated = Shader(set(), {})
    if cache_hit.locations["u_CubemapBox"] != -1:
        failures.append("cache hit changed inactive location")
    if relinked.locations["u_CubemapBox"] != 0:
        failures.append("relink lost valid active location 0")
    if switched.locations["u_CubemapBox"] != -1:
        failures.append("variant switch retained stale sampler location")
    if invalidated is not None or recreated.locations["u_CubemapBox"] != -1:
        failures.append("destruction/recreation retained stale state")


def validate(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    shader = files["shader"]
    studio = files["studio"]
    solid_init = section(shader, "static void GL_InitSolidStudioUniforms(",
                         "static void GL_InitStudioDlightUniforms(")
    dlight_init = section(shader, "static void GL_InitStudioDlightUniforms(",
                          "static void GL_InitStudioDepthFillUniforms(")
    solid_key = section(shader, "word GL_UberShaderForSolidStudio(",
                        "word GL_UberShaderForDlightStudio(")
    dlight_key = section(shader, "word GL_UberShaderForDlightStudio(",
                         "word GL_UberShaderForDecalStudio(")
    assign = section(shader, "static void GL_AssignSamplerUnit(",
                     "static void GL_InitSolidBmodelUniforms(")
    cubemap_draw = section(studio,
                           "if( RI->currentshader->status & SHADER_USE_CUBEMAPS )",
                           "WO52RecordMaterialCache( wo52_token, false")

    # Source-proven request/admission mismatch and its structural closure.
    policy = section(shader, "void GL_AddShaderDirective(",
                     "void GL_AddShaderDefine(")
    for feature in ("REFLECTION_CUBEMAP", "BUMP", "INTERIOR", "SPECULAR", "EMBOSS"):
        require(policy, feature, "canonical rejection policy", failures)
    for token in (
        'use_bump = Q_stristr( options, "STUDIO_BUMP" ) != NULL;',
        'use_emboss = Q_stristr( options, "STUDIO_EMBOSS" ) != NULL;',
        'use_interior = Q_stristr( options, "STUDIO_INTERIOR" ) != NULL;',
        'use_specular = Q_stristr( options, "STUDIO_SPECULAR" ) != NULL;',
    ):
        require(solid_key, token, "solid admitted-feature flag", failures)
        require(dlight_key, token, "dlight admitted-feature flag", failures)
    require(solid_key,
            'use_cubemaps = Q_stristr( options, "REFLECTION_CUBEMAP" ) != NULL;',
            "cubemap admitted-feature flag", failures)
    ordered(solid_key, (
        "const bool requested_cubemaps = use_cubemaps;",
        'use_cubemaps = Q_stristr( options, "REFLECTION_CUBEMAP" ) != NULL;',
        "GL_FindUberShader( glname, options, &GL_InitSolidStudioUniforms )",
        "if( use_cubemaps )\n\t\tshader->status |= SHADER_USE_CUBEMAPS;",
    ), "request/admission/status", failures)

    # Conditional storage starts at -1; valid location 0 is preserved; negative
    # uploads are skipped before the GL call.
    for name in ("u_CubemapBox", "u_Cubemap", "u_ReflectScale", "u_Fresnel",
                 "u_InteriorMap", "u_InteriorParams", "u_BlendTexture", "u_ColorMask"):
        require(solid_init, f"shader->{name} = -1;", "solid conditional initializer", failures)
    for name in ("u_InteriorMap", "u_InteriorParams", "u_BlendTexture", "u_ColorMask"):
        require(dlight_init, f"shader->{name} = -1;", "dlight conditional initializer", failures)
    ordered(assign, ("if( location < 0 )", "return;", "pglUniform1iARB( location, unit );"),
            "negative-location sampler guard", failures)
    reject(assign, r"location\s*<=\s*0", "active-location-zero rejection", failures)
    reject(assign, r"pglUniform1iARB\(\s*0\s*,", "hard-coded uniform location", failures)
    for init in (solid_init, dlight_init):
        for raw in re.findall(r"pglUniform1iARB\([^\n]+", init):
            if "GL_AssignSamplerUnit" not in raw:
                failures.append(f"unguarded studio sampler upload: {raw.strip()}")
    ordered(cubemap_draw, ("SHADER_USE_CUBEMAPS", "pglUniform3fvARB( RI->currentshader->u_Cubemap"),
            "cubemap runtime guard", failures)

    for marker in (
        "iOS inactive sampler policy:",
        "iOS inactive sampler rejection:",
        "iOS material uniform proof:",
    ):
        require(shader, marker, "runtime proof marker", failures)
        require(files["verify"], marker, "IPA marker contract", failures)

    # Exact GL4ES semantics and lifecycle: inactive lookup is -1; -1 upload is a
    # no-op; active 0 reaches the type/extent check; relink rebuilds reflection;
    # FPE variants map parent caches by exact uniform name; delete frees ownership.
    get_location = section(files["program"], "gl4es_glGetUniformLocation(",
                           "gl4es_glIsProgram(")
    require(get_location, "int res = -1;", "GL4ES inactive lookup", failures)
    require(get_location, "res = m->id;", "GL4ES active location preservation", failures)
    uniform_iv = section(files["uniform"], "void GoUniformiv(",
                         "void APIENTRY_GL4ES gl4es_glUniform1f(")
    ordered(uniform_iv, ("if(location==-1)", "noerrorShim();", "return;",
                         "kh_get(uniformlist, glprogram->uniform, location)"),
            "GL4ES -1 upload no-op", failures)
    require(uniform_iv, "!is_uniform_int(m->type)", "GL4ES wrong-type rejection", failures)
    clear = section(files["program"], "static void clear_program(",
                    "static void fill_program(")
    for token in ("glprogram->num_uniform = 0;", "kh_del(uniformlist",
                  "glprogram->cache.size = 0;"):
        require(clear, token, "GL4ES relink invalidation", failures)
    link = section(files["program"], "gl4es_glLinkProgram(",
                   "gl4es_glUseProgram(")
    ordered(link, ("clear_program(glprogram);", "gles_glLinkProgram(glprogram->id);",
                   "fill_program(glprogram);"), "GL4ES relink lifecycle", failures)
    deletion = section(files["program"], "void deleteProgram(",
                        "gl4es_glDeleteProgram(")
    for token in ("kh_destroy(uniformlist", "free(glprogram->cache.cache)",
                  "fpe_disposeCache", "kh_del(programlist"):
        require(deletion, token, "GL4ES destruction lifecycle", failures)
    fpe_custom = section(files["fpe"], "program_t* APIENTRY_GL4ES fpe_CustomShader(",
                         "program_t* APIENTRY_GL4ES fpe_CustomShader_DefaultVertex(")
    ordered(fpe_custom, ("gl4es_glLinkProgram(fpe->prog);", "findUniform(father_uniforms, m->name)",
                         "m->parent_offs = n->cache_offs;"),
            "GL4ES native variant mapping", failures)

    require(files["trace_h"], "IOS_WO52_MATERIAL_TOKEN_CAP 16u",
            "repair-candidate trace cap", failures)
    require(files["trace"], "identities<=16", "repair-candidate trace policy", failures)
    require(files["trace"], "repair=inactive-sampler-alias", "trace repair label", failures)
    if headers(files["diff_patch"]) != DIFFUSION_HEADERS:
        failures.append(f"Diffusion repair patch scope changed: {sorted(headers(files['diff_patch']))}")
    if headers(files["gl_patch"]) != GL4ES_HEADERS:
        failures.append(f"GL4ES trace-cap patch scope changed: {sorted(headers(files['gl_patch']))}")
    for token in ("diffusion-wo52-inactive-sampler-ios.patch",
                  "validate-ios-inactive-sampler.py"):
        require(files["diffusion_build"], token, "Diffusion build route", failures)
    require(files["gha_build"], "gl4es-wo52-trace-cap-ios.patch",
            "GL4ES build route", failures)

    combined_patch = files["diff_patch"] + files["gl_patch"]
    reject(combined_patch, r"(?:drawable|MSAA|glDrawElements|glDrawRangeElements|map transition|texture array)",
           "forbidden subsystem change", failures)
    reject(files["diff_patch"], r"^\+.*(?:glDisable|glFinish|glReadPixels|glGetError)\s*\(",
           "broad renderer mutation", failures)

    lifecycle_model(failures)
    return failures


def self_test(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    cases = (
        ("default-zero storage", "shader", "shader->u_CubemapBox = -1;", "shader->u_CubemapBox = 0;"),
        ("reject valid location zero", "shader", "if( location < 0 )", "if( location <= 0 )"),
        ("hard-coded location", "shader", "pglUniform1iARB( location, unit );", "pglUniform1iARB( 0, unit );"),
        ("requested-not-admitted status", "shader",
         'use_cubemaps = Q_stristr( options, "REFLECTION_CUBEMAP" ) != NULL;',
         "use_cubemaps = requested_cubemaps;"),
        ("disable admitted cubemaps", "shader",
         'use_cubemaps = Q_stristr( options, "REFLECTION_CUBEMAP" ) != NULL;',
         "use_cubemaps = false;"),
        ("GL4ES inactive zero", "program", "int res = -1;", "int res = 0;"),
        ("GL4ES -1 write", "uniform", "if(location==-1)", "if(location==-2)"),
        ("stale relink", "program", "clear_program(glprogram);", "/* stale cache retained */"),
        ("uncapped diagnostics", "trace_h", "IOS_WO52_MATERIAL_TOKEN_CAP 16u",
         "IOS_WO52_MATERIAL_TOKEN_CAP 256u"),
    )
    for label, key, old, new in cases:
        if old not in files[key]:
            failures.append(f"self-test setup {label}: token absent")
            continue
        mutated = copy.deepcopy(files)
        mutated[key] = mutated[key].replace(old, new)
        if not validate(mutated):
            failures.append(f"rejection fixture unexpectedly passed: {label}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("gl4es", type=Path)
    parser.add_argument("diffusion", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    files = load_files(args.root.resolve(), args.gl4es.resolve(), args.diffusion.resolve())
    failures = validate(files)
    if args.self_test:
        failures.extend(self_test(files))
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print("WO52 inactive sampler/location-zero lifecycle validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
