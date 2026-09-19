#!/usr/bin/env python3
"""Validate Work Order 51's consolidated Diffusion material-state invariant."""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass


DIFFUSION_REF = "14d156bf3a6993c172697fac83a937836c3b5561"
PATCH_FILE = "scripts/ios/diffusion-wo51-material-state-ios.patch"
MARKERS = (
    "iOS material-state policy:",
    "iOS studio texture cache epoch:",
    "iOS studio params exact count:",
    "iOS foliage uniform type:",
    "iOS material-state terminal:",
)


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def revision(path: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}", "-C", str(path),
         "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def function(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return text[start:pos + 1]
    return ""


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label} missing {token!r}")


@dataclass(frozen=True)
class MaterialIdentity:
    material: int
    mode: str
    base: int
    normal: int
    aux_mode: str
    aux: int
    cube_owner: int
    cube: int
    colormask: int


class MaterialCache:
    def __init__(self) -> None:
        self.invalidate()

    def invalidate(self) -> None:
        self.base: tuple[int, str, int] | None = None
        self.normal: int | None = None
        self.aux: tuple[int, str, int] | None = None
        self.cube: tuple[int, int] | None = None
        self.colormask: int | None = None

    def apply(self, item: MaterialIdentity) -> list[str]:
        binds: list[str] = []
        base = (item.material, item.mode, item.base)
        if self.base != base:
            self.base = base
            binds.append("base")
        if self.normal != item.normal:
            self.normal = item.normal
            binds.append("normal")
        aux = (item.material, item.aux_mode, item.aux)
        if self.aux != aux:
            self.aux = aux
            binds.append("aux")
        cube = (item.cube_owner, item.cube)
        if self.cube != cube:
            self.cube = cube
            binds.append("cube")
        if self.colormask != item.colormask:
            self.colormask = item.colormask
            binds.append("colormask")
        return binds


def validate_fixture() -> list[str]:
    failures: list[str] = []
    first = MaterialIdentity(7, "base", 70, 71, "interior", 72, 1, 73, 74)
    cache = MaterialCache()
    expected = ["base", "normal", "aux", "cube", "colormask"]
    if cache.apply(first) != expected:
        failures.append("positive fixture did not bind every material family after invalidation")
    if cache.apply(first):
        failures.append("positive fixture lost unchanged same-pass reuse")

    variants = (
        ("animated", 75),
        ("monitor", 76),
        ("drone", 77),
        ("fallback", 78),
        ("white", 79),
    )
    for mode, obj in variants:
        changed = MaterialIdentity(7, mode, obj, 71, "interior", 72, 1, 73, 74)
        if "base" not in cache.apply(changed):
            failures.append(f"positive fixture missed {mode} selected-object rebind")

    same_object_new_mode = MaterialIdentity(7, "monitor", 79, 71, "interior", 72, 1, 73, 74)
    if "base" not in cache.apply(same_object_new_mode):
        failures.append("positive fixture omitted material mode from the base key")
    aux_mode_change = MaterialIdentity(7, "monitor", 79, 71, "blend", 72, 1, 73, 74)
    if "aux" not in cache.apply(aux_mode_change):
        failures.append("positive fixture omitted interior/blend mode from the auxiliary key")
    cube_owner_change = MaterialIdentity(7, "monitor", 79, 71, "blend", 72, 2, 73, 74)
    if "cube" not in cache.apply(cube_owner_change):
        failures.append("positive fixture omitted cubemap owner identity")

    cache.invalidate()
    if cache.apply(cube_owner_change) != expected:
        failures.append("cleanup fixture did not force the next complete rebind")

    # Rejection discriminator for the old/incomplete material-only key.
    broken_key = (first.material,)
    animated_key = (first.material,)
    if broken_key != animated_key:
        failures.append("rejection fixture setup failed for incomplete base key")
    return failures


