# Xash3DiOS Diffusion porting state

Updated: 2026-08-14

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

## Run 41 — work order 40, shared animated-model shader layout

- Candidate commit: `aa5c54dffa40feeb737d18ce59118d2eb8cc8fdd`.
- Workflow: [iOS Proof of Life run 41](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31519910689), ID `31519910689`, result `success`.
- Artifact: `Xash3DiOS-arm64-unsigned`, ID `9112778515`, GitHub artifact ZIP SHA-256 `B1E203E29161446190FCD5689E5AF7D8E7314EF6742B57E74758F6E331003666`.
- IPA: `Xash3DiOS-run41-aa5c54df-arm64-unsigned.ipa`, 8,656,903 bytes, SHA-256 `D15B2A059AAADF6C32519B21839D212D1992DDD75D46D67B8F584A2C6F2FE72C`.
- Change: `GL_UberShaderForSolidStudio` and `GL_UberShaderForDlightStudio` now retain only the source's genuinely distinct `MAXSTUDIOBONES 1` rigid-model path on iOS. Animated models omit per-model bone-count defines and share the default `glConfig.max_skinning_bones` option/layout key.
- Guardrails: the real Diffusion menu remains intact; desktop shader economy behavior is unchanged; no core renderer/model feature is disabled. `validate-diffusion-ios-policy.py` fails CI if an arbitrary model bone count returns to either iOS key builder. IPA verification requires the exact renderer-policy marker.
- Expected marker: `iOS mobile renderer profile: canonical materials, shared animated-model shader layout, on-demand shaders`
- Validation: the updated main patch applies to the exact pinned source tree; the run-39 evidence analyzer passes; the applied-source iOS policy validator passes. CI validated all 350 translated GL4ES mobile shader variants, linked the `XASH_IOS=1` arm64 Diffusion `client`, `server`, and `menu` targets, verified every required arm64 Mach-O and embedded marker in the IPA, and packaged the artifact successfully.
- Device result: not accepted. The real menu, touch callbacks, chapter/difficulty selection, and audio still work, but selecting Normal never exposes an interactive gameplay frame. A second tap only produces looping audio. The shared animated-model shader policy is retained because it removed the run-39 compile storm and is independently validated by the log.
- Run-41 log evidence: attached `engine(20260811-181200).log`/`1-engine.log`, 63,442 bytes, SHA-256 `5F7BFDDE516FC2A26D74220FCFA8AB660A5E748AA941E0FE925F467BD2B6ABE2`.
- Reproducible comparison: `--expect-run41` reports 40 total uber-shader compiles and 33 studio compiles, versus run 39's 138 and 131. Run 41 contains only the rigid `MAXSTUDIOBONES 1` specialization, reaches `Game started`, completes three bounded custom-render traces, and then records 11 completed foliage surfaces before the log ends at a generic foliage-completion message. The analyzer deliberately does not key its verdict to surface 648.
- Verified boundary: the difficulty callback, command dispatch, map load, server activation, renderer initialization, resource propagation, and the first three custom-render calls all return. Because those are distinct frames, the preceding host/post-render/present work must also have returned enough times to advance the loop. The existing framebuffer checkpoints were stubs, however, so run 41 has no direct cumulative presented-frame count. At least 11 foliage constructors return; the next caller, later foliage work, custom-renderer return, post-render, flush, and swap/present boundaries are not distinguished. No crash, signal, or fatal error is logged.
- Acceptance state: device-tested and rejected as an interactive candidate; retained as the implementation baseline for work order 41.
- Completed device test: Run 41 was tested once with the unchanged arguments and supplied the evidence above. Do not retest run 39 or run 41.
- Next action: execute work order 41 as a diagnostics-only Run 42 unless its source audit proves a structural defect.

## Run 42 — work order 41, bounded render/foliage/present liveness

- Candidate/run: Run 42 diagnostics-only candidate. Instrumentation commit `a77cd0bb27a9145b5770c69b5207644eff7d7190`; final candidate commit `0dfab18be9dc79c81151aa9b61cafe27cd5e32b5` restores the retained three-frame renderer-detail counter after the first CI attempt exposed an undeclared legacy reference.
- CI: [iOS Proof of Life run 31529653232](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31529653232), result `success`; engine, pinned Diffusion `client`/`server`/`menu`, 350 translated mobile shaders, IPA contract, and artifact upload all passed. Initial workflows `31526005364` and `31526011076` failed only because `ios_renderer_trace_frames` was removed while two existing bounded detail reads remained; `0dfab18b` restores that independent three-frame counter without shortening the new 12-frame liveness budget.
- Artifact: `Xash3DiOS-arm64-unsigned`, ID `9116500241`, 8,568,460-byte GitHub artifact ZIP, SHA-256 `CBC6956D0460944AFCCB9393C71C4CAE442365E9061968EDB3C83509B42EDC03`, retained through 2026-08-25. Stable artifact page: https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31529653232/artifacts/9116500241
- IPA: `Xash3DiOS-run42-0dfab18b-arm64-unsigned.ipa`, 8,665,523 bytes, SHA-256 `C883DEE6333506BC8775EDD47D3466A9E36B659424904034E3BF57EFC1731CC0`.
- Tempfile delivery: https://tempfile.org/oZjoKQPQdX5/ (direct: https://tempfile.org/oZjoKQPQdX5/download), expires 2026-08-13 20:09:30 UTC. Tempfile's server-side scan reports the same size and SHA-256 with risk level `safe`.
- Classification: diagnostics-only. The source audit found bounded BSP/surface/entry/triangle/sample loops and an allocation sized from the precomputed maximum grass count. The run-41 tail does not prove an infinite foliage loop, memory overrun, GL stall, stale menu framebuffer, or blocked present, so no structural renderer or gameplay behavior is changed.
- Source call path: `CMenuNewGame::StartGameCb` queues `newgame`; `SV_NewGame_f` selects `GI->startmap`; `COM_NewGame` schedules `STATE_LOAD_LEVEL`; `COM_Frame` calls `SV_ExecLoadLevel`; `SV_SpawnServer` queues `maps/ch1map0_load.cfg`; `SV_ActivateServer` emits `Game started`. Each active host frame proceeds through `Host_Frame` → `Host_ClientFrame` → `SCR_UpdateScreen` → `V_RenderView` → engine `GL_RenderFrame` → renderer `R_RenderFrame` → Diffusion `HUD_RenderFrame` → `R_RenderScene` → `R_DrawWorld` → visible-surface traversal → `R_AddGrassToChain` → `R_ConstructGrass`. A returning custom renderer continues through audio/backend completion, `V_PostRender` (HUD, VGUI, menu, touch), `R_EndFrame`, `GL2_ShimEndFrame`, `R_Set2DMode(false)`, and engine `GL_SwapBuffers`; the pinned iOS backend implements that final call with SDL2 `SDL_GL_SwapWindow`, which reaches the UIKit/EAGL present implementation in the bundled SDL framework.
- Bounded diagnostics: the engine arms 12 gameplay frames and reports monotonic host/client/screen/render/post milestones plus UI visibility. The renderer reports custom-render entry/return, GL2 and 2D flush boundaries, swap/present entry/return, and cumulative renderer-call, renderer-return, swap-attempt, and presented counts; after the fixed trace window only a two-second returned-frame heartbeat remains. Diffusion reports the first 12 normal world traversals and caps foliage output at 128 lines, including dispatch, allocation return, matching layer, large-triangle/sample progress, construction return, and caller return. No GL state queries or synchronous GPU waits were added.
- Preserved constraints: the real Diffusion menu and callback path remain enabled; touch, audio, screen fades, world/model rendering, GL4ES, on-demand shared animated shaders, and foliage remain functional. No subsystem is bypassed or disabled.
- Reproducible guards: the run-39 and run-41 analyzers confirm 138/131 versus 40/33 shader counts and the run-41 post-start boundary. The policy validator requires the shared shader key and bounded generic liveness markers while rejecting instrumentation overfit to a specific surface. IPA verification requires the engine, renderer, world-traversal, and foliage markers in their actual arm64 binaries.
- Expected new markers: `iOS liveness instrumentation: host, screen, renderer, foliage, flush, swap/present`; `iOS liveness renderer policy: bounded_frames=12`; `iOS world traversal:`; `iOS foliage liveness policy:`; and `iOS foliage:`. The last returning marker and first absent return marker determine whether the stall is in foliage construction/caller traversal, later custom rendering, post-render/UI, GL flush, swap/present, or the outer host loop.
- Local/build validation: both attached logs pass their exact analyzer expectations; the Python analyzers compile; the liveness patch reverses and reapplies cleanly over the exact pinned Diffusion tree after the accepted patches; and the applied-source iOS policy validator passes. GitHub Actions compiled the engine and exact pinned arm64 `XASH_IOS=1` Diffusion client/server/menu targets, validated every translated mobile shader, and passed the expanded IPA marker/architecture contract.
- Acceptance state: build-qualified but pending one Run-42 device test. Build success alone is not device acceptance.
- Single requested device test: install the Run-42 IPA, launch with `-dev 2 -log -game diffusion -ref gl4es`, tap **New Game → chapter 1 → Normal** exactly once, do not tap again or background the app, wait 60 seconds, then attach one screenshot and the complete new `engine.log`. Do not retest run 39 or run 41.
- Remaining risks: diagnostics may identify a long but ultimately finite foliage build rather than a hard block; a UIKit/EAGL failure inside SDL is visible only as a missing return from the surrounding swap/present call; device termination can truncate buffered log output after the true boundary.

