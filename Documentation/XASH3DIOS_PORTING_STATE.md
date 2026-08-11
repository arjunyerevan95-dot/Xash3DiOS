# Xash3DiOS Diffusion porting state

Updated: 2026-08-11

## Reproducible inputs

- Branch: `agent/ios-proof-of-life`
- Launch arguments: `-dev 2 -log -game diffusion -ref gl4es`
- Diffusion: `14d156bf3a6993c172697fac83a937836c3b5561`
- Diffusion-MainUI: `8c68de2f2325a0130953719efc3ae413eb24e01a`
- Diffusion-executable: `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`

## Run 39 — latest device-tested baseline

- Commit: `073939309e388186641a4d4c93605a4df544fa63`
- Workflow: `31513272674`
- Device result: Diffusion reaches its real menu; touch, menu callbacks, New Game navigation, difficulty selection, and selection audio work. Selecting a difficulty appears frozen during the transition to chapter 1.
- Preserved behavior: iOS skips only the decorative `menux.bsp` background. The real C++ menu and callbacks remain enabled.
- Verified failure boundary: the Normal difficulty callback returns into `newgame`; map startup advances through renderer setup and `maps/ch1map0_load.cfg`; then the first custom-renderer work synchronously compiles the studio shader variants. The 4,073-line log ends with `Game started`, so the boundary is not the menu callback or map loader.
- Device log evidence: attached `engine(20260811-170524).log`/`1-engine.log`, SHA-256 `C9EB501B2984F9A2F9F520D194A22A9212948B1B922B1E8B22713F95CEF85B96`.
- Reproducible analysis: `python3 scripts/ios/analyze-diffusion-shader-log.py engine.log --expect-run39` reports 138 total uber-shader compiles (indices 8–145), including 51 `StudioSolid` and 80 `StudioDlight` programs. It observes 30 exact `MAXSTUDIOBONES` values but only translated `u_BonePosition[128]` and `u_BoneQuaternion[128]` layouts. Removing animated per-model counts from the observed keys reduces 131 studio keys to 33 while retaining one-bone keys.
- Attempted approach and result: run 39 already canonicalized mobile material features and switched to on-demand compilation. Its additional exact per-model bone-count specialization did not reduce the GL4ES-reported layout and instead multiplied first-frame cache entries. Run 36 is obsolete and must not be retested.

## Run 40 — shared animated-model shader layout

- Candidate commit: pending publication.
- Workflow and IPA: pending CI.
- Change: `GL_UberShaderForSolidStudio` and `GL_UberShaderForDlightStudio` now retain only the source's genuinely distinct `MAXSTUDIOBONES 1` rigid-model path on iOS. Animated models omit per-model bone-count defines and share the default `glConfig.max_skinning_bones` option/layout key.
- Guardrails: the real Diffusion menu remains intact; desktop shader economy behavior is unchanged; no core renderer/model feature is disabled. `validate-diffusion-ios-policy.py` fails CI if an arbitrary model bone count returns to either iOS key builder. IPA verification requires the exact renderer-policy marker.
- Expected marker: `iOS mobile renderer profile: canonical materials, shared animated-model shader layout, on-demand shaders`
- Local validation: the updated main patch applies to the three exact pinned source revisions; the run-39 evidence analyzer passes; the applied-source iOS policy validator passes. The macOS CI job is responsible for the `XASH_IOS=1` arm64 `client`, `server`, and `menu` builds, shader translation gate, IPA contract verification, and artifact packaging.
- Acceptance state: pending one device test. A successful compile or CI run is not device acceptance.
- Single requested device test: install the run-40 IPA, launch with the unchanged arguments, select **New Game → chapter 1 → Normal** once, and wait up to 60 seconds without backgrounding. Report whether an interactive gameplay frame appears and whether touch input responds; attach one screenshot and the resulting `engine.log`. Do not retest run 39.
- Next action: publish, complete CI, record the workflow/artifact SHA-256 here, deliver the IPA, then wait for orchestrator review and the single device result before any further patch.
