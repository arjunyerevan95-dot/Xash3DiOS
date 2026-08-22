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

## Phase K issuance snapshot (superseded by Outcome A below)

- Historical status at issuance: Phase K was active and no implementation candidate, workflow, artifact, IPA, or device evidence existed yet. The later Phase K Outcome A section is authoritative for the completed build result.
- Authoritative Google ledger Phase K order was appended under revision guard and verified by readback at revision `AIroW37mgJWSAdh9os0FJ0VzXL-r36Dj5xAz9EfzGMg_oXINPkRe-WWO3uZKluW6OOn4DguV3EyefcmwR0ZwOd7v-shLklDwN20hf5dbH84`.
- Admission baseline: Phase J Outcome A record `cc02ebaa192abb3a11ce5ea520649a096a68ed44`; qualified implementation `bc4b2b7181b3111053f14ff86e8ff634718acf30`.
- Established runtime boundary: the Phase J log reports `GL_EXT_texture_array - failed` after the successful bounded harness because production capability advertisement remains deliberately disabled.
- Engine source boundary: `ref/gl/gl_opengl.c` gates `GL_TEXTURE_ARRAY_EXT` through `GL_CheckExtension("GL_EXT_texture_array", ..., "gl_texture_2d_array", ..., 0)` and queries `GL_MAX_ARRAY_TEXTURE_LAYERS_EXT` only after success.
- Engine loader boundary: `ref/gl/gl_image.c` rejects array targets when `GL_TEXTURE_ARRAY_EXT` is false and contains the production texture-array create/load path.
- Diffusion source boundary: its renderer separately gates `R_TEXTURE_ARRAY_EXT`; `GLSL_ALLOW_TEXTURE_ARRAY`, landscape `LOAD_TEXTURE_ARRAY`, and terrain shader use depend on that state.
- Shader boundary: terrain GLSL uses `sampler2DArray` under `GLSL_ALLOW_TEXTURE_ARRAY && BMODEL_MULTI_LAYERS`; `scripts/ios/diffusion-ios.patch` currently filters `MULTI_LAYERS` on iOS.
- Required Phase K artifact: `scripts/ios/wo56k-production-array-admission-contract.json` or the semantically equivalent machine-readable path named in the worker report.
- Required CI evidence at issuance was exactly one qualifying workflow and artifact tied to one immutable candidate. That evidence is now recorded in the Phase K Outcome A section below.
- Phase K did not authorize device evidence. Its completed candidate remains build-qualified rather than terrain/device-accepted.

## Phase K Outcome A build evidence