## Work order 42 — Run 42 device result and framebuffer/layer discriminator

- Accepted baseline remains Run 39. Run 41's shared animated-model shader layout remains an independently validated retained fix; Run 42 remains diagnostics-only and is not accepted as an interactive candidate.
- Authoritative Run-42 log: Drive file `Xash3DiOS-Run42-engine-20260812-022759.log`, 2,070 lines, 114,487 bytes, SHA-256 `c006b6938cc601adb5e9e3f024691138dc465c666109e2737ea7d9287ff7c1b1`. It is byte-identical to `engine(20260812-021053).log`, so it is one device run, not two.
- Device outcome: the real Diffusion menu remains physically visible after selecting chapter 1 / Normal. The raw log reaches `Game started`; records `ui=0`, `ui_renderworld=1`, `state=4`, and `signon=2`; and completes twelve custom-render, post-render/HUD/VGUI/menu/touch, GL2/2-D flush, `GL_SwapBuffers`, and host-frame returns. Run 42 proves CPU-side call returns, not that the CAEAGLLayer received new pixels.
- Verified failure boundary: after normal map activation and twelve returned render/present paths but before proof that the SDL CAEAGLLayer-backed color renderbuffer was actually presented. No Run-42 marker records native context identity, thread, framebuffer/renderbuffer IDs, drawable geometry, resolve source, `presentRenderbuffer` result, or drawable pixels.
- Phase-A display chain: Valve and Diffusion share one SDL UIKit window, `SDL_uikitopenglview`, `CAEAGLLayer`, and `SDLEAGLContext`. SDL owns `viewRenderbuffer`/`viewFramebuffer` plus an optional MSAA framebuffer and resolves into the view framebuffer before calling `[EAGLContext presentRenderbuffer:GL_RENDERBUFFER]`. The common 2-D/HUD/VGUI/menu/touch path changes viewport/draw state but does not restore framebuffer or renderbuffer ownership. A logically inactive menu therefore leaves no native view to hide; the one layer can continue showing its last successfully presented menu storage.
- Structural differential: regular Valve rendering does not allocate Diffusion's custom depth renderbuffers. Diffusion's `R_AllocFrameBuffer` binds a generated depth renderbuffer and then calls `glBindRenderbuffer(..., 0)`. At pinned GL4ES commit `81547d986798e876de8b434193920b606a72363f`, logical default renderbuffer zero has native name zero, and `gl4es_glBindRenderbuffer` rejects that restore with `GL_INVALID_OPERATION` while leaving the prior nonzero native renderbuffer bound. Pinned SDL commit `5d249570393f7a37e037abf22cd6012a4cc56a71` explicitly assumes external code has rebound its `viewRenderbuffer`, presents whatever native renderbuffer is current, and discards the returned iOS `BOOL`. This is the leading source-supported mismatch, but Run 42 does not prove that the first map frames executed the allocation.
- Ranked hypotheses: (1) a Diffusion custom depth renderbuffer remains bound and EAGL presentation fails; falsified by `observed_rb == expected_rb` plus `result=1` on all three frames and no matching GL4ES error. (2) a custom/read framebuffer or GL4ES main-FBO translation feeds the wrong resolve target; falsified by matching expected draw/read IDs and a pre-sentinel drawable checksum that changes from the pre-world menu baseline. (3) targets and pixels are correct but UIKit/Core Animation ownership or scheduling does not display the layer; falsified by a visibly updated sentinel.
- ScreenFade audit: `CL_DrawScreenFade` is synchronous on the host render path inside `CL_DrawHUD`, after custom rendering and before VGUI/menu/touch/presentation. Its ordinary `V_FadeAlpha` bookkeeping can update `fadeEnd` for `FFADE_STAYOUT`; the retained iOS Diffusion branch returns before drawing and cannot switch UIKit views, GL contexts, framebuffers, renderbuffers, or host scheduling. The final Run-42 ScreenFade line can be emitted by the first unnumbered frame after the twelve-frame trace budget and is not a proven freeze boundary.
- Phase-B candidate: diagnostics only, bounded to the first three gameplay frames. Engine and patched SDL record paired native and GL4ES-side context/thread, window/view/layer, drawable size/scale, FBO/RB, viewport/scissor, and GL-error state at engine entry, before/after renderer dispatch, after 2-D/HUD/menu/touch, immediately before/after EAGL presentation, and the next host entry. SDL logs the actual `presentRenderbuffer` `BOOL` without rebinding the suspected renderbuffer.
- Content discriminator: at frame 1 before world drawing, SDL samples five 4x4 RGBA regions of the actual `viewFramebuffer` as the stale-menu baseline. After SDL's unchanged MSAA resolve on frames 1–3, it samples the same final presentable target, draws a bounded 180x72 black-backed sentinel (one magenta bar, two cyan bars, three yellow bars), verifies it by a second checksum, and restores framebuffer, scissor, color-mask, and clear-color state before the unchanged presentation attempt. No map, renderer, shader, menu, touch, fade, audio, foliage, gameplay, or timing policy is changed.
- One-run decision table: renderbuffer mismatch or `result=0`, with sentinel readback present but no visible sentinel, selects hypothesis 1. Correct renderbuffer but wrong draw/read FBO or a drawable checksum equal to the menu baseline selects hypothesis 2. Correct identities/bindings, changing checksum, verified sentinel, and `result=1` with no visible sentinel selects hypothesis 3. A visible sentinel plus changing checksum proves the native presentation path is live and rejects the stale-menu presentation hypothesis.
- Guardrails and local validation: SDL is now hard-pinned to `5d249570393f7a37e037abf22cd6012a4cc56a71`; `sdl2-display-audit-ios.patch` applies cleanly to that exact tree; `validate-ios-display-audit.py` proves the three-frame bound, state restoration, baseline/readback/sentinel ordering, unchanged renderbuffer binding, paired boundaries, and EAGL result capture. The existing exact Diffusion policy validator still passes the pinned applied tree, and `git diff --check` passes. Arm64/Xcode validation and IPA qualification remain pending GitHub Actions.
- Expected markers: `iOS display audit policy:`; `iOS display audit native:`; `iOS display audit GL4ES:`; `iOS display audit drawable:`; `iOS display audit present:`; and paired `iOS display audit ScreenFade:` entry/return lines.
- Single device test, only after CI produces the diagnostics IPA: start iOS screen recording while the real Diffusion menu is visible; tap **New Game → chapter 1 → Normal** exactly once; do not tap again or background the app; record for 15 seconds; then stop recording, capture one final screenshot, and provide the complete new `engine.log` plus the recording. The first three diagnostic presentations encode frame 1 as one magenta bar, frame 2 as two cyan bars, and frame 3 as three yellow bars near the upper-left. This is one test run. Do not retest Run 39 or Run 41.
- Acceptance/stop state: awaiting one diagnostics-only candidate build and the single orchestrator-reviewed device test above. Do not call this a fix and do not begin another work order.

### Work order 42 build qualification

