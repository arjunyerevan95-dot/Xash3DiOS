# Xash3DiOS Current State

Last updated: `2026-08-22T01:23:41+05:30`

## Repository

- Project: Xash3DiOS / Half-Life Diffusion iOS port
- Branch: `agent/ios-proof-of-life`
- Local HEAD at ControlPlane reconciliation: `a067869505778dcabd8ab47b6b2e583892f8ce36`
- Remote HEAD at ControlPlane reconciliation: `a067869505778dcabd8ab47b6b2e583892f8ce36`
- Worktree before ControlPlane reconciliation: clean; local and remote equal
- Phase K implementation series: `c063202dc0c0111304e2d0a82a2506f1457f1454` → `12a80912c8c18870cad71e6116fbfeda2e26e2c3` → `38d429b189efc9a46e1a47f8463bf04797641fd6` → candidate `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`
- Phase K worker-report commit: `a067869505778dcabd8ab47b6b2e583892f8ce36`

## Current control state

- Current issued work order: [WO-056](../WorkOrders/WO-056.md), Phase K
- Status: worker-reported Outcome A; build-qualified and stopped at the orchestrator-review gate
- Current phase: WO-056 Phase K Outcome A — conditional production texture-array admission build-qualified
- First incomplete step: orchestrator review of the Phase K Outcome A evidence and decision whether to accept it and authorize a separately bounded physical-device production-terrain qualification phase
- Current blocker: Bundle 124 has no device or gameplay evidence for real Diffusion landscape loading, shader execution, rendering, or transition behavior
- Current unresolved boundary: production Diffusion terrain runtime acceptance using the now-conditionally admitted texture-array capability

## Qualification state

- Highest physical-device-qualified gate: WO-056 Phase J / Bundle 116 bounded native texture-array conformance
- Highest build-qualified production gate: WO-056 Phase K / Bundle 124 conditional production texture-array admission
- First unqualified gate: physical-device execution of the real Diffusion landscape loader and terrain shader/material path
- Latest candidate: Bundle 124, candidate `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`, workflow `32510363562`
- Latest IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,717,677` bytes, SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`
- Phase K is not device-accepted; no device test, gameplay test, or Arjun evidence request is currently authorized

## Established Phase K result

- GL4ES conditionally exposes `GL_EXT_texture_array` only for a live ES3+ provider with the required 3-D procedures, at least 16 layers, working ESSL 300, and the compiled qualified array routes.
- The engine independently requires the token, upload procedures, and live layer limit before retaining `GL_TEXTURE_ARRAY_EXT`; disagreement clears the bit and limit.
- Diffusion independently requires the token, at least 16 layers, and both array callbacks before retaining `R_TEXTURE_ARRAY_EXT`.
- The real landscape loader now preserves weight, diffuse, and optional normal array creation with complete failure cleanup and no CPU/2-D/atlas/layer-zero fallback.
- The iOS shader route preserves `GLSL_ALLOW_TEXTURE_ARRAY 1`, `TERRAIN_NUM_LAYERS`, `BMODEL_MULTI_LAYERS`, and the real terrain material features instead of advertising arrays while stripping their consumer.
- Machine-readable contract: `scripts/ios/wo56k-production-array-admission-contract.json`.

## Surviving hypotheses and boundaries

- Source, mutation, exact-pin replay, full arm64 build, and packaged-owner verification establish one coherent conditional production admission path.
- Those gates do not prove that ordinary Diffusion terrain loads, renders, or transitions correctly on physical iOS hardware.
- Bundle 116's device-qualified array primitive remains the runtime prerequisite; Bundle 124 extends it into production admission but has not exercised production terrain on device.
- The independent `ch1map1` transition termination remains quarantined and unchanged.

## Latest important evidence

- Qualifying workflow: `32510363562`, job `96859751554`, success on exact candidate `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`
- Retained artifact: `Xash3DiOS-arm64-unsigned`, ID `9456949434`, archive SHA-256 `5ed24f8a6ad27dfaea62ed315329d8bdf79e95c5a0053a4ba36187236f42b744`
- IPA: Bundle 124, `8,717,677` bytes, SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`
- Exact pins replayed: GL4ES `81547d986798e876de8b434193920b606a72363f`, Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`
- Packaged verification: required production markers in their actual owners, 13 thin-arm64 Mach-O objects, and no proprietary game assets
- Pre-qualification failures `32508365615`, `32509025360`, and `32509723819` are preserved negative evidence and produced no retained artifact
- Complete evidence index: [Evidence/WO-056/manifest.md](../Evidence/WO-056/manifest.md)

## PortingOS experiment references

- Completed and accepted prerequisite: WO-056 Phase J / Bundle 116 physical-device native array conformance
- Worker-reported result awaiting orchestrator acceptance: WO-056 Phase K / Bundle 124 conditional production admission, Outcome A
- Phase I contract: `scripts/ios/wo56i-sampling-readback-contract.json`
- Phase K contract: `scripts/ios/wo56k-production-array-admission-contract.json`
- Canonical Phase K tuple: candidate `976c38f3` / workflow `32510363562` / Bundle 124 / IPA hash above

## Referenced decisions

- [DEC-001 — Complete native texture-array conformance before terrain admission](../Decisions/DEC-001.md)
- [DEC-003 — Repair GL4ES sampler-array uniform classification and require VBO-backed GLES3 vertex input](../Decisions/DEC-003.md)
- [DEC-005 — Accept Bundle 116 native texture-array conformance on device](../Decisions/DEC-005.md)
- [DEC-006 — Admit device-qualified native texture arrays conditionally into production](../Decisions/DEC-006.md)

## Standing ControlPlane command

When the user says **“next order please”**, the orchestrator must: identify only the next justified bounded boundary; materialize it in the active repo-backed ControlPlane work-order/state/decision/evidence records; update both durable ledgers; validate, commit, and push the documentation/control-plane change; then notify the preserved worker to read and implement the published order. Do not create a replacement worker merely because notification is inconvenient or delayed.

Every worker activation must also include a completion callback directive. After the worker has updated and read-back verified ControlPlane and both durable ledgers, pushed its final reporting commit, confirmed local/remote equality and the stop gate, it must message the delegating/source orchestrator directly. The callback must include the selected outcome, final commit, CI run/job/artifact and IPA identity where applicable, qualification boundary, first incomplete step, and explicit stop state. The orchestrator activation message must provide its current thread ID and host ID; do not hard-code a superseded orchestrator identity into future orders.

## Future orchestrator/worker bootstrap

1. Read `Documentation/CURRENT_STATE.md`.
2. Read `WorkOrders/WO-056.md` (Phase K is worker-reported Outcome A at orchestrator review; it is not authorization for device testing).
3. Read only the `Decisions/` and `Evidence/` records referenced there.
4. Verify current Git/remote/CI state before acting.
5. Use the historical Google Docs ledger only when deeper context is required.
6. Do not restart already-qualified work without explicit authorization.
