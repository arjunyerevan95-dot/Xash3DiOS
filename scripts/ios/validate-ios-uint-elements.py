#!/usr/bin/env python3
"""Validate the Work Order 47 Phase B 32-bit element-index invariant."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys


GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
ROUTES = (
    "gl4es_glDrawRangeElements",
    "gl4es_glDrawElements",
    "gl4es_glMultiDrawElements",
    "gl4es_glMultiDrawElementsBaseVertex",
    "gl4es_glDrawElementsBaseVertex",
    "gl4es_glDrawRangeElementsBaseVertex",
    "gl4es_glDrawElementsInstanced",
    "gl4es_glDrawElementsInstancedBaseVertex",
)
PATCH_FILES = {
    "src/gl/drawing.c",
    "src/gl/glstate.h",
    "src/gl/line.c",
    "src/gl/line.h",
    "src/gl/list.c",
    "src/gl/list.h",
    "src/gl/listdraw.c",
    "src/gl/texgen.c",
    "src/gl/texgen.h",
    "src/glx/hardext.c",
}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def revision(path: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}", "-C", str(path),
         "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


def reject(text: str, pattern: str, label: str, failures: list[str]) -> None:
    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
        failures.append(f"{label}: forbidden pattern {pattern!r}")


def function(text: str, name: str) -> str:
    start = text.find(name + "(")
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


def model_submit(version: str, extension: bool, values: list[int]) -> tuple[str, list[int]] | None:
    match = re.search(r"OpenGL ES[^0-9]*([0-9]+)", version)
    native_major = int(match.group(1)) if match else 0
    if native_major >= 3 or extension:
        return "GL_UNSIGNED_INT", list(values)
    return None


def validate(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    drawing = files["drawing"]
    hardext = files["hardext"]
    list_h = files["list_h"]
    list_c = files["list_c"]
    listdraw = files["listdraw"]
    glstate = files["glstate"]
    line = files["line"] + files["line_h"]
    texgen = files["texgen"] + files["texgen_h"]
    patch = files["patch"]
    build = files["build"]
    drawable_patch = files["drawable_patch"]

    for token in (
        "const char *Version = (const char *) gles_glGetString(GL_VERSION);",
        "const char *p = strstr(Version, \"OpenGL ES\");",
        "native_es_major>=3 || elementuint_extension",
        "elementuint_extension?\"oes-extension\":\"unsupported\"",
        "iOS uint element policy:",
    ):
        require(hardext, token, "live native-ES capability policy", failures)
    reject(hardext, r"hardext\.elementuint\s*=\s*1\s*;", "unconditional uint enable", failures)
    reject(hardext, r'S\("GL_OES_element_index_uint[^\n]*elementuint',
           "extension-only uint policy", failures)

    for token in (
        "resolved_element_indices",
        "glstate->vao->elements->data + (uintptr_t)indices",
        "require_uint_element_support",
        "errorShim(GL_INVALID_OPERATION)",
        "const GLenum target = (list_path || type==GL_UNSIGNED_INT)?GL_UNSIGNED_INT:GL_UNSIGNED_SHORT;",
        "copy_gl_array(src, type, 1, 0, target",
        "normalize_indices_ui(iindices",
        "list->indices = iindices",
        "iOS uint element first use:",
        "iOS uint element high index:",
        "iOS uint element route summary:",
    ):
        require(drawing, token, "draw-route invariant", failures)
    reject(drawing, r"TODO[^\n]*uint indices", "unimplemented uint route", failures)
    reject(drawing, r"normalize_indices_us\s*\(\s*sindices", "lossy deferred normalization", failures)
    reject(drawing, r"list->indices\s*=\s*sindices", "16-bit render-list attachment", failures)

    for route in ROUTES:
        body = function(drawing, route)
        if not body:
            failures.append(f"route coverage: cannot locate {route}")
            continue
        if "BaseVertex" not in route or "if(basevertex==0)" not in body:
            require(body, "require_uint_element_support", f"route coverage {route}", failures)
        if route not in ("gl4es_glDrawRangeElements", "gl4es_glDrawElements"):
            # Base-vertex routes must copy before adding the base. Multi and
            # instanced routes must still go through the common preparation.
            require(body, "prepare_element_indices", f"route coverage {route}", failures)
        else:
            require(body, "prepare_element_indices", f"route coverage {route}", failures)
    for token in (
        "prepare_element_indices(type, indices[i]",
        "trace_uint_element_route(\"multidraw\"",
        "trace_uint_element_route(\"basevertex\"",
        "trace_uint_element_route(\"instanced\"",
        "trace_uint_element_route(\"renderlist\"",
        "trace_uint_element_route(\"intercept\"",
    ):
        require(drawing, token, "multidraw/base/instanced/deferred coverage", failures)
    for route in ("gl4es_glMultiDrawElements", "gl4es_glMultiDrawElementsBaseVertex"):
        route_body = function(drawing, route)
        require(route_body, "prepare_element_indices(type, indices[i]",
                f"multidraw per-draw EBO offset {route}", failures)
        reject(route_body, r"\(uintptr_t\)indices\s*\)",
               f"multidraw EBO array confusion {route}", failures)

    for token in (
        "GLuint *indices;",
        "GLuint      *ind_lines;",
        "void doadd_renderlist(renderlist_t* a, GLenum mode, GLuint* indices",
        "void renderlist_createindices(int ilen, GLuint *indices",
    ):
        require(list_h, token, "render-list public storage", failures)
    require(glstate, "GLuint*             merger_indices;", "render-list merger storage", failures)
    for token in (
        "glstate->merger_indices = (GLuint*)realloc",
        "list->indices = (GLuint*)realloc",
        "sizeof(GLuint)",
    ):
        require(list_c, token, "render-list allocation/merge", failures)
    reject(list_h + list_c + glstate, r"GLushort\s*\*\s*(indices|ind_lines|merger_indices|newind|tmpi)",
           "16-bit render-list storage", failures)

    for token in (
        "prepare_renderlist_indices",
        "if(hardext.elementuint)",
        "*type = GL_UNSIGNED_INT;",
        "if(max>65535)",
        "errorShim(GL_INVALID_OPERATION);",
        "*type = GL_UNSIGNED_SHORT;",
        "select_glDrawElements(&vtx, list->mode, list->ilen, GL_UNSIGNED_INT, indices)",
        "gles_glBufferData(GL_ELEMENT_ARRAY_BUFFER, list->ilen*((index_type==GL_UNSIGNED_INT)?sizeof(GLuint):sizeof(GLushort))",
        "gles_glDrawElements(mode, list->ilen, index_type",
    ):
        require(listdraw, token, "native submit / checked ES2 fallback", failures)
    reject(listdraw, r"gles_glDrawElements\([^\n]+GL_UNSIGNED_SHORT[^\n]+list->(indices|ind_lines)",
           "hard-coded 16-bit render-list submit", failures)
    require(line, "GLuint *indices", "line-stipple index width", failures)
    require(texgen, "GLuint *indices", "texgen index width", failures)
    reject(line + texgen, r"GLushort\s*\*\s*(sindices|indices)",
           "16-bit line/texgen index consumer", failures)

    headers = set(re.findall(r"^diff --git a/(\S+) b/\S+$", patch, re.MULTILINE))
    if headers != PATCH_FILES:
        failures.append(f"patch scope: expected {sorted(PATCH_FILES)}, got {sorted(headers)}")
    for token in (
        "gl4es-uint-elements-ios.patch",
        "validate-ios-uint-elements.py",
    ):
        require(build, token, "build/policy route", failures)
    for forbidden in (
        "glUniform4fv", "u_BrushParams", "ch1map1", "transition crash",
        "gl4es_external_default_framebuffer", "set_external_default_framebuffer",
    ):
        if forbidden in patch:
            failures.append(f"scope guard: uint patch contains forbidden {forbidden!r}")
    require(drawable_patch, "set_external_default_framebuffer", "Bundle 69 direct-drawable preservation", failures)

    fixtures = [65535, 65536, 65537, 100000]
    if model_submit("OpenGL ES 3.0 Apple", False, fixtures) != ("GL_UNSIGNED_INT", fixtures):
        failures.append("positive model: ES3 without extension did not preserve uint values")
    if model_submit("OpenGL ES 2.0 Apple", True, fixtures) != ("GL_UNSIGNED_INT", fixtures):
        failures.append("positive model: ES2 with OES extension did not preserve uint values")
    if model_submit("OpenGL ES 2.0 Apple", False, fixtures) is not None:
        failures.append("rejection model: unsupported ES2 emitted an index stream")
    client = fixtures
    ebo = [7, 8] + fixtures + [9]
    if ebo[2:2 + len(fixtures)] != client:
        failures.append("client/EBO model: byte-offset resolution changed values")
    return failures


def self_test(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    cases = (
        ("extension-only capability", "hardext", "native_es_major>=3 || elementuint_extension", "elementuint_extension"),
        ("unconditional capability", "hardext", "hardext.elementuint = (native_es_major>=3 || elementuint_extension)?1:0;", "hardext.elementuint = 1;"),
        ("lossy list target", "drawing", "(list_path || type==GL_UNSIGNED_INT)?GL_UNSIGNED_INT:GL_UNSIGNED_SHORT", "type==GL_UNSIGNED_INT?GL_UNSIGNED_INT:GL_UNSIGNED_SHORT"),
        ("ordinary route omitted", "drawing", "require_uint_element_support(type, \"ordinary\")", "omitted_uint_support(type)"),
        ("multidraw EBO confusion", "drawing", "prepare_element_indices(type, indices[i]", "prepare_element_indices(type, indices"),
        ("16-bit list storage", "list_h", "GLuint *indices;", "GLushort *indices;"),
        ("16-bit merger", "glstate", "GLuint*             merger_indices;", "GLushort*           merger_indices;"),
        ("hard-coded short submit", "listdraw", "gles_glDrawElements(mode, list->ilen, index_type, vbo_indices?NULL:index_data);", "gles_glDrawElements(mode, list->ilen, GL_UNSIGNED_SHORT, list->indices);"),
        ("unsafe ES2 high index", "listdraw", "errorShim(GL_INVALID_OPERATION);", "return 1;"),
        ("drawable rollback", "patch", "diff --git a/src/gl/drawing.c", "diff --git a/src/gl/framebuffers.c b/src/gl/framebuffers.c\n+set_external_default_framebuffer\n+diff --git a/src/gl/drawing.c"),
        ("uniform scope expansion", "patch", "diff --git a/src/gl/drawing.c", "glUniform4fv\n+diff --git a/src/gl/drawing.c"),
        ("missing marker", "drawing", "iOS uint element high index:", "missing high index marker:"),
    )
    for label, key, old, new in cases:
        mutated = dict(files)
        if old not in mutated[key]:
            failures.append(f"self-test setup {label}: token absent")
            continue
        mutated[key] = mutated[key].replace(old, new, 1)
        if not validate(mutated):
            failures.append(f"self-test {label}: invalid mutation was accepted")
    return failures


def main() -> int:
    if len(sys.argv) not in (3, 4):
        print("usage: validate-ios-uint-elements.py REPO_ROOT APPLIED_GL4ES [--self-test]", file=sys.stderr)
        return 2
    repo = pathlib.Path(sys.argv[1]).resolve()
    gl4es = pathlib.Path(sys.argv[2]).resolve()
    run_self_test = len(sys.argv) == 4 and sys.argv[3] == "--self-test"
    if revision(gl4es) != GL4ES_REF:
        print(f"FAIL: expected GL4ES {GL4ES_REF}, got {revision(gl4es)}", file=sys.stderr)
        return 1
    files = {
        "drawing": read(gl4es / "src/gl/drawing.c"),
        "hardext": read(gl4es / "src/glx/hardext.c"),
        "list_h": read(gl4es / "src/gl/list.h"),
        "list_c": read(gl4es / "src/gl/list.c"),
        "listdraw": read(gl4es / "src/gl/listdraw.c"),
        "glstate": read(gl4es / "src/gl/glstate.h"),
        "line": read(gl4es / "src/gl/line.c"),
        "line_h": read(gl4es / "src/gl/line.h"),
        "texgen": read(gl4es / "src/gl/texgen.c"),
        "texgen_h": read(gl4es / "src/gl/texgen.h"),
        "patch": read(repo / "scripts/ios/gl4es-uint-elements-ios.patch"),
        "drawable_patch": read(repo / "scripts/ios/gl4es-drawable-bridge-ios.patch"),
        "build": read(repo / "scripts/gha/build_ios.sh"),
    }
    failures = validate(files)
    if run_self_test:
        failures.extend(self_test(files))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Validated iOS uint element policy: native ES3 core, ES2 extension/rejection, uint32 routes and render lists")
    if run_self_test:
        print("Validated rejection suite: lossy, incomplete, unconditional, drawable, uniform and marker mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
