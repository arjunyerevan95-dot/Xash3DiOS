# Xash3DiOS Current State

Last updated: `2026-08-21T21:21:29+05:30`

## Repository

- Project: Xash3DiOS / Half-Life Diffusion iOS port
- Branch: `agent/ios-proof-of-life`
- Local HEAD before Phase K materialization: `cc02ebaa192abb3a11ce5ea520649a096a68ed44`
- Remote HEAD before Phase K materialization: `cc02ebaa192abb3a11ce5ea520649a096a68ed44`
- Worktree before Phase K materialization: clean; local and remote equal
- Phase I implementation candidate: `bc4b2b7181b3111053f14ff86e8ff634718acf30`
- Phase I repository-ledger commit: `8c9fd723fcaa3aff77178a8496ba82427cc28881`
- Phase J Outcome A record: `cc02ebaa192abb3a11ce5ea520649a096a68ed44`

## Current control state

- Current issued work order: [WO-056](../WorkOrders/WO-056.md), Phase K
- Status: active; authorized for one bounded production texture-array admission audit, coherent implementation, validation, and build qualification
- Current phase: WO-056 Phase K — conditional production texture-array admission
- First incomplete step: the preserved worker must audit the exact end-to-end production admission path and produce the source-proven capability/provenance table required by Phase K before or with one coherent implementation
- Current blocker: production still reports `GL_EXT_texture_array - failed`; engine and Diffusion do not admit the otherwise device-qualified capability
- Current unresolved boundary: the complete guarded route from GL4ES/native ES3 capability advertisement through engine and Diffusion gates, real landscape array loading, and unstripped terrain shaders

## Qualification state

- Highest qualified gate: WO-056 Phase J physical-device acceptance of Bundle 116's bounded native texture-array conformance contract
- First unqualified gate: WO-056 Phase K production engine/Diffusion texture-array admission and build qualification
- Latest qualified candidate: Bundle 116, candidate `bc4b2b7181b3111053f14ff86e8ff634718acf30`, workflow `32489923843`
- Latest IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,716,506` bytes, SHA-256 `4FD8D67DDAEBF1986AC795164B7CD20BA782319B9F29200C9EA76F1A4BA73806`
- Device acceptance: iPhone 16 Pro Max, iOS 26.6, Apple A18 Pro GPU, drawable `2868x1320`
- No Phase K candidate, workflow, artifact, IPA, or device evidence exists yet

## Surviving hypotheses and boundaries

- Native texture arrays are a viable Apple GLES3/GL4ES primitive: Bundle 116 passed object identity, mutable/immutable/compressed upload, ESSL-300 translation/reflection, sampler update, VBO-backed drawing, four-layer sampling, direct-drawable readback, exact checksum, cleanup, and lifecycle on device.
- The next defect boundary is admission/integration, not the native primitive: GL4ES production capability advertisement remains disabled, engine `GL_TEXTURE_ARRAY_EXT` and Diffusion `R_TEXTURE_ARRAY_EXT` remain false, and the landscape route is therefore unavailable.
- An extension-string-only fix is unsafe. Phase K must prove the native entry points, limits, engine and Diffusion agreement, array-loader path, sampler/target contract, and terrain shader feature preservation as one bounded capability.
- The iOS Diffusion shader patch currently filters `MULTI_LAYERS`; this must be audited because advertising arrays while stripping the terrain define would be an incomplete production admission.
- The independent `ch1map1` transition termination remains quarantined and unchanged.

## Latest important evidence

- Phase J device log: `1-engine.log`, `23,255` bytes, `254` lines, SHA-256 `139B15982FEC0B4D34146B3F99A39D4758B36D77925394403B214BE9F5544FF5`
- Phase J result: all 51 immediate calls `0x0000`, checksum `a915906d`, terminal `PASS failures=0 diffusion_started=0`, clean intentional shutdown
- Qualifying workflow: `32489923843`, job `96794910555`, success; artifact `Xash3DiOS-arm64-unsigned`, ID `9449473335`
- CI drift check: no relevant run active; Bundle 116 remains the newest qualifying evidence
- Authoritative Google ledger Phase K order verified by readback at revision `AIroW37mgJWSAdh9os0FJ0VzXL-r36Dj5xAz9EfzGMg_oXINPkRe-WWO3uZKluW6OOn4DguV3EyefcmwR0ZwOd7v-shLklDwN20hf5dbH84`
- Engine gate: `GL_CheckExtension("GL_EXT_texture_array", ..., "gl_texture_2d_array", GL_TEXTURE_ARRAY_EXT, 0)` and `GL_MAX_ARRAY_TEXTURE_LAYERS_EXT`
- Diffusion gate: `R_TEXTURE_ARRAY_EXT` controls `GLSL_ALLOW_TEXTURE_ARRAY`; `LoadTerrainLayers` reaches `LOAD_TEXTURE_ARRAY` for landscape diffuse and normal layers
- Terrain shaders use `sampler2DArray` under `GLSL_ALLOW_TEXTURE_ARRAY && BMODEL_MULTI_LAYERS`; the current iOS shader patch filters `MULTI_LAYERS`
- Complete evidence index: [Evidence/WO-056/manifest.md](../Evidence/WO-056/manifest.md)

## PortingOS experiment references

- Completed: WO-056 Phase I / Bundle 116 native sampling/readback correction
- Completed: WO-056 Phase J / Bundle 116 normal-bootstrap device acceptance
- Active: WO-056 Phase K / conditional production texture-array admission
- Phase I contract: `scripts/ios/wo56i-sampling-readback-contract.json`
- Phase K required contract: `scripts/ios/wo56k-production-array-admission-contract.json` or a semantically equivalent machine-readable contract named in the worker report
- Canonical qualified tuple: candidate `bc4b2b71` / workflow `32489923843` / Bundle 116 / IPA hash above

## Referenced decisions

- [DEC-001 — Complete native texture-array conformance before terrain admission](../Decisions/DEC-001.md)
- [DEC-003 — Repair GL4ES sampler-array uniform classification and require VBO-backed GLES3 vertex input](../Decisions/DEC-003.md)
- [DEC-005 — Accept Bundle 116 native texture-array conformance on device](../Decisions/DEC-005.md)
- [DEC-006 — Admit device-qualified native texture arrays conditionally into production](../Decisions/DEC-006.md)

## Standing ControlPlane command

When the user says **“next order please”**, the orchestrator must: identify only the next justified bounded boundary; materialize it in the active repo-backed ControlPlane work-order/state/decision/evidence records; update both durable ledgers; validate, commit, and push the documentation/control-plane change; then notify the preserved worker to read and implement the published order. Do not create a replacement worker merely because notification is inconvenient or delayed.

## Future orchestrator/worker bootstrap

1. Read `Documentation/CURRENT_STATE.md`.
2. Read the active `WorkOrders/WO-056.md`, currently Phase K.
3. Read only the `Decisions/` and `Evidence/` records referenced there.
4. Verify current Git/remote/CI state before acting.
5. Use the historical Google Docs ledger only when deeper context is required.
6. Do not restart already-qualified work without explicit authorization.