- Candidate commit: `8533f9829acd3bfc36401467ccb1cd49fa15b4f6` (primary discriminator implementation `31cf9ed5b18e093e0cab8708e8968740142f823a`; CI portability corrections `2acc09315e948b4283af3539e0c3655dd3d9f28d` and `8533f9829acd3bfc36401467ccb1cd49fa15b4f6`).
- CI: direct-push [iOS Proof of Life run 50](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31561548790), ID `31561548790`, result `success`; the identical PR event [run 51](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31561551207), ID `31561551207`, also succeeded. Both passed dependency installation, engine/Half-Life/pinned Diffusion client-server-menu builds, the IPA contract, and artifact upload.
- CI corrections were build-only: run `31558823328` exposed an unavailable generated-header `GL_VIEWPORT` token in the audit and was corrected with the equivalent audit-local `0x0BA2` query token. Run `31561205940` then compiled every target but exposed a `set -o pipefail` false negative when `grep -q` closed the long `nm` stream after finding the SDL export; the verifier now materializes the export list before checking it. Neither failure changes the device hypothesis or diagnostic behavior.
- Artifact: `Xash3DiOS-arm64-unsigned`, ID `9127997685`, 8,572,167-byte GitHub artifact ZIP, SHA-256 `DBAE296EBD825553B87DF979AB5C69537D650EDA35F9F5DD2724B8A270807FD6`. Stable artifact page: https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31561551207/artifacts/9127997685
- IPA: `xash3d-fwgs-ios-arm64.ipa`, 8,668,697 bytes, SHA-256 `AA7E3149C89855419300E689216754997E3F23EEC0A596F60DCEE388CB725CCF`.
- Tempfile delivery: https://tempfile.org/oV68KVfN2Xn/ (direct: https://tempfile.org/oV68KVfN2Xn/download), expires 2026-08-14 04:02:57 UTC. Tempfile's server-side metadata and security endpoint report the same filename, size, and SHA-256 with risk level `safe` and no warning.
- Build validation: the patched SDL framework compiled at the exact pinned revision; the engine and all relevant arm64 `XASH_IOS=1` Diffusion targets linked; translated mobile shader validation passed; the final IPA contract found the engine/renderer/SDL diagnostics, the exported SDL snapshot function, required game assets, and arm64 Mach-O payloads.
- Acceptance state: build-qualified diagnostics-only candidate, not device-accepted and not described as a fix. Phase A has produced the required one-run discriminator, so exactly the previously specified 15-second screen-recording/log test is now requested. Stop after that test request for orchestrator review; do not begin a follow-up work order.

## Work order 43 Phase A — Run 51 structural audit

- Proof-gate outcome: **Outcome B**. Run 51 proves that the final iOS drawable can be modified and presented, but the available evidence does not attribute the per-frame `GL_INVALID_OPERATION` to one source call or distinguish invalid normal-scene submission from incomplete synchronous first-map initialization. No behavior edit, CI run, IPA, or device test is authorized from this report.
- Audited implementation: Run-51 candidate `8533f9829acd3bfc36401467ccb1cd49fa15b4f6` (workflow `31561551207`, artifact `9127997685`) against the last behavior-equivalent build `64c71deb`. Pinned inputs are Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, GL4ES `81547d986798e876de8b434193920b606a72363f`, and SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`.
- Evidence integrity: `Xash3DiOS-Run51-device-recording.mp4`, 11,650,176 bytes, SHA-256 `809df9265193c8816b08d25b6f555741547440c20616dce1a84469056cc8f2e9`; `Xash3DiOS-Run51-final-screenshot.png`, 835,225 bytes, SHA-256 `817fcc1aeb0a2f66e1fc92115bf9d56e536dfc41655f0ff2bb90a6e7d54f9fed`; and `Xash3DiOS-Run51-engine-20260812-052139.log`, 139,918 bytes / 2,331 nonempty source lines, SHA-256 `95edda2daac718a8945e26ab6ee40f1312d5d738a6d64f373c64bb458faf572c`. The recording and screenshot show the final three-bar yellow sentinel over the stale Diffusion difficulty screen.
- Exact timeline: Normal invokes `CMenuNewGame::StartGameCb(1)` and logs chapter 1 / skill 1. The queued `newgame` selects `GI->startmap`; `maps/ch1map0_load.cfg` executes; `Game started` is logged; and at `t=35.968` the engine reports `maps/ch1map0.bsp`, `state=4`, `signon=2`, `ui=0`, and `ui_renderworld=1`. Gameplay frames 1–12 all return through the custom renderer, HUD/VGUI/menu/touch, `GL2_ShimEndFrame`, SDL swap/present, and the host loop by `t=36.191`. Foliage then begins at `t=51.317`; surfaces 638 through 648 complete by `t=51.914`; a later batch begins at surface 919 at `t=59.350`; surfaces 915–924 and 948–951 continue through `t=60.967`; and the complete log ends after on-demand `CompileUberShader #48: BmodelSolid`.
- Diagnostic differential: `64c71deb..8533f982` changes 11 files by 705 insertions, all in bounded engine/renderer/SDL display diagnostics, validators, IPA verification, and documentation. It adds no Diffusion render-policy, map, menu, shader-key, or foliage behavior change. The visible result therefore predates Run 51; its readback/sentinel affects only the first three final swaps.
- Call graph: `CMenuNewGame::StartGameCb` → MainUI `pfnClientCmd` → `Cbuf_AddText`/`Cbuf_Execute` → `SV_NewGame_f` → `COM_NewGame` → `COM_Frame` state transition → `SV_ExecLoadLevel` → `SV_SpawnServer`/`SV_SpawnEntities`/`SV_ActivateServer`. Active rendering is `Host_Frame` → `Host_ClientFrame` → `SCR_UpdateScreen` → `V_RenderView` → engine `GL_RenderFrame` → renderer `R_RenderFrame` → Diffusion `HUD_RenderFrame` → `R_RenderScene` → `R_DrawWorld` → visible-surface collection → `R_DrawBrushList`; grass dispatch is `R_AddGrassToChain` → `R_ConstructGrass`; shader requests are `GL_UberShaderFor*` → `GL_FindUberShader` → `GL_CreateUberShader` → GL4ES translation/compile/link. Return/presentation is `V_PostRender` → `R_EndFrame` → `GL2_ShimEndFrame`/`R_Set2DMode(false)` → engine `GL_SwapBuffers` → `SDL_GL_SwapWindow` → `UIKit_GL_SwapWindow` → `SDL_uikitopenglview::swapBuffers` → `[EAGLContext presentRenderbuffer:]`.
- Proven GL boundary: the error queue is empty immediately before Diffusion `HUD_RenderFrame` and contains `0x0502` immediately after it on all 12 audited frames; every later engine, 2-D, flush, swap, and present checkpoint is clean because that fence drains the error. The smallest proven owner is therefore the complete Diffusion custom-renderer callback, not a particular GL call. `R_AllocFrameBuffer` does contain the source-supported candidate `pglBindRenderbuffer(GL_RENDERBUFFER_EXT, 0)`; pinned GL4ES rejects zero when a nonzero renderbuffer is current and leaves that current binding unchanged. But the evidence does not prove that allocation executes on each audited frame, and it cannot explain the visible sentinel as a dead final drawable. Promoting it to the root cause would violate the proof gate.
- Missing native records: the patched SDL snapshot sets `xashAuditFrame` at `immediately-before-presentation`; only that state can make `swapBuffers` draw the sentinel, so the visible sentinel proves execution reached the snapshot and later presentation code. The same snapshot and swap code emit the promised native, drawable, checksum, and present records with `SDL_Log`. `SDLash_Init` installs the engine callback and the same log contains an earlier callback-formatted SDL error; source contains no later output-function reset. Their total absence is therefore classified as an **instrumentation implementation/transport defect**, not evidence of conditional compilation or a failed drawable. Its exact runtime cause is not established by Run 51.
- Drawable classification: a non-presented final target is ruled out by the verified yellow sentinel. The GL4ES-side `fb=0 rb=1` values are logical wrapper state and cannot identify SDL's native `viewFramebuffer`/`viewRenderbuffer` without the missing records. Because Diffusion normally clears depth but does not unconditionally clear color, failed/skipped normal draw submission can legitimately leave menu pixels underneath the sentinel. The present evidence still cannot distinguish that branch from synchronous initialization that has not yet produced a completed normal scene.
- Finite-work audit: the log contains 41 uber-shader creations, indices 8–48: `GenericDlight` 2, `BmodelSolid` 4, `BmodelDlight` 2, `StudioSolid` 15, and `StudioDlight` 18. Animated studio keys use the shared `STUDIO_BONEWEIGHTING` layout and only rigid models retain `MAXSTUDIOBONES 1`; no arbitrary per-model bone count reappears. `GL_FindUberShader` hashes the shader name plus canonical options and reuses an existing entry; the table is finite at 2,048 slots, so after #48 at most 1,999 new unique slots remain, although the actual remaining map set cannot be derived from the truncated log. Foliage logs 23 completed surfaces and 278 bushes; 22 bounded dispatch records account for 264, followed by surface 951's 14. Every observed `R_ConstructGrass` returns in 0–1 ms, and `es->grass` prevents regeneration for that surface. With 2,732 map surfaces, at most 2,709 unobserved surfaces could still become one-time foliage owners. The 7.436-second gap from surface 648 completion to surface 919 dispatch is outside the instrumented constructor. This proves monotonic finite progress and rejects a stable foliage deadlock, but it does not quantify the full completion time.
- Minimum one-run discriminator if the orchestrator later authorizes Phase B: one bounded diagnostics-only build must (1) return a POD native snapshot/result from patched SDL to the engine and log it with `Con_Printf`, avoiding `SDL_Log`; (2) record the first `glGetError` transition at ordered Diffusion phase boundaries, narrowing recursively within the first failing phase to the exact source-owned GL operation; and (3) time/count the complete first-map shader and foliage pipeline through its first fully presented normal scene. The discriminator must preserve renderer behavior and stop logging after the first attribution plus pipeline completion.
- Local/source validation: `validate-ios-display-audit.py . build/run42-sdl-patch-test3`, `validate-diffusion-ios-policy.py build/run40-audit/Diffusion`, and `git diff --check` pass. The local pinned revisions match the commits above. No compile or CI run is warranted for a documentation-only Phase A report.
- Files changed by Phase A: `Documentation/XASH3DIOS_PORTING_STATE.md` only. The Google Docs authoritative ledger receives the same report after repository publication. No engine, Diffusion, GL4ES, SDL, asset, build, or workflow file changes.
- Workflow/artifact/IPA: none created for Work Order 43 Phase A. Run-51 identifiers above are evidence only. No IPA link or SHA-256 is applicable, and no tempfile.org upload is permitted without an authorized candidate.
- Expected new log markers: none; Phase A changes no binary. Single device test requested: none. Do not retest Run 39, Run 41, or Run 51.
- Remaining risks: the first-error call, native drawable identities/checksum before the sentinel, and total first-map completion time remain unknown; the broad `HUD_RenderFrame` fence and failed SDL-log transport are insufficient to choose a structural repair.
- Stop gate: stop at Outcome B for orchestrator review. Do not implement Phase B, publish an IPA, or ask Arjun for evidence or a device test unless the authoritative ledger later authorizes it.

