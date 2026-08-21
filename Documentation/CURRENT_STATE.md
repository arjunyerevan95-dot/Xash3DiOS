# Xash3DiOS Current State

Last updated: `2026-08-21T19:51:53+05:30`

## Repository

- Project: Xash3DiOS / Half-Life Diffusion iOS port
- Branch: `agent/ios-proof-of-life`
- Local HEAD at materialization verification: `8c9fd723fcaa3aff77178a8496ba82427cc28881`
- Remote HEAD at materialization verification: `8c9fd723fcaa3aff77178a8496ba82427cc28881`
- Control-plane materialization HEAD: the commit containing this file; its parent is the verified HEAD above
- Worktree at verification: clean, with local and remote equal (`+0/-0`)

## Current control state

- Current issued work order: [WO-056 Phase I](../WorkOrders/WO-056.md), completed at Outcome A and retained as the current control record pending orchestrator review. No engineering or device-evidence phase is active.
- Current phase: orchestrator-review gate after WO-056 Phase I
- First incomplete step: review and accept or reject the WO-056 Phase I Outcome A report and Bundle 116 build qualification; do not start a device-evidence phase without a new explicit orchestrator order
- Current blocker: Bundle 116 has no physical-device evidence and is not device-accepted
- Current unresolved boundary: physical-device confirmation that every new immediate sampling call reports `0x0000`, the expected checksum remains `a915906d`, and the terminal becomes `PASS failures=0 diffusion_started=0`

## Qualification state

- Highest qualified gate: source-proven correction, mutation/rejection validation, exact-pin patch replay, full iPhoneOS arm64 engine/Half-Life/Diffusion build, IPA-contract inspection, embedded-marker verification, artifact publication, and tempfile round-trip verification for Bundle 116
- First unqualified gate: physical-device execution of the corrected native sampling/readback contract
- Latest qualified candidate: Bundle 116, candidate `bc4b2b7181b3111053f14ff86e8ff634718acf30`, workflow `32489923843`
- Ledger commit: `8c9fd723fcaa3aff77178a8496ba82427cc28881`
- Latest IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,716,506` bytes, SHA-256 `4FD8D67DDAEBF1986AC795164B7CD20BA782319B9F29200C9EA76F1A4BA73806`
- Device acceptance: not established; no device test or evidence request is currently authorized

## Established cause and correction

- Bundle 114's recorded `0x0502` originated immediately at `gl4es_glUniform1i(u_Array, 0)`.
- GL4ES reflected `GL_SAMPLER_2D_ARRAY` but omitted it from `uniformsize`, `is_uniform_int`, and `n_uniform`; the incompatible cached classification deterministically emitted `GL_INVALID_OPERATION`.
- The audit also found a native-GLES3-invalid client-side vertex pointer. The harness now uses a VBO-backed quad so the first fixed error cannot expose a second invalid operation.
- The exact Bundle 114 checksum `a915906d` is the FNV-1a-32 value of the 16 expected quadrant bytes: red RGBA, green RGBA, magenta RGBA, and yellow RGBA. It proves that array upload, layer selection, drawing, readback, and drawable presentation worked despite the rejected sampler-uniform update.

## Surviving hypotheses and boundaries

- Source and build evidence predict that Bundle 116 will report `0x0000` for each immediate sampling call and retain checksum `a915906d`; this remains unproven on a physical device.
- A device-only Apple GLES3/GL4ES state or lifecycle defect could still reject Bundle 116 even though the source-proven errors are corrected.
- Terrain remains disabled and `GL_EXT_texture_array` remains unadvertised to Diffusion until a later explicitly authorized device-acceptance gate passes.
- The independent `ch1map1` transition termination remains quarantined and unchanged.

## Latest important evidence

- Phase I candidate: `bc4b2b7181b3111053f14ff86e8ff634718acf30`
- Qualifying workflow: `32489923843`, job `96794910555`, success
- Artifact: `Xash3DiOS-arm64-unsigned`, ID `9449473335`, ZIP SHA-256 `dacfb9d82bce5c3f777b2c77b38fa038d24655260c0438d199a6b596479355d2`
- Predecessor device log: `engine(20260821-122858).log`, SHA-256 `2A0A70CC3005795626ADF1597E656FBE30FEBEFBF0EACE0D9342BD09399FB32B`
- Complete evidence index: [Evidence/WO-056/manifest.md](../Evidence/WO-056/manifest.md)

## PortingOS experiment references

- Predecessor bounded experiment: `WO-056 Phase H / Bundle 114 normal-bootstrap native texture-array conformance`
- Completed correction experiment: `WO-056 Phase I / Bundle 116 native sampling/readback correction`
- Phase I contract: `scripts/ios/wo56i-sampling-readback-contract.json`
- Canonical Phase I tuple: candidate `bc4b2b71` / workflow `32489923843` / Bundle 116 / IPA hash above
- No separate PortingOS snapshot identifier is recorded; use the work-order, commit, contract, run, bundle, and artifact tuple

## Referenced decisions

- [DEC-001 — Complete native texture-array conformance before terrain admission](../Decisions/DEC-001.md)
- [DEC-002 — Use the normal Diffusion game-info bootstrap for the conformance route](../Decisions/DEC-002.md)
- [DEC-003 — Repair GL4ES sampler-array uniform classification and require VBO-backed GLES3 vertex input](../Decisions/DEC-003.md)

## Future orchestrator/worker bootstrap

1. Read `Documentation/CURRENT_STATE.md`.
2. Read the active `WorkOrders/WO-056.md` (currently complete at the orchestrator-review gate; do not treat it as new authorization).
3. Read only the `Decisions/` and `Evidence/` records referenced there.
4. Verify current Git/remote/CI state before acting.
5. Use the historical Google Docs ledger only when deeper context is required.
6. Do not restart already-qualified work without explicit authorization.
