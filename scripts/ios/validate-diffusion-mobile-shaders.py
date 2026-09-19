#!/usr/bin/env python3

import argparse
import ast
import re
import subprocess
import tempfile
from pathlib import Path


INCLUDE = re.compile(r'^\s*#include\s+["<]([^">]+)[">]')
ENTRY = re.compile(r'\{\s*"([^"\\]+)"\s*,\s*("(?:[^"\\]|\\.)*")\s*\}', re.DOTALL)
LITERAL_CALL = re.compile(
    r'GL_InitGPUShader\(\s*"[^"]+"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"'
    r'(?:\s*,\s*("(?:[^"\\]|\\.)*"))?\s*\)', re.DOTALL
)

POSTPROCESS_BASES = {
    "bilateralblur", "bloom", "blurmip", "drawshafts", "drawssao",
    "dronescreen", "enhance", "fsr_easu", "fsr_rcas", "gaussblur",
    "generate_exposure", "generate_luminance", "genhbao", "genshafts",
    "genssao", "glitch", "heat", "horizontalblur", "lensflare",
    "monochrome", "motionblur", "screenwater", "smaaedgedetect",
    "smaablendweight", "smaaneighborblend", "tonemap", "waterdrops",
}
UNSUPPORTED_DIRECTIVES = (
    "MULTI_LAYERS", "EMBOSS", "HAS_SHADOWS", "INTERIOR",
    "SPECULAR", "BUMP", "REFLECTION_CUBEMAP",
)

# Work Order 56 Phase K admits only the complete production terrain feature.
# These jobs are intentionally not passed through the ordinary mobile-profile
# sanitizer and cover both the base and normal/specular/emboss array variants.
TEXTURE_ARRAY_JOBS = (
    ("vertex", "bmodelsolid_vp.glsl", "#define BMODEL_APPLY_STYLE0\n#define TERRAIN_NUM_LAYERS 4\n#define BMODEL_MULTI_LAYERS\n"),
    ("fragment", "bmodelsolid_fp.glsl", "#define BMODEL_APPLY_STYLE0\n#define TERRAIN_NUM_LAYERS 4\n#define BMODEL_MULTI_LAYERS\n"),
    ("vertex", "bmodeldlight_vp.glsl", "#define BMODEL_LIGHT_PROJECTION\n#define TERRAIN_NUM_LAYERS 4\n#define BMODEL_MULTI_LAYERS\n"),
    ("fragment", "bmodeldlight_fp.glsl", "#define BMODEL_LIGHT_PROJECTION\n#define TERRAIN_NUM_LAYERS 4\n#define BMODEL_MULTI_LAYERS\n"),
    ("vertex", "bmodelsolid_vp.glsl", "#define BMODEL_APPLY_STYLE0\n#define TERRAIN_NUM_LAYERS 4\n#define BMODEL_MULTI_LAYERS\n#define BMODEL_BUMP\n#define NORMAL_AG_PARABOLOID\n#define BMODEL_SPECULAR\n#define BMODEL_EMBOSS\n"),
    ("fragment", "bmodelsolid_fp.glsl", "#define BMODEL_APPLY_STYLE0\n#define TERRAIN_NUM_LAYERS 4\n#define BMODEL_MULTI_LAYERS\n#define BMODEL_BUMP\n#define NORMAL_AG_PARABOLOID\n#define BMODEL_SPECULAR\n#define BMODEL_EMBOSS\n"),
    ("vertex", "bmodeldlight_vp.glsl", "#define BMODEL_LIGHT_PROJECTION\n#define TERRAIN_NUM_LAYERS 4\n#define BMODEL_MULTI_LAYERS\n#define BMODEL_BUMP\n#define NORMAL_AG_PARABOLOID\n#define BMODEL_SPECULAR\n#define BMODEL_EMBOSS\n"),
    ("fragment", "bmodeldlight_fp.glsl", "#define BMODEL_LIGHT_PROJECTION\n#define TERRAIN_NUM_LAYERS 4\n#define BMODEL_MULTI_LAYERS\n#define BMODEL_BUMP\n#define NORMAL_AG_PARABOLOID\n#define BMODEL_SPECULAR\n#define BMODEL_EMBOSS\n"),
)


def sanitize_defines(defines: str) -> str:
    return "".join(
        line for line in defines.splitlines(keepends=True)
        if not any(token in line.upper() for token in UNSUPPORTED_DIRECTIVES)
    )


