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

- Status: superseded by the completed Phase M Outcome A evidence below; no device test was authorized or performed.
- Control baseline: `c7be0a237ad223e60b7808a903d2411a9154c153`; qualified production baseline: `976c38f3d99d7ef6eaf348188fabf4fe4e722be9` / workflow `32510363562` / artifact `9456949434` / Bundle 124 SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`.
- Required source tuple: exact standalone `-dev 2 -log -game diffusion -ref gl4es` in the disabled iOS launch field.
- Required negative proof: the combined tuple ending in `-gl4es_texture_array_selftest` is absent as a default source/package string; no substring-only verifier may satisfy this gate.
- Required retained proof: explicit self-test flag parsing, conditional dispatch, bounded terminal machinery, historical markers, and all Phase K provider/engine/Diffusion markers remain compiled and correctly owned, but the default launch cannot arm the diagnostic route.
- Pending contract: `scripts/ios/wo56m-ordinary-bootstrap-contract.json` or the semantically equivalent path named in the worker report.
- Pending build evidence for Outcome A: implementation commit, qualifying workflow/job/artifact, IPA bundle version/name/bytes/SHA-256, package-string/owner/architecture/proprietary-data checks, and optional mirror round-trip identity.
- Qualification boundary: Phase M can build-qualify argument routing only. It cannot consume a device authorization or qualify live admission, terrain, maps, transitions, gameplay, or `ch1map1`.
- Related decision: [`DEC-008`](../../Decisions/DEC-008.md).
- Authoritative Google ledger: Phase M order appended under revision guard and stop-state paragraph read-back verified at revision `AIroW37tae1LAWrBYYTMvYeeh_9sHD6ReMvvblPZDotrbAQSlIRULeEX4Xtbxvp6FKtHH08vVjI5DdWIvkmENwrDk9vVvA2jZdRMSmIwXfY`.

## Phase M completed ordinary-bootstrap candidate evidence

- Selected outcome: Outcome A; build-qualified only.
- Baseline: control commit `38114ad981ecc145c16e2672abbc2dc688bcdaad`; implementation/candidate commit `5a529ff41d23b557e6e4e7878fb31284c7dfc661`.
- Contract: `scripts/ios/wo56m-ordinary-bootstrap-contract.json`; the argument table covers locked source value, tokenization, `IOS_GetArgs`, and `Host_Main` admission.
- Source/package discriminator: exact standalone `-dev 2 -log -game diffusion -ref gl4es` present once in `xash`; combined default absent; separate self-test token, flag parser, conditional dispatch, harness terminal, and accepted markers retained.
- Local validation: Python compilation, JSON parsing, focused positive/rejection fixtures, self-test bootstrap and 57-item renderer contract, exact-pin GL4ES/Diffusion patch replay, native array, production admission, drawable, uint-index, index trace, WO49 topology/transform/per-unit target, WO51 material, WO52 trace/inactive-sampler, Diffusion policy, and `git diff --check` passed.
- Pins: GL4ES `81547d986798e876de8b434193920b606a72363f`; Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`; MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`; executable `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`; SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`.
- Qualifying workflow: [32551387441](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32551387441), job [96978610370](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32551387441/job/96978610370), success. Duplicate PR run `32551389885` cancelled before build/artifact.
- Artifact: [ID 9470194619](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32551387441/artifacts/9470194619), `8,617,082`-byte archive, digest `sha256:400cde7cf33dc29b6ca72e0376f6d05bc979202622e1e3b98d5cb3d7126e3eef`, expiry `2026-09-05T04:23:34Z`.
- IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 126, `8,717,507` bytes, SHA-256 `F5FE061690C0532C3086B2CCD650E541FCEB14F35128F7A35C66B670AE105ACF`.
- Mirror: [tempfile page](https://tempfile.org/MrnVs2sedq5/), [direct IPA](https://tempfile.org/MrnVs2sedq5/download); server metadata/security and a fresh download reproduce the IPA identity, `safe` risk, and no warning.
- Independent contents: all three production markers in proper owners, diagnostic machinery retained, 13 thin-arm64 objects, zero proprietary game assets.
- Runtime evidence: none authorized or collected. Physical-device admission, terrain, maps, transitions, gameplay, and `ch1map1` remain unqualified.
- First incomplete step: orchestrator review and explicit decision whether a new evidence-only device phase is justified.

## Phase N ordinary-device Outcome B evidence

- Status: accepted Outcome B from exactly one orchestrator-authorized Bundle 126 run; no rerun is authorized.
- Candidate/control tuple: `5a529ff41d23b557e6e4e7878fb31284c7dfc661` / Phase M report `308978fde8f7904c3511ccd6eed6bfb5c975ad5c`.
- Workflow/job/artifact: [32551387441](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32551387441) / `96978610370` / [9470194619](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32551387441/artifacts/9470194619). The workflow is successful and the artifact was unexpired at Phase O issuance.
- IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 126, `8,717,507` bytes, SHA-256 `F5FE061690C0532C3086B2CCD650E541FCEB14F35128F7A35C66B670AE105ACF`.
- Tempfile identity at review: [page](https://tempfile.org/MrnVs2sedq5/) / [direct IPA](https://tempfile.org/MrnVs2sedq5/download), ID `MrnVs2sedq5`; metadata reported the exact filename/bytes, no warning, and the direct round-trip hash recorded in Phase M.
- Device: iPhone 16 Pro Max, iOS 26.6; Apple A18 Pro GPU; `2868x1320` drawable.
- Runtime identity: `5a529ff4-dirty`, `agent/ios-proof-of-life`, `apple-arm64`; exact ordinary arguments `(null) -dev 2 -log -game diffusion -ref gl4es`.
- Screenshot attachment: `C:\Users\arjun\.codex\codex-remote-attachments\01a02450-2442-7bd3-9232-46419e80d731\A4B61257-63D1-4C6F-80E0-67E7106A501C\1-Photo-1.jpg`; `53,760` bytes; SHA-256 `9FF030CE0FA2471AF3A7DE354C610A1E1C9DC41CE02878B3DDE88EBE0AABBB47`. It visibly shows sky, water/reflection and intro text but no complete terrain/object scene.
- Engine-log attachment: `C:\Users\arjun\.codex\codex-remote-attachments\01a02450-2442-7bd3-9232-46419e80d731\A4B61257-63D1-4C6F-80E0-67E7106A501C\2-engine.log`; `189,696` bytes; 2,976 lines; SHA-256 `F1888BC343ADECEFF74A697B7C9E8B73A6D3F0271E336D5D4BD9B929F479459D`.
- Positive runtime evidence: Diffusion module initialization; `maps/ch1map0.bsp`; first three complete map-trace frames; at least frame 56; world uint-index ingress/native match; drawable presentation.
- First production divergence: packaged provider marker absent from the log; `GL_EXT_texture_array - failed`; engine `procedures=4 max_layers=0 minimum=16 enabled=0`; Diffusion `extension=0 callbacks=1 max_layers=0 minimum=16 terrain_shaders=full enabled=0`; landscapes explicitly unavailable.
- Downstream evidence: `GL_EXT_shader_texture_lod` rejected, `texture2DLodEXT` undeclared in Bmodel/Studio fragments, and 593 `StudioSolid` rejections. These are preserved but are not the selected Phase O repair boundary.
- Termination evidence: log ends after further vegetation-surface creation without an in-process fatal/signal/clean-exit record. Matching current `.ips`: unavailable.
- Rejected `.ips`: `C:\Users\arjun\.codex\codex-remote-attachments\01a02450-2442-7bd3-9232-46419e80d731\4D6959C3-4408-417A-A202-A0D383E43EE7\1-xash-2026-08-21-120428.ips`; `28,954` bytes; SHA-256 `CE2FF0E4938E929B6C2A5308BFE5F48FAE745120CC9637F14ADF85510D9310F9`; August 21 / Bundle 105. It is not attributable to the August 22 Bundle 126 run.
- Qualification boundary: Bundle 126 fails live production texture-array admission and complete visible-scene/stability acceptance. Bundle 116 native conformance and Bundle 126 build/argument qualification remain valid.

## Phase O pending provider-lifecycle evidence

- Status: active; no implementation candidate, workflow, artifact, IPA, upload or device test exists at issuance.
- Control baseline: `308978fde8f7904c3511ccd6eed6bfb5c975ad5c`; implementation baseline: `5a529ff41d23b557e6e4e7878fb31284c7dfc661`.
- Required machine contract: `scripts/ios/wo56o-provider-lifecycle-contract.json` or the semantically equivalent path named in the report.
- Required proof: context/currentness and provider discovery ordering; all writes/reads/resets of native ES version, procedures, layer limit, ESSL 300 and array capability; extension-list construction/cache lifecycle; native/wrapper limit agreement; diagnostic-versus-ordinary route comparison; and provider-marker execution-versus-transport.
- Required rejection evidence: early/stale discovery, state reset, missing procedures, zero/insufficient layers, ESSL 300 failure, unavailable array route, cached list before capability, unconditional advertisement, fabricated limit, force path, direct native bypass, and every terrain fallback.
- Preserved out-of-scope evidence: shader-LOD/Bmodel/Studio failures, 593 Studio rejections, incomplete scene, abrupt termination, maps/transitions/gameplay and `ch1map1`.
- Outcome A may retain exactly one qualifying workflow/artifact and one verified IPA/tempfile identity; Outcomes B/C produce no partial runtime candidate.
- Related decision: [`DEC-009`](../../Decisions/DEC-009.md).
- Authoritative Google ledger Phase N/Phase O append: revision-guarded and verified by readback at revision `AIroW34aaNvQXMEgSa7x-l1eTqapjucXUj7nWl7rYAVamGDQKOk4YpYSSIBbEDA5_eZcuAhIlBdmkfCdh9xViN5R1a3p26kB_PqnzcSQWsM`.

## Phase O Outcome A build evidence — Bundle 130

- Starting ControlPlane/remote head: `4591b6753ca068185c7edb2be62348a5be99692e`.
- Structural implementation: `15b831ae6a25d79a01cff0a2d14c53e13cd9f89a`; exact rejection-fixture correction/candidate head: `f42f2c96b61624fe510fe32288bfbfa6873cc686`.
- Machine-readable audit: `scripts/ios/wo56o-provider-lifecycle-contract.json`; validator: `scripts/ios/validate-ios-provider-lifecycle.py`.
- Source proof: `GetHardwareExtensions` ran after current-context establishment, but `testGLSL("#version 300 es", 0)` generated malformed source and prevented `hardext.glsl300es`; conditional extension construction then withheld `GL_EXT_texture_array`.
- Qualifying push workflow: [32570119378](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32570119378), success; job [97024299913](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32570119378/job/97024299913).
- Retained artifact: [Xash3DiOS-arm64-unsigned](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32570119378/artifacts/9475150885), ID `9475150885`, archive size `8,620,189` bytes, digest `sha256:0ff55313fc563a301563af10724de5ced9555d518a24768f46c2673e47099293`, expiry `2026-09-05T11:27:53Z`.
- Exact IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 130, `8,718,358` bytes, SHA-256 `9FD6E3DD7E8FE19B4B3987479D2E69FFD99EF7FF4368FD1F9884286BB095BB5D`.
- Tempfile publication: [information page](https://tempfile.org/EA5v8CtY9bT/) and [direct IPA](https://tempfile.org/EA5v8CtY9bT/download), ID `EA5v8CtY9bT`, expiry `2026-08-24T11:37:45.305Z`. Metadata/security and a fresh direct download match the exact byte count and SHA-256; risk is `safe`, with no warning or suspicious patterns.
- Pre-artifact CI evidence: push run `32569704879` and its PR duplicate `32569706595` failed at the Phase K zero-layer mutation fixture because the old validator matched a second legitimate `>=16` snapshot expression. Neither produced an artifact. The exact-assignment fixture was corrected without changing runtime code. The later PR duplicate `32570121887` was cancelled and produced no artifact.
- Independent extraction: Bundle 130; main executable, GL4ES renderer, and Diffusion client/server/menu Mach-O headers are thin arm64 (`CFFAEDFE`, CPU `0C000001`); provider/engine/admission markers are in their owning binaries; the package inventory contains no proprietary game data.

Phase O's worker-produced result was build-qualified only. The later user-performed Bundle 130 observation below is separate evidence and does not retroactively change Phase O's authorization.

## Bundle 130 device observation and Phase P prerequisite

- Status: unplanned but accepted single ordinary-runtime observation on the established iPhone 16 Pro Max / iOS 26.6; no rerun requested.
- Candidate: `f42f2c96b61624fe510fe32288bfbfa6873cc686`; runtime `f42f2c96-dirty`, branch `agent/ios-proof-of-life`, `apple-arm64`.
- Exact arguments: `(null) -dev 2 -log -game diffusion -ref gl4es`.
- Provider marker: `native_es_major=3 procedures=1 max_layers=2048 minimum=16 glsl300=1 route=1 advertised=1 source=live-context`.
- Engine marker: `GL_EXT_texture_array` enabled; `procedures=4 max_layers=2048 minimum=16 enabled=1`.
- Diffusion marker: `extension=1 callbacks=1 max_layers=2048 minimum=16 terrain_shaders=full enabled=1`.
- Accepted boundary: live ordinary provider/engine/Diffusion texture-array admission. Landscape creation/drawing and complete scene/stability are not established.
- First deterministic remaining divergence: native `GL4ES_EXTENSIONS` includes `GL_EXT_shader_texture_lod`, yet 44 fragment compilations reject the extension, 396 `texture2DLodEXT` calls are undeclared, affected Bmodel/Studio/Grass programs fail, and 593 `StudioSolid` submissions are rejected.
- Screenshot: `C:\Users\arjun\.codex\codex-remote-attachments\01a02450-2442-7bd3-9232-46419e80d731\A69C4C28-8963-4A2C-AAA7-BF134733EECF\1-Photo-1.jpg`; `55,609` bytes; SHA-256 `C88414F8C5B66644D645E13F6B60A3B1DF94FCD0084F4A7793E58B57CE4D7ED9`.
- Engine log: `C:\Users\arjun\.codex\codex-remote-attachments\01a02450-2442-7bd3-9232-46419e80d731\A69C4C28-8963-4A2C-AAA7-BF134733EECF\2-engine.log`; `196,032` bytes; 3,055 lines; SHA-256 `A4D92F07FCC2401C615B7179D45A06EB01289007D40AFDF537B3324510ACAE47`.
- User observation: the process hard crashed. The log has no fatal/signal/assertion/shutdown record and ends after frame 56 with the render gate open; no matching Bundle 130 `.ips` is supplied.
- Phase P required audit: Diffusion `GL_ProcessShader` / `GL_LoadGPUShader`; GL4ES `gl4es_glShaderSource` / `ConvertShader`; `hardext.shaderlod` / `cubelod`; emitted native version/directive/intrinsic; native compile/link and shared `texfetch.h` consumer lineage.
- Phase P machine contract: `scripts/ios/wo56p-shader-lod-compatibility-contract.json` or the semantic equivalent named in the worker report.
- Related decision: [DEC-010](../../Decisions/DEC-010.md).
- Authoritative Google ledger: revision-guarded and verified by readback at `AIroW36mLoq7WrJrz_hQ7VNAZ8_Cp4ALusa3DW2ZE0kSZO_GS5x9v3CU-c9dwzB8xNVgb24EwecG-HOmPXZeJG3_1ndUT06S-r9l7deSS2o`.
- Stop state: WO-056 Phase P active; no device test, crash investigation, or later phase authorized.

## Phase P worker-continuity evidence

- Active worker: `Continue Work Order 56`, thread `01a022ae-5ea9-7121-8512-2fe40f5e99a2`, host `slingshot:env_e_6a6f826a8f4483218b6956e12dea53cc`; its last completed durable work was earlier WO-056 ledger-based execution, so it must adopt the current repo-backed ControlPlane before acting.
- Superseded worker: `Xash3DiOS Worker Bootstrap`, thread `019ff1ea-8387-7291-b391-f030d22db2ef`; current connector status `systemError`. Its session remains retained and is evidence only, subordinate to Git, CI, device evidence, and ControlPlane.
- Latest useful prior-worker report: no Phase P commit, CI run, candidate, artifact, upload, or device test was consumed. It identified that fragment-only ESSL 300 promotion would pair with an ESSL 100 vertex shader and fail linking, requiring audit of GL4ES's existing cross-stage compatibility/reconversion owner.
- Preserved exploratory workspace: ignored nested checkout `build/wo56m-gl4es-replay4`; notable unaccepted edits are in `src/gl/shaderconv.c` and `src/glx/hardext.c`. The replay checkout also contains the retained patch-stack modifications, so its aggregate dirty status is not itself a Phase P diff.
- Qualification rule: the active worker must inspect and source-prove the cross-stage finding within the required BmodelSolid/StudioSolid/GrassDlight lineage before promoting, rewriting, or discarding the exploratory implementation. The finding does not authorize a candidate by itself.

## Phase P source-lineage checkpoint

- Status: complete at documentation-only checkpoint `2026-08-22T22:44:34+05:30`; no production source, CI, IPA, or device action was consumed.
- Preserved inputs: `build/wo56p-gl4es-baseline`, `build/wo56p-gl4es-replay`, and `C:\Users\arjun\Documents\Codex\2026-08-22\you-are-the-fresh-implementation-worker\.tmp\wo56p`; all were inspected without alteration.
- Representative evidence: the exact `BmodelSolid`, `StudioSolid`, and `GrassDlight` source/output SHA-256 tuples and the compact vertex/fragment lineage table are recorded in the active Phase P section of [WO-056](../../WorkOrders/WO-056.md).
- Verified Diffusion origin: `GL_ProcessShader` assembles each stage as desktop `#version 130`; all three fragment families directly include shared `glsl/texfetch.h`, which supplies their `texture2DLod` helpers.
- Verified provider/baseline: native ES/ESSL 3 and `hardext.glsl300es=1`; the native extension string plus `noshaderlod=0` sets `hardext.shaderlod=1`, while `hardext.cubelod` is not exercised by these 2-D fixtures. Vertices emit ESSL 100; texture-array fragments emit ESSL 300 but still receive the ESSL 100 `GL_EXT_shader_texture_lod` directive and `texture2DLodEXT` rewrite. Apple rejects the fragment extension path, leaving the affected programs unlinked.
- Verified replay: fragments emit ESSL 300 core `textureLod` with no LOD extension; `need_essl300` is accumulated by `gl4es_glLinkProgram`, makes the initial ESSL 100 vertex conversion incompatible, and causes `redoShader` / `ConvertShader` to reconvert it as ESSL 300.
- Qualification boundary: source lineage and shared ownership are verified; production patch-stack implementation and native compile/link validation are not.
- First incomplete action: encode the verified three-file convergence in a new top-level `scripts/ios/gl4es-wo56-shader-lod-compatibility-ios.patch`. Nested GL4ES checkouts remain replay/validation environments only.
- Stop state: documentation checkpoint only; no CI, IPA, device test, crash investigation, or later phase is authorized or started.

## Phase P downstream patch-materialization checkpoint — evidence required

- Baseline/control: `8391769f836d38636895c607180b2b6c83975909`; local and remote were equal and the tree was clean when this checkpoint was issued.
- Active executor: fresh Xash3DiOS ControlPlane worker, thread `01a02a6a-349a-75f1-88dc-c1ad920dd38e`.
- Required durable implementation: `scripts/ios/gl4es-wo56-shader-lod-compatibility-ios.patch`.
- Authorized replay scope: exact GL4ES pin `81547d986798e876de8b434193920b606a72363f`; accepted iOS patch stack followed by the new patch; upstream paths limited to `src/gl/shader.c`, `src/gl/shader.h`, and `src/gl/shaderconv.c`.
- Required positive evidence: clean stack application; core ESSL 300 `textureLod` for `BmodelSolid`, `StudioSolid`, and `GrassDlight`; program-level reconversion of paired vertices to ESSL 300; retained ESSL 100/ES2 behavior; clean reverse and disposable-checkout state.
- Required negative evidence: no rejected EXT directive/intrinsic in ESSL 300 output; no family-specific bypass, semantic weakening, fabricated capability, unlinked acceptance, error suppression, direct nested-checkout promotion, or unrelated file scope.
- Required identities: implementation/reporting commit(s), patch bytes and SHA-256, representative output fingerprints, exact replay checkout/pin and accepted patch order, commands/results, and any minimal proof fixture.
- Explicitly absent at this gate: full Phase P validator-matrix integration, production patch-stack wiring, CI run/job, candidate, artifact, IPA/tempfile, device test, crash investigation, and Phase P final outcome selection.
- Stop gate: worker updates and read-back verifies ControlPlane and both ledgers, pushes, confirms clean local/remote equality, sends the mandatory callback, and stops for orchestrator review.
- Authoritative Google ledger order record: target document `1IYL3pI07fWvoYniP_NxZ7yO3gz9vbnM6sBFK8BT2zLU`, tab `t.0`; revision-guarded append and heading/stop-state readback verified at revision `AIroW37dnb32wczhEtqJuP9iOHLjo5RJGSvYiJXADi9pEq0Myki7rJpJ30vQDRxyHZrca7wDOitGkb6Ak6uR6jp39WTo_H_-1OlxQ6_Bu8Y`.

## Phase P downstream patch-materialization checkpoint — completed evidence

- Implementation commit: `d37bf36a5b707273359728a5ae08f81e712bea5d`; patch path `scripts/ios/gl4es-wo56-shader-lod-compatibility-ios.patch`; `10,564` bytes; SHA-256 `91AB64B6C392303BEA189BE2D66E409836489DFC6F46F2FC3DFB0BACCFA60FE4`.
- Exact patch scope: `src/gl/shader.c`, `src/gl/shader.h`, and `src/gl/shaderconv.c`; three `diff --git` entries and no other path.
- Exact replay pin: `81547d986798e876de8b434193920b606a72363f` in both preserved baseline/replay environments.
- Apply/reverse: non-mutating pinned checks passed. Disposable proof directory: `C:\Users\arjun\Documents\Codex\2026-08-21\you-are-the-successor-orchestrator-for\.tmp\wo56p-patch-proof-d37bf36a`; applied content matched all three replay files after newline normalization and reverse matched all three baseline files exactly.
- Family outputs: `BmodelSolid` and `StudioSolid` fragment core-LOD count `11`; `GrassDlight` count `9`; extension-directive and EXT-intrinsic counts are zero for all replay fragments. Paired reconverted vertices report ESSL 300, stage mappings, and `need_essl300=1`.
- Legacy negative control: before/after byte equality `true`; SHA-256 `937a60863d52d6b5ff7d73aa19baa8ea13c81a8a7cde325193f368860e8cd387`; ESSL 300 false; one extension directive and one EXT intrinsic retained.
- Negative scope: no family-specific path, semantic weakening, fabricated capability, unlinked acceptance, error suppression, nested-checkout promotion, or unrelated top-level change.
- Worker transport: repeated old/fresh worker failures and one orchestrator prompt failure occurred before repository writes. The durable patch was mechanically derived from accepted before/after evidence; no failed-thread state was adopted.
- Explicitly absent: production-stack integration, Phase P machine contract/full validator matrix, CI run/job, candidate, artifact, IPA/tempfile, device test, crash work, and Phase P final outcome.
- Authoritative Google ledger completion: target document `1IYL3pI07fWvoYniP_NxZ7yO3gz9vbnM6sBFK8BT2zLU`, tab `t.0`; verified readback revision `AIroW36Pdd17P_c07iiUWT1H5qZhSF4470eZUOzzRjpe2LF1HZpQtgCMZeEUVer8BH9LQupDTCYHSFdWZYkBpBeJNlUHYSU-AJzqnn8uHag`.
- Stop gate: checkpoint complete at orchestrator review; first incomplete action is the explicit validator/integration decision.
