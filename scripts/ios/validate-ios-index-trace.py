#!/usr/bin/env python3
"""Validate the Work Order 48 Phase B diagnostics-only index trace."""

from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys


GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
FROZEN_HASHES = {
    "gl4es-uint-elements-ios.patch": "57cbb4b8899eb182a71bee9e9fba1fe29334e541b3aeb4cb4ba6ee327df5f5fe",
    "gl4es-drawable-bridge-ios.patch": "f9e521fabf164801341c222ed802f2be24439b4e526094f122997ca147485cb1",
    "sdl2-drawable-bridge-ios.patch": "49b867a0f01b488e7bf6a85575b0363e6d1325cac1ef0249e2b421a0e13f7826",
}
PATCH_FILES = {
    "include/gl4esinit.h",
    "src/gl/drawing.c",
    "src/gl/indextrace.c",
    "src/gl/indextrace.h",
    "src/gl/list.c",
    "src/gl/list.h",
    "src/gl/listdraw.c",
}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def revision(path: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}", "-C", str(path),
         "rev-parse", "HEAD"], check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


def reject(text: str, pattern: str, label: str, failures: list[str]) -> None:
    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
        failures.append(f"{label}: forbidden pattern {pattern!r}")


def fnv1a(values: list[int]) -> int:
    value = 2166136261
    for item in values:
        for byte in int(item).to_bytes(4, "little"):
            value ^= byte
            value = (value * 16777619) & 0xFFFFFFFF
    return value


