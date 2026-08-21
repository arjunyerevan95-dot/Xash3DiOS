# Xash3DiOS Current State

Last updated: `2026-08-21T21:00:37+05:30`

## Repository

- Project: Xash3DiOS / Half-Life Diffusion iOS port
- Branch: `agent/ios-proof-of-life`
- Phase I repository/remote ledger HEAD: `8c9fd723fcaa3aff77178a8496ba82427cc28881`
- Control-plane materialization commit: `d91e2f5965d3b56eab95c50458f0931316aac50c`
- Phase J authorization commit: `7fb6030bd75d03b47c83aa1d20a03df23753780b`
- Phase J Outcome A record HEAD: the commit containing this revision of the file; its parent is `7fb6030bd75d03b47c83aa1d20a03df23753780b`
- Remote HEAD immediately before Phase J Outcome A publication: `7fb6030bd75d03b47c83aa1d20a03df23753780b`
- Worktree before Phase J Outcome A documentation: clean, with local and remote equal

## Current control state

- Current issued work order: [WO-056](../WorkOrders/WO-056.md). Phase J completed at Outcome A and is stopped at the orchestrator-review gate.
- Current phase: WO-056 Phase J Outcome A — Bundle 116 native texture-array conformance is device-accepted
- First incomplete step: orchestrator review of Phase J Outcome A and a decision whether to authorize a separately bounded production Diffusion terrain-admission phase
- Current blocker: no blocker remains inside the native texture-array conformance contract
- Current unresolved boundary: safe production admission of the qualified array capability into Diffusion terrain, including extension advertisement and the real terrain shader/material path

## Qualification state

- Highest qualified gate: physical-device acceptance of Bundle 116's normal-bootstrap native texture-array contract across object identity, mutable/immutable/compressed upload, ESSL-300 translation/reflection, sampler uniform update, VBO-backed drawing, four-layer sampling, direct-drawable readback, exact checksum, restoration, lifecycle, and bounded shutdown
- First unqualified gate: production Diffusion terrain admission and use of the now-qualified native array capability
- Latest qualified candidate: device-accepted Bundle 116, candidate `bc4b2b7181b3111053f14ff86e8ff634718acf30`, workflow `32489923843`
- Ledger commit: `8c9fd723fcaa3aff77178a8496ba82427cc28881`
- Latest IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,716,506` bytes, SHA-256 `4FD8D67DDAEBF1986AC795164B7CD20BA782319B9F29200C9EA76F1A4BA73806`
- Device acceptance: established on iPhone 16 Pro Max running iOS 26.6 by WO-056 Phase J Outcome A

## Established cause and correction

- Bundle 114's recorded `0x0502` originated immediately at `gl4es_glUniform1i(u_Array, 0)`.
- GL4ES reflected `GL_SAMPLER_2D_ARRAY` but omitted it from `uniformsize`, `is_uniform_int`, and `n_uniform`; the incompatible cached classification deterministically emitted `GL_INVALID_OPERATION`.
- The audit also found a native-GLES3-invalid client-side vertex pointer. The harness now uses a VBO-backed quad so the first fixed error cannot expose a second invalid operation.
- The exact Bundle 114 checksum `a915906d` is the FNV-1a-32 value of the 16 expected quadrant bytes: red RGBA, green RGBA, magenta RGBA, and yellow RGBA. It proves that array upload, layer selection, drawing, readback, and drawable presentation worked despite the rejected sampler-uniform update.

## Surviving hypotheses and boundaries

- Bundle 116 physically reported `0x0000` for all 51 immediate sampling/cleanup calls and retained checksum `a915906d`; the corrected native array conformance contract is qualified.
- No device-only Apple GLES3/GL4ES defect appeared within the bounded object/upload/shader/sampling/readback/restoration/lifecycle contract.
- Production terrain remains disabled and `GL_EXT_texture_array` remains unadvertised to Diffusion. Harness acceptance does not prove the real terrain shader/material integration.
- The independent `ch1map1` transition termination remains quarantined and unchanged.

## Latest important evidence

- Phase I candidate: `bc4b2b7181b3111053f14ff86e8ff634718acf30`
- Orchestrator decision: WO-056 Phase I Outcome A accepted; Phase J device evidence authorized
- Phase J device: iPhone 16 Pro Max, iOS 26.6, Apple A18 Pro GPU, drawable `2868x1320`
- Phase J log: `1-engine.log`, `23,255` bytes, `254` lines, SHA-256 `139B15982FEC0B4D34146B3F99A39D4758B36D77925394403B214BE9F5544FF5`
- Phase J result: all 51 immediate calls `0x0000`, checksum `a915906d`, terminal `PASS failures=0 diffusion_started=0`, clean intentional shutdown
- Authoritative Google ledger Phase J Outcome A readback revision: `AIroW35eAHEQsIjng7koSVYL26SxH_LPplNTY2_pP2hkjH5sDD-v7Sa_DztjVI28T3Rh0oHuQNk1fdRkpHFvUX0cTfPZNGDFprZXSl-CK-o`
- Qualifying workflow: `32489923843`, job `96794910555`, success
- Artifact: `Xash3DiOS-arm64-unsigned`, ID `9449473335`, ZIP SHA-256 `dacfb9d82bce5c3f777b2c77b38fa038d24655260c0438d199a6b596479355d2`
- Predecessor device log: `engine(20260821-122858).log`, SHA-256 `2A0A70CC3005795626ADF1597E656FBE30FEBEFBF0EACE0D9342BD09399FB32B`
- Complete evidence index: [Evidence/WO-056/manifest.md](../Evidence/WO-056/manifest.md)

## PortingOS experiment references

- Predecessor bounded experiment: `WO-056 Phase H / Bundle 114 normal-bootstrap native texture-array conformance`
- Completed correction experiment: `WO-056 Phase I / Bundle 116 native sampling/readback correction`
- Completed device experiment: `WO-056 Phase J / Bundle 116 normal-bootstrap device acceptance`
- Phase I contract: `scripts/ios/wo56i-sampling-readback-contract.json`
- Canonical Phase I tuple: candidate `bc4b2b71` / workflow `32489923843` / Bundle 116 / IPA hash above
- No separate PortingOS snapshot identifier is recorded; use the work-order, commit, contract, run, bundle, and artifact tuple

## Referenced decisions

- [DEC-001 — Complete native texture-array conformance before terrain admission](../Decisions/DEC-001.md)
- [DEC-002 — Use the normal Diffusion game-info bootstrap for the conformance route](../Decisions/DEC-002.md)
- [DEC-003 — Repair GL4ES sampler-array uniform classification and require VBO-backed GLES3 vertex input](../Decisions/DEC-003.md)
- [DEC-004 — Accept Phase I and authorize one Bundle 116 device qualification](../Decisions/DEC-004.md)
- [DEC-005 — Accept Bundle 116 native texture-array conformance on device](../Decisions/DEC-005.md)

## Future orchestrator/worker bootstrap

1. Read `Documentation/CURRENT_STATE.md`.
2. Read `WorkOrders/WO-056.md` (Phase J is complete at Outcome A; it is not authorization for terrain work).
3. Read only the `Decisions/` and `Evidence/` records referenced there.
4. Verify current Git/remote/CI state before acting.
5. Use the historical Google Docs ledger only when deeper context is required.
6. Do not restart already-qualified work without explicit authorization.
