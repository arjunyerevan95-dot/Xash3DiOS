# Xash3DiOS Current State

Last updated: `2026-08-22T10:02:07+05:30`

## Repository

- Project: Xash3DiOS / Half-Life Diffusion iOS port
- Branch: `agent/ios-proof-of-life`
- Phase M implementation commit: `5a529ff41d23b557e6e4e7878fb31284c7dfc661`
- Local/remote implementation HEAD before final reporting: `5a529ff41d23b557e6e4e7878fb31284c7dfc661`; equal and clean
- Phase K implementation series: `c063202dc0c0111304e2d0a82a2506f1457f1454` → `12a80912c8c18870cad71e6116fbfeda2e26e2c3` → `38d429b189efc9a46e1a47f8463bf04797641fd6` → candidate `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`
- Phase K worker-report commit: `a067869505778dcabd8ab47b6b2e583892f8ce36`

## Current control state

- Current issued work order: [WO-056](../WorkOrders/WO-056.md), Phase M complete
- Status: Outcome A complete at the orchestrator-review gate; Bundle 126 is build-qualified only
- Current phase: WO-056 Phase M — locked ordinary-bootstrap candidate build qualification, complete
- First incomplete step: orchestrator review and an explicit decision whether to authorize a separate physical-device ordinary-bootstrap admission test
- Current blocker: live provider/engine/Diffusion production texture-array agreement has not been observed on physical iOS hardware with the ordinary tuple
- Current unresolved boundary: physical-device ordinary-bootstrap production texture-array admission before any terrain, map, transition, or gameplay execution

## Qualification state

- Highest physical-device-qualified gate: WO-056 Phase J / Bundle 116 bounded native texture-array conformance
- Highest build-qualified production gate: WO-056 Phase M / Bundle 126 locked ordinary-bootstrap production admission
- First unqualified gate: physical-device provider/engine/Diffusion admission agreement during an ordinary self-test-free bootstrap
- Latest candidate: Bundle 126, candidate `5a529ff41d23b557e6e4e7878fb31284c7dfc661`, workflow `32551387441`, job `96978610370`, artifact `9470194619`
- Latest IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,717,507` bytes, SHA-256 `F5FE061690C0532C3086B2CCD650E541FCEB14F35128F7A35C66B670AE105ACF`
- Phase K Outcome A remains accepted as build-qualified production admission. Phase L Outcome C remains a correct pre-launch stop. Phase M Outcome A adds exact ordinary-argument package qualification only; no device, terrain, map, transition, or gameplay test was authorized or performed.

## Accepted Phase K result

- GL4ES conditionally exposes `GL_EXT_texture_array` only for a live ES3+ provider with the required 3-D procedures, at least 16 layers, working ESSL 300, and the compiled qualified array routes.
- The engine independently requires the token, upload procedures, and live layer limit before retaining `GL_TEXTURE_ARRAY_EXT`; disagreement clears the bit and limit.
- Diffusion independently requires the token, at least 16 layers, and both array callbacks before retaining `R_TEXTURE_ARRAY_EXT`.
- The real landscape loader now preserves weight, diffuse, and optional normal array creation with complete failure cleanup and no CPU/2-D/atlas/layer-zero fallback.
- The iOS shader route preserves `GLSL_ALLOW_TEXTURE_ARRAY 1`, `TERRAIN_NUM_LAYERS`, `BMODEL_MULTI_LAYERS`, and the real terrain material features instead of advertising arrays while stripping their consumer.
- Machine-readable contract: `scripts/ios/wo56k-production-array-admission-contract.json`.

## Phase L Outcome C stop boundary

- Exact IPA identity passed: Bundle 124, `8,717,677` bytes, SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`.
- Argument identity failed before launch: source and packaged executable enforce `-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest` through a disabled launch field, while Phase L requires the same string without the self-test flag.
- No install, launch, screenshot, log, `.ips`, terrain, map, transition, gameplay, or `ch1map1` action occurred. The one-run authorization was not consumed.
- Outcome C does not reject the renderer or production-admission implementation. It leaves live ordinary-bootstrap agreement unqualified.

## Completed Phase M boundary