## Work order 43 Phase B — diagnostics-only build report

Candidate/run: Work Order 43 Phase B diagnostics-only candidate after Run 51; build-qualified, not device-tested or accepted.

Commit: `b56699df808b25c3ea57aab8f670c676b97f00f2` (`Instrument WO43 Phase B presentation boundary`).

Workflow URL/ID and result: direct-push [iOS Proof of Life run 31572853730](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31572853730), result `success`; job `Unsigned arm64 IPA` ID `94038377537`, all steps successful. GitHub also started PR-event run `31572857250` for the identical commit because this branch has an open PR; it produced no distinct code candidate. The direct-push run is the qualifying workflow recorded here.

IPA filename/link: `xash3d-fwgs-ios-arm64.ipa`, 8,672,544 bytes. Artifact `Xash3DiOS-arm64-unsigned`, ID `9132108713`; stable page: https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31572853730/artifacts/9132108713. No tempfile.org upload was made because the Phase B authorization explicitly prohibits it.

SHA-256: `63328B4FA5839CEE888298F9AA955A8AD92CD4D542BFCD291BFEE9B7AFAA17E1` for the retrieved IPA.

Exact files changed: `engine/client/dll_int/cl_gameui.c`; `engine/common/common.h`; `engine/common/host.c`; `engine/platform/sdl2/vid_sdl2.c`; `scripts/gha/deps_ios.sh`; `scripts/ios/builddiffusion.sh`; `scripts/ios/diffusion-wo43-diagnostics-ios.patch`; `scripts/ios/sdl2-wo43-diagnostics-ios.patch`; `scripts/ios/validate-diffusion-ios-policy.py`; `scripts/ios/validate-ios-display-audit.py`; `scripts/ios/verify_ipa.sh`.

Verified failure boundary: unchanged from Phase A. On Run 51 the GL queue was clean before the custom renderer and contained `GL_INVALID_OPERATION` after `HUD_RenderFrame` on every audited gameplay frame, while the yellow final-drawable sentinel was visibly presented and CPU progress continued through foliage and shader #48. No exact source operation or completed normal-scene presentation was proven by Run 51.

Structural cause: still unproven; this candidate deliberately contains no renderer repair. It adds bounded attribution for the first clean-to-error transition, native presentation state returned from SDL to engine logging, and cumulative initialization/submission timing so a future single observation can distinguish an exact bad GL call from finite excessive initialization, monotonic noncompletion, or a stable last-progress call.

Why the diagnostic change addresses the evidence gap: patched SDL returns a fixed-size POD record to `vid_sdl2.c`, where `Con_Printf` records EAGL context, view/layer identities, native framebuffer/renderbuffer bindings, drawable size, final pre-present checksum, and the actual `presentRenderbuffer` result or explicit unavailability. The Run-51 colored sentinel is disabled. Diffusion empties the bounded audit queue at frame start, places hierarchical fences through `HUD_RenderFrame`/`R_RenderScene`/`R_DrawWorld`/`R_DrawBrushList`, and checks source-owned framebuffer, shader, uniform, and draw calls immediately after execution; the first failure reports a stable site, API, arguments, file/line, FB/RB/program state and stops per-call tracing. Shader lookup/translation/compile/link, foliage ownership/duplicate avoidance, world/brush/studio submissions, over-250 ms gaps, and compact heartbeats provide the finite-work timeline. Engine normal-scene proof requires active game state, world and brush submissions, successful presentation, and a final-drawable checksum change from the stale-menu baseline; checksum alone cannot pass it.

Local/build validation: both new patches apply with `--unidiff-zero` to the already accepted exact pinned SDL `5d249570393f7a37e037abf22cd6012a4cc56a71` and Diffusion `14d156bf3a6993c172697fac83a937836c3b5561` trees after their retained patches. `validate-ios-display-audit.py` reports the twelve-frame engine-routed POD/no-sentinel contract; `validate-diffusion-ios-policy.py` reports the retained shared animated-model key plus bounded WO43 diagnostics; both Python validators compile, and repository `git diff --check` passed before commit. CI built the engine, Half-Life, and pinned arm64 `XASH_IOS=1` Diffusion client/server/menu targets; validated mobile shaders; and passed the IPA contract. The IPA reports bundle version 52, minimum iOS 12.0, 13 arm64 Mach-O files, and 11 game dylibs.

Expected new log markers: `WO43 Phase B diagnostics:`; `WO43 init timing:`; `WO43 GL interval begin:`; `WO43 GL phase transition:`; `WO43 GL exact first failure:`; `WO43 init gap:`; `WO43 init heartbeat:`; `WO43 native presentation:`; and `WO43 normal-scene proof:`. The retained `iOS display audit policy:` marker now states `gameplay_frames=12` and `sentinel=disabled`.

Proposed single observation for orchestrator review only: if separately authorized, one unchanged launch and one Normal difficulty selection would be sufficient; the complete resulting engine log should select the Work Order 43 decision table from the exact-failure marker, the native presentation/result/checksum record, and the cumulative heartbeat. This report does not request that observation and does not contact Arjun for logs or testing.

Future one-run discriminator decision table: **A** is selected if `WO43 GL exact first failure:` identifies the first `0x0502` source operation before any `WO43 normal-scene proof:`. **B** is selected if audited GL submission is clean, cumulative initialization reaches completion, and `WO43 normal-scene proof:` appears only after a finite but excessive elapsed interval. **C** is selected if shader/foliage/submission milestones continue increasing through the observation window without normal-scene proof. **D** is selected if the same last phase/site and unchanged cumulative counters repeat without normal-scene proof. None of these branches is called a renderer fix without device evidence.

