# Xash3DiOS Current State

Last updated: `2026-08-22T23:16:43+05:30`

## Repository

- Project: Xash3DiOS / Half-Life Diffusion iOS port
- Branch: `agent/ios-proof-of-life`
- Phase O starting ControlPlane commit: `4591b6753ca068185c7edb2be62348a5be99692e`
- Phase O implementation/candidate commits: `15b831ae6a25d79a01cff0a2d14c53e13cd9f89a` and `f42f2c96b61624fe510fe32288bfbfa6873cc686`
- Phase O reporting / Phase P ControlPlane baseline: `78ae00a86b2938943b8c0d2f7ba6846bee6b7538`
- Latest build-qualified candidate: Bundle 130 at `f42f2c96b61624fe510fe32288bfbfa6873cc686`
- Qualifying workflow `32570119378`, job `97024299913`, artifact `9475150885`; no relevant workflow remains active

## Current control state

- Current issued work order: [WO-056](../WorkOrders/WO-056.md), Phase P active
- Status: Phase O Outcome A is accepted; the Phase P source-lineage checkpoint is complete, and the bounded downstream patch-materialization checkpoint is active
- Current phase: WO-056 Phase P - ordinary-runtime fragment explicit-LOD shader compatibility
- First incomplete step: encode the verified `shader.c` / `shader.h` / `shaderconv.c` cross-stage ESSL 300 convergence as a new top-level `scripts/ios/gl4es-wo56-shader-lod-compatibility-ios.patch`; preserved nested GL4ES checkouts remain evidence only
- Corrected boundary: GL4ES's generic ESSL probe formed malformed `#version 300 es#extension ...` source, leaving `hardext.glsl300es=0`; `BuildExtensionsList` therefore withheld `GL_EXT_texture_array` before the engine layer query
- Verified Phase P boundary: texture-array use promotes the affected fragment shaders to ESSL 300, but baseline GL4ES still applies its ESSL 100 extension rewrite, emitting a rejected `GL_EXT_shader_texture_lod` directive and undeclared `texture2DLodEXT`; the paired vertex stage remains ESSL 100 unless GL4ES's existing program compatibility/reconversion state carries an ESSL 300 requirement across both stages
- Preserved unresolved boundary: the user-observed hard crash occurs after the last durable engine record and remains separate from Phase P

## Active worker binding

- Active implementation worker: fresh Xash3DiOS ControlPlane worker, thread `01a02a6a-349a-75f1-88dc-c1ad920dd38e`, host `slingshot:env_e_6a6f826a8f4483218b6956e12dea53cc`.
- Superseded continuation worker: `Continue Work Order 56`, thread `01a022ae-5ea9-7121-8512-2fe40f5e99a2`; retained as implementation history after repeated context/policy transport failures and no longer the active executor.
- Superseded execution worker: `Xash3DiOS Worker Bootstrap`, thread `019ff1ea-8387-7291-b391-f030d22db2ef`; retained as implementation history but removed from active execution after repeated context/policy transport failures and current `systemError` status.
- Handoff boundary: the superseded worker consumed no Phase P CI run or candidate and made no top-level source commit. It left exploratory, unaccepted edits in the ignored replay checkout `build/wo56m-gl4es-replay4`, principally `src/gl/shaderconv.c` and `src/glx/hardext.c`.
- Verified lineage finding: fragment-only ESSL 300 promotion leaves the paired vertex shader at ESSL 100; adding `need_essl300` to GL4ES's existing `shaderconv_need_t` accumulation, compatibility, and `redoShader` reconversion owner makes both stages converge on ESSL 300. This is source-lineage qualification only, not production implementation or native compile/link qualification.
- The active worker must read this file, [WO-056](../WorkOrders/WO-056.md), [DEC-010](../Decisions/DEC-010.md), and the referenced evidence; execute only the active Phase P downstream patch-materialization checkpoint; and stop before CI, candidate, IPA, or device work.
- Completion callback target: orchestrator thread `01a02450-2442-7bd3-9232-46419e80d731` on host `slingshot:env_e_6a6f826a8f4483218b6956e12dea53cc`.

## Qualification state

