#!/usr/bin/env python3
"""Validate Work Order 56's first-party GL4ES texture-array contract."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import subprocess
import sys

GL4ES_REF = "81547d986798e876de8b434193920b606a72363f"
PATCH = "scripts/ios/gl4es-wo56-texture-array-ios.patch"
PATCH_FILES = {
    "src/gl/enable.c", "src/gl/fpe.c", "src/gl/getter.c", "src/gl/gles.h",
    "src/gl/glstate.c", "src/gl/glstate.h", "src/gl/init.c",
    "src/gl/program.c", "src/gl/program.h", "src/gl/shaderconv.c",
    "src/gl/texture.h", "src/gl/texture_3d.c", "src/gl/texture_array.c",
    "src/gl/texture_compressed.c", "src/gl/texture_params.c",
    "src/gl/uniform.c",
    "src/glx/hardext.c", "src/glx/hardext.h",
}
MARKERS = (
    "iOS texture array selftest policy:",
    "iOS texture array selftest object:",
    "iOS texture array selftest upload:",
    "iOS texture array selftest shader:",
    "iOS texture array selftest sampling-call:",
    "iOS texture array selftest sampling-fbo:",
    "iOS texture array selftest sampling-contract:",
    "iOS texture array selftest sample:",
    "iOS texture array selftest lifecycle:",
    "iOS texture array selftest terminal:",
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


def ordered(text: str, tokens: tuple[str, ...], label: str, failures: list[str]) -> None:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            failures.append(f"{label}: missing or out of order {token!r}")
            return


def validate(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    texture_h = files["texture_h"]
    state = files["state"]
    params = files["params"]
    array = files["array"]
    tex3d = files["tex3d"]
    compressed = files["compressed"]
    program = files["program"]
    program_h = files["program_h"]
    uniform = files["uniform"]
    fpe = files["fpe"]
    shader = files["shader"]
    hardext = files["hardext"]
    hardext_h = files["hardext_h"]
    init = files["init"]
    getter = files["getter"]
    harness = files["harness"]
    context = files["context"]
    client = files["client"]
    launch = files["launch"]
    build = files["build"]
    verify = files["verify"]
    shader_gate = files["shader_gate"]
    patch = files["patch"]
    try:
        contract = json.loads(files["contract"])
    except (TypeError, json.JSONDecodeError) as exc:
        failures.append(f"sampling/readback contract is not valid JSON: {exc}")
        contract = {}

    for token in (
        "ENABLED_TEXTURE_ARRAY", "GL_TEXTURE_2D_ARRAY",
        "actual_texarray", "TU_ARRAY", "GL_SAMPLER_2D_ARRAY",
    ):
        require(texture_h + state + program_h + program, token, "distinct identity", failures)
    for token in (
        "gl4es_texture_array_bind", "gles_glBindTexture(GL_TEXTURE_2D, t)",
        "glstate->actual_texarray", "tex->target != target",
        "GL_INVALID_OPERATION", "GL_TEXTURE_BINDING_2D_ARRAY",
    ):
        require(params + array + getter, token, "binding/lifecycle route", failures)
    require(params, "if(tgt==ENABLED_TEXTURE_ARRAY)", "separate realization", failures)
    if re.search(r"actual_tex2d\[[^]]+\]\s*=\s*.*actual_texarray", params):
        failures.append("array binding aliases the 2D binding cache")

    for token in (
        'gles_getProcAddress("glTexImage3D")',
        'gles_getProcAddress("glTexSubImage3D")',
        'gles_getProcAddress("glTexStorage3D")',
        "native_es_major>=3", "GL_MAX_ARRAY_TEXTURE_LAYERS",
        "source=live-context",
    ):
        require(array + hardext, token, "live-context capability", failures)
    for token in (
        "native_teximage3d(target, level, internalformat, width, height, depth",
        "native_texsubimage3d(target, level, xoffset, yoffset, zoffset, width",
        "native_texstorage3d(target, levels, internalformat, width, height, depth)",
        "glstate->vao->unpack->data + (uintptr_t)data",
        "tex->immutable", "immutable_levels",
    ):
        require(array + texture_h, token, "3D upload semantics", failures)
    for token in (
        "layerbytes * depth", "uncompressDXTc(width, height",
        "layerbytes*layer", "width*height*4*layer",
        "gl4es_texture_array_subimage(target, level, xoffset, yoffset, zoffset",
    ):
        require(compressed, token, "compressed array route", failures)
    require(tex3d, "gl4es_texture_array_storage", "immutable dispatch", failures)

    for token in (
        "type==GL_SAMPLER_2D_ARRAY", "type=TU_ARRAY",
        "m->type == GL_SAMPLER_2D_ARRAY",
        "glprogram->texunits[tu_idx].type - 1",
    ):
        require(program + fpe, token, "sampler reflection/routing", failures)
    for token in (
        "GO(GL_SAMPLER_2D_ARRAY, GLint, 1)",
        "case GL_SAMPLER_2D_ARRAY:",
    ):
        require(uniform, token, "complete sampler uniform type", failures)
    if uniform.count("GL_SAMPLER_2D_ARRAY") != 3:
        failures.append("sampler2DArray must be present in uniformsize, is_uniform_int, and n_uniform exactly")
    for token in (
        'strstr(pBuffer, "sampler2DArray")', 'strstr(pEntry, "#define BMODEL_MULTI_LAYERS")',
        "GL4ES_TEXTURE_ARRAY_PROGRAM", "#version 300 es", "#define GLSL_ALLOW_TEXTURE_ARRAY 1",
        "#define varying out", "#define varying in",
        "#define texture2DArray texture", "#define texture2DProj textureProj", "gl4es_FragColor",
        "precision mediump sampler2DArray",
        "if(!texture_array_shader && !fpeShader",
        "derivatives are core in ESSL 300", "gl_FragDepth is core in ESSL 300",
    ):
        require(shader, token, "stage-correct ESSL300", failures)

    for token in (
        "ResetHardwareExtensions", "gl4es_texture_array_reset",
        "inited = 0", "tested = 0", "memset(&hardext, 0",
    ):
        require(init + hardext + hardext_h, token, "context lifecycle reset", failures)
    if "GL_EXT_texture_array" in getter:
        failures.append("terrain admission/extension advertisement enabled prematurely")

    for marker in MARKERS:
        require(harness, marker, "selftest marker", failures)
        require(verify, marker, "packaged marker contract", failures)
    for token in (
        '"-gl4es_texture_array_selftest"', "R_IOSTextureArraySelftest();",
        "Sys_Quit( \"iOS texture array selftest complete\" )",
        "-ref gl4es -gl4es_texture_array_selftest", "setEnabled:NO",
        "layers=0,1,2,3", "zoffset=2", "zoffset=3", "zoffset=1",
        "levels=3", "texture2DArray(u_Array", "GL_SAMPLER_2D_ARRAY",
        "pglReadPixels", "checksum", "diffusion_started=0",
    ):
        require(harness + context + client + launch, token, "selftest gate", failures)

    for token in (
        "IOS_ARRAY_EXPECTED_CHECKSUM 0xA915906Du",
        '"stage-entry"', "gl4es_external_default_framebuffer_state",
        "IOS_ARRAY_FRAMEBUFFER_COMPLETE", "logical_current",
        '"glUniform1i(u_Array)"', "gl4es_glUniform1i( samplerLocation, 0 )",
        '"glBindTexture(GL_TEXTURE_2D_ARRAY)"',
        "pglBindTexture( GL_TEXTURE_2D_ARRAY, textures[0] )",
        "pglGenBuffersARB", "pglBufferDataARB", "GL_STATIC_DRAW_ARB",
        "gl4es_glVertexAttribPointer( 0, 2, GL_FLOAT, GL_FALSE, 0, (const GLvoid *)0 )",
        "pglDisable( GL_SCISSOR_TEST )", "pglPixelStorei( GL_PACK_ALIGNMENT, 1 )",
        "{ 0, 0, width/2, height/2 }", "(GLfloat)layer ));",
        "pglFinish()", "checksum != IOS_ARRAY_EXPECTED_CHECKSUM",
        "byte pixel[4];", "pglReadPixels( x, y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel )",
        "pglDeleteBuffersARB", "glDisable(GL_TEXTURE_2D_ARRAY,restore)",
        "glBindTexture(GL_TEXTURE_2D_ARRAY,restore)", "glUseProgram(restore)",
        "glPixelStorei(GL_PACK_ALIGNMENT,restore)", "glViewport(restore)",
    ):
        require(harness, token, "sampling/readback source contract", failures)
    require(harness, "diffusion_started=0", "bounded selftest terminal", failures)
    if "gl4es_glVertexAttribPointer( 0, 2, GL_FLOAT, GL_FALSE, 0, quad )" in harness:
        failures.append("Apple GLES3 sampling route still uses forbidden client-side vertex storage")
    ordered(harness, (
        "iOS texture array selftest shader:",
        '"stage-entry"',
        '"glUniform1i(u_Array)"',
        '"glDrawArrays(GL_TRIANGLE_STRIP)"',
        '"glFinish"',
        '"glReadPixels(GL_RGBA,GL_UNSIGNED_BYTE)"',
        "checksum != IOS_ARRAY_EXPECTED_CHECKSUM",
        "iOS texture array selftest sampling-contract:",
        "iOS texture array selftest sample:",
        "iOS texture array selftest lifecycle:",
    ), "sampling/readback order", failures)

    if contract.get("schema") != 1 or contract.get("workOrder") != "56I":
        failures.append("sampling/readback contract identity changed")
    evidence = contract.get("phaseHEvidence", {})
    if evidence.get("bundle") != 114 or evidence.get("boundedExit") is not True or evidence.get("hardCrash") is not False:
        failures.append("Phase H bounded-exit evidence contract changed")
    if evidence.get("logSha256") != "2A0A70CC3005795626ADF1597E656FBE30FEBEFBF0EACE0D9342BD09399FB32B":
        failures.append("Phase H evidence hash changed")
    origin = contract.get("sourceProvenOrigin", {})
    for key, value in (
        ("wrapperEntry", "gl4es_glUniform1i"),
        ("failingHelper", "GoUniformiv"),
        ("uniformType", "GL_SAMPLER_2D_ARRAY"),
        ("errorResult", "errorShim(GL_INVALID_OPERATION)"),
    ):
        if origin.get(key) != value:
            failures.append(f"source-proven error origin changed: {key}")
    framebuffer = contract.get("framebuffer", {})
    for key, value in (
        ("target", "GL_FRAMEBUFFER"), ("logicalRead", 0), ("logicalDraw", 0),
        ("requiredStatus", "GL_FRAMEBUFFER_COMPLETE"),
        ("drawBuffer", "GL_COLOR_ATTACHMENT0 implicit for the registered nonzero FBO"),
        ("readBuffer", "GL_COLOR_ATTACHMENT0 implicit for the registered nonzero FBO"),
        ("level", 0), ("samples", 0),
    ):
        if framebuffer.get(key) != value:
            failures.append(f"framebuffer contract changed: {key}")
    checksum_contract = contract.get("checksum", {})
    colors = [q.get("rgba") for q in checksum_contract.get("quadrants", [])]
    expected_colors = [[255, 0, 0, 255], [0, 255, 0, 255], [255, 0, 255, 255], [255, 255, 0, 255]]
    if colors != expected_colors:
        failures.append("source layer colors or quadrant ordering changed")
    hash_value = 2166136261
    for color in expected_colors:
        for channel in color:
            hash_value = ((hash_value ^ channel) * 16777619) & 0xFFFFFFFF
    if f"{hash_value:08x}" != "a915906d" or checksum_contract.get("expected") != "a915906d":
        failures.append("source-derived FNV-1a checksum changed")
    if checksum_contract.get("format") != "GL_RGBA" or checksum_contract.get("type") != "GL_UNSIGNED_BYTE":
        failures.append("readback pixel format/type contract changed")
    if checksum_contract.get("comparison") != "both per-pixel tolerance and exact source-derived checksum":
        failures.append("checksum comparison was weakened")
    required_calls = [
        "stage-entry", "gl4es_external_default_framebuffer_state", "glGetIntegerv state capture",
        "glUseProgram", "glGetUniformLocation", "glUniform1i(u_Array)",
        "glActiveTexture/glEnable/glBindTexture", "glGenBuffers/glBindBuffer/glBufferData",
        "glEnableVertexAttribArray/glVertexAttribPointer", "glDisable(GL_SCISSOR_TEST)",
        "glPixelStorei(GL_PACK_ALIGNMENT,1)", "glClearColor/glClear",
        "glViewport(quadrant)", "glUniform1f(u_Layer)",
        "glDrawArrays(GL_TRIANGLE_STRIP)", "glFinish",
        "glReadPixels(GL_RGBA,GL_UNSIGNED_BYTE)", "checksum", "state restoration",
        "lifecycle continuation",
    ]
    calls = contract.get("calls", [])
    if [call.get("call") for call in calls] != required_calls:
        failures.append("call-level sampling/readback provenance table changed")
    if any(not call.get("legal") or not call.get("owner") or not call.get("preconditions") for call in calls):
        failures.append("call-level provenance is missing legality, owner, or preconditions")
    require(build, "gl4es-wo56-texture-array-ios.patch", "build patch replay", failures)
    require(build, "validate-ios-texture-array.py", "build validator", failures)
    for token in ("TEXTURE_ARRAY_JOBS", "BMODEL_MULTI_LAYERS", "bmodelsolid_fp.glsl", "bmodeldlight_fp.glsl"):
        require(shader_gate, token, "pinned terrain shader gate", failures)

    headers = set(re.findall(r"^diff --git a/(\S+) b/\S+$", patch, re.MULTILINE))
    if headers != PATCH_FILES:
        failures.append(f"GL4ES patch scope changed: {sorted(headers)}")
    return failures


def fixtures(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    mutations = (
        ("alias", "state", "actual_texarray", "actual_tex2d"),
        ("lost depth", "array", "width, height, depth", "width, height, 1"),
        ("lost zoffset", "array", "xoffset, yoffset, zoffset", "xoffset, yoffset, 0"),
        ("sampler misclassification", "program", "type=TU_ARRAY", "type=TU_TEX2D"),
        ("ESSL100 fallback", "shader", "#version 300 es", "#version 100"),
        ("raw inactive array token", "shader", 'strstr(pBuffer, "sampler2DArray")', 'strstr(pEntry, "sampler2DArray")'),
        ("wrong unit", "fpe", "glprogram->texunits[tu_idx].type - 1", "ENABLED_TEX2D"),
        ("missing uniform size", "uniform", "GO(GL_SAMPLER_2D_ARRAY, GLint, 1)", "GO(GL_SAMPLER_2D, GLint, 1)"),
        ("wrong uniform type", "uniform", "case GL_SAMPLER_2D_ARRAY:", "case GL_SAMPLER_2D:"),
        ("missing lifecycle", "init", "gl4es_texture_array_reset", "array_reset_removed"),
        ("layer-zero-only", "harness", "layers=0,1,2,3", "layers=0"),
        ("stale error attribution", "harness", '"stage-entry"', '"stage-entry-removed"'),
        ("missing framebuffer proof", "harness", "gl4es_external_default_framebuffer_state", "framebuffer_state_removed"),
        ("wrong sampler unit", "harness", "gl4es_glUniform1i( samplerLocation, 0 )", "gl4es_glUniform1i( samplerLocation, 1 )"),
        ("missing array binding", "harness", "pglBindTexture( GL_TEXTURE_2D_ARRAY, textures[0] )", "missingArrayBind()"),
        ("wrong layer coordinate", "harness", "(GLfloat)layer ));", "0.0f ));"),
        ("client vertex state", "harness", "(const GLvoid *)0 ));", "quad ));"),
        ("wrong viewport", "harness", "width/2, height/2", "0, height/2"),
        ("unsupported read type", "harness", "GL_RGBA, GL_UNSIGNED_BYTE, pixel", "GL_RGBA, GL_FLOAT, pixel"),
        ("bad pack alignment", "harness", "GL_PACK_ALIGNMENT, 1 )", "GL_PACK_ALIGNMENT, 3 )"),
        ("small destination", "harness", "byte pixel[4];", "byte pixel[3];"),
        ("missing synchronization", "harness", "pglFinish()", "missingFinish()"),
        ("checksum weakening", "harness", "checksum != IOS_ARRAY_EXPECTED_CHECKSUM", "checksum == 0xffffffffu"),
        ("skipped readback", "harness", "pglReadPixels( x, y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel )", "skipReadback()"),
        ("ordinary 2D fallback", "harness", '"glBindTexture(GL_TEXTURE_2D_ARRAY)"', '"glBindTexture(GL_TEXTURE_2D)"'),
        ("atlas fallback", "harness", "texture2DArray(u_Array", "texture2D(u_Array"),
        ("state leakage", "harness", "pglDeleteBuffersARB( 1, &vertexBuffer )", "leakVertexBuffer()"),
        ("continuation after failure", "harness", "diffusion_started=0", "diffusion_started=1"),
        ("selftest bypass", "client", "Sys_Quit( \"iOS texture array selftest complete\" )", "/* bypass */"),
    )
    for label, key, old, new in mutations:
        candidate = copy.deepcopy(files)
        if old not in candidate[key]:
            failures.append(f"fixture {label}: source token absent")
            continue
        candidate[key] = candidate[key].replace(old, new)
        if not validate(candidate):
            failures.append(f"fixture {label}: validator accepted mutation")

    contract_mutations = (
        ("incomplete framebuffer", '"requiredStatus": "GL_FRAMEBUFFER_COMPLETE"', '"requiredStatus": "GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT"'),
        ("wrong attachment target", '"target": "GL_FRAMEBUFFER"', '"target": "GL_RENDERBUFFER"'),
        ("wrong attachment level", '"level": 0', '"level": 1'),
        ("wrong read framebuffer", '"logicalRead": 0', '"logicalRead": 7'),
        ("wrong draw framebuffer", '"logicalDraw": 0', '"logicalDraw": 7'),
        ("illegal read buffer", '"readBuffer": "GL_COLOR_ATTACHMENT0 implicit for the registered nonzero FBO"', '"readBuffer": "GL_BACK"'),
        ("wrong sample count", '"samples": 0', '"samples": 4'),
        ("wrong pixel format", '"format": "GL_RGBA"', '"format": "GL_RGB"'),
        ("checksum contract weakening", '"comparison": "both per-pixel tolerance and exact source-derived checksum"', '"comparison": "observed checksum accepted"'),
    )
    for label, old, new in contract_mutations:
        candidate = copy.deepcopy(files)
        if old not in candidate["contract"]:
            failures.append(f"fixture {label}: contract token absent")
            continue
        candidate["contract"] = candidate["contract"].replace(old, new, 1)
        if not validate(candidate):
            failures.append(f"fixture {label}: validator accepted mutation")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=pathlib.Path)
    parser.add_argument("gl4es", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root, gl4es = args.root.resolve(), args.gl4es.resolve()
    if revision(gl4es) != GL4ES_REF:
        print("texture-array validation failed: wrong pinned GL4ES revision", file=sys.stderr)
        return 1
    files = {
        "texture_h": read(gl4es / "src/gl/texture.h"),
        "state": read(gl4es / "src/gl/glstate.h") + read(gl4es / "src/gl/glstate.c"),
        "params": read(gl4es / "src/gl/texture_params.c"),
        "array": read(gl4es / "src/gl/texture_array.c"),
        "tex3d": read(gl4es / "src/gl/texture_3d.c"),
        "compressed": read(gl4es / "src/gl/texture_compressed.c"),
        "program": read(gl4es / "src/gl/program.c"),
        "program_h": read(gl4es / "src/gl/program.h"),
        "uniform": read(gl4es / "src/gl/uniform.c"),
        "fpe": read(gl4es / "src/gl/fpe.c"),
        "shader": read(gl4es / "src/gl/shaderconv.c"),
        "hardext": read(gl4es / "src/glx/hardext.c"),
        "hardext_h": read(gl4es / "src/glx/hardext.h"),
        "init": read(gl4es / "src/gl/init.c"),
        "getter": read(gl4es / "src/gl/getter.c"),
        "harness": read(root / "ref/gl/gl_texture_array_selftest.c"),
        "context": read(root / "ref/gl/gl_opengl.c"),
        "client": read(root / "engine/client/cl_main.c"),
        "launch": read(root / "engine/platform/ios/launchdialog.m"),
        "build": read(root / "scripts/gha/build_ios.sh"),
        "verify": read(root / "scripts/ios/verify_ipa.sh"),
        "shader_gate": read(root / "scripts/ios/validate-diffusion-mobile-shaders.py"),
        "patch": read(root / PATCH),
        "contract": read(root / "scripts/ios/wo56i-sampling-readback-contract.json"),
    }
    failures = validate(files)
    if args.self_test:
        failures += fixtures(files)
    if failures:
        print("texture-array validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("texture-array validation passed: native ES3 route, selftest, and rejection fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