Remaining risks: instrumentation checks only the bounded source-owned call sites and phase fences represented in this candidate, so an error in an unwrapped helper may resolve first to a phase rather than an exact operation. Diagnostic `glGetError` calls serialize enough state to perturb timing, and the 12-frame/32-error bounds may truncate a later transition. The checksum is a five-region sample rather than a full-frame hash. A successful CI build is not device acceptance.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`; candidate commit `b56699df808b25c3ea57aab8f670c676b97f00f2`. This post-build report is published separately as a documentation-only `[skip ci]` ledger commit so it cannot create another qualifying IPA build.

Stop state: Phase B candidate publication and both-ledger reporting are complete. Stop for orchestrator review; do not request evidence, initiate a device test, diagnose a future log, implement a repair, or begin another work order.

## Work order 43 Phase B correction — independent initialization window

Candidate/run and acceptance status: corrected Work Order 43 Phase B diagnostics-only candidate, bundle version 54. Build-qualified by CI; not device-tested, accepted, or authorized for installation by this report. The rejected bundle-version-52 candidate remains rejected.

Commit: `6a3b44d2e66f4bfb73b8f85f906aebb40a94c9c5` (`Correct WO43 Phase B initialization window`).

Workflow URL/ID and result: qualifying direct-push [iOS Proof of Life run 31592838179](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31592838179), result `success`; unsigned arm64 IPA job `94101462106`, every step successful. The open PR automatically started duplicate run `31592842093`; cancellation raced with its successful completion. Its artifact `9139947607` was deleted, so it is not retained or treated as a distinct candidate. The direct-push run is the sole qualifying workflow and retained artifact.

Artifact/IPA: `xash3d-fwgs-ios-arm64.ipa`, 8,676,760 bytes, SHA-256 `A33F10A5E51D70F9B58CFD9113B11394D3EEEC6A24AA714F0943878C873E9A7A`. Retained artifact `Xash3DiOS-arm64-unsigned`, ID `9140019628`; stable page: https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31592838179/artifacts/9140019628. No tempfile.org upload was made, as forbidden by the correction order.

Exact candidate files changed: `engine/common/common.h`; `engine/common/host.c`; `engine/platform/sdl2/vid_sdl2.c`; `scripts/gha/deps_ios.sh`; `scripts/ios/builddiffusion.sh`; `scripts/ios/diffusion-wo43-phase-b-correction-ios.patch`; `scripts/ios/sdl2-wo43-phase-b-correction-ios.patch`; `scripts/ios/validate-diffusion-ios-policy.py`; `scripts/ios/validate-ios-display-audit.py`; `scripts/ios/verify_ipa.sh`.

Verified failure boundary: the underlying Run-51 boundary is unchanged: the GL queue is clean before Diffusion's custom renderer and contains `GL_INVALID_OPERATION` after `HUD_RenderFrame`, while native presentation succeeds and CPU work continues. The correction-order defect is proven in the rejected candidate source: `WO43_BeginFrame` tied detailed accounting to frames 1–12; `WO43_PhaseDuration` required that flag; `WO43_EndFrame` returned after frame 12; engine and SDL native sampling rejected later frames; and host liveness exhausted after twelve returned frames. Run 51 had already shown those frames return before the useful foliage/shader interval, so branches B/C/D could not be observed.

Structural cause: the rejected candidate conflated two lifetimes: a bounded GL error-consumption window and the complete first-map initialization discriminator. The gameplay renderer cause remains explicitly unresolved; this correction makes no renderer or gameplay repair.

Why the change satisfies the work order: the difficulty/map command now starts one generation-scoped initialization window and resets transport/cumulative counters once. Diffusion synchronizes to that generation without per-frame cumulative resets. The GL error-attribution window remains limited to the first twelve gameplay frames and stops after attribution. Engine accounting remains active independently until normal-scene proof or 120 seconds, emits a cumulative heartbeat no more than once per two seconds, and emits exactly one terminal `result=normal-scene` or `result=timeout` summary. Begin/end records bracket shader translation, compile, link, foliage construction, cubemap rebuild, and `R_RenderScene`, leaving a durable last phase/site if synchronous work is force-closed. Native presentation/checksum sampling occurs at first world-plus-brush submission and at a throttled two-second cadence until proof/timeout. Normal-scene proof still requires engine-active/sign-on state, normal world and brush submissions, successful presentation, and checksum change from the stale-menu baseline. Sentinel-disabled and normal behavior policy are preserved.

Exact-attribution invariant: 20 selected source-owned GL calls are covered by a validator-enforced pre-call clean check plus immediate post-call check. Only a clean-to-error transition may emit `WO43 GL exact first failure:`. An error already present before a wrapped call or first seen at a phase fence emits `WO43 GL attribution gap:` with `exact_first=0`, stops attribution, and preserves the smallest proven phase rather than inventing an exact cause.

Validation performed: both correction patches apply with `--unidiff-zero` to the already accepted, fully patched pinned Diffusion `14d156bf3a6993c172697fac83a937836c3b5561` and SDL `5d249570393f7a37e037abf22cd6012a4cc56a71` trees. The updated Diffusion validator passes the corrected tree with independent accounting, 20 pre-clean sites, and phase fallback, and rejects the rejected frame-12 tree. The display validator passes the corrected SDL/engine contract and rejects the frame-12 SDL tree. Both validators compile under Python and repository `git diff --check` passed before commit. CI built SDL, engine, Half-Life, and pinned Diffusion client/server/menu targets; ran both policy validators; validated mobile shaders; and passed the IPA contract. The IPA reports bundle version 54, minimum iOS 12.0, 13 arm64 Mach-O files, and 11 game dylibs. Waf's configure-probe summaries contain expected `test failed` probe counts, but every workflow step and target succeeded.

Expected log markers: `iOS display audit policy: gl_attribution_frames=12 init_timeout_seconds=120 native_sample_seconds=2`; `WO43 Phase B diagnostics:`; `WO43 init timing:`; `WO43 GL interval begin:`; `WO43 GL exact first failure:`; `WO43 GL attribution gap:`; `WO43 init phase: state=begin`; `WO43 init phase: state=end`; `WO43 init gap:`; `WO43 init heartbeat:`; `WO43 native presentation:`; `WO43 normal-scene proof:`; and `WO43 init terminal:`.

Remaining risks: no device evidence exists for this correction. The exact tracer intentionally covers selected pre-clean sites rather than every GL call; unwrapped operations fall back to a phase boundary. `glGetError` and checksum sampling can perturb timing, although error consumption remains bounded and native sampling is throttled. A single synchronous phase longer than the heartbeat interval cannot emit an in-phase heartbeat, but its flushed begin record and terminal/end accounting preserve the last-progress boundary. A successful CI build is not device acceptance.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`; candidate commit `6a3b44d2e66f4bfb73b8f85f906aebb40a94c9c5`. This post-build report is published in a separate documentation-only `[skip ci]` commit so it cannot create another qualifying IPA build.

Stop state: the one authorized Phase-B correction candidate, retained artifact, CI inspection, and worker reporting are complete. Stop for orchestrator review. Do not request a device test, contact Arjun for logs, upload to tempfile.org, install/recommend the IPA, diagnose future evidence, implement a renderer/gameplay repair, or begin another work order.

## Work order 44 Phase A — render-to-drawable and first-transition subsystem audit

Candidate/run and acceptance status: audit-only analysis of the bundle-version-54 diagnostics candidate. No candidate, workflow, artifact, IPA, tempfile.org upload, or device-test request is authorized or produced. Bundle version 54 remains build-qualified evidence, not an accepted gameplay candidate.

Exact commits and evidence inspected:

- Repository candidate: `6a3b44d2e66f4bfb73b8f85f906aebb40a94c9c5`; repository-ledger commit: `7d27600fb11e97294d643fd7b0ae7484d1891f3e`.
- Pinned external inputs: Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`; SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`; GL4ES `81547d986798e876de8b434193920b606a72363f`; Diffusion-MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`.
- Complete authoritative log: Drive file `WO43-B54-device-engine-20260813-111631.log` (`1UW0REa00fVegpsb1s0oi2jExMzL5FQXt`), 5,417,703 bytes and 35,481 text lines. It identifies `6a3b44d-dirty`, records 12 completed audited gameplay frames, 7,908 gameplay frames before the 120-second terminal summary, and 12,788 renderer/swap/present returns by the final heartbeat.
- Recording: Drive file `WO43-B54-device-Xashrec2.mp4` (`1r811f00TWrAC4lvFp0zI2JRetdayrRuW`), 8,660,711 bytes and 141.8 seconds. The connector verified the exact MP4 identity and the authoritative orchestrator review records an unchanged difficulty image while gameplay/cutscene audio proceeds; the recording ends before the later transition termination. This worker runtime exposed the MP4 as a streamed file reference but no binary playback surface, so frame-by-frame independent replay remains an evidence limitation. The log and source traces below independently establish the render-target result.

### Render-target ownership and presentation trace

Exact files/functions inspected: `wscript` and `3rdparty/gl4es/wscript`; `ref/gl/gl_opengl.c::GL_OnContextCreated`; pinned GL4ES `src/gl/framebuffers.c::{gl4es_glBindFramebuffer,createMainFBO,unbindMainFBO,blitMainFBO,bindMainFBO}`, `src/gl/gl4es.c::{gl4es_pre_swap,gl4es_post_swap}`, `src/glx/glx.c::gl4es_glXSwapBuffers`, and `src/gl/uniform.c::GoUniformfv`; `ref/gl/gl_rmain.c::R_EndFrame`; `engine/platform/sdl2/vid_sdl2.c::GL_SwapBuffers`; pinned SDL `src/video/uikit/SDL_uikitopengles.m::UIKit_GL_SwapWindow` and `src/video/uikit/SDL_uikitopenglview.m::{initWithFrame,swapBuffers}`.

Ownership diagram and observed namespace mapping:

```text
Diffusion + Xash OpenGL calls
        |
        | logical glBindFramebuffer(..., 0)
        v