def validate_texts(texts: dict[str, str]) -> list[str]:
    failures: list[str] = []
    studio = texts["studio"]
    studio_h = texts["studio_h"]
    shader = texts["shader"]
    shader_h = texts["shader_h"]
    shader_patch = texts["shader_patch"]
    patch = texts["patch"]
    build = texts["build"]
    verify = texts["verify"]

    reset = function(studio, "void CStudioModelRenderer::ResetRenderCache( void )")
    solid = function(studio, "void CStudioModelRenderer::DrawStudioMeshes( void )")
    dlight = function(studio, "void CStudioModelRenderer::DrawLightForMeshList( plight_t *pl )")
    render_lights = function(studio, "void CStudioModelRenderer::RenderDynLightList( void )")
    shadow = function(studio, "void CStudioModelRenderer::DrawStudioMeshesShadow( void )")
    solid_shader = function(shader, "word GL_UberShaderForSolidStudio(")
    init_uniforms = function(shader, "static void GL_InitSolidStudioUniforms(")

    for label, body in (
        ("ResetRenderCache", reset), ("DrawStudioMeshes", solid),
        ("DrawLightForMeshList", dlight), ("RenderDynLightList", render_lights),
        ("DrawStudioMeshesShadow", shadow), ("GL_UberShaderForSolidStudio", solid_shader),
        ("GL_InitSolidStudioUniforms", init_uniforms),
    ):
        if not body:
            failures.append(f"missing {label} implementation")

    cache_fields = (
        "cached_texture_object = -1", "cached_texture_mode = STUDIO_TEXTURE_MODE_INVALID",
        "cached_normalmap = -1", "cached_aux_texture = -1",
        "cached_aux_mode = STUDIO_TEXTURE_MODE_INVALID", "cached_aux_material = -1",
        "cached_colormask = -1", "cached_cubemap_texture = -1",
    )
    for token in cache_fields:
        require(reset, token, "cache reset", failures)
        require(studio_h, token.split(" =", 1)[0], "cache declaration", failures)

    cleanup_pair = "GL_CleanUpTextureUnits( 0 );\n\tInvalidateStudioMaterialCache();"
    if studio.count(cleanup_pair) != 3:
        failures.append("all three authoritative studio cleanup routes must invalidate the material cache")
    for label, body in (("solid", solid), ("dynamic-light terminal", render_lights),
                        ("shadow", shadow)):
        require(body, cleanup_pair, label, failures)

    base_key = (
        "cached_texture != iTexnum || cached_texture_object != texture_object ||\n"
        "\t\t\tcached_texture_mode != texture_mode"
    )
    for label, body in (("solid", solid), ("dynamic light", dlight)):
        require(body, base_key, f"{label} actual-object/mode key", failures)
        for token in (
            "STUDIO_TEXTURE_MODE_BASE", "STUDIO_TEXTURE_MODE_WHITE",
            "STUDIO_TEXTURE_MODE_MONITOR", "STUDIO_TEXTURE_MODE_FALLBACK",
            "STUDIO_TEXTURE_MODE_ANIMATED", "STUDIO_TEXTURE_MODE_DRONE",
            "cached_normalmap", "cached_aux_texture", "cached_aux_mode",
            "cached_aux_material", "cached_colormask",
        ):
            require(body, token, f"{label} material family", failures)
        if "cached_texture == -1 || cached_texture != iTexnum" in body:
            failures.append(f"{label} restored the incomplete material-only cache key")
    for token in ("cached_cubemap_texture", "cached_cubemap != m_pModelInstance->cubemap",
                  "tr.blackCubeTexture"):
        require(solid, token, "solid cubemap identity", failures)

    for token in ("int studio_params_count;", "int studio_params_linked_count;"):
        require(shader_h, token, "shader metadata", failures)
    expected = (
        'shader->studio_params_count = GL_FindShaderDirective( shader, "STUDIO_ADDITIVE" ) ?\n'
        '\t\t( GL_FindShaderDirective( shader, "STUDIO_HAS_CHROME" ) ? 2 : 1 ) : 3;'
    )
    require(init_uniforms, expected, "linked variant extent", failures)
    require(init_uniforms,
            'GL_ActiveUniformExtent( shader, "u_StudioParams", GL_FLOAT_VEC4_ARB )',
            "linked uniform reflection", failures)
    require(solid_shader,
            "const int studio_params_count = additive ? ( has_chrome ? 2 : 1 ) : 3;",
            "producer variant extent", failures)
    require(solid_shader, "shader->studio_params_count != studio_params_count",
            "metadata mismatch rejection", failures)
    require(solid_shader, "shader->studio_params_linked_count != studio_params_count",
            "linked mismatch rejection", failures)
    require(solid, "RI->currentshader->studio_params_count, &studio_params[0][0]",
            "exact upload count", failures)
    if re.search(r"u_StudioParams\s*,\s*3\s*,", solid):
        failures.append("solid producer restored unconditional u_StudioParams count 3")

    require(shader_patch, "+uniform float", "foliage shader declaration", failures)
    if "pglUniform1iARB( RI->currentshader->u_FoliageSwayHeight" in studio:
        failures.append("solid foliage producer restored the integer upload API")
    for label, body in (("solid", solid), ("dynamic light", dlight), ("depth", shadow)):
        require(body, "pglUniform1fARB( RI->currentshader->u_FoliageSwayHeight",
                f"{label} foliage float upload", failures)

    for marker in MARKERS:
        if studio.count(marker) != 1:
            failures.append(f"bounded marker count is not one for {marker!r}")
        require(verify, marker, "IPA marker contract", failures)

    headers = set(re.findall(r"^diff --git a/(\S+) b/\S+$", patch, re.MULTILINE))
    expected_headers = {
        "client/render/r_shader.cpp", "client/render/r_shader.h",
        "client/render/r_studio.cpp", "client/render/r_studio.h",
    }
    if headers != expected_headers:
        failures.append(f"WO51 patch scope changed: {sorted(headers)}")
    added_lines = "\n".join(line[1:] for line in patch.splitlines()
                             if line.startswith("+") and not line.startswith("+++"))
    for token in ("sampler2DArray", "ESSL", "ConvertShader", "glTexImage3D",
                  "presentRenderbuffer", "glDrawElements"):
        if token in added_lines:
            failures.append(f"WO51 patch contains forbidden architecture expansion {token!r}")
    for token in ("u_StudioParams", "glUniform", "uniform.c", "src/gl/"):
        if token in patch and token == "src/gl/":
            failures.append("WO51 repair moved into GL4ES")

    for token in ("diffusion-wo51-material-state-ios.patch",
                  "validate-ios-material-state.py"):
        require(build, token, "build route", failures)
    failures.extend(validate_fixture())
    return failures