- Highest physical-device-qualified gate: Bundle 130 ordinary provider/engine/Diffusion texture-array admission with `2,048` live layers
- Highest build-qualified ordinary candidate: WO-056 Phase O / Bundle 130
- Latest device result: unplanned but accepted Bundle 130 observation; array admission succeeds, the same incomplete sky/water/text scene appears, affected fragment shader families fail, and the user observes a hard crash after frame 56 or later
- First unqualified gate: production patch-stack implementation and local compile/link validation of the source-proven GL4ES cross-stage ESSL 300 explicit-LOD correction
- Latest candidate tuple: `f42f2c96b61624fe510fe32288bfbfa6873cc686`; workflow `32570119378`; job `97024299913`; artifact `9475150885`
- Latest IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 130, `8,718,358` bytes, SHA-256 `9FD6E3DD7E8FE19B4B3987479D2E69FFD99EF7FF4368FD1F9884286BB095BB5D`

## Phase N device result

- After Phase M review, the orchestrator explicitly authorized one bounded Bundle 126 run on the established iPhone 16 Pro Max running iOS 26.6. The user installed the exact IPA, launched the ordinary tuple, selected Start once, observed the result, exported the complete log, and did not rerun.
- Runtime identity: `5a529ff4-dirty`, branch `agent/ios-proof-of-life`, `apple-arm64`; arguments `(null) -dev 2 -log -game diffusion -ref gl4es`.
- Positive boundary: Diffusion mounted, the engine/renderer/client initialized, `maps/ch1map0.bsp` loaded, the first three traced frames completed, world uint-index ingress matched native realization, and the screenshot proves drawable presentation of sky/water/text.
- First deterministic production divergence: the provider marker packaged in `libref_gl4es.dylib` is absent from `engine.log`; the engine reports `procedures=4 max_layers=0 minimum=16 enabled=0`; Diffusion reports `extension=0 callbacks=1 max_layers=0 minimum=16 terrain_shaders=full enabled=0`; and it warns that landscapes are unavailable.
- Later evidence: `GL_EXT_shader_texture_lod` / `texture2DLodEXT` compilation fails in Bmodel/Studio shader families and 593 `StudioSolid` variants are rejected because their programs are unlinked. These explain much of the missing scene but occur after the Phase O first divergence.
- Termination boundary: the log ends after frame 56 and further vegetation-surface creation without an in-process fatal/signal record. No matching current `.ips` exists. The supplied August 21 `.ips` is Bundle 105 and is rejected as evidence for this run.
- Outcome B does not revoke Bundle 116 native-array conformance or Bundle 126's build/argument qualification. It rejects live production admission and visible-scene qualification for Bundle 126.

## Bundle 130 device evidence

- Runtime identity: `f42f2c96-dirty`, branch `agent/ios-proof-of-life`, `apple-arm64`; exact ordinary arguments `(null) -dev 2 -log -game diffusion -ref gl4es`.
- Provider: `native_es_major=3 procedures=1 max_layers=2048 minimum=16 glsl300=1 route=1 advertised=1 source=live-context`.
- Engine: `GL_EXT_texture_array` enabled; `procedures=4 max_layers=2048 minimum=16 enabled=1`.
- Diffusion: `extension=1 callbacks=1 max_layers=2048 minimum=16 terrain_shaders=full enabled=1`.
- First remaining divergence: 44 fragment compile failures reject `GL_EXT_shader_texture_lod`; 396 `texture2DLodEXT` calls are undeclared; Bmodel/Studio/Grass programs fail and 593 `StudioSolid` submissions are rejected.
- Termination: the user directly observes a hard crash. The log has no fatal/signal/shutdown marker and ends after frame 56 with the render gate open; no matching Bundle 130 `.ips` is supplied.

## Phase P verified lineage and remaining boundaries

- Representative `BmodelSolid`, `StudioSolid`, and `GrassDlight` vertex/fragment lineage is verified from Diffusion's assembled desktop GLSL 130 through matched baseline/replay `ConvertShader` output; the exact table and fingerprints are recorded in [WO-056](../WorkOrders/WO-056.md) and the evidence manifest.
- Baseline fragments are ESSL 300 because of texture arrays yet carry the ESSL 100 `GL_EXT_shader_texture_lod` / `texture2DLodEXT` path; replay fragments use core `textureLod`, and GL4ES program-level need accumulation/reconversion promotes their ESSL 100 vertex partners to ESSL 300.
- Source lineage identifies one shared structural owner: GL4ES `shaderconv_need_t` plus `gl4es_glLinkProgram` compatibility/reconversion. Native Apple compile/link success has not been claimed or tested in this documentation-only checkpoint.
- The active checkpoint authorizes only the top-level patch-stack materialization named above and focused deterministic local replay proof. Complete validator-matrix integration, native/CI qualification, artifact/IPA production, and device testing remain later gates under this Phase P order.
- Preserve explicit mip-LOD behavior; no implicit sampling, constant-LOD, disabled-family, per-family, force, fabricated-capability, unlinked-program, CPU/2-D/atlas, or error-suppression workaround is allowed.
- Do not alter accepted texture-array admission, arguments, diagnostic harness, materials/data, model/vegetation policy, maps, menus, input, transitions, gameplay, `ch1map1`, crash handling, or platform lifecycle. No Phase P device test is authorized.

