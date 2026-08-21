# WO-056 Evidence Manifest

This manifest references the evidence used to close WO-056 Phases I and J at Outcome A. Large artifacts are referenced rather than copied into the repository.

## Repository provenance

- Repository: `arjunyerevan95-dot/Xash3DiOS`
- Branch: `agent/ios-proof-of-life`
- Phase I baseline: `68f0c1c5`
- Phase I candidate: `bc4b2b7181b3111053f14ff86e8ff634718acf30`
- Phase I ledger checkpoint: `8c9fd723fcaa3aff77178a8496ba82427cc28881`
- Predecessor Phase H / Bundle 114 candidate: `281eb237d0d9f5387814b3fdfa740524aeac459a`
- Repository ledger: [`Documentation/XASH3DIOS_PORTING_STATE.md`](../../Documentation/XASH3DIOS_PORTING_STATE.md), WO-056 Phase I entry beginning near line 2470
- Authoritative Google ledger: [Xash3DiOS project ledger](https://docs.google.com/document/d/1IYL3pI07fWvoYniP_NxZ7yO3gz9vbnM6sBFK8BT2zLU/edit)

## CI and artifact evidence

- Workflow run: [32489923843 — success](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32489923843)
- Tested commit: `bc4b2b7181b3111053f14ff86e8ff634718acf30`
- Job: `96794910555`, `Unsigned arm64 IPA` — success
- Artifact: [9449473335 — Xash3DiOS-arm64-unsigned](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32489923843/artifacts/9449473335)
- GitHub artifact archive size: `8,616,958` bytes
- GitHub artifact digest: `sha256:dacfb9d82bce5c3f777b2c77b38fa038d24655260c0438d199a6b596479355d2`
- GitHub artifact expiry: `2026-09-04T14:06:13Z`
- IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,716,506` bytes
- IPA SHA-256: `4FD8D67DDAEBF1986AC795164B7CD20BA782319B9F29200C9EA76F1A4BA73806`
- Temporary mirror: [information page](https://tempfile.org/FQBk1nBoC51/) / [direct IPA download](https://tempfile.org/FQBk1nBoC51/download), reported 48-hour retention
- The IPA and temporary-mirror round-trip hashes matched exactly.
- Duplicate automatic PR run `32489927380` was cancelled; related Build & Deploy runs `32489924024` and `32489927404` were skipped. No newer relevant run was active at migration verification.

## Implementation and contract evidence

- `ref/gl/gl_texture_array_selftest.c`
- `scripts/ios/gl4es-wo56-texture-array-ios.patch`
- `scripts/ios/validate-ios-renderer-contract.py`
- `scripts/ios/validate-ios-selftest-boot.py`
- `scripts/ios/validate-ios-texture-array.py`
- `scripts/ios/verify_ipa.sh`
- `scripts/ios/wo56i-sampling-readback-contract.json`
- Pinned GL4ES source revision: `81547d986798e876de8b434193920b606a72363f`
- The full validator and rejection suite passed.
- The exact pinned patch stack replayed cleanly.
- CI built the relevant arm64 engine, Half-Life, and Diffusion targets.

## Diagnostic and device evidence

- Phase H raw device log: `1-engine.log`, SHA-256 `2A0A70CC3005795626ADF1597E656FBE30FEBEFBF0EACE0D9342BD09399FB32B`.
- Exact successful readback checksum: `a915906d`.
- Phase H device observation: the normal-bootstrap native-array route reached sampling/readback; `glUniform1i(u_Array, 0)` reported `GL_INVALID_OPERATION`, while the exact checksum proved the expected array layer sample was drawn, read back, and presented.
- Phase I established the source cause and supplied a build-qualified corrected bundle.
- Phase J supplied one complete Bundle 116 device run and closed at Outcome A.

## Phase J device evidence

- Status: Phase J Outcome A; Bundle 116 device-accepted for the bounded native texture-array conformance harness.
- Device: iPhone 16 Pro Max, iOS 26.6; Apple A18 Pro GPU; drawable `2868x1320`.
- Log: `1-engine.log`, `23,255` bytes, `254` lines, SHA-256 `139B15982FEC0B4D34146B3F99A39D4758B36D77925394403B214BE9F5544FF5`.
- Log candidate identity: `bc4b2b71-dirty`, branch `agent/ios-proof-of-life`, `apple-arm64`; exact locked diagnostic arguments.
- Normal Diffusion game information and all 57 contract items completed; one renderer dispatch; no `CL_LoadProgs`, module, map, terrain, cutscene, or gameplay admission.
- Mutable/immutable/compressed upload, object identity, shader translation/reflection, and lifecycle stages: PASS.
- Direct-drawable framebuffer: complete; sampling/cleanup calls `seq=1..51`: all `error=0x0000 result=PASS`.
- Sample: four quadrants, layers `0,1,2,3`, checksum `a915906d`, PASS.
- Terminal: `PASS failures=0 diffusion_started=0`; explicit intentional shutdown reason and clean context-destroy lifecycle.
- User observation: app closed about one second after the interaction described as clicking Start. The complete log proves this was the self-test's bounded intentional exit, not a hard crash; no `.ips` was required.
- `GL_EXT_texture_array - failed` after the terminal is expected because production capability advertisement remains disabled.
- No rebuild, second launch, gameplay run, terrain admission, or `ch1map1` change was performed or authorized.
- Authoritative Google ledger Outcome A/readback revision: `AIroW35eAHEQsIjng7koSVYL26SxH_LPplNTY2_pP2hkjH5sDD-v7Sa_DztjVI28T3Rh0oHuQNk1fdRkpHFvUX0cTfPZNGDFprZXSl-CK-o`.

## PortingOS references

- Phase H / Bundle 114: predecessor normal-bootstrap device experiment.
- Phase I / Bundle 116: completed build-qualified diagnostic/correction experiment.
- Phase J / Bundle 116: completed physical-device conformance experiment at Outcome A.
- Contract identifier: `scripts/ios/wo56i-sampling-readback-contract.json`.
- No separate PortingOS snapshot ID was recorded for Phase I.

## Related control-plane records

- [`Documentation/CURRENT_STATE.md`](../../Documentation/CURRENT_STATE.md)
- [`WorkOrders/WO-056.md`](../../WorkOrders/WO-056.md)
- [`DEC-001`](../../Decisions/DEC-001.md)
- [`DEC-002`](../../Decisions/DEC-002.md)
- [`DEC-003`](../../Decisions/DEC-003.md)
- [`DEC-004`](../../Decisions/DEC-004.md)
- [`DEC-005`](../../Decisions/DEC-005.md)
- [`DEC-006`](../../Decisions/DEC-006.md)

## Phase K admission evidence and pending proof

- Status: Phase K active; no implementation candidate, workflow, artifact, IPA, or device evidence exists yet.
- Authoritative Google ledger Phase K order was appended under revision guard and verified by readback at revision `AIroW37mgJWSAdh9os0FJ0VzXL-r36Dj5xAz9EfzGMg_oXINPkRe-WWO3uZKluW6OOn4DguV3EyefcmwR0ZwOd7v-shLklDwN20hf5dbH84`.
- Admission baseline: Phase J Outcome A record `cc02ebaa192abb3a11ce5ea520649a096a68ed44`; qualified implementation `bc4b2b7181b3111053f14ff86e8ff634718acf30`.
- Established runtime boundary: the Phase J log reports `GL_EXT_texture_array - failed` after the successful bounded harness because production capability advertisement remains deliberately disabled.
- Engine source boundary: `ref/gl/gl_opengl.c` gates `GL_TEXTURE_ARRAY_EXT` through `GL_CheckExtension("GL_EXT_texture_array", ..., "gl_texture_2d_array", ..., 0)` and queries `GL_MAX_ARRAY_TEXTURE_LAYERS_EXT` only after success.
- Engine loader boundary: `ref/gl/gl_image.c` rejects array targets when `GL_TEXTURE_ARRAY_EXT` is false and contains the production texture-array create/load path.
- Diffusion source boundary: its renderer separately gates `R_TEXTURE_ARRAY_EXT`; `GLSL_ALLOW_TEXTURE_ARRAY`, landscape `LOAD_TEXTURE_ARRAY`, and terrain shader use depend on that state.
- Shader boundary: terrain GLSL uses `sampler2DArray` under `GLSL_ALLOW_TEXTURE_ARRAY && BMODEL_MULTI_LAYERS`; `scripts/ios/diffusion-ios.patch` currently filters `MULTI_LAYERS` on iOS.
- Required Phase K artifact: `scripts/ios/wo56k-production-array-admission-contract.json` or the semantically equivalent machine-readable path named in the worker report.
- Required CI evidence if Outcome A: exactly one qualifying workflow and artifact tied to one immutable candidate; all identifiers and IPA hash remain pending.
- Phase K does not authorize device evidence. A build-qualified candidate, if produced, must stop at orchestrator review and must not be described as terrain/device-accepted.