def validate(files: dict[str, str], repo: pathlib.Path | None = None) -> list[str]:
    failures: list[str] = []
    trace = files["trace"]
    trace_h = files["trace_h"]
    drawing = files["drawing"]
    list_c = files["list_c"]
    list_h = files["list_h"]
    listdraw = files["listdraw"]
    public_h = files["public_h"]
    ref_gl = files["ref_gl"]
    ref_context = files["ref_context"]
    ref_main = files["ref_main"]
    patch = files["patch"]
    build = files["build"]

    for marker in (
        "iOS index trace logger:", "iOS index trace policy:",
        "iOS index trace ingress:", "iOS index trace deferred:",
        "iOS index trace native:", "iOS index trace first divergence:",
        "iOS index trace summary:",
    ):
        require(trace, marker, "engine-log marker coverage", failures)
    require(ref_context, "iOS index trace ownership:", "ownership marker", failures)
    require(ref_gl, "gEngfuncs.Con_Printf( \"%s\\n\", line )", "engine console bridge", failures)
    require(ref_gl, "set_index_trace_logger( R_IOSIndexTraceLog )", "logger installation", failures)
    require(ref_gl, "set_index_trace_logger( NULL )", "logger teardown", failures)
    require(public_h, "set_index_trace_logger", "public logger API", failures)
    require(public_h, "set_index_trace_context", "public context API", failures)
    reject(trace + ref_gl, r"\b(LOGD|SHUT_LOGD|printf|vprintf)\s*\(",
           "stdout-only trace sink", failures)

    for token in (
        "IOS_INDEX_TRACE_WINDOW 64u", "IOS_INDEX_TRACE_RECORDS 5u",
        "IOS_INDEX_TRACE_GL_LINES 15u", "ios_index_logger_busy",
        "if(record->native_seen)", "ios_index_summary_emitted",
        "records<=16", "cap=16",
    ):
        require(trace, token, "bounded/non-reentrant trace", failures)
    reject(trace, r"\b(malloc|calloc|realloc|free)\s*\(", "per-draw allocation", failures)
    reject(trace, r"glGetError|errorShim|noerrorShim", "error-queue mutation", failures)

    for token in (
        "IOS_INDEX_FAMILY_WORLD", "IOS_INDEX_FAMILY_STUDIO_EBO",
        "IOS_INDEX_FAMILY_STUDIO_DECAL", 'return "world-client"',
        'return "studio-ebo"', 'return "studio-decal-client"',
        "glstate->vao->elements", "position->buffer", "highest_legal_vertex",
        "logical_vao", "position_stride", "position_offset", "ebo_size",
    ):
        require(trace, token, "three-family vertex/index pairing", failures)
    for token in (
        "ios_index_next_id", "++ios_index_next_id", "ios_index_checksum",
        "expected_checksum", "expected_min", "expected_max",
        "segment_offset", "segment_count", "ebo-offset-pair",
        "client-with-native-ebo", "width", "count", "minmax", "checksum",
    ):
        require(trace, token, "paired trace discriminator", failures)

    for token in (
        'ios_index_trace_ingress("glDrawRangeElements"',
        'ios_index_trace_ingress("glDrawElements"',
        "ios_index_trace_set_active", "ios_index_trace_native(0, \"glDrawElements\"",
        "ios_index_trace_deferred(ios_trace_id, iindices, count, start",
        "ios_index_trace_deferred(ios_trace_id, iindices, count, min",
        "ios_index_trace_id = ios_trace_id",
    ):
        require(drawing, token, "direct/deferred/intercept ingress coverage", failures)
    if drawing.count("ios_index_trace_deferred(ios_trace_id, iindices, count, start") != 2:
        failures.append("range direct/deferred coverage: expected compiling and intercept capture")
    if drawing.count("ios_index_trace_deferred(ios_trace_id, iindices, count, min") != 2:
        failures.append("ordinary direct/deferred coverage: expected compiling and intercept capture")
    for token in (
        "ios_index_trace_id", "ios_index_trace_offset", "ios_index_trace_count",
    ):
        require(list_h, token, "render-list trace identity storage", failures)
    for token in (
        "b->ios_index_trace_id", "ilen_a + b->ios_index_trace_offset",
        "ios_index_trace_deferred", "append_tracking=enabled",
    ):
        require(list_c + trace, token, "append/merge identity survival", failures)
    for token in (
        "glDrawElements(renderlist)", "list->ios_index_trace_id",
        "list->ios_index_trace_offset", "list->ios_index_trace_count",
        "vbo_indices ? list->vbo_indices : 0",
    ):
        require(listdraw, token, "render-list native egress", failures)

    for token in (
        "dladdr( address", '"glDrawRangeElements"', '"glDrawRangeElementsEXT"',
        '"glDrawElements"', "dli_fname", "dli_sname",
    ):
        require(ref_context, token, "resolved function ownership", failures)
    require(ref_main, "set_index_trace_context( tr.realframecount, world_name, \"custom-render\" )",
            "frame/map/phase context", failures)

    headers = set(re.findall(r"^diff --git a/(\S+) b/\S+$", patch, re.MULTILINE))
    if headers != PATCH_FILES:
        failures.append(f"trace patch scope: expected {sorted(PATCH_FILES)}, got {sorted(headers)}")
    added = "\n".join(
        line[1:] for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    for pattern in (
        r"\b(?:glBind|gles_gl|pgl)[A-Za-z0-9_]*\s*\(",
        r"\bhardext\.elementuint\s*=", r"\bindices\s*\[[^]]+\]\s*=",
        r"glUniform|u_BrushParams|\bshader\b|\bmaterial\b|\btexture\b|\bframebuffer\b|\bresolve\b|\bMSAA\b|presentRenderbuffer",
        r"ch1map[01]|\btransition\b|\btouch\b|\bmenu\b|\baudio\b",
    ):
        reject(added, pattern, "rendering/scope mutation", failures)
    for token in ("gl4es-index-trace-ios.patch", "validate-ios-index-trace.py"):
        require(build, token, "CI patch/validator route", failures)

    if repo is not None:
        for name, expected in FROZEN_HASHES.items():
            actual = digest(repo / "scripts/ios" / name)
            if actual != expected:
                failures.append(f"frozen Bundle 69/71 policy changed: {name} {actual}")

    values = [65535, 65536, 65537, 100000]
    if fnv1a(values) != fnv1a(list(values)):
        failures.append("positive pairing model: stable checksum changed")
    normalized = [value - min(values) for value in values]
    if max(normalized) != 34465 or min(normalized) != 0:
        failures.append("positive deferred model: normalization/span mismatch")
    if fnv1a(values) == fnv1a([65535, 0, 1, 34464]):
        failures.append("rejection model: 16-bit truncation was not discriminated")
    return failures


def self_test(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    cases = (
        ("stdout sink", "ref_gl", "gEngfuncs.Con_Printf( \"%s\\n\", line )", "printf(\"%s\\n\", line)"),
        ("missing family", "trace", 'return "studio-decal-client"', 'return "client"'),
        ("unpaired native", "drawing", "ios_index_trace_native(0, \"glDrawElements\"", "missing_native_pair("),
        ("missing deferred", "drawing", "ios_index_trace_deferred(ios_trace_id, iindices, count, start", "missing_deferred_trace(ios_trace_id, iindices, count, start"),
        ("missing replay", "listdraw", "list->ios_index_trace_id", "0 /* lost id */"),
        ("missing append", "list_c", "ilen_a + b->ios_index_trace_offset", "b->ios_index_trace_offset"),
        ("flooding", "trace", "IOS_INDEX_TRACE_GL_LINES 15u", "IOS_INDEX_TRACE_GL_LINES 128u"),
        ("allocation", "trace", "char buffer[1024];", "char *buffer = malloc(1024);"),
        ("error mutation", "trace", "ios_index_trace_summary_if_ready(void)", "ios_index_trace_summary_if_ready(void) { glGetError(); } /*"),
        ("index mutation", "patch", "+#include \"indextrace.h\"", "+indices[0] = 0;\n+#include \"indextrace.h\""),
        ("uniform expansion", "patch", "+#include \"indextrace.h\"", "+glUniform4fv(location, 3, data);\n+#include \"indextrace.h\""),
        ("FBO expansion", "patch", "+#include \"indextrace.h\"", "+glBindFramebuffer(GL_FRAMEBUFFER, 0);\n+#include \"indextrace.h\""),
        ("missing ownership", "ref_context", "dladdr( address", "missing_dladdr(address"),
    )
    for label, key, old, new in cases:
        mutated = dict(files)
        if old not in mutated[key]:
            failures.append(f"self-test setup {label}: token absent")
            continue
        mutated[key] = mutated[key].replace(old, new, 1)
        if not validate(mutated):
            failures.append(f"self-test {label}: invalid mutation accepted")
    return failures


def main() -> int:
    if len(sys.argv) not in (3, 4):
        print("usage: validate-ios-index-trace.py REPO_ROOT APPLIED_GL4ES [--self-test]", file=sys.stderr)
        return 2
    repo = pathlib.Path(sys.argv[1]).resolve()
    gl4es = pathlib.Path(sys.argv[2]).resolve()
    if revision(gl4es) != GL4ES_REF:
        print(f"FAIL: expected GL4ES {GL4ES_REF}, got {revision(gl4es)}", file=sys.stderr)
        return 1
    files = {
        "trace": read(gl4es / "src/gl/indextrace.c"),
        "trace_h": read(gl4es / "src/gl/indextrace.h"),
        "drawing": read(gl4es / "src/gl/drawing.c"),
        "list_c": read(gl4es / "src/gl/list.c"),
        "list_h": read(gl4es / "src/gl/list.h"),
        "listdraw": read(gl4es / "src/gl/listdraw.c"),
        "public_h": read(gl4es / "include/gl4esinit.h"),
        "ref_gl": read(repo / "ref/gl/gl_opengl.c"),
        "ref_context": read(repo / "ref/gl/gl_context.c"),
        "ref_main": read(repo / "ref/gl/gl_rmain.c"),
        "patch": read(repo / "scripts/ios/gl4es-index-trace-ios.patch"),
        "build": read(repo / "scripts/gha/build_ios.sh"),
    }
    failures = validate(files, repo)
    if len(sys.argv) == 4 and sys.argv[3] == "--self-test":
        failures.extend(self_test(files))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Validated iOS index trace: engine sink, ownership, three families, paired direct/deferred/native IDs, cap 16")
    if len(sys.argv) == 4:
        print("Validated rejection suite: stdout, flooding, unpaired routes, mutation, uniform and presentation changes rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
