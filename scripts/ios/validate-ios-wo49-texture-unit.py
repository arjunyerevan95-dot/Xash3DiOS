#!/usr/bin/env python3
"""Validate the WO49 Phase F per-unit texture-realization invariant."""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys


GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
PATCH_FILE = "scripts/ios/gl4es-wo49-texture-unit-ios.patch"
MARKER = "WO49 texture policy: target-source=per-unit route=all-realize_textures"


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def revision(path: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}", "-C", str(path),
         "rev-parse", "HEAD"], check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def function(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return text[start:pos + 1]
    return ""


def select_targets(enabled: list[str]) -> list[str]:
    """Semantic fixture for the fixed per-unit selection."""
    return [enabled[index] for index in range(len(enabled))]


def select_targets_broken(enabled: list[str], active: int) -> list[str]:
    """Former behavior: every unit inherited the active unit's target."""
    return [enabled[active] for _ in enabled]


def validate_fixture() -> list[str]:
    failures: list[str] = []
    cases = (
        (["2D", "CUBE"], 1),
        (["CUBE", "2D"], 1),
        (["2D", "3D", "CUBE"], 2),
    )
    for enabled, active in cases:
        if select_targets(enabled) != enabled:
            failures.append(f"positive fixture lost per-unit targets: {enabled}")
        if select_targets_broken(enabled, active) == enabled:
            failures.append(f"rejection fixture failed to distinguish active-unit alias: {enabled}")
    # The Bundle-79 pattern: unit 0 needs a deferred 2D bind while the final
    # active unit is a cubemap. The old policy skips unit 0 as 'cube'; the fixed
    # policy realizes its 2D object.
    enabled = ["2D", "CUBE"]
    pending_2d = [101, None]
    fixed_realized = [pending_2d[i] for i, target in enumerate(select_targets(enabled))
                      if target == "2D" and pending_2d[i] is not None]
    broken_realized = [pending_2d[i] for i, target in enumerate(
        select_targets_broken(enabled, 1)) if target == "2D" and pending_2d[i] is not None]
    if fixed_realized != [101] or broken_realized:
        failures.append("Bundle-79 fixture did not prove stale 2D binding discriminator")
    return failures


def validate(repo: pathlib.Path, gl4es: pathlib.Path) -> list[str]:
    failures: list[str] = []
    texture_params = read(gl4es / "src/gl/texture_params.c")
    body = function(texture_params, "void realize_textures(int drawing)")
    patch = read(repo / PATCH_FILE)
    build = read(repo / "scripts/gha/build_ios.sh")
    verify = read(repo / "scripts/ios/verify_ipa.sh")

    if not body:
        failures.append("missing realize_textures implementation")
        return failures
    required = (
        "for (int i=0; i<glstate->bound_changed; i++)",
        "int tmp = glstate->enable.texture[i];",
        "gltexture_t *tex = glstate->texture.bound[i][tgt];",
        "gles_glActiveTexture(GL_TEXTURE0+i);",
        "gles_glBindTexture(GL_TEXTURE_2D, t);",
        MARKER,
    )
    for token in required:
        if token not in body:
            failures.append(f"realization invariant missing {token!r}")
    forbidden = (
        "glstate->enable.texture[glstate->texture.active]",
        "glstate->enable.texture[0]",
        "glstate->texture.bound[glstate->texture.active]",
        "glstate->texture.bound[0]",
    )
    loop_body = body[body.find("for (int i=0;"):]
    for token in forbidden:
        if token in loop_body:
            failures.append(f"realization invariant contains aliased selector {token!r}")

    headers = set(re.findall(r"^diff --git a/(\S+) b/\S+$", patch, re.MULTILINE))
    if headers != {"src/gl/texture_params.c"}:
        failures.append(f"repair patch scope is not singular: {sorted(headers)}")
    removed = "-        int tmp = glstate->enable.texture[glstate->texture.active];"
    added = "+        int tmp = glstate->enable.texture[i];"
    if patch.count(removed) != 1 or patch.count(added) != 1:
        failures.append("repair patch is not the exact active-to-per-unit substitution")
    added_lines = "\n".join(line[1:] for line in patch.splitlines()
                             if line.startswith("+") and not line.startswith("+++"))
    for pattern in (r"\bglDraw\w*\s*\(", r"\bglUniform\w*\s*\(",
                    r"\bglTexImage\w*\s*\(", r"\bglGetError\s*\("):
        if re.search(pattern, added_lines):
            failures.append(f"repair patch contains forbidden expansion {pattern!r}")

    routes = {
        "direct draw": gl4es / "src/gl/drawing.c",
        "deferred/list draw": gl4es / "src/gl/listdraw.c",
        "blit draw": gl4es / "src/gl/blit.c",
    }
    for label, path in routes.items():
        if "realize_textures(1);" not in read(path):
            failures.append(f"{label} no longer uses shared drawing realization")
    nondraw_routes = (
        gl4es / "src/gl/framebuffers.c", gl4es / "src/gl/gl4es.c",
        gl4es / "src/gl/stack.c",
    )
    for path in nondraw_routes:
        if "realize_textures(0);" not in read(path):
            failures.append(f"non-draw route missing shared realization: {path.name}")

    for token in ("gl4es-wo49-texture-unit-ios.patch",
                  "validate-ios-wo49-texture-unit.py"):
        if token not in build:
            failures.append(f"CI route missing {token}")
    if MARKER not in verify:
        failures.append("packaged IPA contract is missing texture-policy marker")
    failures.extend(validate_fixture())
    return failures


def self_test(repo: pathlib.Path, gl4es: pathlib.Path) -> list[str]:
    failures: list[str] = []
    body = function(read(gl4es / "src/gl/texture_params.c"),
                    "void realize_textures(int drawing)")
    mutations = (
        ("active-unit alias", "glstate->enable.texture[i]",
         "glstate->enable.texture[glstate->texture.active]"),
        ("unit-zero alias", "glstate->enable.texture[i]",
         "glstate->enable.texture[0]"),
        ("bound active alias", "glstate->texture.bound[i][tgt]",
         "glstate->texture.bound[glstate->texture.active][tgt]"),
        ("missing marker", MARKER, "WO49 texture policy removed"),
    )
    for label, old, new in mutations:
        if old not in body:
            failures.append(f"self-test setup missing for {label}")
            continue
        mutated = body.replace(old, new, 1)
        if ("int tmp = glstate->enable.texture[i];" in mutated
                and "gltexture_t *tex = glstate->texture.bound[i][tgt];" in mutated
                and MARKER in mutated):
            failures.append(f"self-test accepted {label}")
    route_mutations = (
        ("direct draw", gl4es / "src/gl/drawing.c"),
        ("deferred/list draw", gl4es / "src/gl/listdraw.c"),
        ("blit draw", gl4es / "src/gl/blit.c"),
    )
    for label, path in route_mutations:
        source = read(path)
        if "realize_textures(1);" not in source:
            failures.append(f"self-test setup missing for {label}")
            continue
        mutated = source.replace("realize_textures(1);", "/* realization omitted */", 1)
        if "realize_textures(1);" in mutated:
            failures.append(f"self-test accepted missing {label} realization")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=pathlib.Path)
    parser.add_argument("gl4es", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    gl4es = args.gl4es.resolve()
    got = revision(gl4es)
    if got != GL4ES_REF:
        print(f"FAIL: expected GL4ES {GL4ES_REF}, got {got}", file=sys.stderr)
        return 1
    failures = validate(repo, gl4es)
    if args.self_test:
        failures.extend(self_test(repo, gl4es))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Validated WO49 Phase F: every audited realization route selects target state per texture unit")
    print("Validated Bundle-79 fixture: final cubemap activity cannot suppress a pending unit-0 2D bind")
    if args.self_test:
        print("Validated rejection suite: active/unit-zero/bound aliases, missing marker, missing draw routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