- Status: worker-reported Outcome A; build-qualified and awaiting orchestrator acceptance. No device/gameplay evidence was requested or produced.
- Coherent implementation commit: `c063202dc0c0111304e2d0a82a2506f1457f1454`.
- Qualification corrections: `12a80912c8c18870cad71e6116fbfeda2e26e2c3` and `38d429b189efc9a46e1a47f8463bf04797641fd6`.
- Exact candidate: `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`.
- Repository-ledger report commit: `a067869505778dcabd8ab47b6b2e583892f8ce36`.
- Contract: `scripts/ios/wo56k-production-array-admission-contract.json`.
- Qualifying workflow: [32510363562 — success](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32510363562), job [96859751554](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32510363562/job/96859751554).
- Retained artifact: [9456949434 — Xash3DiOS-arm64-unsigned](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32510363562/artifacts/9456949434), archive size `8,618,551` bytes, SHA-256 `5ed24f8a6ad27dfaea62ed315329d8bdf79e95c5a0053a4ba36187236f42b744`.
- IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 124, `8,717,677` bytes, SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`.
- Temporary mirror: [information page](https://tempfile.org/qyUGaEfR9Jp/) / [direct IPA](https://tempfile.org/qyUGaEfR9Jp/download), recorded expiry `2026-08-23T18:53:49.725Z`; round-trip size/hash matched.
- Bounded negative workflows: `32508365615` (shader macro-value mismatch), `32509025360` (missing pinned Diffusion limit token), and `32509723819` (wrong packaged marker owner). They produced no retained artifact.
- Exact pins: GL4ES `81547d986798e876de8b434193920b606a72363f`; Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`; SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`.
- Package proof: required production markers in their actual owners, 13 thin-arm64 Mach-O objects, and zero proprietary game assets.
- Durable reports: repository ledger Phase K Outcome A entry near line 2627 and the authoritative Google Docs ledger, both reported read-back verified by the worker.
- Qualification boundary: production capability admission is build-qualified only. Real Diffusion terrain loading, shader execution, rendering, transition behavior, gameplay, and `ch1map1` remain outside this evidence.

## Phase L Outcome C pre-launch evidence

- Status: complete at Outcome C; stopped before installation/launch because the exact Bundle 124 argument identity cannot satisfy the order.
- Exact candidate/workflow/artifact: `976c38f3d99d7ef6eaf348188fabf4fe4e722be9` / `32510363562` / `9456949434`.
- Exact IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 124, `8,717,677` bytes, SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`.
- Locked arguments: `-dev 2 -log -game diffusion -ref gl4es`; no self-test or force-enable flag.
- Target device: established iPhone 16 Pro Max / iOS 26.6.
- Local IPA readback matched the authorized filename, Bundle 124 version, `8,717,677` bytes, and SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`.
- `engine/platform/ios/launchdialog.m` hardcodes `-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest`, writes it into the launch field, disables that field, and derives `argv` from it.
- The exact extracted Bundle 124 `xash` executable contains the full hardcoded self-test argument string; `Info.plist` reports version `124`.
- Required Phase L arguments omit `-gl4es_texture_array_selftest`; therefore the exact candidate cannot pass the pre-launch argument guard. No device launch, screenshot, log, `.ips`, or marker evidence was produced, and the one-run authorization remains unconsumed.
- Qualification boundary: Phase K production admission remains build-qualified; live ordinary-bootstrap production admission remains unqualified. Terrain loading, terrain shader execution, drawing, maps, gameplay, transitions, and `ch1map1` remain prohibited and unqualified.
- Related decision: [`DEC-007`](../../Decisions/DEC-007.md).
- First incomplete step: orchestrator review and decision whether a separately authorized ordinary-argument candidate is justified. No automatic patch/build/retry is authorized.

## Phase M pending ordinary-bootstrap candidate evidence

- Status: active; one bounded audit, locked-tuple implementation, validation update, and build-qualified candidate are authorized. No device test is authorized.
- Control baseline: `c7be0a237ad223e60b7808a903d2411a9154c153`; qualified production baseline: `976c38f3d99d7ef6eaf348188fabf4fe4e722be9` / workflow `32510363562` / artifact `9456949434` / Bundle 124 SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`.
- Required source tuple: exact standalone `-dev 2 -log -game diffusion -ref gl4es` in the disabled iOS launch field.
- Required negative proof: the combined tuple ending in `-gl4es_texture_array_selftest` is absent as a default source/package string; no substring-only verifier may satisfy this gate.
- Required retained proof: explicit self-test flag parsing, conditional dispatch, bounded terminal machinery, historical markers, and all Phase K provider/engine/Diffusion markers remain compiled and correctly owned, but the default launch cannot arm the diagnostic route.
- Pending contract: `scripts/ios/wo56m-ordinary-bootstrap-contract.json` or the semantically equivalent path named in the worker report.
- Pending build evidence for Outcome A: implementation commit, qualifying workflow/job/artifact, IPA bundle version/name/bytes/SHA-256, package-string/owner/architecture/proprietary-data checks, and optional mirror round-trip identity.
- Qualification boundary: Phase M can build-qualify argument routing only. It cannot consume a device authorization or qualify live admission, terrain, maps, transitions, gameplay, or `ch1map1`.
- Related decision: [`DEC-008`](../../Decisions/DEC-008.md).
- Authoritative Google ledger: Phase M order appended under revision guard and stop-state paragraph read-back verified at revision `AIroW37tae1LAWrBYYTMvYeeh_9sHD6ReMvvblPZDotrbAQSlIRULeEX4Xtbxvp6FKtHH08vVjI5DdWIvkmENwrDk9vVvA2jZdRMSmIwXfY`.
