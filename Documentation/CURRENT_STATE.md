# Xash3DiOS Current State

Last updated: `2026-08-22T01:32:42+05:30`

## Repository

- Project: Xash3DiOS / Half-Life Diffusion iOS port
- Branch: `agent/ios-proof-of-life`
- Local HEAD before Phase L materialization: `62ce9f8da4f095122d69628af53a9dfb4b9a16ac`
- Remote HEAD before Phase L materialization: `62ce9f8da4f095122d69628af53a9dfb4b9a16ac`
- Worktree before ControlPlane reconciliation: clean; local and remote equal
- Phase K implementation series: `c063202dc0c0111304e2d0a82a2506f1457f1454` → `12a80912c8c18870cad71e6116fbfeda2e26e2c3` → `38d429b189efc9a46e1a47f8463bf04797641fd6` → candidate `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`
- Phase K worker-report commit: `a067869505778dcabd8ab47b6b2e583892f8ce36`

## Current control state

- Current issued work order: [WO-056](../WorkOrders/WO-056.md), Phase L
- Status: active; one evidence-only normal-bootstrap device launch of exact Bundle 124 is authorized
- Current phase: WO-056 Phase L — Bundle 124 normal-bootstrap production texture-array admission device acceptance
- First incomplete step: the preserved worker must request and validate the exact one-run Phase L device evidence package
- Current blocker: no physical-device evidence yet proves that Bundle 124's provider, engine, and Diffusion production-admission gates all enable and agree during ordinary startup
- Current unresolved boundary: live physical-device production texture-array admission before any terrain, map, transition, or gameplay execution

## Qualification state

- Highest physical-device-qualified gate: WO-056 Phase J / Bundle 116 bounded native texture-array conformance
- Highest build-qualified production gate: WO-056 Phase K / Bundle 124 conditional production texture-array admission
- First unqualified gate: physical-device normal-bootstrap agreement of the three Bundle 124 production-admission markers
- Latest candidate: Bundle 124, candidate `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`, workflow `32510363562`
- Latest IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,717,677` bytes, SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`
- Phase K Outcome A is accepted as build-qualified only. Phase L authorizes one menu-only device launch of exact Bundle 124; terrain, map, transition, and gameplay testing remain prohibited.

## Accepted Phase K result

- GL4ES conditionally exposes `GL_EXT_texture_array` only for a live ES3+ provider with the required 3-D procedures, at least 16 layers, working ESSL 300, and the compiled qualified array routes.
- The engine independently requires the token, upload procedures, and live layer limit before retaining `GL_TEXTURE_ARRAY_EXT`; disagreement clears the bit and limit.
- Diffusion independently requires the token, at least 16 layers, and both array callbacks before retaining `R_TEXTURE_ARRAY_EXT`.
- The real landscape loader now preserves weight, diffuse, and optional normal array creation with complete failure cleanup and no CPU/2-D/atlas/layer-zero fallback.
- The iOS shader route preserves `GLSL_ALLOW_TEXTURE_ARRAY 1`, `TERRAIN_NUM_LAYERS`, `BMODEL_MULTI_LAYERS`, and the real terrain material features instead of advertising arrays while stripping their consumer.
- Machine-readable contract: `scripts/ios/wo56k-production-array-admission-contract.json`.

## Active Phase L boundary

- Reuse Bundle 124 exactly; do not build, patch, launch CI, alter data, or create another artifact.
- Locked ordinary arguments: `-dev 2 -log -game diffusion -ref gl4es` with no self-test flag.
- Install over the existing app/data, launch once, reach the stable Diffusion menu, wait about 10 seconds, take one screenshot, export the complete log, and stop.
- Do not click Start/New Game/difficulty, load a map, enter terrain/gameplay, or exercise the quarantined `ch1map1` path.
- Device acceptance requires the provider, engine, and Diffusion admission markers to agree on enabled native ES3 texture arrays with at least 16 layers, with no `GL_EXT_texture_array - failed`, landscape-unavailable warning, relevant GL/shader failure, or crash.

## Surviving hypotheses and boundaries

- Source, mutation, exact-pin replay, full arm64 build, and packaged-owner verification establish one coherent conditional production admission path.
- Those gates do not prove that ordinary Diffusion terrain loads, renders, or transitions correctly on physical iOS hardware. Phase L intentionally stops before that boundary.
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
- Authoritative Google ledger Phase L order was appended under revision guard and verified by readback at revision `AIroW36cJUxGI7JGaMrb1e_-ZnY-2hz35dp3f9oR5_8XOk5WxxvOGFH_ylpE2YQB81wyRM8whgNLXFbiu6v0RmievJgG1VBId2Arbg8P0Cg`.

## PortingOS experiment references

- Completed and accepted prerequisite: WO-056 Phase J / Bundle 116 physical-device native array conformance
- Accepted build-qualified result: WO-056 Phase K / Bundle 124 conditional production admission, Outcome A
- Active experiment: WO-056 Phase L / Bundle 124 one-run normal-bootstrap admission-marker device acceptance
- Phase I contract: `scripts/ios/wo56i-sampling-readback-contract.json`
- Phase K contract: `scripts/ios/wo56k-production-array-admission-contract.json`
- Canonical Phase K tuple: candidate `976c38f3` / workflow `32510363562` / Bundle 124 / IPA hash above

## Referenced decisions

- [DEC-001 — Complete native texture-array conformance before terrain admission](../Decisions/DEC-001.md)
- [DEC-003 — Repair GL4ES sampler-array uniform classification and require VBO-backed GLES3 vertex input](../Decisions/DEC-003.md)
- [DEC-005 — Accept Bundle 116 native texture-array conformance on device](../Decisions/DEC-005.md)
- [DEC-006 — Admit device-qualified native texture arrays conditionally into production](../Decisions/DEC-006.md)
- [DEC-007 — Accept Phase K and qualify live production admission before terrain](../Decisions/DEC-007.md)

## Standing ControlPlane command

When the user says **“next order please”**, the orchestrator must: identify only the next justified bounded boundary; materialize it in the active repo-backed ControlPlane work-order/state/decision/evidence records; update both durable ledgers; validate, commit, and push the documentation/control-plane change; then notify the preserved worker to read and implement the published order. Do not create a replacement worker merely because notification is inconvenient or delayed.

Every worker activation must also include a completion callback directive. After the worker has updated and read-back verified ControlPlane and both durable ledgers, pushed its final reporting commit, confirmed local/remote equality and the stop gate, it must message the delegating/source orchestrator directly. The callback must include the selected outcome, final commit, CI run/job/artifact and IPA identity where applicable, qualification boundary, first incomplete step, and explicit stop state. The orchestrator activation message must provide its current thread ID and host ID; do not hard-code a superseded orchestrator identity into future orders.

## Future orchestrator/worker bootstrap

1. Read `Documentation/CURRENT_STATE.md`.
2. Read `WorkOrders/WO-056.md` (Phase L authorizes exactly one normal-bootstrap, menu-only Bundle 124 device run; it does not authorize terrain or gameplay).
3. Read only the `Decisions/` and `Evidence/` records referenced there.
4. Verify current Git/remote/CI state before acting.
5. Use the historical Google Docs ledger only when deeper context is required.
6. Do not restart already-qualified work without explicit authorization.