GL4ES virtual default framebuffer 0
        |
        | gl4es_glBindFramebuffer maps logical 0 to mainfbo_fbo
        v
native GLES FBO 2: GL4ES texture-backed main FBO (normal scene/UI draw target)
        |
        | REQUIRED transfer is absent on the embedded iOS swap path
        v
native GLES FBO 1 + renderbuffer 1: SDL UIKit CAEAGLLayer drawable
        |
        | [EAGLContext presentRenderbuffer:GL_RENDERBUFFER]
        v
physical display

native FBO 0: GLES platform default name; not SDL's generated view FBO 1
native read binding 0 in the audit: native bookkeeping, not proof of drawable ownership
```

The complete return path is Diffusion `HUD_RenderFrame` -> Xash `V_PostRender` -> renderer `R_EndFrame` -> `GL2_ShimEndFrame`/`R_Set2DMode(false)` -> engine `GL_SwapBuffers` -> `SDL_GL_SwapWindow` -> `UIKit_GL_SwapWindow` -> `SDL_uikitopenglview::swapBuffers` -> `presentRenderbuffer`. The first native record has `view_fb=1`, `view_rb=1`, `current_fb=2`, `draw_fb=2`, `read_fb=0`, and `current_rb=1`. Before and after each audited custom-renderer call the native draw target remains FBO 2. Immediately before presentation, the five-region checksum of SDL's FBO 1 equals the stale-menu baseline; `present_result=1` and `changed=0`. Thus the API successfully presents renderbuffer 1, but its pixels were never replaced by the normal scene held in FBO 2.

The missing owner is the GL4ES-to-SDL embedding boundary. With `NOX11`, `NOEGL`, and `LIBGL_FB=2`, GL4ES creates the texture-backed main FBO and exports `gl4es_pre_swap`/`gl4es_post_swap`; Xash's SDL path calls neither. GL4ES's GLX swap wrapper would call them, but the iOS `NOEGL` embedding bypasses that wrapper. Moreover, stock `gl4es_pre_swap` first raw-binds native FBO 0 and blits the main texture there. SDL's drawable is the separately generated FBO 1, so merely adding a call to `gl4es_pre_swap` would still target the wrong native destination. SDL's `swapBuffers` resolves only its own optional `msaaFramebuffer` into `viewFramebuffer`; when that SDL-owned MSAA FBO is absent, it performs no bind, blit, or copy from GL4ES FBO 2 to view FBO 1. `present_result=1` proves presentation of the currently bound renderbuffer, not transfer of GL4ES scene pixels.

Structural conclusion: the stale difficulty image is caused by a missing explicit FBO-2-to-FBO-1 transfer before presentation, not by a dead drawable, active menu overlay, or stopped renderer. The transfer must be owned by a target-specific GL4ES/iOS presentation bridge because GL4ES owns the source texture/logical namespace while SDL UIKit owns the actual nonzero drawable FBO and renderbuffer.

Minimum future repair boundary, not implemented in Phase A: after all renderer and 2-D/UI flushing but before `presentRenderbuffer`, pass SDL's live `viewFramebuffer` and drawable geometry into a GL4ES-side pre-present callback. The callback must flush pending GL4ES work, bind native FBO 1 as the explicit destination, blit the GL4ES main-FBO texture, preserve/restore viewport, scissor, color-mask and related blit state, leave view renderbuffer 1 presentable, and report success. After presentation, a matching callback must rebind GL4ES native main FBO 2 while keeping logical framebuffer 0 coherent. A future proof invariant is: immediately pre-present native draw FBO equals SDL view FBO 1, FBO-1 checksum differs from its menu baseline after the transfer, renderbuffer 1 is bound, presentation returns true, and immediately post-present native FBO 2 is restored while the GL4ES logical current framebuffer remains 0. This is an interface repair, not a hard-coded `glBindFramebuffer` guess.

### Exact `glUniform4fv` finding

Diffusion `client/render/r_world.cpp::R_DrawBrushList` creates `Vector4D brush_params[3]` and at line 2952 unconditionally calls `pglUniform4fvARB(location, 3, ...)`. `glsl/bmodelsolid_vp.glsl` and `glsl/bmodelsolid_fp.glsl` both declare `uniform vec4 u_BrushParams[3]`; `client/render/r_shader.cpp::GL_InitSolidBmodelUniforms` stores the base location. GL4ES's linked-program introspection in the log reports active `u_BrushParams[1]` or `[2]` for optimized BmodelSolid variants because unused tail elements were removed. Pinned GL4ES `src/gl/uniform.c::GoUniformfv` rejects an upload when `count > m->size` and raises `GL_INVALID_OPERATION` before copying the values. The first exact audit failure is therefore source-backed: frame 1, `r_world.cpp:2952`, program 52, location 15, `count=3`, error `0x0502`, with the queue clean before the call.

Classification: independently incorrect and capable of leaving fog/view-origin/water brush parameters stale for affected programs, but not causal for the stale physical framebuffer. It occurs on every audited frame yet rendering, foliage, shader creation, swaps, presentations, and host frames continue. It cannot explain why FBO 1's checksum never changes while normal work targets FBO 2. Phase A makes no uniform patch.

### UI/menu reconciliation

The audit's `ui` field is `engine/client/dll_int/cl_gameui.c::UI_IsVisible`, which directly calls MainUI's `pfnIsVisible`. During gameplay the log repeatedly records `ui=0`, `state=4`, and `signon=2`. `engine/client/parse/cl_parse.c::CL_ParseServerData` calls `UI_SetActiveMenu(cl.background)` after normal map setup, so the real menu is logically inactive and is not an overlay redrawn over gameplay. The difficulty pixels are retained physical content in SDL view FBO 1 from the last successful menu-era draw. This reconciles `ui=0` with the visible difficulty screen without disabling or bypassing MainUI.

### First `ch1map0` -> `ch1map1` transition trace

Exact files/functions inspected: Diffusion `server/entities/changelevel.cpp::CChangeLevel::ChangeLevelNow`; `engine/server/sv_game.c::SV_QueueChangeLevel`; `engine/common/host_state.c::{COM_ChangeLevel,COM_Frame}`; `engine/server/sv_init.c::{SV_ExecChangeLevel,SV_SpawnServer,SV_ActivateServer}`; `engine/server/sv_save.c::{SV_ChangeLevel,SaveGameState,LoadGameState,LoadAdjacentEnts}`; `engine/server/sv_game.c::SV_SpawnEntities`; `engine/common/model.c::{Mod_FreeUserData,Mod_UnloadRenderData}`; Diffusion `client/render/r_world.cpp::{R_ProcessWorldData,Mod_FreeWorld}`, `client/cdll_int.cpp::HUD_VidInit`, and `client/render/r_misc.cpp::R_VidInit`; `engine/client/parse/cl_parse.c::{CL_ParseServerData,svc_changing}`.

Source sequence:

```text
CChangeLevel::ChangeLevelNow
  -> engine pfnChangeLevel / SV_QueueChangeLevel
  -> COM_ChangeLevel stores levelName=ch1map1, landmark=to_map1,
     loadGame=true, next state=STATE_CHANGELEVEL
  -> next COM_Frame -> SV_ExecChangeLevel -> SV_ChangeLevel
     -> SaveGameState(true) for ch1map0
     -> SV_InactivateClients -> SV_FinalMessage -> SV_DeactivateServer
     -> SV_SpawnServer(ch1map1, to_map1)
        -> world/model/collision load and renderer Mod_ProcessRenderData(create=true)
     -> SaveFinish
     -> LoadGameState(ch1map1, true)
        -> LoadSaveData fails for save/ch1map1.HL1 and returns 0
     -> explicit fallback SV_SpawnEntities(ch1map1)
     -> LoadAdjacentEnts(ch1map0, to_map1)
     -> SV_ActivateServer(false) -> expected new "Game started"
