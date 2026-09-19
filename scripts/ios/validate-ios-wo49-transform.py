#!/usr/bin/env python3
"""Validate the WO49 Phase E diagnostics-only transform discriminator."""

from __future__ import annotations

import argparse
import copy
import pathlib
import re
import subprocess
import sys


GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
DIFFUSION_REF = "14d156bf3a6993c172697fac83a937836c3b5561"
GL4ES_PATCH_FILES = {
    "src/gl/indextrace.h", "src/gl/indextrace.c", "src/gl/uniform.c",
    "src/gl/fpe.c", "src/gl/gl_lookup.c",
}
DIFFUSION_PATCH_FILES = {
    "engine/studio.h", "client/render/r_studio.h", "client/render/r_studio.cpp",
}
TERMINALS = {
    "application-source-transform-mismatch",
    "GL4ES-reflection/cache-mismatch",
    "GL4ES-native-forward-mismatch",
    "full-application-to-native-transform-match",
    "incomplete/absent-evidence",
}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


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


def patch_headers(text: str) -> set[str]:
    return set(re.findall(r"^diff --git a/(\S+) b/\S+$", text, re.MULTILINE))


def added_lines(text: str) -> str:
    return "\n".join(
        line[1:] for line in text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def section(text: str, start: str, end: str | None = None) -> str:
    begin = text.find(start)
    if begin < 0:
        return ""
    if end is None:
        return text[begin:]
    finish = text.find(end, begin + len(start))
    return text[begin:] if finish < 0 else text[begin:finish]


def ordered(text: str, tokens: tuple[str, ...], label: str,
            failures: list[str]) -> None:
    cursor = -1
    for token in tokens:
        position = text.find(token, cursor + 1)
        if position < 0:
            failures.append(f"{label}: missing ordered token {token!r}")
            return
        cursor = position


def fixture(sway: bool = False) -> dict:
    names = ["MVP", "modelview", "u_BoneQuaternion[0]", "u_BonePosition[0]"]
    if sway:
        names.append("u_FoliageSwayHeight")
    fields = {}
    for index, name in enumerate(names):
        fields[name] = {
            "reflected": True, "type_ok": True, "extent_ok": True,
            "app": True, "app_type_ok": True, "app_shape_ok": True,
            "app_hash": index + 10, "cache": True, "cache_hash": index + 10,
            "native": True, "native_hash": index + 10, "wrong_bound": False,
        }
    return {"source_ok": True, "armed": True, "program": True, "fields": fields}


def classify(state: dict) -> str:
    if not state["source_ok"]:
        return "application-source-transform-mismatch"
    if not state["armed"] or not state["program"]:
        return "incomplete/absent-evidence"
    for value in state["fields"].values():
        if not value["reflected"]:
            return "incomplete/absent-evidence"
        if not value["type_ok"] or not value["extent_ok"]:
            return "GL4ES-reflection/cache-mismatch"
        if not value["app"]:
            return "incomplete/absent-evidence"
        if not value["app_type_ok"] or not value["app_shape_ok"]:
            return "application-source-transform-mismatch"
        if not value["cache"]:
            return "incomplete/absent-evidence"
        if value["cache_hash"] != value["app_hash"]:
            return "GL4ES-reflection/cache-mismatch"
        if not value["native"] and value["wrong_bound"]:
            return "GL4ES-native-forward-mismatch"
        if not value["native"]:
            return "incomplete/absent-evidence"
        if value["native_hash"] != value["cache_hash"]:
            return "GL4ES-native-forward-mismatch"
    return "full-application-to-native-transform-match"


def eligible(flags: set[str], model: str, map_name: str, layout: int,
             bones_upload: bool) -> bool:
    return (
        flags.issuperset({"rigid", "vertexlit"})
        and "boneweighting" not in flags
        and model == "models/bmec/cars/truck_new.mdl"
        and map_name == "maps/ch1map0.bsp"
        and layout == 1 and bones_upload
    )


def validate_fixtures() -> list[str]:
    failures: list[str] = []
    base = fixture()
    if classify(base) != "full-application-to-native-transform-match":
        failures.append("fixture full match: matching values were rejected")
    mutations = (
        ("producer", lambda x: x.update(source_ok=False),
         "application-source-transform-mismatch"),
        ("reflection", lambda x: x["fields"]["MVP"].update(type_ok=False),
         "GL4ES-reflection/cache-mismatch"),
        ("cache", lambda x: x["fields"]["modelview"].update(cache_hash=999),
         "GL4ES-reflection/cache-mismatch"),
        ("wrong native program", lambda x: x["fields"]["u_BoneQuaternion[0]"].update(
            native=False, wrong_bound=True), "GL4ES-native-forward-mismatch"),
        ("native value", lambda x: x["fields"]["u_BonePosition[0]"].update(
            native_hash=999), "GL4ES-native-forward-mismatch"),
        ("missing", lambda x: x["fields"]["MVP"].update(native=False),
         "incomplete/absent-evidence"),
    )
    for label, mutate, wanted in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        got = classify(candidate)
        if got != wanted:
            failures.append(f"fixture {label}: expected {wanted}, got {got}")
    no_sway = fixture(False)
    with_sway = fixture(True)
    with_sway["fields"]["u_FoliageSwayHeight"].update(app=False)
    if classify(no_sway) != "full-application-to-native-transform-match":
        failures.append("fixture conditional sway: non-sway shader required sway")
    if classify(with_sway) != "incomplete/absent-evidence":
        failures.append("fixture conditional sway: sway shader did not require sway")
    if not eligible({"rigid", "vertexlit"}, "models/bmec/cars/truck_new.mdl",
                    "maps/ch1map0.bsp", 1, True):
        failures.append("fixture selector: valid rigid truck draw rejected")
    for flags in ({"vertexlit"}, {"rigid"}, {"rigid", "vertexlit", "boneweighting"}):
        if eligible(flags, "models/bmec/cars/truck_new.mdl", "maps/ch1map0.bsp", 1, True):
            failures.append(f"fixture selector: invalid flags accepted {flags}")
    return failures


def validate(files: dict[str, str], require_diffusion: bool) -> list[str]:
    failures: list[str] = []
    trace = files["trace"]
    trace_h = files["trace_h"]
    uniform = files["uniform"]
    fpe = files["fpe"]
    lookup = files["lookup"]
    gl_patch = files["gl_patch"]
    build = files["build"]
    verify = files["verify"]

    markers = (
        "WO49 transform policy:", "WO49 transform producer:",
        "WO49 transform clip:", "WO49 transform program:",
        "WO49 transform uniform:", "WO49 transform native:",
        "WO49 transform terminal:",
    )
    for marker in markers:
        require(trace, marker, "required engine.log marker", failures)
        require(verify, marker, "packaged marker contract", failures)
    for terminal in TERMINALS:
        require(trace, terminal, "terminal classifier", failures)
    for token in (
        "tokens=1 programs=1 draws=1 frames=1", "storage=fixed",
        "ios_wo49_transform_trace_t", "unsigned char app_value[64]",
        "unsigned char cache_value[64]", "unsigned char native_value[64]",
        "if(!ios_wo49_transform.claimed || ios_wo49_transform.terminal_emitted)",
        "if(!u->reflected)", "if(!u->app_seen)", "if(!u->cache_seen)",
        "if(!u->native_seen)", "sway=conditional", "error_queue=untouched",
    ):
        require(trace + trace_h, token, "bounded terminal proof", failures)
    reject(trace, r"\b(malloc|calloc|realloc|free)\s*\(",
           "transform trace allocation", failures)
    reject(trace + uniform + fpe,
           r"\b(glGetError|glReadPixels|glGetVertexAttrib[A-Za-z0-9_]*|sleep|usleep)\s*\(",
           "forbidden observer", failures)

    for token in (
        "producer_mv_hash", "producer_projection_hash", "producer_mvp_hash",
        "source_mv_hash", "source_projection_hash", "source_mvp_hash",
        "source_mismatch_component", "localPosition", "localIndex",
        "boneQuaternion", "bonePosition", "clipPosition", "optionsHash",
        "logical_shader_hash", "native_shader_hash", "rigid_branch_present",
        "position_branch_present", "reflected_type", "reflected_extent",
        "application_location", "gl4es_location", "native_location",
        "app_entry", "app_width", "app_count", "app_hash", "cache_hash",
        "native_entry", "native_count", "native_hash", "wrong_bound_program",
    ):
        require(trace + trace_h, token, "producer/reflection/native coverage", failures)
    for token in (
        "matrix_mul(getPMat(), getMVMat(), stack_mvp)",
        'strstr(source, "u_BoneQuaternion[0]")',
        'strstr(source, "u_BonePosition[0]")',
        'strstr(source, "_gl4es_ModelViewProjectionMatrix")',
        "ios_wo49_transform_expected_type", "ios_wo49_transform_expected_width",
        "ios_wo49_transform_expected_count",
    ):
        require(trace, token, "exact shader/matrix semantics", failures)

    for token in (
        'MAP("gl4es_iOSWO49TransformBegin", gl4es_wo49_transform_begin)',
        'MAP("gl4es_iOSWO49TransformFinish", gl4es_wo49_transform_finish)',
    ):
        require(lookup, token, "exported diagnostic API", failures)
    require(trace, "ios_wo49_transform.armed = 1", "topology-token arm", failures)

    use_program = section(fpe, "void realize_glenv(", "int realize_bufferIndex(")
    ordered(use_program, ("gles_glUseProgram(glstate->gleshard->program)",
                          "ios_wo49_transform_program_realized(glprogram)",
                          "fpe_SyncUniforms("),
            "post-native-bind/pre-sync program proof", failures)
    draw = section(fpe, "void APIENTRY_GL4ES fpe_glDrawElements(",
                   "void APIENTRY_GL4ES fpe_glDrawArraysInstanced(")
    ordered(draw, ("realize_glenv(", "realize_bufferIndex();",
                   "ios_wo49_transform_before_draw(",
                   "ios_wo49_topology_realized(", "gles_glDrawElements("),
            "immediately-pre-native draw proof", failures)

    go_float = section(uniform, "void GoUniformfv(", "void GoUniformiv(")
    if go_float.count("ios_wo49_transform_cache_uniform") != 2:
        failures.append("float cache proof: expected unchanged and updated cache hooks")
    ordered(go_float, ("ios_wo49_transform_native_uniform(", "switch (size)",
                       "gles_glUniform1fv("),
            "immediately-pre-native float upload proof", failures)
    go_matrix = section(uniform, "void GoUniformMatrix4fv(", "int GetUniformi(")
    if go_matrix.count("ios_wo49_transform_cache_uniform") != 2:
        failures.append("matrix cache proof: expected unchanged and updated cache hooks")
    ordered(go_matrix, ("ios_wo49_transform_native_uniform(",
                        "gles_glUniformMatrix4fv("),
            "immediately-pre-native matrix upload proof", failures)
    for wrapper, entry in (("gl4es_glUniform1i", "glUniform1i"),
                           ("gl4es_glUniform3fv", "glUniform3fv"),
                           ("gl4es_glUniform4fv", "glUniform4fv")):
        body = section(uniform, f"void APIENTRY_GL4ES {wrapper}(", "\n}")
        ordered(body, ("ios_wo49_transform_application_uniform(", entry,
                       "GoUniform"), f"application wrapper {entry}", failures)

    if patch_headers(gl_patch) != GL4ES_PATCH_FILES:
        failures.append(f"GL4ES patch scope: got {sorted(patch_headers(gl_patch))}")
    gl_added = added_lines(gl_patch)
    reject(gl_added, r"\b(?:gles_gl|glBind|glDraw|glUniform)[A-Za-z0-9_]*\s*\(",
           "diagnostic-added GL mutation", failures)
    reject(gl_added, r"\b(?:malloc|calloc|realloc|free|glGetError|glReadPixels|sleep|usleep)\s*\(",
           "diagnostic-added forbidden call", failures)
    for token in ("gl4es-wo49-transform-ios.patch", "validate-ios-wo49-transform.py"):
        require(build, token, "CI patch/validator route", failures)

    if require_diffusion:
        studio = files["studio"]
        diff_patch = files["diff_patch"]
        begin = section(studio, "bool CStudioModelRenderer::WO49BeginTransform(",
                        "#endif")
        for token in (
            '"models/bmec/cars/truck_new.mdl"', '"maps/ch1map0.bsp"',
            '"#define MAXSTUDIOBONES 1"', '"STUDIO_VERTEX_LIGHTING"',
            '"STUDIO_BONEWEIGHTING"', '"STUDIO_SWAY_FOLIAGE"',
            "mesh->wo49_layout != 1", "bones_upload", "entry->wo49_token",
            "desc.elementOrdinal = 0", "desc.localIndex = mesh->wo49_firstIndex",
            "desc.localPosition", "desc.boneQuaternion", "desc.bonePosition",
            "RI->modelviewMatrix.CopyToArray", "RI->projectionMatrix.CopyToArray",
            "RI->projectionMatrix.Concat( RI->modelviewMatrix )",
            "bone.VectorTransform( local )", "mvp.VectorTransform( world )",
            "pWO49TransformBegin( &desc )", "wo49_transform_claimed = true",
            "if( wo49_transform_claimed ||", "if( !rigid || !vertex_lighting || bone_weighting )",
        ):
            require(begin, token, "Diffusion exact producer", failures)
        draw_studio = section(studio, "void CStudioModelRenderer::DrawStudioMeshes( void )",
                              "void CStudioModelRenderer::DrawStudioMeshesShadow(")
        ordered(draw_studio, ("GL_BindShader(", "WO49BeginTransform(",
                              "pglUniform4fvARB( RI->currentshader->u_BoneQuaternion"),
                "producer before required application upload", failures)
        require(studio, "pWO49TransformFinish( wo49_token )",
                "single draw terminal fallback", failures)
        if patch_headers(diff_patch) != DIFFUSION_PATCH_FILES:
            failures.append(f"Diffusion patch scope: got {sorted(patch_headers(diff_patch))}")
        diff_added = added_lines(diff_patch)
        reject(diff_added, r"\b(?:pgl|glBind|glDraw|glUniform)[A-Za-z0-9_]*\s*\(",
               "Diffusion diagnostic-added GL mutation", failures)
        reject(diff_added, r"\b(?:malloc|calloc|realloc|free|glGetError|glReadPixels|sleep|usleep)\s*\(",
               "Diffusion diagnostic-added forbidden call", failures)
    failures.extend(validate_fixtures())
    return failures


def self_test(files: dict[str, str], require_diffusion: bool) -> list[str]:
    failures: list[str] = []
    cases = [
        ("cap raised", "trace", "tokens=1 programs=1 draws=1 frames=1",
         "tokens=2 programs=1 draws=1 frames=1"),
        ("pre-realize lost", "fpe", "ios_wo49_transform_program_realized(glprogram)",
         "program_realization_omitted(glprogram)"),
        ("missing terminal field", "trace", "if(!u->native_seen)",
         "if(0 /* native evidence ignored */)"),
        ("stale attribute read", "trace", "ios_wo49_bytes_checksum",
         "glGetVertexAttribfv(7, 0, 0); /* ios_wo49_bytes_checksum */"),
        ("error queue", "trace", "ios_wo49_bytes_checksum",
         "glGetError(); /* ios_wo49_bytes_checksum */"),
        ("runtime mutation", "gl_patch", "+    ios_wo49_transform_before_draw(",
         "+    gles_glDrawArrays(0, 0, 0);\n+    ios_wo49_transform_before_draw("),
    ]
    if require_diffusion:
        cases.extend((
            ("more than one claim", "studio", "if( wo49_transform_claimed ||",
             "if( false ||"),
            ("bone weighting accepted", "studio", "if( !rigid || !vertex_lighting || bone_weighting )",
             "if( !rigid || !vertex_lighting )"),
            ("post-bone producer", "studio", "WO49BeginTransform( entry, pMesh, num_bones,",
             "/* WO49BeginTransform moved after bone uploads */"),
        ))
    for label, key, old, new in cases:
        if old not in files[key]:
            failures.append(f"self-test setup {label}: token absent")
            continue
        mutated = dict(files)
        mutated[key] = mutated[key].replace(old, new)
        if not validate(mutated, require_diffusion):
            failures.append(f"self-test {label}: invalid mutation accepted")
    return failures


def load_files(repo: pathlib.Path, gl4es: pathlib.Path,
               diffusion: pathlib.Path | None) -> dict[str, str]:
    files = {
        "trace": read(gl4es / "src/gl/indextrace.c"),
        "trace_h": read(gl4es / "src/gl/indextrace.h"),
        "uniform": read(gl4es / "src/gl/uniform.c"),
        "fpe": read(gl4es / "src/gl/fpe.c"),
        "lookup": read(gl4es / "src/gl/gl_lookup.c"),
        "gl_patch": read(repo / "scripts/ios/gl4es-wo49-transform-ios.patch"),
        "diff_patch": read(repo / "scripts/ios/diffusion-wo49-transform-ios.patch"),
        "build": read(repo / "scripts/gha/build_ios.sh") + read(repo / "scripts/ios/builddiffusion.sh"),
        "verify": read(repo / "scripts/ios/verify_ipa.sh"),
    }
    if diffusion is not None:
        files["studio"] = read(diffusion / "client/render/r_studio.cpp")
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=pathlib.Path)
    parser.add_argument("gl4es", type=pathlib.Path)
    parser.add_argument("diffusion", nargs="?", type=pathlib.Path)
    parser.add_argument("--gl4es-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    gl4es = args.gl4es.resolve()
    diffusion = args.diffusion.resolve() if args.diffusion else None
    got_gl4es = revision(gl4es)
    if got_gl4es != GL4ES_REF:
        print(f"FAIL: expected GL4ES {GL4ES_REF}, got {got_gl4es}", file=sys.stderr)
        return 1
    if not args.gl4es_only:
        if diffusion is None:
            parser.error("DIFFUSION is required unless --gl4es-only is used")
        got_diffusion = revision(diffusion)
        if got_diffusion != DIFFUSION_REF:
            print(f"FAIL: expected Diffusion {DIFFUSION_REF}, got {got_diffusion}", file=sys.stderr)
            return 1
    files = load_files(repo, gl4es, None if args.gl4es_only else diffusion)
    failures = validate(files, not args.gl4es_only)
    if args.self_test:
        failures.extend(self_test(files, not args.gl4es_only))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Validated WO49 Phase E transform discriminator: producer -> GL4ES cache -> native upload -> draw")
    print("Validated fixtures: source, reflection/cache, native-forward, full match, missing, conditional sway")
    if args.self_test:
        print("Validated rejection suite: cap, ordering, required evidence, stale attribute, GL mutation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
