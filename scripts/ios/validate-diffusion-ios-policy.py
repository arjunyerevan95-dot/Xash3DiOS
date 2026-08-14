#!/usr/bin/env python3
"""Reject per-model studio bone-count shader keys in the iOS Diffusion source."""

from __future__ import annotations

import pathlib
import re
import sys


EXPECTED_MARKER = (
    "iOS mobile renderer profile: canonical materials, "
    "shared animated-model shader layout, on-demand shaders"
)


def function_source(source: str, name: str, next_name: str) -> str:
    start = source.find(f"word {name}(")
    end = source.find(f"word {next_name}(", start + 1)
    if start < 0 or end < 0:
        raise ValueError(f"could not locate {name} source boundary")
    return source[start:end]


def ios_branch(function: str, name: str) -> str:
    match = re.search(r"#if XASH_IOS\s*(.*?)\s*#else", function, re.DOTALL)
    if not match:
        raise ValueError(f"could not locate the XASH_IOS branch in {name}")
    return match.group(1)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {pathlib.Path(sys.argv[0]).name} DIFFUSION_SOURCE_DIR", file=sys.stderr)
        return 2

    shader_path = pathlib.Path(sys.argv[1]) / "client" / "render" / "r_shader.cpp"
    source = shader_path.read_text(encoding="utf-8", errors="strict")
    failures: list[str] = []

    boundaries = (
        ("GL_UberShaderForSolidStudio", "GL_UberShaderForDlightStudio"),
        ("GL_UberShaderForDlightStudio", "GL_UberShaderForStudioDecal"),
    )
    for name, next_name in boundaries:
        try:
            branch = ios_branch(function_source(source, name, next_name), name)
        except ValueError as error:
            failures.append(str(error))
            continue

        if "if( numbones == 1 )" not in branch:
            failures.append(f"{name}: iOS branch does not preserve the one-bone rigid path")
        if branch.count('GL_AddShaderDefine( options, "#define MAXSTUDIOBONES 1\\n" );') != 1:
            failures.append(f"{name}: iOS branch must contain exactly one fixed one-bone define")
        forbidden = ("numbones > 0", "Q_min(", "MAXSTUDIOBONES %", "va(")
        for token in forbidden:
            if token in branch:
                failures.append(f"{name}: iOS branch contains forbidden per-model key token {token!r}")

    if EXPECTED_MARKER not in source:
        failures.append("shared animated-model renderer diagnostic marker is missing")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print("Diffusion iOS shader policy: shared animated-model key; one-bone rigid key retained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