```

The missing `save/ch1map1.HL1` is non-causal by source: `LoadGameState` returns false and `SV_ChangeLevel` immediately falls back to `SV_SpawnEntities`. The full log's last transition records are `Spawn Server: ch1map1 [to_map1]`, `total 242 packed normals`, `Loaded 8 cubemap boxes.`, the missing-save error, `execing maps/ch1map0_unload.cfg`, and `execing maps/ch1map1_load.cfg`, followed by EOF. The last source-backed safe boundary is therefore: new BSP/world renderer processing and cubemap loading returned, the missing-save read returned into its handled fallback path, and both queued config executions were reached. There is no marker proving return from fallback `SV_SpawnEntities`, `LoadAdjacentEnts`, `SV_ActivateServer`, or a new `Game started`. The termination boundary is after new-world load plus entry into the fallback/config interval and before proven activation of the new server; the exact crash operation is unresolved.

Resource ownership is structured rather than obviously leaked across the transition. Engine model release runs `Mod_FreeUserData` -> `Mod_UnloadRenderData` -> renderer `Mod_ProcessRenderData(create=false)`; Diffusion `R_ProcessWorldData` calls `Mod_FreeWorld`, which frees cubemap boxes, world framebuffer textures, leaf/vertex/vertex-lighting data, VBO/VAO resources, cinematics, landscapes, per-surface foliage, and animations. On the new server/client data, `CL_ParseServerData` calls the client `pfnVidInit`; Diffusion `HUD_VidInit` calls `R_VidInit`, which frees/recreates screen color/depth/native textures, subview textures, custom framebuffers, shadow/post resources and studio-renderer video objects, then advances the shader validity sequence. `svc_changing` sets `cls.changelevel`, stops active sounds, and clears client state. The GL4ES main FBO and SDL drawable are context-global presentation objects, not per-map Diffusion world objects; their missing bridge persists independently of per-map teardown. Current evidence does not prove a double-free, use-after-free, audio teardown defect, or GL object ownership violation at the crash boundary.

### Diagnostic perturbation assessment

The log contains 32,408 `WO43 init phase` records in 35,481 lines over about 178 seconds. Per-phase synchronous logging, repeated `glGetError` fences, checksums, and multi-line records can materially change I/O volume, storage latency, GPU/CPU synchronization, thermal behavior, memory pressure, and transition timing. It does not invalidate the stable FBO-ID/checksum mismatch or the exact clean-to-error uniform call, but it prevents treating the observed crash timing as representative without an iOS diagnostic report.

Any future diagnostic candidate should emit only: one generation-start record; one first-error record; one baseline and first world/brush pre/post-transfer sample; a cumulative heartbeat at no more than one record per two seconds; phase records only on phase change or duration over 250 ms; once-only transition records per subsystem/generation with object counts; a capped ring/output budget of at most 256 records per 120 seconds; flushes only at changelevel/terminal boundaries; and one terminal summary. Per-frame phase begin/end logging must be removed.

### Hypothesis decision table

| Hypothesis | Supporting evidence | Contradicting evidence / Phase-A classification | Next discriminator |
| --- | --- | --- | --- |
| Missing final FBO-to-drawable transfer | Normal draws remain in native FBO 2; SDL presents FBO/RB 1; FBO-1 checksum stays at the menu baseline; no Xash call reaches GL4ES pre/post swap. | None for the stale-frame symptom. Stock GL4ES pre-swap would target native FBO 0, so it is not already the required transfer. **Established structural cause of stale display.** | Target-aware bridge invariant: FBO 2 -> explicit FBO 1, changed FBO-1 checksum, RB 1 bound, successful present, FBO 2 rebound. |
| Wrong framebuffer/renderbuffer binding at swap | Native draw FBO is 2 while SDL expects view FBO 1. | Current renderbuffer equals expected RB 1 and presentation returns true; this is a missing color transfer, not a wrong-RB presentation failure. **Partially true only for draw-target ownership.** | Same pre/post bridge invariant with both native draw-FBO and RB checks. |
| Active menu overlay | Difficulty pixels remain visible. | `UI_IsVisible/pfnIsVisible` is false (`ui=0`) throughout active/sign-on gameplay; FBO-1 checksum is unchanged instead of receiving a newly composited overlay. **Rejected.** | No further discriminator needed unless future evidence shows `ui=1` or changing overlay pixels. |
| `glUniform4fv` state corruption | Exact first `0x0502` is `r_world.cpp:2952`; count 3 exceeds GL4ES active extent 1/2 and blocks the update. | Renderer and host continue for thousands of frames; error cannot copy FBO 2 into FBO 1 or explain a constant drawable checksum. **Independently incorrect, non-causal for stale presentation.** | Later bounded fix should upload only the active extent or preserve a three-element active declaration, then verify no error and correct brush parameters; do not use it as display repair. |
| Transition resource-lifetime/use-after-free | Termination occurs during the first map transition, which destroys and recreates world, foliage, cubemap, studio and custom-FBO resources. | Source shows explicit ownership/teardown paths; log proves new-world/cubemap work returns and contains no allocator, GL-object, or fatal marker. **Plausible but unproven for termination.** | iOS `.ips` crash report with crashed thread/backtrace and used images; if memory fault, instrument only the last proven transition interval with generation/object-owner IDs. |
| Memory pressure or watchdog termination | Diagnostics are extremely verbose and synchronizing; transition has simultaneous old-state save and new-map resource creation. | No JetsamEvent, memory footprint, watchdog reason, or timing classification is present; the recording ends before the termination. **Unresolved.** | Matching-timestamp iOS app `.ips` or `JetsamEvent` report containing exception/termination reason, memory footprint and process state. |
| Missing-save fallback failure | EOF follows `Couldn't open save data file save/ch1map1.HL1`. | `LoadGameState` returns 0 and `SV_ChangeLevel` explicitly calls `SV_SpawnEntities` as the normal fallback. **Rejected as cause absent contrary crash evidence.** | A crash backtrace inside fallback entity spawn/adjacent restore could reclassify the later operation, but the missing file itself remains handled. |

### Remaining evidence gaps and stop state

The stale-frame cause is established at the GL4ES/SDL presentation interface. The transition termination cause is not established: the log lacks proof after fallback entity-spawn entry and contains no OS-level termination record. The exact report needed is the iOS app crash `.ips` or `JetsamEvent` matching the incident timestamp, including exception/termination reason, crashed thread and backtrace, memory footprint, and used images. Its retrieval path is iPhone **Settings -> Privacy & Security -> Analytics & Improvements -> Analytics Data**, or Xcode **Devices and Simulators -> View Device Logs**. This specifies the evidence gap only; Phase A does not contact the user or request it.

Validation performed: exact repository/pinned revisions were verified; Codebase Memory was used only for discovery and all material claims were checked in the pinned/applied source trees; the complete authoritative log was scanned for ordered markers and counts; source-level render and transition call sequences were inspected end to end; and `git diff --check` is required before publication. No compile, build, GitHub Actions run, or binary validation is warranted or allowed for this documentation-only phase.

Exact files changed by Work Order 44 Phase A: `Documentation/XASH3DIOS_PORTING_STATE.md` only. Expected new log markers: none. Candidate/IPA/SHA-256/device test: not applicable and not authorized.

Durable ledger commit: populated by the documentation-only `[skip ci]` publication commit containing this report. Both the repository ledger and authoritative Google Doc must be read back after publication.

Stop state: Work Order 44 Phase A stops after the two subsystem traces and decision table for orchestrator review. Do not implement the bridge or uniform fix, create a candidate, run Actions, retrieve/upload an IPA, contact Arjun, request testing or evidence, or begin another work order.

## Work order 44 Phase B — target-aware GL4ES-to-SDL drawable bridge

Candidate/run and acceptance status: bundle version 60 is the single Work Order 44 Phase-B behavioral candidate. It is locally and CI build-qualified, but it is **not device-tested or accepted**. The accepted device baseline remains Run 39 until the orchestrator evaluates new device evidence.

Commits:

