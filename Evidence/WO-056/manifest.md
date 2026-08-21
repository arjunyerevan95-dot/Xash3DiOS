# WO-056 Evidence Manifest

This manifest references the evidence used to close WO-056 Phase I at Outcome A and the evidence required by active Phase J. Large artifacts are referenced rather than copied into the repository.

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
- No Bundle 116 device test had been requested or performed before Phase J authorization. Phase J is now authorized, but no Phase J device evidence has yet been received and Bundle 116 is not device-accepted.

## Phase J pending evidence

- Status: authorized; no Phase J device evidence has yet been received.
- Exact candidate under test: Bundle 116 IPA and SHA-256 listed above.
- Required device identity: model and iOS version.
- Required primary artifact: complete engine log from the sole authorized launch, including filename, byte count, and SHA-256.
- Required success boundary: all retained PASS stages; each immediate sampling call `error=0x0000 result=PASS`; checksum `a915906d`; terminal `PASS failures=0 diffusion_started=0`; bounded intentional shutdown.
- Conditional artifact: matching iOS `.ips` only when the process terminates unexpectedly without the complete terminal marker and the report exists.
- No rebuild, second launch, gameplay run, or terrain admission is authorized.
- Authoritative Google ledger authorization/readback revision: `AIroW37HusfW5RcASaQXlFaFbLG6Gn6MQSQKue4vM5AcoplbZxyRyXtBUv4dHDYxPXkic431rdzCcxaXlSDz3IUyB9P73Jr-36zbyq1Cbi8`.

## PortingOS references

- Phase H / Bundle 114: predecessor normal-bootstrap device experiment.
- Phase I / Bundle 116: completed build-qualified diagnostic/correction experiment.
- Contract identifier: `scripts/ios/wo56i-sampling-readback-contract.json`.
- No separate PortingOS snapshot ID was recorded for Phase I.

## Related control-plane records

- [`Documentation/CURRENT_STATE.md`](../../Documentation/CURRENT_STATE.md)
- [`WorkOrders/WO-056.md`](../../WorkOrders/WO-056.md)
- [`DEC-001`](../../Decisions/DEC-001.md)
- [`DEC-002`](../../Decisions/DEC-002.md)
- [`DEC-003`](../../Decisions/DEC-003.md)
- [`DEC-004`](../../Decisions/DEC-004.md)
