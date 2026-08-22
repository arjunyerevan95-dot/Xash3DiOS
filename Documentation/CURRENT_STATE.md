# Xash3DiOS Current State

Last updated: `2026-08-22T14:35:55+05:30`

## Repository

- Project: Xash3DiOS / Half-Life Diffusion iOS port
- Branch: `agent/ios-proof-of-life`
- Control baseline before Phase O issuance: `308978fde8f7904c3511ccd6eed6bfb5c975ad5c`
- Local HEAD and `origin/agent/ios-proof-of-life`: equal at the control baseline with a clean worktree
- Latest implementation candidate: `5a529ff41d23b557e6e4e7878fb31284c7dfc661` (Bundle 126)
- No relevant GitHub Actions run is active at Phase O issuance

## Current control state

- Current issued work order: [WO-056](../WorkOrders/WO-056.md), Phase O active
- Status: Phase N physical-device run complete at Outcome B; Phase O provider-admission first-divergence audit/correction is authorized
- Current phase: WO-056 Phase O - ordinary-runtime GL4ES texture-array provider admission
- First incomplete step: the preserved worker must trace and record the live context/provider/extension-list lifecycle from SDL/EAGL context currentness through `GetHardwareExtensions`, `BuildExtensionsList`, engine `GL_CheckExtension`, the layer-limit query, and Diffusion admission before changing runtime code
- Current blocker: Bundle 126 ordinary startup exposes four engine callbacks but reports `GL_EXT_texture_array - failed`, `max_layers=0`, and disabled engine/Diffusion admission despite Bundle 116's device-qualified native array primitive
- Current unresolved boundary: why the qualified native ES3 array capability is not reflected through GL4ES's ordinary production provider state. The later shader failures and termination are preserved but are not Phase O repair scope

## Qualification state

- Highest physical-device-qualified gate: WO-056 Phase J / Bundle 116 bounded native texture-array conformance
- Highest build-qualified ordinary candidate: WO-056 Phase M / Bundle 126
- Latest device result: WO-056 Phase N / Bundle 126 Outcome B; `ch1map0.bsp` loaded and drawable frames were presented, but production texture-array admission failed, landscapes were disabled, model/world shader families failed, and the process terminated after at least 56 frames
- First unqualified gate: live GL4ES provider initialization and conditional `GL_EXT_texture_array` advertisement during ordinary startup
- Latest candidate tuple: `5a529ff41d23b557e6e4e7878fb31284c7dfc661`; workflow `32551387441`; job `96978610370`; artifact `9470194619`
- Latest IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 126, `8,717,507` bytes, SHA-256 `F5FE061690C0532C3086B2CCD650E541FCEB14F35128F7A35C66B670AE105ACF`

## Phase N device result

- After Phase M review, the orchestrator explicitly authorized one bounded Bundle 126 run on the established iPhone 16 Pro Max running iOS 26.6. The user installed the exact IPA, launched the ordinary tuple, selected Start once, observed the result, exported the complete log, and did not rerun.
- Runtime identity: `5a529ff4-dirty`, branch `agent/ios-proof-of-life`, `apple-arm64`; arguments `(null) -dev 2 -log -game diffusion -ref gl4es`.
- Positive boundary: Diffusion mounted, the engine/renderer/client initialized, `maps/ch1map0.bsp` loaded, the first three traced frames completed, world uint-index ingress matched native realization, and the screenshot proves drawable presentation of sky/water/text.
- First deterministic production divergence: the provider marker packaged in `libref_gl4es.dylib` is absent from `engine.log`; the engine reports `procedures=4 max_layers=0 minimum=16 enabled=0`; Diffusion reports `extension=0 callbacks=1 max_layers=0 minimum=16 terrain_shaders=full enabled=0`; and it warns that landscapes are unavailable.
- Later evidence: `GL_EXT_shader_texture_lod` / `texture2DLodEXT` compilation fails in Bmodel/Studio shader families and 593 `StudioSolid` variants are rejected because their programs are unlinked. These explain much of the missing scene but occur after the Phase O first divergence.
- Termination boundary: the log ends after frame 56 and further vegetation-surface creation without an in-process fatal/signal record. No matching current `.ips` exists. The supplied August 21 `.ips` is Bundle 105 and is rejected as evidence for this run.
- Outcome B does not revoke Bundle 116 native-array conformance or Bundle 126's build/argument qualification. It rejects live production admission and visible-scene qualification for Bundle 126.

## Phase O objective and boundaries