def expand(shader_dir: Path, filename: str, stack: list[str]) -> str:
    if filename in stack:
        raise RuntimeError(f"recursive include: {' -> '.join(stack + [filename])}")

    output = ["#line 0\n"]
    text = (shader_dir / filename).read_bytes().decode("latin-1")
    for line_number, line in enumerate(text.splitlines(keepends=True), 1):
        match = INCLUDE.match(line)
        if match:
            output.append(expand(shader_dir, match.group(1), stack + [filename]))
            output.append(f"#line {line_number}\n")
        else:
            output.append(line if line.endswith("\n") else line + "\n")
    return "".join(output)


def build_source(shader_dir: Path, shader: str, defines: str) -> str:
    prefix = """#version 130
#define XASH_MOBILE_GLES 1
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#ifndef M_PI2
#define M_PI2 6.28318530717958647692
#endif
"""
    constants = """#ifndef MAXSTUDIOBONES
#define MAXSTUDIOBONES 128
#endif
#ifndef MAX_LIGHTSTYLES
#define MAX_LIGHTSTYLES 64
#endif
#ifndef MAXLIGHTMAPS
#define MAXLIGHTMAPS 4
#endif
#ifndef GRASS_ANIM_DIST
#define GRASS_ANIM_DIST 512.000000
#endif
"""
    return prefix + defines + constants + expand(shader_dir, shader, [])


def jobs(source_root: Path):
    result = set()
    renderer = (source_root / "client/render/r_shader.cpp").read_text()
    for vp_name, fp_name, defines_literal in LITERAL_CALL.findall(renderer):
        defines = sanitize_defines(ast.literal_eval(defines_literal) if defines_literal else "")
        result.add(("vertex", f"{vp_name.lower()}_vp.glsl", defines))
        result.add(("fragment", f"{fp_name.lower()}_fp.glsl", defines))

    shader_list = (source_root / "client/render/r_shaderlist.h").read_text()
    for name, defines_literal in ENTRY.findall(shader_list):
        defines = sanitize_defines(ast.literal_eval(defines_literal))
        base = name.lower()
        for stage, suffix in (("vertex", "vp"), ("fragment", "fp")):
            filename = f"{base}_{suffix}.glsl"
            if (source_root / "glsl" / filename).is_file():
                result.add((stage, filename, defines))

    for path in (source_root / "glsl").glob("*_vp.glsl"):
        result.add(("vertex", path.name, ""))
    for path in (source_root / "glsl").glob("*_fp.glsl"):
        result.add(("fragment", path.name, ""))

    result.update(
        (stage, filename, "#define GLSL_ALLOW_TEXTURE_ARRAY 1\n" + defines)
        for stage, filename, defines in TEXTURE_ARRAY_JOBS
    )

    return sorted(
        job for job in result
        if job[1].rsplit("_", 1)[0] not in POSTPROCESS_BASES
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    parser.add_argument("converter", type=Path)
    parser.add_argument("validator", type=Path)
    args = parser.parse_args()

    failures = []
    shader_jobs = jobs(args.source_root)
    for index, (stage, filename, defines) in enumerate(shader_jobs, 1):
        source = build_source(args.source_root / "glsl", filename, defines)
        converted = subprocess.run(
            [str(args.converter), stage], input=source, text=True,
            capture_output=True, check=True,
        ).stdout
        suffix = ".vert" if stage == "vertex" else ".frag"
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix) as shader_file:
            shader_file.write(converted)
            shader_file.flush()
            checked = subprocess.run(
                [str(args.validator), "-S", "vert" if stage == "vertex" else "frag", shader_file.name],
                text=True, capture_output=True,
            )
        if checked.returncode:
            failures.append((stage, filename, defines, checked.stdout + checked.stderr))
        if index % 100 == 0:
            print(f"validated {index}/{len(shader_jobs)} mobile shader variants")

    if failures:
        for stage, filename, defines, error in failures[:20]:
            print(f"FAIL {stage} {filename} {defines!r}\n{error}")
        raise SystemExit(f"{len(failures)} of {len(shader_jobs)} mobile shader variants failed")
    print(f"validated all {len(shader_jobs)} GL4ES mobile shader variants")


if __name__ == "__main__":
    main()