## Latest important evidence

- Bundle 130 screenshot: `1-Photo-1.jpg`, `55,609` bytes, SHA-256 `C88414F8C5B66644D645E13F6B60A3B1DF94FCD0084F4A7793E58B57CE4D7ED9`
- Bundle 130 engine log: `engine.log`, `196,032` bytes, 3,055 lines, SHA-256 `A4D92F07FCC2401C615B7179D45A06EB01289007D40AFDF537B3324510ACAE47`
- Nonmatching historical crash report: `xash-2026-08-21-120428.ips`, Bundle 105, SHA-256 `CE2FF0E4938E929B6C2A5308BFE5F48FAE745120CC9637F14ADF85510D9310F9`; not attributable to Bundle 126
- Complete evidence index: [Evidence/WO-056/manifest.md](../Evidence/WO-056/manifest.md)
- Phase K contract: `scripts/ios/wo56k-production-array-admission-contract.json`
- Phase M contract: `scripts/ios/wo56m-ordinary-bootstrap-contract.json`
- Phase O contract: `scripts/ios/wo56o-provider-lifecycle-contract.json`
- Phase P required contract: `scripts/ios/wo56p-shader-lod-compatibility-contract.json` or the semantic equivalent named in the worker report
- Authoritative Google ledger Phase P downstream patch-materialization checkpoint was revision-guarded and verified by readback at revision `AIroW37dnb32wczhEtqJuP9iOHLjo5RJGSvYiJXADi9pEq0Myki7rJpJ30vQDRxyHZrca7wDOitGkb6Ak6uR6jp39WTo_H_-1OlxQ6_Bu8Y`

## Referenced decisions

- [DEC-005 - Accept Bundle 116 native texture-array conformance on device](../Decisions/DEC-005.md)
- [DEC-006 - Admit device-qualified native texture arrays conditionally into production](../Decisions/DEC-006.md)
- [DEC-007 - Accept Phase K and qualify live production admission before terrain](../Decisions/DEC-007.md)
- [DEC-008 - Build one locked ordinary-argument candidate before device admission](../Decisions/DEC-008.md)
- [DEC-009 - Preserve Phase N Outcome B and repair the first provider-admission divergence](../Decisions/DEC-009.md)
- [DEC-010 - Accept Bundle 130 array admission and select shader-LOD compatibility](../Decisions/DEC-010.md)

## Standing ControlPlane commands

When the user says **"next order please"**, the orchestrator must identify only the next justified bounded boundary; materialize it in the active repo-backed ControlPlane work-order/state/decision/evidence records; update both durable ledgers; validate, commit, and push the control-plane change; then notify the preserved worker to read and implement the published order. Do not create a replacement worker merely because notification is inconvenient or delayed.

When the user says **"the worker finished"**, the orchestrator must review the active ControlPlane state, Git/local-remote equality, relevant CI run/job/artifact, candidate/IPA identity, qualification boundary, and discrepancies before accepting the report. When a tempfile IPA exists, return its verified direct link to the user.

Every worker activation must include a completion callback directive. After the worker has updated and read-back verified ControlPlane and both durable ledgers, pushed its final reporting commit, confirmed local/remote equality and the stop gate, it must message the delegating/source orchestrator directly. The callback must include the selected outcome, final commit, CI run/job/artifact and IPA identity where applicable, qualification boundary, first incomplete step, and explicit stop state.

## Future orchestrator/worker bootstrap

1. Read `Documentation/CURRENT_STATE.md`.
2. Read `WorkOrders/WO-056.md` (Phase P is active).
3. Read only the `Decisions/` and `Evidence/` records referenced there.
4. Verify current Git/remote/CI state before acting.
5. Use the historical Google Docs ledger only when deeper context is required.
6. Do not restart already-qualified work without explicit authorization.