- Prove whether ordinary GL4ES provider discovery runs against a current ES3 context, whether `hardext.maxarraylayers` and `hardext.texture_array` are populated and retained, whether the extension list is constructed or cached before those values exist, whether `gl4es_texture_array_available()` participates at the correct time, and whether the absent provider marker is execution or transport loss.
- Compare the Bundle 116 diagnostic route with the Bundle 126 ordinary route without moving production ownership outside GL4ES.
- If and only if one structural cause is source-proven, correct it at its owner, add the complete contract/positive/rejection coverage, and build at most one qualifying ordinary candidate.
- Preserve conditional rejection for ES2/unknown providers, missing procedures, fewer than 16 layers, failed ESSL 300, or unavailable GL4ES array routes. No unconditional token, fabricated limit, force-enable, direct engine/Diffusion native bypass, 2-D/atlas/CPU fallback, or layer-zero substitution is allowed.
- Do not change the locked ordinary arguments, diagnostic harness, Diffusion shader-LOD/model families, materials, data, maps, input, transitions, gameplay, crash handling, or `ch1map1`. Do not request or perform a device test in Phase O.

## Latest important evidence

- Screenshot: `1-Photo-1.jpg`, `53,760` bytes, SHA-256 `9FF030CE0FA2471AF3A7DE354C610A1E1C9DC41CE02878B3DDE88EBE0AABBB47`
- Engine log: `2-engine.log`, `189,696` bytes, 2,976 lines, SHA-256 `F1888BC343ADECEFF74A697B7C9E8B73A6D3F0271E336D5D4BD9B929F479459D`
- Nonmatching historical crash report: `xash-2026-08-21-120428.ips`, Bundle 105, SHA-256 `CE2FF0E4938E929B6C2A5308BFE5F48FAE745120CC9637F14ADF85510D9310F9`; not attributable to Bundle 126
- Complete evidence index: [Evidence/WO-056/manifest.md](../Evidence/WO-056/manifest.md)
- Phase K contract: `scripts/ios/wo56k-production-array-admission-contract.json`
- Phase M contract: `scripts/ios/wo56m-ordinary-bootstrap-contract.json`
- Phase O required contract: `scripts/ios/wo56o-provider-lifecycle-contract.json` or the semantic equivalent named in the worker report
- Authoritative Google ledger Phase N/Phase O append was revision-guarded and verified by readback at revision `AIroW34aaNvQXMEgSa7x-l1eTqapjucXUj7nWl7rYAVamGDQKOk4YpYSSIBbEDA5_eZcuAhIlBdmkfCdh9xViN5R1a3p26kB_PqnzcSQWsM`

## Referenced decisions

- [DEC-005 - Accept Bundle 116 native texture-array conformance on device](../Decisions/DEC-005.md)
- [DEC-006 - Admit device-qualified native texture arrays conditionally into production](../Decisions/DEC-006.md)
- [DEC-007 - Accept Phase K and qualify live production admission before terrain](../Decisions/DEC-007.md)
- [DEC-008 - Build one locked ordinary-argument candidate before device admission](../Decisions/DEC-008.md)
- [DEC-009 - Preserve Phase N Outcome B and repair the first provider-admission divergence](../Decisions/DEC-009.md)

## Standing ControlPlane commands

When the user says **"next order please"**, the orchestrator must identify only the next justified bounded boundary; materialize it in the active repo-backed ControlPlane work-order/state/decision/evidence records; update both durable ledgers; validate, commit, and push the control-plane change; then notify the preserved worker to read and implement the published order. Do not create a replacement worker merely because notification is inconvenient or delayed.

When the user says **"the worker finished"**, the orchestrator must review the active ControlPlane state, Git/local-remote equality, relevant CI run/job/artifact, candidate/IPA identity, qualification boundary, and discrepancies before accepting the report. When a tempfile IPA exists, return its verified direct link to the user.

Every worker activation must include a completion callback directive. After the worker has updated and read-back verified ControlPlane and both durable ledgers, pushed its final reporting commit, confirmed local/remote equality and the stop gate, it must message the delegating/source orchestrator directly. The callback must include the selected outcome, final commit, CI run/job/artifact and IPA identity where applicable, qualification boundary, first incomplete step, and explicit stop state.

## Future orchestrator/worker bootstrap

1. Read `Documentation/CURRENT_STATE.md`.
2. Read `WorkOrders/WO-056.md` (Phase O is active).
3. Read only the `Decisions/` and `Evidence/` records referenced there.
4. Verify current Git/remote/CI state before acting.
5. Use the historical Google Docs ledger only when deeper context is required.
6. Do not restart already-qualified work without explicit authorization.