def load_texts(repo: pathlib.Path, diffusion: pathlib.Path) -> dict[str, str]:
    return {
        "studio": read(diffusion / "client/render/r_studio.cpp"),
        "studio_h": read(diffusion / "client/render/r_studio.h"),
        "shader": read(diffusion / "client/render/r_shader.cpp"),
        "shader_h": read(diffusion / "client/render/r_shader.h"),
        "shader_patch": read(repo / "scripts/ios/diffusion-shaders-ios.patch"),
        "patch": read(repo / PATCH_FILE),
        "build": read(repo / "scripts/ios/builddiffusion.sh"),
        "verify": read(repo / "scripts/ios/verify_ipa.sh"),
    }


def self_test(texts: dict[str, str]) -> list[str]:
    failures: list[str] = []
    mutations = (
        ("stale cleanup", "studio", "\tInvalidateStudioMaterialCache();",
         "\t/* cache left stale */"),
        ("incomplete object key", "studio", "cached_texture_object != texture_object",
         "cached_texture_object == cached_texture_object"),
        ("incomplete mode key", "studio", "cached_texture_mode != texture_mode",
         "cached_texture_mode == cached_texture_mode"),
        ("missing animated route", "studio", "STUDIO_TEXTURE_MODE_ANIMATED",
         "STUDIO_TEXTURE_MODE_BASE"),
        ("unconditional count 3", "studio",
         "RI->currentshader->studio_params_count, &studio_params[0][0]",
         "3, &studio_params[0][0]"),
        ("wrong additive no-chrome count", "shader",
         "( GL_FindShaderDirective( shader, \"STUDIO_HAS_CHROME\" ) ? 2 : 1 ) : 3",
         "( GL_FindShaderDirective( shader, \"STUDIO_HAS_CHROME\" ) ? 2 : 2 ) : 3"),
        ("wrong additive chrome count", "shader",
         "( GL_FindShaderDirective( shader, \"STUDIO_HAS_CHROME\" ) ? 2 : 1 ) : 3",
         "( GL_FindShaderDirective( shader, \"STUDIO_HAS_CHROME\" ) ? 3 : 1 ) : 3"),
        ("wrong non-additive count", "shader",
         "( GL_FindShaderDirective( shader, \"STUDIO_HAS_CHROME\" ) ? 2 : 1 ) : 3",
         "( GL_FindShaderDirective( shader, \"STUDIO_HAS_CHROME\" ) ? 2 : 1 ) : 2"),
        ("missing linked rejection", "shader",
         "shader->studio_params_linked_count != studio_params_count",
         "shader->studio_params_linked_count == studio_params_count"),
        ("integer foliage upload", "studio",
         "pglUniform1fARB( RI->currentshader->u_FoliageSwayHeight",
         "pglUniform1iARB( RI->currentshader->u_FoliageSwayHeight"),
        ("integer foliage declaration", "shader_patch", "+uniform float",
         "+uniform int"),
        ("GL4ES coercion expansion", "patch", "diff --git a/client/render/r_shader.cpp",
         "diff --git a/src/gl/uniform.c b/src/gl/uniform.c\n"
         "+/* u_StudioParams name-based truncation */\n"
         "diff --git a/client/render/r_shader.cpp"),
    )
    for label, key, old, new in mutations:
        if old not in texts[key]:
            failures.append(f"self-test setup missing for {label}")
            continue
        mutated = dict(texts)
        mutated[key] = texts[key].replace(old, new)
        if not validate_texts(mutated):
            failures.append(f"self-test accepted {label}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=pathlib.Path)
    parser.add_argument("diffusion", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    diffusion = args.diffusion.resolve()
    got = revision(diffusion)
    if got != DIFFUSION_REF:
        print(f"FAIL: expected Diffusion {DIFFUSION_REF}, got {got}", file=sys.stderr)
        return 1
    texts = load_texts(repo, diffusion)
    failures = validate_texts(texts)
    if args.self_test:
        failures.extend(self_test(texts))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Validated WO51 material state: cleanup epochs and actual object/mode keys cover every audited studio route")
    print("Validated WO51 studio params: producer metadata, linked vec4 extent, and upload counts agree at 1/2/3")
    print("Validated WO51 foliage: solid, dynamic-light, and depth producers match the float shader type")
    if args.self_test:
        print("Validated rejection suite: stale/incomplete keys, every wrong count, GL4ES coercion, and integer foliage fail")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
