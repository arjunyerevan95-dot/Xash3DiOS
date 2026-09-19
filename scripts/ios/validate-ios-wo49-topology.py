#!/usr/bin/env python3
"""Validate the WO49 Phase B diagnostics-only topology discriminator."""

from __future__ import annotations

import argparse
import copy
import hashlib
import pathlib
import re
import subprocess
import sys


GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
DIFFUSION_REF = "14d156bf3a6993c172697fac83a937836c3b5561"
FROZEN_HASHES = {
    "gl4es-drawable-bridge-ios.patch": "f9e521fabf164801341c222ed802f2be24439b4e526094f122997ca147485cb1",
    "sdl2-drawable-bridge-ios.patch": "49b867a0f01b488e7bf6a85575b0363e6d1325cac1ef0249e2b421a0e13f7826",
    "gl4es-uint-elements-ios.patch": "57cbb4b8899eb182a71bee9e9fba1fe29334e541b3aeb4cb4ba6ee327df5f5fe",
    "gl4es-index-trace-ios.patch": "e226737a2bc6ac90c15141efb48e5259fffaf420c1e39152891750cdefc23874",
}
GL4ES_PATCH_FILES = {
    "src/gl/indextrace.h", "src/gl/indextrace.c", "src/gl/gl_lookup.c",
    "src/gl/list.h", "src/gl/drawing.c", "src/gl/list.c",
    "src/gl/listdraw.c", "src/gl/fpe.c",
}
DIFFUSION_PATCH_FILES = {
    "engine/studio.h", "client/render/r_studio.h", "client/render/r_studio.cpp",
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


def patch_headers(text: str) -> set[str]:
    return set(re.findall(r"^diff --git a/(\S+) b/\S+$", text, re.MULTILINE))


def added_lines(text: str) -> str:
    return "\n".join(
        line[1:] for line in text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def ordered(text: str, tokens: tuple[str, ...], label: str, failures: list[str]) -> None:
    cursor = -1
    for token in tokens:
        location = text.find(token, cursor + 1)
        if location < 0:
            failures.append(f"{label}: missing ordered token {token!r}")
            return
        if location <= cursor:
            failures.append(f"{label}: incorrect order at {token!r}")
            return
        cursor = location


def section(text: str, start: str, end: str | None = None) -> str:
    begin = text.find(start)
    if begin < 0:
        return ""
    if end is None:
        return text[begin:]
    finish = text.find(end, begin + len(start))
    return text[begin:] if finish < 0 else text[begin:finish]


def topology_fixture() -> tuple[dict, dict]:
    expected = {
        "native_vao": 0, "logical_vao": 31, "vbo": 41, "ebo": 51,
        "source": "ebo-offset", "base": 0, "range": (0, 799),
        "index_checksum": 0x1234ABCD, "storage_generation": 7,
        "position": 0,
        "attrs": {
            0: {"enabled": 1, "vbo": 41, "stride": 60, "offset": 0, "bounds": 1},
            3: {"enabled": 1, "vbo": 41, "stride": 60, "offset": 12, "bounds": 1},
        },
    }
    return expected, copy.deepcopy(expected)


def compare_fixture(expected: dict, actual: dict) -> str | None:
    for field in ("native_vao", "logical_vao", "vbo", "ebo", "source",
                  "base", "range", "index_checksum", "storage_generation"):
        if expected[field] != actual[field]:
            return field
    position = expected["position"]
    if position not in actual["attrs"]:
        return "position-missing"
    for index, wanted in expected["attrs"].items():
        got = actual["attrs"].get(index)
        if got is None:
            return "attribute-missing"
        for field in ("enabled", "vbo", "stride", "offset", "bounds"):
            if wanted[field] != got[field]:
                return f"attribute-{field}"
    return None


def validate_fixtures() -> list[str]:
    failures: list[str] = []
    expected, actual = topology_fixture()
    cases = (
        ("wrong native VAO", lambda x: x.update(native_vao=9), "native_vao"),
        ("wrong native VBO", lambda x: x["attrs"][0].update(vbo=99), "attribute-vbo"),
        ("wrong stride", lambda x: x["attrs"][0].update(stride=32), "attribute-stride"),
        ("wrong offset", lambda x: x["attrs"][0].update(offset=16), "attribute-offset"),
        ("disabled position", lambda x: x["attrs"][0].update(enabled=0), "attribute-enabled"),
        ("missing position", lambda x: x["attrs"].pop(0), "position-missing"),
        ("wrong EBO", lambda x: x.update(ebo=77), "ebo"),
        ("wrong classification", lambda x: x.update(source="client-pointer"), "source"),
        ("lost base", lambda x: x.update(base=3), "base"),
        ("lost range", lambda x: x.update(range=(0, 0)), "range"),
        ("stale deferred storage", lambda x: x.update(storage_generation=6), "storage_generation"),
    )
    for label, mutate, wanted in cases:
        candidate = copy.deepcopy(actual)
        mutate(candidate)
        got = compare_fixture(expected, candidate)
        if got != wanted:
            failures.append(f"fixture {label}: expected {wanted}, got {got}")
    if compare_fixture(expected, actual) is not None:
        failures.append("fixture full match: matching topology was rejected")
    return failures


def validate(files: dict[str, str], repo: pathlib.Path | None,
             require_diffusion: bool) -> list[str]:
    failures: list[str] = []
    trace = files["trace"]
    trace_h = files["trace_h"]
    drawing = files["drawing"]
    fpe = files["fpe"]
    list_h = files["list_h"]
    list_c = files["list_c"]
    listdraw = files["listdraw"]
    lookup = files["lookup"]
    gl_patch = files["gl_patch"]
    build = files["build"]
    verify = files["verify"]

    for marker in (
        "WO49 topology policy:", "WO49 topology producer:",
        "WO49 topology ingress:", "WO49 topology route:",
        "WO49 topology realized:", "WO49 topology mismatch:",
        "WO49 topology absence:", "WO49 topology summary:",
    ):
        require(trace, marker, "required engine.log markers", failures)
    for token in (
        "IOS_WO49_TOPOLOGY_TOKEN_CAP 4u", "ios_wo49_records[IOS_WO49_TOPOLOGY_TOKEN_CAP]",
        "++ios_wo49_next_id", "if(record->stage >= 3)",
        "if(!record || record->absence_emitted || record->stage >= 4)",
        "if(record->mismatch_emitted)", "ios_wo49_summary_emitted",
        "first_mismatch_per_token=bounded", "records_per_stage<=1",
    ):
        require(trace + trace_h, token, "bounds and one-record contract", failures)
    reject(trace, r"\b(malloc|calloc|realloc|free)\s*\(", "per-draw allocation", failures)
    reject(trace + drawing + fpe + list_c + listdraw,
           r"\b(glGetError|glReadPixels|sleep|usleep)\s*\(",
           "forbidden observation/mutation", failures)

    for token in (
        "producer.attrCount", "logical_attrs", "logical_vertex_checksum",
        "logical_position_checksum", "route_position_checksum",
        "glstate->gleshard->vertexattrib[index]", "program->va_size[index]",
        "native_attr->real_buffer", "native_attr->stride", "native_attr->real_pointer",
        "native_attr->normalized", "native_attr->integer", "native_attr->divisor",
        "highest < buffer_bytes", "attribute-bounds", "position-attribute",
        "native_vao=0", "vao_policy=gl4es-emulated", "native-ebo",
        "route-position-checksum", "storage=fixed-owned",
    ):
        require(trace, token, "producer/ingress/realized topology coverage", failures)

    fpe_draw = section(fpe, "void APIENTRY_GL4ES fpe_glDrawElements(",
                       "void APIENTRY_GL4ES fpe_glDrawElementsInstanced(")
    ordered(fpe_draw, ("realize_glenv", "realize_bufferIndex();",
                       "ios_wo49_topology_realized(", "gles_glDrawElements("),
            "true direct post-realization hook", failures)
    replay_at = listdraw.find("ios_wo49_topology_set_replay(")
    if replay_at < 0 or listdraw.find("gles_glDrawElements(", replay_at) < replay_at:
        failures.append("deferred/list replay: token state is not set before the GLES draw")
    require(listdraw, "listActiveVBO(list", "deferred vertex realization", failures)

    for token in (
        'ios_wo49_topology_ingress("glDrawRangeElements"',
        'ios_wo49_topology_ingress("glDrawElements"',
        'ios_wo49_topology_route(ios_wo49_token, "direct"',
        'ios_wo49_topology_route(ios_wo49_token, "deferred"',
        'ios_wo49_topology_route(ios_wo49_token, "intercept"',
        "ios_wo49_topology_set_active(ios_wo49_token)",
    ):
        require(drawing, token, "direct/intercept/deferred ingress", failures)
    if drawing.count("ios_wo49_topology_set_active(ios_wo49_token);") != 2:
        failures.append("direct route coverage: expected range and ordinary token activation")
    for token in (
        "ios_wo49_tokens[4]", "ios_wo49_offsets[4]", "ios_wo49_counts[4]",
        "ios_wo49_vertex_offsets[4]", "ios_wo49_vertex_counts[4]",
    ):
        require(list_h, token, "fixed render-list token storage", failures)
    for token in (
        "a->ios_wo49_tokens[slot]", "a->ios_wo49_offsets[slot]",
        "a->ios_wo49_vertex_offsets[slot]", "ios_wo49_topology_route",
    ):
        require(list_c, token, "append/merge propagation", failures)
    for token in (
        'gl4es_iOSWO49TopologyProducer', 'gl4es_iOSWO49TopologyArm',
        'gl4es_iOSWO49TopologyFinish', 'gl4es_iOSWO49TopologyAbsence',
    ):
        require(lookup, token, "exported diagnostic API", failures)

    if patch_headers(gl_patch) != GL4ES_PATCH_FILES:
        failures.append(f"GL4ES patch scope: got {sorted(patch_headers(gl_patch))}")
    gl_added = added_lines(gl_patch)
    reject(gl_added, r"\b(?:glBind|gles_gl|pgl|glUniform)[A-Za-z0-9_]*\s*\(",
           "diagnostic-added GL state/data mutation", failures)
    reject(gl_added, r"\b(?:malloc|calloc|realloc|glGetError|glReadPixels|sleep|usleep)\s*\(",
           "diagnostic-added forbidden call", failures)
    for token in ("gl4es-wo49-topology-ios.patch", "validate-ios-wo49-topology.py"):
        require(build, token, "CI patch/validator route", failures)
    for marker in ("WO49 topology policy:", "WO49 topology producer:",
                   "WO49 topology realized:", "WO49 topology summary:"):
        require(verify, marker, "packaged marker contract", failures)

    if require_diffusion:
        studio = files["studio"]
        diff_patch = files["diff_patch"]
        produce = section(studio, "unsigned long long CStudioModelRenderer::WO49ProduceTopology(",
                          "bool CStudioModelRenderer::WO49BeginTransform(")
        add_mesh = section(studio, "void CStudioModelRenderer::AddMeshToDrawList(",
                           "void CStudioModelRenderer::AddBodyPartToDrawList(")
        for token in (
            "MF_VERTEX_LIGHTING", "m_VlCache", "wo49_aggregateVerts <= 65535u",
            "pWO49TopologyProducer( &desc )", "desc.indexChecksum",
            "desc.vertexChecksum", "desc.positionChecksum", "WO49DescribeLayout( &desc )",
        ):
            require(produce, token, "structural producer selection", failures)
        ordered(add_mesh, ("wo49_token = WO49ProduceTopology( mesh );",
                           "ChooseStudioProgram( phdr, mat, lightpass )"),
                "pre-shader producer placement", failures)
        if add_mesh.find("WO49ProduceTopology") - add_mesh.rfind("WO49_MESH_RETURN", 0, add_mesh.find("WO49ProduceTopology")) > 700:
            failures.append("producer placement: not immediately after eligibility checks")
        for token in (
            "entry->wo49_token = wo49_token", "pWO49TopologyArm( wo49_token )",
            "pWO49TopologyFinish( wo49_token )", "DrawMeshFromBuffer( pMesh",
        ):
            require(studio, token, "Diffusion token propagation", failures)
        reject(produce, r"models[/\\]|ch1map|shader\s*#|frame\s*==|0x[0-9a-f]+\s*==",
               "hard-coded selector", failures)
        reject(produce, r"aggregateVerts\s*==|numVerts\s*==\s*\d|numElems\s*==\s*\d",
               "hard-coded count selector", failures)
        if patch_headers(diff_patch) != DIFFUSION_PATCH_FILES:
            failures.append(f"Diffusion patch scope: got {sorted(patch_headers(diff_patch))}")
        diff_added = added_lines(diff_patch)
        reject(diff_added, r"\b(?:glBind|gles_gl|pgl|glUniform)[A-Za-z0-9_]*\s*\(",
               "Diffusion diagnostic-added GL mutation", failures)
        reject(diff_added, r"\b(?:malloc|calloc|realloc|glGetError|glReadPixels|sleep|usleep)\s*\(",
               "Diffusion diagnostic-added forbidden call", failures)

    require(files["ref_gl"], "gEngfuncs.Con_Printf( \"%s\\n\", line )",
            "engine-owned sink", failures)
    require(files["ref_gl"], "set_index_trace_logger( R_IOSIndexTraceLog )",
            "engine-owned sink installation", failures)
    ordered(files["sys_con"], ("Sys_WriteLogfile(", "Sys_FlushLogfile();"),
            "per-write engine.log durability", failures)

    if repo is not None:
        for name, expected in FROZEN_HASHES.items():
            actual = digest(repo / "scripts/ios" / name)
            if actual != expected:
                failures.append(f"retained Bundle 69/71/75 policy changed: {name} {actual}")
    failures.extend(validate_fixtures())
    return failures


def self_test(files: dict[str, str], require_diffusion: bool) -> list[str]:
    failures: list[str] = []
    cases: list[tuple[str, str, str, str]] = [
        ("pre-realization hook", "fpe", "realize_bufferIndex();\n    ios_wo49_transform_before_draw(\"fpe_glDrawElements\", mode, count, type);\n    ios_wo49_topology_realized(\"fpe_glDrawElements\", mode, count, type, indices);", "ios_wo49_topology_realized(\"early\", mode, count, type, indices);\n    realize_bufferIndex();\n    ios_wo49_transform_before_draw(\"fpe_glDrawElements\", mode, count, type);"),
        ("missing direct", "drawing", "ios_wo49_topology_set_active(ios_wo49_token);", "missing_direct(ios_wo49_token);"),
        ("missing replay", "listdraw", "ios_wo49_topology_set_replay(", "missing_replay("),
        ("index only", "trace", "program->va_size[index]", "0 /* attributes omitted */"),
        ("bounds omitted", "trace", "highest < buffer_bytes", "1 /* bounds omitted */"),
        ("cap raised", "trace_h", "IOS_WO49_TOPOLOGY_TOKEN_CAP 4u", "IOS_WO49_TOPOLOGY_TOKEN_CAP 5u"),
        ("allocation", "trace", "char attrs[2304]", "char *attrs = malloc(2304)"),
        ("error queue", "trace", "ios_wo49_bytes_checksum", "glGetError(); /* ios_wo49_bytes_checksum */"),
        ("pixel read", "trace", "ios_wo49_bytes_checksum", "glReadPixels(0,0,1,1,0,0,0); /* ios_wo49_bytes_checksum */"),
        ("sink lost", "ref_gl", "gEngfuncs.Con_Printf( \"%s\\n\", line )", "printf(\"%s\\n\", line)"),
    ]
    if require_diffusion:
        cases.extend((
            ("hard-coded model", "studio", "unsigned long long CStudioModelRenderer::WO49ProduceTopology( const vbomesh_t *mesh )\n{", "unsigned long long CStudioModelRenderer::WO49ProduceTopology( const vbomesh_t *mesh )\n{\n\tif( strstr(m_pRenderModel->name, \"models/fixed.mdl\") ) return 0;"),
            ("hard-coded count", "studio", "mesh->wo49_aggregateVerts <= 65535u", "mesh->wo49_aggregateVerts == 112981u"),
            ("post-shader producer", "studio", "wo49_token = WO49ProduceTopology( mesh );", "/* producer moved */"),
        ))
    for label, key, old, new in cases:
        if old not in files[key]:
            failures.append(f"self-test setup {label}: token absent")
            continue
        mutated = dict(files)
        mutated[key] = mutated[key].replace(old, new, 1)
        if not validate(mutated, None, require_diffusion):
            failures.append(f"self-test {label}: invalid mutation accepted")
    return failures


def load_files(repo: pathlib.Path, gl4es: pathlib.Path,
               diffusion: pathlib.Path | None) -> dict[str, str]:
    files = {
        "trace": read(gl4es / "src/gl/indextrace.c"),
        "trace_h": read(gl4es / "src/gl/indextrace.h"),
        "drawing": read(gl4es / "src/gl/drawing.c"),
        "fpe": read(gl4es / "src/gl/fpe.c"),
        "list_h": read(gl4es / "src/gl/list.h"),
        "list_c": read(gl4es / "src/gl/list.c"),
        "listdraw": read(gl4es / "src/gl/listdraw.c"),
        "lookup": read(gl4es / "src/gl/gl_lookup.c"),
        "gl_patch": read(repo / "scripts/ios/gl4es-wo49-topology-ios.patch"),
        "diff_patch": read(repo / "scripts/ios/diffusion-wo49-topology-ios.patch"),
        "build": read(repo / "scripts/gha/build_ios.sh") + read(repo / "scripts/ios/builddiffusion.sh"),
        "verify": read(repo / "scripts/ios/verify_ipa.sh"),
        "ref_gl": read(repo / "ref/gl/gl_opengl.c"),
        "sys_con": read(repo / "engine/common/sys_con.c"),
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
    if revision(gl4es) != GL4ES_REF:
        print(f"FAIL: expected GL4ES {GL4ES_REF}, got {revision(gl4es)}", file=sys.stderr)
        return 1
    if not args.gl4es_only:
        if diffusion is None:
            parser.error("DIFFUSION is required unless --gl4es-only is used")
        if revision(diffusion) != DIFFUSION_REF:
            print(f"FAIL: expected Diffusion {DIFFUSION_REF}, got {revision(diffusion)}", file=sys.stderr)
            return 1
    files = load_files(repo, gl4es, None if args.gl4es_only else diffusion)
    failures = validate(files, repo, not args.gl4es_only)
    if args.self_test:
        failures.extend(self_test(files, not args.gl4es_only))
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Validated WO49 topology discriminator: pre-shader producer, direct/list post-realization, attrs+bounds, cap=4")
    print("Validated fixtures: VBO/VAO, stride/offset, position, EBO/source, base/range, stale list, full match")
    if args.self_test:
        print("Validated rejection suite: early hook, missing routes, index-only, hard-coding, allocation and GL mutation rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
