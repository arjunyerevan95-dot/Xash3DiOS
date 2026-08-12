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
    grass_source = (pathlib.Path(sys.argv[1]) / "client" / "render" / "r_grass.cpp").read_text(
        encoding="utf-8", errors="strict"
    )
    world_source = (pathlib.Path(sys.argv[1]) / "client" / "render" / "r_world.cpp").read_text(
        encoding="utf-8", errors="strict"
    )
    main_source = (pathlib.Path(sys.argv[1]) / "client" / "render" / "r_main.cpp").read_text(
        encoding="utf-8", errors="strict"
    )
    backend_source = (pathlib.Path(sys.argv[1]) / "client" / "render" / "r_backend.cpp").read_text(
        encoding="utf-8", errors="strict"
    )
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

    required_liveness_tokens = {
        "r_grass.cpp": (
            "iOS foliage liveness policy: bounded_lines=%d sample_stride=%d",
            "stage=construct-begin",
            "stage=sample-progress",
            "stage=construct-end",
            "stage=dispatch-end",
            "#define IOS_GRASS_TRACE_LIMIT 128",
        ),
        "r_world.cpp": (
            "iOS world traversal:",
            "before-visible-surfaces",
            "after-visible-surfaces",
            "before-brush-list",
            "after-brush-list",
            "ios_normal_world && ios_world_draw <= 12",
        ),
    }
    for filename, tokens in required_liveness_tokens.items():
        liveness_source = grass_source if filename == "r_grass.cpp" else world_source
        for token in tokens:
            if token not in liveness_source:
                failures.append(f"{filename}: missing bounded iOS liveness token {token!r}")

    if "Surface 648" in grass_source or "Surface 648" in world_source:
        failures.append("foliage instrumentation is overfit to the last observed surface")

    wo43_tokens = {
        "r_main.cpp": (
            "WO43 GL interval begin:",
            "WO43 GL phase transition:",
            "WO43 GL exact first failure:",
            "WO43 init heartbeat:",
            "WO43 init gap:",
            "WO43_ShaderLookup",
            "WO43_RecordSubmission",
            "tracer=stopped",
        ),
        "r_backend.cpp": (
            "R_AllocFrameBuffer/unbind-rb-zero",
            '"glBindRenderbuffer"',
            "R_AllocFrameBuffer/draw-buffer",
        ),
        "r_shader.cpp": (
            "WO43_ShaderTranslate",
            "WO43_ShaderCompile",
            "WO43_ShaderLink",
            "GL_BindShader/bind",
        ),
        "r_world.cpp": (
            "HUD/R_RenderScene/R_DrawWorld/R_DrawBrushList",
            "R_DrawBrushList/final-batch",
        ),
        "r_grass.cpp": (
            "WO43_FoliageDuplicateAvoided",
            "WO43_FoliageConstructed",
        ),
    }
    sources = {
        "r_main.cpp": main_source,
        "r_backend.cpp": backend_source,
        "r_shader.cpp": source,
        "r_world.cpp": world_source,
        "r_grass.cpp": grass_source,
    }
    for filename, tokens in wo43_tokens.items():
        for token in tokens:
            if token not in sources[filename]:
                failures.append(f"{filename}: missing WO43 Phase B token {token!r}")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print(
        "Diffusion iOS policy: shared animated-model key; one-bone rigid key retained; "
        "bounded foliage/world liveness enabled"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