- Change only the locked iOS launch tuple from the diagnostic self-test form to exact ordinary arguments `-dev 2 -log -game diffusion -ref gl4es`; keep the launch field disabled for this candidate.
- Preserve the self-test implementation and its explicit flag gates as dormant regression machinery. The combined ordinary-plus-self-test launch string must disappear from source and the packaged executable.
- Update the affected source, validation, mutation, contract, and IPA-verification surfaces so they prove exact ordinary default arguments, reject automatic self-test activation, and retain the already-qualified renderer and harness contracts.
- Sole retained qualifying workflow `32551387441` succeeded; automatic PR duplicate `32551389885` was cancelled before build/artifact upload.
- Bundle 126 contains exactly one standalone ordinary tuple, no combined automatic-self-test tuple, the separate self-test token and machinery, and all three Phase K production markers in their required owners.
- GitHub artifact `9470194619` and the one tempfile mirror `MrnVs2sedq5` reproduce the exact IPA identity above. Stop at orchestrator review without requesting or performing a device test.

## Surviving hypotheses and boundaries

- Source, mutation, exact-pin replay, full arm64 build, and packaged-owner verification establish one coherent conditional production admission path.
- Those gates do not prove that ordinary Diffusion terrain loads, renders, or transitions correctly on physical iOS hardware. Phase L intentionally stops before that boundary.
- Phase M was an argument-routing/build experiment only. It did not reinterpret Phase K, change capability predicates, or exercise production terrain.
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
- Authoritative Google ledger Phase M order was appended under revision guard and its stop-state paragraph was verified by readback at revision `AIroW37tae1LAWrBYYTMvYeeh_9sHD6ReMvvblPZDotrbAQSlIRULeEX4Xtbxvp6FKtHH08vVjI5DdWIvkmENwrDk9vVvA2jZdRMSmIwXfY`.
- Phase L order revision: `AIroW36cJUxGI7JGaMrb1e_-ZnY-2hz35dp3f9oR5_8XOk5WxxvOGFH_ylpE2YQB81wyRM8whgNLXFbiu6v0RmievJgG1VBId2Arbg8P0Cg`.

## PortingOS experiment references

- Completed and accepted prerequisite: WO-056 Phase J / Bundle 116 physical-device native array conformance
- Accepted build-qualified result: WO-056 Phase K / Bundle 124 conditional production admission, Outcome A
- Latest experiment: WO-056 Phase L / Bundle 124 ordinary-bootstrap admission-marker acceptance — Outcome C before launch
- Latest experiment: WO-056 Phase M / Bundle 126 exact locked ordinary-bootstrap candidate build qualification — Outcome A
- Phase I contract: `scripts/ios/wo56i-sampling-readback-contract.json`
- Phase K contract: `scripts/ios/wo56k-production-array-admission-contract.json`
- Canonical Phase K tuple: candidate `976c38f3` / workflow `32510363562` / Bundle 124 / IPA hash above

## Referenced decisions

- [DEC-001 — Complete native texture-array conformance before terrain admission](../Decisions/DEC-001.md)
- [DEC-003 — Repair GL4ES sampler-array uniform classification and require VBO-backed GLES3 vertex input](../Decisions/DEC-003.md)
- [DEC-005 — Accept Bundle 116 native texture-array conformance on device](../Decisions/DEC-005.md)
- [DEC-006 — Admit device-qualified native texture arrays conditionally into production](../Decisions/DEC-006.md)
- [DEC-007 — Accept Phase K and qualify live production admission before terrain](../Decisions/DEC-007.md)
- [DEC-008 — Build one locked ordinary-argument candidate before device admission](../Decisions/DEC-008.md)

## Standing ControlPlane command

When the user says **“next order please”**, the orchestrator must: identify only the next justified bounded boundary; materialize it in the active repo-backed ControlPlane work-order/state/decision/evidence records; update both durable ledgers; validate, commit, and push the documentation/control-plane change; then notify the preserved worker to read and implement the published order. Do not create a replacement worker merely because notification is inconvenient or delayed.

Every worker activation must also include a completion callback directive. After the worker has updated and read-back verified ControlPlane and both durable ledgers, pushed its final reporting commit, confirmed local/remote equality and the stop gate, it must message the delegating/source orchestrator directly. The callback must include the selected outcome, final commit, CI run/job/artifact and IPA identity where applicable, qualification boundary, first incomplete step, and explicit stop state. The orchestrator activation message must provide its current thread ID and host ID; do not hard-code a superseded orchestrator identity into future orders.

## Future orchestrator/worker bootstrap

1. Read `Documentation/CURRENT_STATE.md`.
2. Read `WorkOrders/WO-056.md` (Phase M is active for one build-qualified ordinary-argument candidate; it does not authorize a device test).
3. Read only the `Decisions/` and `Evidence/` records referenced there.
4. Verify current Git/remote/CI state before acting.
5. Use the historical Google Docs ledger only when deeper context is required.
6. Do not restart already-qualified work without explicit authorization.
