#!/usr/bin/env python3
"""Validate Work Order 52 Phase B's diagnostics-only material trace."""

from __future__ import annotations

import argparse
import copy
import pathlib
import re
import subprocess
import sys


GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
DIFFUSION_REF = "14d156bf3a6993c172697fac83a937836c3b5561"
GL_PATCH = "scripts/ios/gl4es-wo52-material-trace-ios.patch"
DIFFUSION_PATCH = "scripts/ios/diffusion-wo52-material-trace-ios.patch"
GL_HEADERS = {
    "src/gl/drawing.c", "src/gl/fpe.c", "src/gl/gl_lookup.c",
    "src/gl/indextrace.c", "src/gl/indextrace.h", "src/gl/list.c",
    "src/gl/list.h", "src/gl/listdraw.c", "src/gl/texture_params.c",
}
DIFFUSION_HEADERS = {
    "client/render/r_local.h", "client/render/r_misc.cpp",
    "client/render/r_shader.cpp", "client/render/r_studio.cpp",
    "client/render/r_studio.h", "client/render/r_world.cpp",
}
MARKERS = (
    "WO52 material trace policy:", "WO52 material trace producer:",
    "WO52 material trace shader:", "WO52 material trace bind:",
    "WO52 material trace gl4es:", "WO52 material trace native:",
    "WO52 material trace transition:", "WO52 material trace terminal:",
    "WO52 material trace summary:",
)
TERMINALS = (
    "producer/material selection mismatch", "bind/cache skip mismatch",
    "GL4ES logical-to-native realization mismatch",
    "sampler/program routing mismatch",
    "texture/sampler chain matches but captured color/material/shader state differs",
    "incomplete/overflow",
)


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def revision(path: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={path.resolve().as_posix()}",
         "-C", str(path), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


def reject(text: str, pattern: str, label: str, failures: list[str]) -> None:
    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
        failures.append(f"{label}: forbidden pattern {pattern!r}")


def headers(text: str) -> set[str]:
    return set(re.findall(r"^diff --git a/(\S+) b/\S+$", text, re.MULTILINE))


def additions(text: str) -> str:
    return "\n".join(line[1:] for line in text.splitlines()
                     if line.startswith("+") and not line.startswith("+++"))


def section(text: str, start: str, end: str | None = None) -> str:
    begin = text.find(start)
    if begin < 0:
        return ""
    finish = text.find(end, begin + len(start)) if end else -1
    return text[begin:] if finish < 0 else text[begin:finish]


def ordered(text: str, tokens: tuple[str, ...], label: str,
            failures: list[str]) -> None:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            failures.append(f"{label}: missing ordered token {token!r}")
            return


def classify(state: dict) -> str:
    if not state["ready"]:
        return TERMINALS[0]
    if not state["bind"]:
        return TERMINALS[5]
    if state["cache_after"] != state["requested"]:
        return TERMINALS[1]
    if not state["route"] or not state["native"]:
        return TERMINALS[5]
    if state["logical"] != state["expected"] or state["native_name"] != state["glname"]:
        return TERMINALS[2]
    if not state["sampler"]:
        return TERMINALS[3]
    return TERMINALS[4]


def validate_fixtures() -> list[str]:
    failures: list[str] = []
    base = {
        "ready": True, "bind": True, "requested": 17, "cache_after": 17,
        "route": True, "native": True, "logical": 71, "expected": 71,
        "native_name": 171, "glname": 171, "sampler": True,
    }
    if classify(base) != TERMINALS[4]:
        failures.append("positive classifier fixture did not reach chain-match terminal")
    cases = (
        ("producer", lambda x: x.update(ready=False), TERMINALS[0]),
        ("cache", lambda x: x.update(cache_after=18), TERMINALS[1]),
        ("missing bind", lambda x: x.update(bind=False), TERMINALS[5]),
        ("route loss", lambda x: x.update(route=False), TERMINALS[5]),
        ("missing native", lambda x: x.update(native=False), TERMINALS[5]),
        ("stale logical", lambda x: x.update(logical=72), TERMINALS[2]),
        ("stale native", lambda x: x.update(native_name=172), TERMINALS[2]),
        ("sampler", lambda x: x.update(sampler=False), TERMINALS[3]),
    )
    for label, mutate, wanted in cases:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        got = classify(candidate)
        if got != wanted:
            failures.append(f"fixture {label}: expected {wanted}, got {got}")
    return failures


def validate(files: dict[str, str], require_diffusion: bool) -> list[str]:
    failures: list[str] = []
    trace = files["trace"]
    trace_h = files["trace_h"]
    drawing = files["drawing"]
    list_c = files["list"]
    list_h = files["list_h"]
    listdraw = files["listdraw"]
    fpe = files["fpe"]
    texture = files["texture"]
    lookup = files["lookup"]
    engine = files["engine"]
    build = files["build"]
    diffusion_build = files["diffusion_build"]
    verify = files["verify"]
    gl_patch = files["gl_patch"]

    for marker in MARKERS:
        require(trace, marker, "engine.log marker", failures)
        require(verify, marker, "packaged marker contract", failures)
    engine_bind_contract = section(
        verify, "if ! grep -q 'gl4es_iOSWO52EngineBind'", "fi"
    )
    require(engine_bind_contract, '"$GL4ES_RENDERER_STRINGS"',
            "packaged engine-bind bridge owner", failures)
    reject(engine_bind_contract, r'"\$ENGINE_STRINGS"',
           "packaged engine-bind bridge owner", failures)
    for result in TERMINALS:
        require(trace, result, "terminal classifier", failures)

    for token in (
        "IOS_WO52_MATERIAL_TOKEN_CAP 16u", "IOS_WO52_MATERIAL_UNIT_CAP 6u",
        "IOS_WO52_MATERIAL_LIST_CAP 32u", "identities<=16",
        "records_per_stage<=1", "fixed-storage=1",
        "error_queue=untouched", "mutation=none", "state_restored=not-mutated",
        "first-draw+first-post-transition", "direct+deferred+renderlist+replay",
        "ios_wo52_material_terminal", "ios_wo52_material_route_loss",
        "ios_wo52_material_cache_unit", "IOS_WO52_MODE_COLORMAP",
        "gl4es-immediate-bind-observation", "gl4es-native-shadow",
        "model_handle=%u", "gl_diffuse_id=%d", "selected_mode=%s",
        "fallback=%d", "animation_id=%d", "monitor=%d", "drone=%d",
        "normal=%d", "cube=%d", "interior=%d", "blend=%d", "mask=%d",
        "sampler=%s:type0x%04x:extent%d:native_location%d:value%d:req%d:act%d",
        "logical_program_match=%d", "render_color=type0x%04x/extent%d",
        "mesh_params2=type0x%04x/extent%d", "studio_lighting=type0x%04x/extent%d",
        "ios_wo52_material_uniform_location", "GetUniformi(program, sampler->id)",
    ):
        require(trace + trace_h + files.get("studio", ""), token,
                "bounded structural proof", failures)
    reject(trace, r"\b(malloc|calloc|realloc|free|glGetError|glReadPixels|glGetVertexAttrib[A-Za-z0-9_]*|sleep|usleep)\s*\(",
           "trace observer", failures)
    reject(trace, r"all renderer state correct", "unsupported diagnostic claim", failures)
    require(trace, "!sampler || sampler->type != expected_type ||",
            "sampler type/extent classifier", failures)

    for symbol in (
        "gl4es_iOSWO52MaterialBegin", "gl4es_iOSWO52MaterialCache",
        "gl4es_iOSWO52EngineBind", "gl4es_iOSWO52MaterialArm",
        "gl4es_iOSWO52MaterialFinish", "gl4es_iOSWO52MaterialTransition",
    ):
        require(lookup, symbol, "dynamic diagnostic API", failures)
    require(engine, 'gEngfuncs.GL_GetProcAddress( "gl4es_iOSWO52EngineBind" )',
            "engine bind hook", failures)
    engine_bind = section(engine, "void GL_Bind(", "void GL_DisableAllTexGens(")
    ordered(engine_bind, ("wo52_before_logical", "R_GetTexture( texnum )",
                          "if( glState.currentTextures[tmu] == texture->texnum )",
                          "pglBindTexture(", "pIOSWO52EngineBind("),
            "engine cache/bind ordering", failures)

    for draw_name in ("glDrawRangeElements", "glDrawElements"):
        body = section(drawing, f"void APIENTRY_GL4ES gl4es_{draw_name}(",
                       "void APIENTRY_GL4ES" if draw_name == "glDrawRangeElements" else None)
        ordered(body, ("ios_wo52_material_ingress(", "ios_wo52_attach_list(",
                       "ios_wo52_material_set_active("),
                f"{draw_name} route ownership", failures)
    for token in ("renderlist-token-cap", "deferred-renderlist",
                  "intercept-renderlist", "renderlist-merged-replay"):
        require(drawing + list_c, token, "render-list ownership", failures)
    require(list_h, "ios_wo52_tokens[IOS_WO52_MATERIAL_LIST_CAP]",
            "bounded render-list token storage", failures)
    ordered(list_h, ("#define IOS_WO52_MATERIAL_LIST_CAP 32u",
                     "ios_wo52_tokens[IOS_WO52_MATERIAL_LIST_CAP]"),
            "self-contained render-list cap", failures)

    direct = section(fpe, "void APIENTRY_GL4ES fpe_glDrawElements(",
                     "void APIENTRY_GL4ES fpe_glDrawArraysInstanced(")
    ordered(direct, ("realize_glenv(", "realize_bufferIndex();",
                     "ios_wo52_material_native(", "gles_glDrawElements("),
            "direct post-realization pre-native proof", failures)
    replay = section(listdraw, "realize_textures(1);", "wantBufferIndex(old_index);")
    ordered(replay, ("realize_textures(1);", "ios_wo52_material_set_replay(",
                     "ios_wo52_material_native(", "gles_glDrawElements("),
            "replay post-realization pre-native proof", failures)
    for token in ("selection-render-mode", "polygon-line-transform"):
        require(listdraw, token, "deterministic route-loss", failures)
    require(listdraw,
            'ios_wo52_material_route_loss(list->ios_wo52_tokens[wo52_i],\n                        "selection-render-mode")',
            "selection-mode WO52 route-loss call", failures)
    require(texture, "ios_wo52_material_gl4es_bind", "GL4ES bind ingress", failures)

    if headers(gl_patch) != GL_HEADERS:
        failures.append(f"GL4ES patch scope changed: {sorted(headers(gl_patch))}")
    gl_added = additions(gl_patch)
    reject(gl_added, r"\b(glGetError|glReadPixels|sleep|usleep)\s*\(",
           "GL4ES added observer", failures)
    reject(gl_added, r"\b(?:printf|fprintf|LOGD)\s*\(",
           "diagnostic stdout/stderr route", failures)
    reject(gl_added,
           r"\b(?:gles_gl|gl4es_gl)(?:ActiveTexture|BindTexture|UseProgram|Draw|Uniform)[A-Za-z0-9_]*\s*\(",
           "diagnostic-added GL state mutation", failures)
    for token in ("gl4es-wo52-material-trace-ios.patch",
                  "validate-ios-wo52-material-trace.py"):
        require(build, token, "engine/GL4ES build route", failures)

    if require_diffusion:
        studio = files["studio"]
        studio_h = files["studio_h"]
        diff_patch = files["diff_patch"]
        for token in (
            "WO52BeginMaterialTrace", "WO52RecordMaterialCache",
            "wo52_bodypart", "wo52_mesh", "wo52_requested[6]",
            "wo52_before[6]", "wo52_before_mode[6]", "wo52_issued[6]",
            "texture_object", "gl_normalmap_id", "gl_interiormap_id",
            "gl_blendtex_id", "gl_colormask_id", "wo52_cubemap_texture",
            "shaderIndex", "logicalProgram", "optionsHash", "renderColor",
            "meshParams", "modelHandle", "diffuseObject", "fallbackObject",
            "animationId", "monitorObject", "droneObject", "normalObject",
            "cubemapObject", "interiorObject", "blendObject", "maskObject",
            "material_cache_epoch", "pWO52MaterialArm",
            "pWO52MaterialFinish", "R_IOSWO52MaterialTransition",
            '"Mod_PrepareModelInstances"', '"Mod_ThrowModelInstances"',
            '"Mod_LoadWorld"', '"R_NewMap"', '"VidInit"',
            '"shader-reuse:%s"', '"shader-create:%s"',
            '"transition-overflow-cap-128"',
            "wo52_transition_hashes[128]", "wo52_transition_generations[128]",
            "wo52_transition_hashes[i] == event_hash",
        ):
            require(studio + studio_h + files["world"] + files["misc"] + files["shader"],
                    token, "Diffusion producer/transition coverage", failures)
        if studio.count("WO52BeginMaterialTrace( entry,") != 2:
            failures.append("exactly solid and dynamic-light producer routes must be traced")
        if studio.count("WO52RecordMaterialCache( wo52_token,") != 2:
            failures.append("exactly solid and dynamic-light cache stages must be traced")
        if studio.count("entry->wo49_token, wo52_token") != 2:
            failures.append("both traced studio routes must arm the same WO52 token at draw")
        if studio.count("wo52_before[0] = cached_texture_object;") != 2:
            failures.append("both producer routes must capture the pre-decision base cache")
        require(studio, "pWO52MaterialTransition && wo52_transition_count < 128",
                "bounded transition marker route", failures)
        if headers(diff_patch) != DIFFUSION_HEADERS:
            failures.append(f"Diffusion patch scope changed: {sorted(headers(diff_patch))}")
        diff_added = additions(diff_patch)
        reject(diff_added, r"\b(glGetError|glReadPixels|sleep|usleep)\s*\(",
               "Diffusion added observer", failures)
        for token in ("diffusion-wo52-material-trace-ios.patch",
                      "validate-ios-wo52-material-trace.py"):
            require(diffusion_build, token, "Diffusion build route", failures)

    failures.extend(validate_fixtures())
    return failures


def self_test(files: dict[str, str], require_diffusion: bool) -> list[str]:
    failures: list[str] = []
    cases = [
        ("unbounded tokens", "trace_h", "IOS_WO52_MATERIAL_TOKEN_CAP 16u",
         "IOS_WO52_MATERIAL_TOKEN_CAP 1024u"),
        ("list cap not header-visible", "list_h",
         "#define IOS_WO52_MATERIAL_LIST_CAP 32u",
         "/* list cap declaration omitted */"),
        ("early native hook", "fpe", "ios_wo52_material_native(\"fpe_glDrawElements\");",
         "/* native observation removed */"),
        ("missing replay", "listdraw", "ios_wo52_material_set_replay(",
         "ios_wo52_material_replay_omitted("),
        ("route loss removed", "listdraw",
         'ios_wo52_material_route_loss(list->ios_wo52_tokens[wo52_i],\n                        "selection-render-mode")',
         'ios_wo52_material_route_omitted(list->ios_wo52_tokens[wo52_i],\n                        "selection-render-mode")'),
        ("error drain", "trace", "ios_wo52_material_summary(void)",
         "ios_wo52_material_summary(void) { glGetError(); } /*"),
        ("stale attribute query", "trace", "ios_wo52_material_summary(void)",
         "ios_wo52_material_summary(void) { glGetVertexAttribiv(0, 0, 0); } /*"),
        ("stdout route", "gl_patch", "+    ios_wo52_material_native(\"fpe_glDrawElements\");",
         "+    printf(\"WO52 stdout\");\n+    ios_wo52_material_native(\"fpe_glDrawElements\");"),
        ("state mutation", "gl_patch", "+    ios_wo52_material_native(\"fpe_glDrawElements\");",
         "+    gles_glActiveTexture(GL_TEXTURE0);\n+    ios_wo52_material_native(\"fpe_glDrawElements\");"),
        ("unsupported terminal", "trace", TERMINALS[4], "all renderer state correct"),
        ("missing sampler type", "trace", "sampler->type != expected_type",
         "sampler->type == expected_type"),
        ("wrong packaged engine-bind owner", "verify",
         "if ! grep -q 'gl4es_iOSWO52EngineBind' \"$GL4ES_RENDERER_STRINGS\"",
         "if ! grep -q 'gl4es_iOSWO52EngineBind' \"$ENGINE_STRINGS\""),
    ]
    if require_diffusion:
        cases.extend((
            ("missing solid producer", "studio", "WO52BeginMaterialTrace( entry,",
             "WO52BeginMaterialTraceOmitted( entry,"),
            ("stale cache input", "studio", "wo52_before[0] = cached_texture_object;",
             "wo52_before[0] = texture_object;"),
            ("unbounded transition", "studio", "wo52_transition_count < 128",
             "true /* unbounded */"),
        ))
    for label, key, old, new in cases:
        if old not in files[key]:
            failures.append(f"self-test setup {label}: token absent")
            continue
        mutated = dict(files)
        mutated[key] = files[key].replace(old, new, 1)
        if not validate(mutated, require_diffusion):
            failures.append(f"self-test {label}: invalid mutation accepted")
    return failures


def load(repo: pathlib.Path, gl4es: pathlib.Path,
         diffusion: pathlib.Path | None) -> dict[str, str]:
    files = {
        "trace": read(gl4es / "src/gl/indextrace.c"),
        "trace_h": read(gl4es / "src/gl/indextrace.h"),
        "drawing": read(gl4es / "src/gl/drawing.c"),
        "list": read(gl4es / "src/gl/list.c"),
        "list_h": read(gl4es / "src/gl/list.h"),
        "listdraw": read(gl4es / "src/gl/listdraw.c"),
        "fpe": read(gl4es / "src/gl/fpe.c"),
        "texture": read(gl4es / "src/gl/texture_params.c"),
        "lookup": read(gl4es / "src/gl/gl_lookup.c"),
        "engine": read(repo / "ref/gl/gl_backend.c"),
        "build": read(repo / "scripts/gha/build_ios.sh"),
        "diffusion_build": read(repo / "scripts/ios/builddiffusion.sh"),
        "verify": read(repo / "scripts/ios/verify_ipa.sh"),
        "gl_patch": read(repo / GL_PATCH),
    }
    if diffusion:
        files.update({
            "studio": read(diffusion / "client/render/r_studio.cpp"),
            "studio_h": read(diffusion / "client/render/r_studio.h"),
            "world": read(diffusion / "client/render/r_world.cpp"),
            "misc": read(diffusion / "client/render/r_misc.cpp"),
            "shader": read(diffusion / "client/render/r_shader.cpp"),
            "diff_patch": read(repo / DIFFUSION_PATCH),
        })
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=pathlib.Path)
    parser.add_argument("gl4es", type=pathlib.Path)
    parser.add_argument("diffusion", nargs="?", type=pathlib.Path)
    parser.add_argument("--gl4es-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    require_diffusion = not args.gl4es_only
    if require_diffusion and args.diffusion is None:
        parser.error("Diffusion path is required unless --gl4es-only is used")
    if revision(args.gl4es) != GL4ES_REF:
        print(f"expected GL4ES {GL4ES_REF}, got {revision(args.gl4es)}", file=sys.stderr)
        return 1
    if require_diffusion and revision(args.diffusion) != DIFFUSION_REF:
        print(f"expected Diffusion {DIFFUSION_REF}, got {revision(args.diffusion)}", file=sys.stderr)
        return 1
    files = load(args.repo, args.gl4es, args.diffusion if require_diffusion else None)
    failures = validate(files, require_diffusion)
    if args.self_test:
        failures.extend(self_test(files, require_diffusion))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("WO52 material trace validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
