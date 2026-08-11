#!/usr/bin/env python3
"""Summarize Diffusion uber-shader variants from an Xash engine log."""

from __future__ import annotations

import argparse
import collections
import dataclasses
import pathlib
import re
import sys


COMPILE_RE = re.compile(r"^CompileUberShader #(\d+): (.+)$")
STUDIO_VERTEX_RE = re.compile(r"^loading 'glsl/(StudioSolid|StudioDlight)_vp\.glsl'$")
BONE_DEFINE_RE = re.compile(r"^#define MAXSTUDIOBONES (\d+)$")
BONE_UNIFORM_RE = re.compile(r"^uniform vec[34] u_Bone(Position|Quaternion)\[(\d+)\];$")

RUN39_BONE_KEYS = (
    1, 2, 4, 5, 6, 8, 12, 13, 20, 21, 22, 24, 27, 28, 36,
    37, 38, 39, 42, 48, 49, 51, 53, 55, 56, 59, 67, 68, 69, 70,
)


@dataclasses.dataclass
class StudioCompile:
    name: str
    bone_key: int | None = None
    defines: list[str] = dataclasses.field(default_factory=list)
    bone_position_layouts: set[int] = dataclasses.field(default_factory=set)
    bone_quaternion_layouts: set[int] = dataclasses.field(default_factory=set)


def parse_log(lines: list[str]) -> tuple[list[tuple[int, str]], list[StudioCompile]]:
    compiles: list[tuple[int, str]] = []
    studio_compiles: list[StudioCompile] = []
    pending: StudioCompile | None = None

    for line in lines:
        match = STUDIO_VERTEX_RE.match(line)
        if match:
            pending = StudioCompile(match.group(1))
            continue

        if pending is not None:
            if line.startswith("#define ") and line not in pending.defines:
                pending.defines.append(line)

            match = BONE_DEFINE_RE.match(line)
            if match and pending.bone_key is None:
                pending.bone_key = int(match.group(1))

            match = BONE_UNIFORM_RE.match(line)
            if match:
                layout = int(match.group(2))
                if match.group(1) == "Position":
                    pending.bone_position_layouts.add(layout)
                else:
                    pending.bone_quaternion_layouts.add(layout)

        match = COMPILE_RE.match(line)
        if not match:
            continue

        index, name = int(match.group(1)), match.group(2)
        compiles.append((index, name))
        if name in {"StudioSolid", "StudioDlight"}:
            if pending is None or pending.name != name:
                raise ValueError(f"studio compile #{index} has no matching vertex-shader block")
            studio_compiles.append(pending)
            pending = None

    return compiles, studio_compiles


def summarize(path: pathlib.Path, expect_run39: bool) -> int:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    compiles, studio_compiles = parse_log(lines)
    names = collections.Counter(name for _, name in compiles)
    bone_keys = sorted({record.bone_key for record in studio_compiles if record.bone_key is not None})
    position_layouts = sorted({value for record in studio_compiles for value in record.bone_position_layouts})
    quaternion_layouts = sorted({value for record in studio_compiles for value in record.bone_quaternion_layouts})
    current_studio_keys = {(record.name, tuple(record.defines)) for record in studio_compiles}
    shared_animated_keys = set()
    for record in studio_compiles:
        defines = tuple(
            define
            for define in record.defines
            if not define.startswith("#define MAXSTUDIOBONES ") or record.bone_key == 1
        )
        shared_animated_keys.add((record.name, defines))

    print(f"lines={len(lines)}")
    print(f"compile_total={len(compiles)}")
    if compiles:
        print(f"compile_index_range={compiles[0][0]}-{compiles[-1][0]}")
    print("compile_by_name=" + ",".join(f"{name}:{names[name]}" for name in sorted(names)))
    print(f"studio_total={len(studio_compiles)}")
    print(f"studio_unique_current_keys={len(current_studio_keys)}")
    print(f"studio_unique_shared_animated_keys={len(shared_animated_keys)}")
    print("studio_bone_keys=" + ",".join(map(str, bone_keys)))
    print("studio_bone_position_layouts=" + ",".join(map(str, position_layouts)))
    print("studio_bone_quaternion_layouts=" + ",".join(map(str, quaternion_layouts)))
    print(f"game_started={bool(lines and lines[-1] == 'Game started')}".lower())

    if not expect_run39:
        return 0

    expected_names = {
        "BmodelDlight": 2,
        "BmodelSolid": 3,
        "GenericDlight": 2,
        "StudioDlight": 80,
        "StudioSolid": 51,
    }
    failures = []
    if len(lines) != 4073:
        failures.append(f"expected 4073 lines, got {len(lines)}")
    if len(compiles) != 138:
        failures.append(f"expected 138 uber-shader compiles, got {len(compiles)}")
    if names != expected_names:
        failures.append(f"unexpected compile counts: {dict(names)}")
    if len(studio_compiles) != 131:
        failures.append(f"expected 131 studio compiles, got {len(studio_compiles)}")
    if len(current_studio_keys) != 131:
        failures.append(f"expected 131 distinct run-39 studio keys, got {len(current_studio_keys)}")
    if len(shared_animated_keys) != 33:
        failures.append(
            f"expected shared animated-model policy to reduce the observed keys to 33, "
            f"got {len(shared_animated_keys)}"
        )
    if tuple(bone_keys) != RUN39_BONE_KEYS:
        failures.append(f"unexpected studio bone keys: {bone_keys}")
    if position_layouts != [128] or quaternion_layouts != [128]:
        failures.append(
            "expected every observed translated studio bone uniform layout to use 128 entries"
        )
    if not lines or lines[-1] != "Game started":
        failures.append("log does not end with Game started")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print("run39_evidence=confirmed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=pathlib.Path)
    parser.add_argument(
        "--expect-run39",
        action="store_true",
        help="fail unless the attached run-39 shader evidence matches the accepted counts",
    )
    args = parser.parse_args()
    return summarize(args.log, args.expect_run39)


if __name__ == "__main__":
    raise SystemExit(main())