- Behavioral implementation: `cff801017b8682f1172fde5627ad7fd34b60152b`.
- Final build head: `dbb8a3d85296cbf5ecde7b840db14375bda0ac7a`. The two commits after the behavioral implementation only corrected artifact-verifier assumptions about hidden/static GL4ES helper symbols and LTO inlining; they did not alter runtime behavior.
- Exact pinned inputs retained: Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`; SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`; GL4ES `81547d986798e876de8b434193920b606a72363f`; Diffusion-MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`.

Workflow and artifact:

- Sole retained qualifying workflow: GitHub Actions run `31765624536`, run number 60, direct-push event, successful, head `dbb8a3d85296cbf5ecde7b840db14375bda0ac7a`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31765624536`.
- Retained artifact ID `9206294601`, `Xash3DiOS-arm64-unsigned`, archive size 8,562,952 bytes: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31765624536/artifacts/9206294601`.
- Actual IPA: `xash3d-fwgs-ios-arm64.ipa`, 8,660,812 bytes, SHA-256 `F19BBA87A9AFEF721948800F607FB00230B621746A3C2E6EDAA86E5DF77B6111`.
- tempfile.org page: `https://tempfile.org/6mHp8rG2s7H/`; direct download: `https://tempfile.org/6mHp8rG2s7H/download`; reported expiry `2026-08-16 03:51:44 UTC`. API readback confirmed the exact filename, size, hash, existence, and safe scan result.
- Automatic/superseded qualification attempts were removed or canceled rather than retained: initial push run `31762687538` canceled/deleted; PR run `31762690104` failed only because the verifier required a hidden GL4ES symbol and was deleted; push run `31764261049` failed only because LTO inlined the post helper and was deleted; PR duplicates `31764263431` and `31765627060` were canceled/deleted. These verifier-only follow-ups did not create additional behavioral candidates. Skipped nonqualifying workflow entries may remain in Actions history.

Exact files changed by the Phase-B behavioral implementation:

- `engine/client/cl_main.c`
- `engine/client/cl_scrn.c`
- `engine/client/cl_view.c`
- `engine/client/dll_int/cl_game.c`
- `engine/client/dll_int/cl_gameui.c`
- `engine/common/common.h`
- `engine/common/host.c`
- `engine/platform/platform.h`
- `engine/platform/sdl2/vid_sdl2.c`
- `engine/ref_api.h`
- `ref/gl/gl_context.c`
- `ref/gl/gl_rmain.c`
- `scripts/gha/build_ios.sh`
- `scripts/gha/deps_ios.sh`
- `scripts/ios/builddiffusion.sh`
- `scripts/ios/gl4es-drawable-bridge-ios.patch`
- `scripts/ios/sdl2-drawable-bridge-ios.patch`
- `scripts/ios/validate-diffusion-ios-policy.py`
- `scripts/ios/validate-ios-drawable-bridge.py`
- `scripts/ios/verify_ipa.sh`

The verifier-only follow-up commits changed only `scripts/ios/verify_ipa.sh`.

Verified failure boundary: Work Order 44 Phase A established that the normal scene was rendered into GL4ES's texture-backed native main FBO 2 while SDL UIKit presented its separate CAEAGLLayer drawable FBO/renderbuffer 1. The live drawable checksum retained the stale difficulty-menu image even though map loading, rendering, swaps, and successful `presentRenderbuffer` calls continued. The iOS `NOEGL` SDL route bypassed GL4ES's GLX pre/post-swap path, and stock `gl4es_pre_swap` targets native FBO 0 rather than SDL's live nonzero view FBO. Therefore the structural cause was a missing target-aware GL4ES-to-SDL drawable transfer at the embedded presentation boundary.

Implemented structural repair and ordering:

1. Reference API 18 appends a versioned iOS drawable-bridge callback with a bounded 64-record-per-context contract; non-GL4ES paths register no callback.
2. SDL UIKit supplies the live current EAGL context, `viewFramebuffer`, `viewRenderbuffer`, and live backing width/height. No FBO, renderbuffer, or geometry value is hard-coded.
3. After SDL's optional MSAA resolve and immediately before presentation, the pre-present callback verifies context/target/geometry, flushes pending GL4ES display-list and bitmap work, requires logical framebuffer 0 and the actual GL4ES native main FBO source, raw-binds the explicit nonzero SDL destination, validates it, and uses GL4ES's existing GLES2-compatible textured-blit machinery.
4. The live SDL view renderbuffer is rebound and presented. The actual `presentRenderbuffer` result is passed to the post-present callback.
5. Post-present checks the expected source native FBO/renderbuffer and logical framebuffer state, restores the native GL4ES main FBO and expected renderbuffer, re-queries them, and reports success only when the native and logical state match the invariant.

Why this satisfies the order: it repairs the precise ownership interface proved missing in Phase A while preserving the renderer, real Diffusion menu callbacks, touch controls, map loading, shaders, animated-model shader sharing, one-bone rigid path, and Half-Life behavior. It does not route stock pre-swap to FBO 0, does not add a sentinel, does not bypass the menu or 3-D rendering, and does not attempt the separately forbidden uniform or map-transition fixes.

Diagnostic policy: the old Work Order 43 high-volume renderer/swap/present instrumentation is no longer active in engine/reference/build routes. Phase B emits only one policy/context record; source/target/geometry and before/after five-region checksum proof for at most the first three transfers; one successful-present record; one restore record; and one terminal summary, with a hard maximum of 64 records per context and no per-frame log flushing. Historical patch files remain in the repository for provenance but are not applied, and the IPA verifier rejects their runtime markers and the sentinel marker.

Expected bounded log markers:

- `iOS drawable bridge policy:`
- `iOS drawable bridge source:`
- `iOS drawable bridge proof:`
- `iOS drawable bridge present:`
- `iOS drawable bridge restore:`
- `iOS drawable bridge terminal:`

Local and CI validation:

- The SDL bridge patch passed `--check` and applied cleanly against exact SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`.
- The GL4ES bridge patch passed `--check` and applied cleanly after the accepted base iOS patch against exact GL4ES `81547d986798e876de8b434193920b606a72363f`.
- Accepted Diffusion patches applied against the exact pinned tree; the Windows checkout required whitespace-tolerant validation for one shader patch because of line-ending conversion, while CI applied the pinned patch route normally.
- Python scripts compiled; the bridge validator passed its positive policy audit and rejected mutations for hard-coded targets, hard-coded geometry, stock pre-swap routing, sentinel insertion, missing restore, and unbounded diagnostics.
- The existing Diffusion validator reconfirmed the shared animated shader key/layout and preserved one-bone rigid path.
- `git diff --check` passed. A local Unix/iOS build was unavailable on the Windows worker, so compilation and binary checks were performed by the qualifying macOS Actions job.
- CI successfully checked out every exact revision, built the arm64 engine plus Half-Life and Diffusion client/server/menu targets with `XASH_IOS=1`, validated bundle version 60 and minimum iOS 12.0, found 13 Mach-O files and 11 game dylibs, ran the policy mutation tests, verified bridge markers and the absence of forbidden diagnostics/sentinel strings, packaged the unsigned IPA, and uploaded the retained artifact.
- The downloaded IPA was independently listed and hashed after retrieval; tempfile.org API readback matched its filename, byte size, and SHA-256.

Remaining risks: this candidate has not run on a device. A successful target checksum change proves different pixels reached the SDL drawable, but device evidence is still required to establish visible scene presentation. The bridge may expose a later independent rendering defect or the already-unresolved first `ch1map0` to `ch1map1` termination. The known `glUniform4fv` active-extent error remains deliberately unfixed, and the missing transition save remains a handled fallback rather than this work order's target.

Single device test proposed for orchestrator review only — **not requested from Arjun by the worker**: install bundle version 60, launch with `-dev 2 -log -game diffusion -ref gl4es`, select New Game and a difficulty once, observe whether the stale difficulty image is replaced by the 3-D scene, then continue through the first `ch1map0` to `ch1map1` transition and preserve `engine.log` plus any matching app crash or Jetsam report. The orchestrator alone decides whether to issue this test.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is the content of the immediately following documentation-only `[skip ci]` commit. Its exact ledger commit is recorded in the authoritative Google Doc and final worker handoff because a commit cannot contain its own hash.

Stop state: Work Order 44 Phase B is implemented, locally validated, built, artifact-verified, uploaded, and reported. Stop for orchestrator review. Do not request device testing, diagnose unreviewed future evidence, change the renderer or gameplay, or begin another work order.
