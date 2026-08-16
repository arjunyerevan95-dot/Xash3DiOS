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

## Work order 45 Phase A - GL4ES main-FBO lifecycle and drawable-source ownership audit

Candidate/run and acceptance status: **Outcome B, audit only**. Bundle version 60 is rejected device evidence and is not rebuilt, republished, uploaded, or proposed for another test. This phase creates no candidate, workflow, artifact, IPA, SHA-256, or expected runtime marker. The accepted device baseline remains Run 39.

Repository and evidence boundary:

- Audited repository head: `f20d5b8aaafb501e7ce31c805f97bca4c6f5532a`; Bundle-60 behavioral head: `cff801017b8682f1172fde5627ad7fd34b60152b`; Bundle-60 build head: `dbb8a3d85296cbf5ecde7b840db14375bda0ac7a`.
- Exact pinned inputs: Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`; SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`; GL4ES `81547d986798e876de8b434193920b606a72363f`; Diffusion-MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`.
- Authoritative device result: `DEVICE RESULT 44-B60 - REJECTED`, recording `Xashrec2(1).mp4`, and log `engine(20260814-063601).log`. The recording shows the difficulty screen unchanged through about 112.5 seconds while audio and processing continue. The log reaches `ch1map0`, records at least three returned custom-renderer frames, and continues through foliage work and shader 48.
- Exact first bridge sample: `context match=1; source_fb=2; source_tex=0; source_rb=1; target_fb=1; target_rb=1; drawable=2868x1320; logical_fb=0; target_status=0x0000; transferred=0; failure=4`; the before checksum is valid, no after checksum exists, `changed=0`, presentation is attempted and succeeds, and the terminal record is `result=failure samples=1 success=0 failure=1`.
- The Google Docs ledger exposes those authoritative names, recording properties, and exact records, but not a Drive object URL for either raw Bundle-60 file. A Drive search for the exact names resolves only the ledger. This audit therefore does not claim an independent byte-for-byte replay of the raw files and does not request them; that missing raw identity is treated as an evidence limit.

### Corrected interpretation of Bundle 60's first failure

The Work Order 44 statement that native FBO 2 was proven to be GL4ES's texture-backed `mainfbo_fbo` was false. In the implemented bridge, `source_fb` is assigned from raw `GL_FRAMEBUFFER_BINDING`, while `source_tex` is assigned separately from `glstate->fbo.mainfbo_tex` (`scripts/ios/gl4es-drawable-bridge-ios.patch`; exact applied source `build/wo44-gl4es-applytest3/src/gl/framebuffers.c:1339-1362`). The log never reports `glstate->fbo.mainfbo_fbo`. Thus `source_fb=2` proves only that native FBO 2 was bound when the callback ran; it does not establish its owner or attachment.

Failure code 4 is the wrapper's aggregate for a false return from `gl4es_drawable_bridge_pre`. The helper initializes `target_status` to zero and evaluates one compound guard before it binds or checks the target. Consequently `target_status=0x0000` is **not** evidence that FBO 1 was incomplete; the target status query was never reached. The first exact failure boundary is:

```text
SDL UIKit swapBuffers
  -> callback PRE_PRESENT with live EAGL context, view FBO 1/RB 1, 2868x1320
  -> GL4ES flushes pending list/bitmap work
  -> blitMainFBOTo reads native FBO 2/RB 1 and logical FBO 0
  -> the pre-transfer main-FBO guard fails
  -> no target bind, no transfer, and no after checksum
  -> SDL rebinds RB 1 and presentRenderbuffer succeeds
```

Source inspection proves why the assumed main-FBO side of that guard cannot be satisfied on this build route:

1. `3rdparty/gl4es/wscript:21-24` compiles only `gl/*.c`, `gl/*/*.c`, and `glx/hardext.c`. It deliberately excludes `src/glx/glx.c` and defines `NOEGL`, `NO_INIT_CONSTRUCTOR`, `DEFAULT_ES=2`, and `STATICLIB`.
2. The only non-definition calls to `createMainFBO` in the pinned GL4ES source are in the excluded `src/glx/glx.c:1475-1486` make-current path and `src/glx/glx.c:1563-1582` swap/resize path. There is no caller in the compiled source set.
3. Xash requests an ES 3 backing context on iOS and calls `initialize_gl4es` explicitly after installing SDL-backed proc-address and main-size callbacks (`ref/gl/gl_opengl.c:1376-1386,1511-1555`). It never calls `createMainFBO`.
4. `initialize_gl4es` zeroes `globals4es`. Without a compile-time `LIBGL_FB`, it reads the process environment; only value 2 enables `usefb=1,usefbo=1` (`init.c:85-95,124-158`). Repository source, scripts, workflow configuration, and plist/project inputs contain no `LIBGL_FB` setter or `LIBGL_FB=2` define. Even an externally injected value 2 would enable the flags but would not restore the excluded creation caller.
5. `gl_init` creates GL4ES's logical framebuffer-zero and default-renderbuffer bookkeeping and initializes their current pointers, but the `mainfbo_fbo`, `mainfbo_tex`, depth, and stencil object names remain zero (`glstate.c:396-429,621-627`). The sole creation function allocates a texture, depth/stencil renderbuffers, and an FBO, attaches the texture to color 0, checks completeness, and deletes/zeros all objects on failure (`framebuffers.c:1209-1305`). `deleteMainFBO` also zeros every owned object (`framebuffers.c:1443-1465`). There is no supported persistent state in which a successfully created GL4ES main FBO retains a nonzero FBO while its recorded texture is zero.
6. `LIBGL_FBOFORCETEX` defaults to 1, but it affects wrapper handling of ordinary renderbuffer color attachments. It neither creates the GL4ES main FBO nor changes `createMainFBO`, which always directly allocates and attaches a texture. It cannot explain or repair this boundary.

The source-proven model is therefore: GL4ES logical framebuffer 0 exists as bookkeeping, but the compiled SDL/NOEGL path has no GL4ES main-FBO object lifecycle. At the first Bundle-60 callback the GL4ES-owned source texture is zero, so the texture-blit bridge cannot run. Native FBO 2 belongs to some other native lifecycle.

### SDL UIKit ownership and remaining ambiguity

Pinned SDL creates the CAEAGLLayer-backed view renderbuffer first, then view FBO 1 with a color-renderbuffer attachment (`SDL_uikitopenglview.m:148-170`). If runtime `samples > 0`, it next creates an MSAA framebuffer and a multisample color renderbuffer, attaches the renderbuffer to that FBO, and leaves the MSAA FBO bound (`:172-218`). `drawableFramebuffer` returns the MSAA FBO when present and the view FBO otherwise (`:226-249`). On swap it resolves MSAA into view FBO 1, rebinds the MSAA draw FBO, calls the bridge, explicitly rebinds view RB 1, and presents (`:364-447`). Resize reallocates renderbuffer storage without replacing the object names (`:252-279`); destruction deletes and zeros view, depth, and MSAA objects (`:475-500`).

Xash's `gl_msaa_samples` default is 0, but user configuration may select 2/4/8/16 and `GL_SetupAttributes` then requests SDL multisampling (`engine/client/dll_int/ref_common.c:39`; `ref/gl/gl_opengl.c:1473-1500`). Bundle 60 did not record the runtime sample count, SDL `msaaFramebuffer`/`msaaRenderbuffer` names, or FBO-2 attachment. Therefore FBO 2 is consistent with SDL's renderbuffer-backed MSAA draw FBO if multisampling was active. It is also consistent with a renderer-created native FBO that happened to be current. The current evidence cannot distinguish those owners.

The observed `logical_fb=0` does not contradict raw native FBO 2. GL4ES tracks the logical current framebuffer separately. SDL and other native code can raw-bind a native framebuffer without updating GL4ES's logical pointer; SDL's MSAA resolve path explicitly does so. GL4ES's process-global `glstate` pointer is not thread-local, and Bundle 60 logs only the EAGL-context equality, not the GL4ES state identity or lifecycle generation. A context/state recreation is not supported by current evidence, but it is not instrumented well enough to eliminate completely.

Rejected explanations:

- **Successful GL4ES allocation followed by texture deletion:** rejected. The only GL4ES delete path zeros both the texture and FBO; the create-failure path calls it.
- **`glGenTextures` returned zero while main FBO 2 remained valid:** rejected. The resulting color attachment cannot establish the required texture-backed main FBO; incomplete creation deletes and zeros the owned objects.
- **A valid GL4ES texture exists but its name is unavailable:** rejected. The bridge reads the owning field directly; there is no hidden alternate name in the main-FBO lifecycle.
- **`LIBGL_FBOFORCETEX` should synthesize the missing source:** rejected. That policy applies to ordinary wrapper FBO renderbuffer attachment conversion, not main-FBO creation.
- **FBO 2 is proven SDL MSAA:** not established. SDL's allocation order makes it plausible, but runtime samples and object equality were not logged.
- **FBO 2 is proven a Diffusion/custom-renderer FBO:** not established. Attachment type/name and object owner were not logged.
- **FBO 1 was incomplete:** rejected as an inference from `target_status=0`; the status query did not run. The valid pre-checksum and successful presentation instead support a usable SDL view target.

### Complete presentation path and why later state is unknown

The live path is Diffusion/Xash rendering -> `R_EndFrame` -> engine `GL_SwapBuffers` -> `SDL_GL_SwapWindow` -> UIKit `swapBuffers` -> optional SDL MSAA resolve -> registered `R_IOSDrawableBridge(PRE_PRESENT)` -> `gl4es_drawable_bridge_pre` -> SDL view-renderbuffer bind -> `presentRenderbuffer` -> `R_IOSDrawableBridge(POST_PRESENT)`. GL4ES's GLX make-current and swap functions, including their create/resize/delete/main-FBO calls, are not part of this compiled or invoked route.

After the first failed proof sample, `ref/gl/gl_context.c:615-625` sets `terminalPrinted`. The PRE callback still executes on later swaps, but `proofSample` becomes false and the source/proof records are suppressed; SDL's proof counter also cannot produce a new GL4ES diagnostic sample after that terminal state. Thus the authoritative log proves only the first pre-map snapshot. Continued gameplay, foliage, shader, and present work proves liveness, but it does not prove whether FBO 2's owner, attachment, completeness, dimensions, or binding changed later. The unchanged recording is consistent with repeated failure, but it is not a per-frame attachment audit.

### Source-supported transfer inventory, not an authorized repair

No transfer should be selected until source ownership is observed:

- If the actual rendered source has a texture color attachment, the existing GL4ES textured-blit machinery can draw that texture into SDL's view FBO, subject to explicit dimensions, orientation, viewport/scissor/color-mask preservation, and proof that the texture is not simultaneously sampled and written.
- If the source is a renderbuffer-backed GLES 3 FBO, `glBlitFramebuffer` can copy or resolve into SDL's single-sample view FBO when format, dimensions, sample counts, read/draw bindings, and completeness are compatible. The device uses an ES 3 backing context, but the code must use native GLES capabilities without corrupting GL4ES's logical state.
- If FBO 2 is SDL's own MSAA FBO, SDL already owns the correct resolve into view FBO 1 before the bridge. Treating it as a GL4ES texture source is structurally wrong; the diagnostic must instead determine why the resolved drawable retained the menu image.
- An ES 2 renderbuffer has no general texture-sampling path. Apple MSAA resolve or copy-to-texture routes have stricter ownership, format, and orientation hazards and are not justified as a generic fallback by current evidence.
- Stock `gl4es_pre_swap` is not a solution: its GLX route is excluded, and its generic destination is native FBO 0 rather than SDL's generated view FBO 1.

### Smallest authorized next boundary - diagnostics-only Phase B proposal

Outcome B requires one bounded observation candidate before any behavioral repair. The smallest adequate boundary is to retain the existing no-op-on-failure bridge and add read-only lifecycle/attachment snapshots; it must not create a GL4ES main FBO, change `LIBGL_FB`, change MSAA, select a transfer, bind a new rendering target persistently, alter gameplay, or change menu behavior.

Proposed exact future files:

- `engine/ref_api.h`: version the bridge record and append engine-visible audit fields.
- `ref/gl/gl_context.c`: count every bridge invocation across the terminal condition; log first, state-change, first active-map, and bounded later samples; emit the precondition mask and one terminal summary without suppressing later observation after an early failure.
- `scripts/ios/gl4es-drawable-bridge-ios.patch`: expose `usefb/usefbo`, GL4ES state identity/generation, logical/current/default objects, all `mainfbo_*` names/dimensions, create/resize/delete counters and last status; split the compound guard into a bit mask; query raw native attachment state while restoring all bindings.
- `scripts/ios/sdl2-drawable-bridge-ios.patch`: expose EAGL API/context identity, view/MSAA/depth FBO/RB names, requested/effective samples, drawable dimensions, and raw color/depth/stencil attachment type/name/status for source and target; preserve read/draw framebuffer and renderbuffer bindings around queries.
- `scripts/ios/validate-ios-drawable-bridge.py`: require the bounded observation contract, mutation-test each precondition bit and binding restore, and reject behavioral FBO creation/transfer-policy changes.
- `scripts/ios/verify_ipa.sh`: require only the new bounded audit policy/marker contract and continue rejecting the old high-volume Work Order 43 markers and sentinel.
- `Documentation/XASH3DIOS_PORTING_STATE.md`: record the eventual authorized Phase-B candidate and device outcome.

The raw attachment observation must use native GLES queries, not GL4ES's translated logical query: save draw/read FBO and renderbuffer bindings; bind only the queried FBO transiently; record `glCheckFramebufferStatus`; query `GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE` and `GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME` for color/depth/stencil; for renderbuffer attachments query width, height, internal format, and sample count; record known texture identity and owning dimensions where the owner exposes them; then restore and re-query the exact original native and logical state. SDL object equality (`source == msaaFramebuffer`, `source == viewFramebuffer`) must be reported directly.

Proposed bounded markers:

```text
iOS main-FBO audit policy:
iOS main-FBO lifecycle:
iOS main-FBO state:
iOS native attachment:
iOS drawable bridge attempt:
iOS drawable bridge present:
iOS drawable bridge restore:
iOS main-FBO audit terminal:
```

Every sampled attempt must include a monotonic invocation number, engine connection/active phase, EAGL context and GL4ES state generation, `usefb/usefbo`, logical/native draw/read/RB bindings, GL4ES main FBO/texture/depth/stencil names and dimensions, SDL view/MSAA/depth identities and effective samples, source/target attachment type/name/status/dimensions/samples, a named precondition bit mask, transfer attempted/result, destination checksum before/after when a transfer is already valid, presentation result, and post-present restore result. Emit at most: one policy line; lifecycle events only on init/create/resize/delete/context change; the first three menu attempts; the first active-map attempt; the next six active-map attempts at increasing invocation gaps or on state change; one present/restore anomaly; and one terminal summary, with a hard cap of 64 records per context. This is sufficient to prove whether the later source becomes texture-backed, remains SDL MSAA/renderbuffer-backed, changes owner, or never exists.

Phase-B proof gate: a behavioral repair remains forbidden until one observation run identifies the source owner and attachment at both the early menu and active-map boundaries, proves the matching lifecycle and context, and demonstrates a source-supported transfer with explicit state-restore invariants. If the observed source is SDL MSAA and its resolve into view FBO 1 succeeds without checksum change, the next audit must move upstream to the draw ownership before changing presentation. If a stable texture-backed renderer source is proven, a target-aware textured transfer may be proposed. If a distinct renderbuffer-backed renderer source is proven on GLES 3, a bounded native blit/resolve may be proposed. None is implemented here.

Why this satisfies Work Order 45 Phase A: it corrects the unsupported FBO-2 ownership claim, proves the actual compiled main-FBO lifecycle defect and exact first failure boundary, traces SDL and GL4ES ownership through create/resize/swap/delete, separates compile-time and runtime configuration, eliminates source-inconsistent alternatives, explains why Bundle 60 cannot answer later-frame ownership, inventories only source-supported transfer classes, and defines a single-run discriminator without making a renderer/gameplay change.

Validation performed: Codebase Memory was used only for discovery; every material claim was checked in repository source and exact pinned/applied SDL and GL4ES trees. Pinned revisions and local/remote branch heads were verified. Compiled GL4ES source globs and every `createMainFBO`/`deleteMainFBO` caller were enumerated. Repository/workflow/environment setters for `LIBGL_FB`, `LIBGL_FBOFORCETEX`, and MSAA were searched. The bridge guard, terminal suppression, SDL create/resize/resolve/present/delete paths, GL4ES logical/native bind mapping, main-FBO create/failure/delete path, and engine context initialization were read directly. No source, patch, build script, gameplay, renderer, workflow, or artifact was changed or run by this phase; only this durable ledger is changed. `git diff --check` is required before the documentation-only publication.

Expected new log markers: none from Phase A. The marker list above is a proposal for orchestrator authorization only.

Remaining risks: the raw Bundle-60 file objects are not connector-addressable from the ledger, runtime MSAA count and FBO-2 attachment remain unknown, a later source-state change is unobserved, and GL4ES state/context recreation is not instrumented. The stale-drawable symptom remains real, but its safe transfer mechanism is unresolved. Any immediate `LIBGL_FB=2`, `createMainFBO`, hard-coded FBO-2, texture-blit, native-blit, MSAA-disable, menu, or renderer patch would exceed the proof gate.

Exact files changed by Work Order 45 Phase A: `Documentation/XASH3DIOS_PORTING_STATE.md` only.

Workflow/artifact/IPA/SHA-256: not run or produced; forbidden by this audit-only phase.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This section is published in one documentation-only `[skip ci]` commit. The exact commit is recorded in the authoritative Google Docs mirror and final handoff because a commit cannot contain its own hash.

Stop state: Work Order 45 Phase A ends at **Outcome B** for orchestrator review. Do not implement the proposed diagnostics, create or publish a candidate, run GitHub Actions, retrieve or upload an IPA, use tempfile.org, contact Arjun, request evidence or device testing, revive Bundle 60, diagnose a future run, or begin another work order.

## Work Order 45 Phase B - bundle version 64 diagnostics-only main-FBO audit

Candidate/run and acceptance status: **bundle version 64, build-qualified diagnostics-only candidate; not device-accepted and not a rendering fix**. The accepted device baseline remains Run 39. Bundle 60 remains rejected and was not rebuilt or proposed for another test. Phase B implements only the authorized one-run ownership/presentation discriminator and preserves the visible stale-difficulty-screen expectation until later device evidence is reviewed by the orchestrator.

Commits and exact pinned inputs:

- Behavioral diagnostic implementation: `380e31d90addc4a7540dfea5c0d10de5ffc6565b` (`Instrument Work Order 45 main-FBO pipeline`).
- Final build commit: `7d8ed08c980cc15797d52b9d645f476a08c6ed00` (`Make Work Order 45 validation LTO-safe [skip ci]`). The second commit changes only an over-strict IPA symbol-export assertion; LTO may internalize the linked audit helper, while the required compiled marker contract remains directly verifiable.
- Exact source pins remain Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, GL4ES `81547d986798e876de8b434193920b606a72363f`, and Diffusion-MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`.

Workflow URL/ID and result:

- Sole qualifying candidate workflow: workflow-dispatch [iOS Proof of Life run 31793116163](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31793116163), head `7d8ed08c980cc15797d52b9d645f476a08c6ed00`, result `success`; unsigned arm64 IPA job `94744240681`, every build, contract, and upload step successful.
- The first behavioral push run `31787263990` successfully compiled all targets but failed the pre-upload verifier because it required the LTO-internal `gl4es_drawable_bridge_audit` helper to remain globally exported. Artifact upload was skipped, so it is not a candidate. The open PR automatically started duplicate run `31787266890`; cancellation raced its verifier-only failure and it likewise produced no artifact or candidate. The validation-only fix was pushed with `[skip ci]`, creating no automatic build, and the one corrected workflow was then dispatched manually.

Artifact and IPA:

- Retained artifact `Xash3DiOS-arm64-unsigned`, ID `9216452753`, archive size 8,566,145 bytes, GitHub digest `sha256:a840d0914483231057e3647364d4d7b0fee9e3712c0fd333fb23e84cdea13a5a`: https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31793116163/artifacts/9216452753
- Actual IPA `xash3d-fwgs-ios-arm64.ipa`: 8,663,710 bytes; SHA-256 `A2D409EE3374C39224A8E3795D0381FF541918C548C0EB34875DEA71932FAD49`.
- Tempfile delivery page: https://tempfile.org/cotnm2PPBEy/ ; direct download: https://tempfile.org/cotnm2PPBEy/download ; reported expiry `2026-08-16 10:49:05 UTC`. API readback confirmed the exact filename, byte size, SHA-256, existence, and safe/no-warning scan result.

Exact files changed:

- Behavioral implementation: `engine/ref_api.h`; `ref/gl/gl_context.c`; `scripts/ios/gl4es-drawable-bridge-ios.patch`; `scripts/ios/sdl2-drawable-bridge-ios.patch`; `scripts/ios/validate-ios-drawable-bridge.py`; `scripts/ios/verify_ipa.sh`.
- Validation-only follow-up: `scripts/ios/verify_ipa.sh`.
- Durable report: `Documentation/XASH3DIOS_PORTING_STATE.md` only in the following documentation-only `[skip ci]` commit.

Verified failure boundary: the underlying device boundary is unchanged from rejected Bundle 60: Diffusion reaches `ch1map0`, normal CPU/render processing and successful EAGL presentation continue, but the stale difficulty image remains visible; the first bridge call observed raw native FBO 2, GL4ES logical framebuffer zero, no GL4ES main texture, and failed the pre-transfer main-FBO guard before target status or transfer. Phase A proved that FBO 2's owner and attachment were unresolved and that the compiled SDL/NOEGL GL4ES route has no active main-FBO creator. Phase B intentionally does not reinterpret that raw binding or select a transfer.

Structural cause: **still unresolved pending the authorized observation evidence**. Source proves only the diagnostic gap: the previous candidate collapsed all guard failures, did not expose GL4ES main-object lifecycle or SDL MSAA/depth identities, did not query source/target attachments, and stopped detailed sampling after the first failure. It could not distinguish SDL's renderbuffer-backed MSAA FBO, a different native renderer FBO, or a later ownership/binding change.

Why this change satisfies Work Order 45 Phase B:

- Checkpoint A wraps the engine swap function at the immediate renderer handoff after normal `R_EndFrame`; B records SDL swap entry before the ordinary resolve; C records immediately after SDL's unchanged resolve; D records the existing bridge's entry and return; E records immediately before presentation and after presentation plus the existing restore attempt. Every sampled record carries one monotonic invocation and the same engine phase/map/host/client timestamp identity.
- The versioned ABI now carries EAGL API/context generation, SDL view/MSAA/depth FBO/RB names, requested/effective samples, geometry/resize generation, and a named bridge-precondition mask.
- GL4ES exposes read-only state identity/generation, `usefb/usefbo`, logical/current/default/main objects and dimensions, bounded create/success/resize/delete counters and status, native draw/read/RB bindings, transient source/target completeness and color/depth/stencil attachment type/name, renderbuffer dimensions/format/samples, known main-texture dimensions, five fixed 4x4-region checksums, the first exact query failure operation/error, and post-query restored native/logical state.
- Sampling is the first three menu invocations, first active-map invocation, active offsets 2/4/8/16/32/64, and observed identity/lifecycle changes, with one terminal record and a hard maximum of 64 records per context.
- The existing bridge guard, transfer implementation, SDL resolve, view-renderbuffer binding, and EAGL present remain behaviorally unchanged. Failed guards remain no-ops. No main FBO or persistent render target is created, `LIBGL_FB` and MSAA are not changed, no new blit/resolve/copy/transfer or sentinel is introduced, and menu/gameplay/renderer functionality is not disabled or bypassed.

Validation performed:

- The SDL diagnostics patch passed `git apply --check --unidiff-zero` and applied cleanly to exact SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`.
- The accepted base iOS GL4ES patch and Phase-B audit patch passed `git apply --check --unidiff-zero` and applied in order to exact GL4ES `81547d986798e876de8b434193920b606a72363f`.
- `validate-ios-drawable-bridge.py ... --self-test` passed its positive policy audit and rejected nine deliberate mutations: unauthorized main-FBO creation, `LIBGL_FB` injection, MSAA-policy change, hard-coded FBO identity, new transfer, persistent attachment mutation, sentinel insertion, unbounded record cap, and missing native restore.
- `git diff --check` and Python bytecode compilation passed. A local arm64 iOS toolchain is unavailable on the Windows worker; the qualifying macOS job compiled the engine and relevant Half-Life/Diffusion client/server/menu targets with `XASH_IOS=1`, passed the policy and IPA contract, and published the artifact.
- Independent downloaded-IPA validation found bundle version 64, minimum iOS 12.0, file sharing enabled, 13 Mach-O payloads and no non-arm64 Mach-O, all required engine/SDL/renderer/Diffusion payloads, all ten expected markers, no sentinel/legacy proof markers, and the exact SHA-256 above.

Expected new log markers:

```text
iOS main-FBO audit policy:
iOS main-FBO lifecycle:
iOS main-FBO state:
iOS native attachment:
iOS presentation pipeline:
iOS pixel checkpoint:
iOS drawable bridge attempt:
iOS drawable bridge present:
iOS drawable bridge restore:
iOS main-FBO audit terminal:
```

Preserved baseline: the real Diffusion menu and callbacks, touch, button audio, New Game/difficulty selection, canonical materials, shared animated-model shader layout, on-demand shaders, GL4ES, SDL presentation, gameplay, foliage, and all unrelated fixes remain enabled. This diagnostics-only build is not expected or claimed to improve visible rendering.

Remaining risks: no device evidence exists for bundle version 64, so source ownership, attachment type, MSAA state, and the exact checksum divergence checkpoint remain unknown. Bounded native queries/readbacks add diagnostic GPU synchronization and may affect timing. A default/native framebuffer attachment query may itself be unsupported; the exact query operation/error field exists to make that outcome explicit while restoring and re-querying bindings. The known first custom-renderer `GL_INVALID_OPERATION`, possible later first-map transition defect, and rendering repair remain deliberately outside this phase.

Single device test requested: **none by the worker**. This report does not contact Arjun, request evidence, recommend installation, or begin Phase C. The orchestrator alone reviews whether the candidate meets the proof gate and whether any later device test is authorized.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in the immediately following documentation-only `[skip ci]` commit. Its exact hash is recorded in the authoritative Google Docs ledger and the final worker handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 45 Phase B diagnostics, validation, one qualifying candidate, artifact retrieval, independent verification, the one authorized tempfile.org upload, and both ledger reports are complete. Stop for orchestrator review. Do not request device testing, contact Arjun, diagnose future evidence, implement a renderer/gameplay repair, begin Phase C, or create another work order.

## Work Order 46 Phase A - iOS drawable architecture audit

Candidate/run and acceptance status: **Outcome A selected, source audit only; no candidate and no device acceptance**. Bundle version 64 is decisive diagnostic evidence but remains diagnostics-only and is not accepted, rebuilt, republished, uploaded, or proposed for another test. Run 39 remains the accepted device baseline. This phase creates no behavioral change, workflow, artifact, IPA, SHA-256, or runtime marker.

Audited inputs and evidence:

- Repository audit head: `b3c9e69166e9c11c0ebb96d2201aad65ea9a0b60`; Bundle-64 build head: `7d8ed08c980cc15797d52b9d645f476a08c6ed00`.
- Exact source pins: Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`; SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`; GL4ES `81547d986798e876de8b434193920b606a72363f`; Diffusion-MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`.
- Authoritative Run-64 evidence is `engine(20260814-121434).log` (2,168 lines, 120,738 bytes) and `Xashrec3.mp4` (about 171.3 seconds of video and 172.7 seconds of audio, 1112x512). The ledger records 57 bounded checkpoint records spanning invocations 1, 2, 3, 478, 479, 480, 481, 487, 489, 491, 495, and 503. Complete A-through-E samples exist through invocation 495; invocation 503 is intentionally bounded at A/B.
- Device evidence proves the app is not frozen: `ch1map0.bsp` loads, at least 12 gameplay frames complete, processing continues through foliage and shader 48, later reaches `ch1map1`, and EAGL presentation succeeds on every complete sampled invocation. The stale view checksum remains `0x384e1e45`.
- Ownership is now resolved: native FBO 2 is SDL's live multisample framebuffer with a 2868x1320 RGBA8, four-sample color renderbuffer 2 and depth/stencil renderbuffer 3. Native FBO 1 with color renderbuffer 1 is SDL's live CAEAGLLayer-backed view target. Requested MSAA was 8 and the device clamped the effective sample count to 4. GL4ES reports logical framebuffer zero, `usefb=0`, `usefbo=0`, and no texture-backed main FBO. The remaining question is not object ownership; it is where the normal scene pixels are lost before the view target is presented.

### End-to-end handoff and GL symbol ownership

The complete live path is:

```text
Diffusion/custom renderer
  -> ref/gl R_EndFrame
  -> engine GL_SwapBuffers
  -> SDL_GL_SwapWindow
  -> UIKit_GL_SwapWindow
  -> SDL_uikitopenglview swapBuffers
  -> optional SDL MSAA blit/resolve
  -> bind view color renderbuffer
  -> EAGLContext presentRenderbuffer
```

`R_EndFrame` flushes 2-D mode and calls `gEngfuncs.GL_SwapBuffers` (`ref/gl/gl_rmain.c:1192-1213`). The SDL2 platform implementation calls `SDL_GL_SwapWindow(host.hWnd)` (`engine/platform/sdl2/vid_sdl2.c:807-818`). Pinned SDL routes that call through `UIKit_GL_SwapWindow` to `[context.sdlView swapBuffers]` (`src/video/uikit/SDL_uikitopengles.m:112-128`). In the GLES 3 MSAA branch, `swapBuffers` binds only the view FBO as `GL_DRAW_FRAMEBUFFER`, calls `glBlitFramebuffer`, invalidates the assumed read buffer, restores only the draw binding to the MSAA FBO, binds the view renderbuffer, and presents (`src/video/uikit/SDL_uikitopenglview.m:300-383`). The upstream comment explicitly requires the drawable/MSAA framebuffer to have remained bound before swap. The project SDL patch adds diagnostics and an explicit view-renderbuffer bind but does not make the read source explicit or repair this assumption.

The symbols in that SDL Objective-C file are raw Apple OpenGLES calls. It includes the Apple OpenGLES headers, and GL4ES's alias implementation is excluded on Apple (`src/gl/attributes.h:69-123`); SDL therefore does not enter GL4ES for `glBindFramebuffer`, `glBlitFramebuffer`, `glInvalidateFramebuffer`, `glBindRenderbuffer`, attachment queries, or `presentRenderbuffer`. The Xash renderer is different: on Apple with `XASH_GL4ES`, `ref/gl/gl_export.h:27-35` mangles renderer calls to `gl4es_gl*`. Diffusion loads `pglBindFramebuffer` through its render API; `R_GetProcAddress` returns `gl4es_GetProcAddress` on this configuration (`ref/gl/gl_context.c:390-396,468`), while GL4ES obtains its underlying `gles_gl*` functions through Xash -> `SDL_GL_GetProcAddress` -> UIKit `dlsym(RTLD_DEFAULT, ...)`. Thus the exact ownership boundary is wrapper GL in Diffusion/ref, raw GL inside SDL/UIKit, and EAGL at presentation.

### The structural mismatch

Pinned SDL creates the view renderbuffer from the CAEAGLLayer, attaches it to view FBO 1, then creates multisample FBO 2/color renderbuffer 2 and a four-sample depth/stencil renderbuffer 3. It leaves FBO 2 bound (`SDL_uikitopenglview.m:95-209`). `drawableFramebuffer` returns FBO 2 while MSAA is enabled and FBO 1 otherwise (`:217-230`). The maximum-samples query clamps requested 8 to effective 4. Resize reallocates storage for the same object names and restores the prior renderbuffer; background/foreground delivers app events and `UIKit_GL_RestoreCurrentContext` repairs EAGL current-context ownership. Object IDs change only when SDL destroys and recreates the view/context; destruction deletes the view, depth/stencil, and MSAA objects (`:385-444`). SDL's existing `SDL_SysWMinfo` already exposes the live drawable framebuffer, color renderbuffer, and resolve framebuffer rather than requiring hard-coded IDs (`include/SDL_syswm.h:276-290`; `SDL_uikitwindow.m:379-408`).

The GL4ES build deliberately compiles the GL wrapper sources and `glx/hardext.c`, excludes the GLX lifecycle, and defines `NOEGL` (`3rdparty/gl4es/wscript:21-24`). `gl_init` creates logical framebuffer-zero bookkeeping, but the excluded GLX path is the only caller that would create a texture-backed GL4ES main FBO. Run 64 confirms `usefb=0`, `usefbo=0`, and all `mainfbo_*` objects zero.

This is not equivalent to a native default framebuffer. `gl4es_glBindFramebuffer(..., 0)` maps logical zero to `mainfbo_fbo`; when no main FBO exists, it calls raw `gles_glBindFramebuffer(..., 0)` (`src/gl/framebuffers.c:231-274`). The same zero substitution occurs in `readfboBegin`/`readfboEnd`, `ReadDraw_Push`/`ReadDraw_Pop`, and `gl4es_setCurrentFBO` (`:61-105,279-305,1819-1828`). Raw SDL binds never update GL4ES's cached logical current/read/draw objects. Initial logical-zero rendering therefore reaches SDL FBO 2 only because SDL happened to leave it raw-bound. The wrapper and embedder have no explicit contract saying that logical zero means SDL's live nonzero drawable.

Diffusion makes the mismatch observable. `R_AllocFrameBuffer` creates a renderer FBO and restores with `pglBindFramebuffer(..., 0)`; `GL_BindFrameBuffer` and `GL_BindFBO(FBO_MAIN)` do the same (`client/render/r_backend.cpp:315-419`, with `FBO_MAIN == -1` in `r_const.h:54`). Map/subview transitions call those helpers (`r_world.cpp:1846-1860`; `r_subview.cpp:394-418,605-635`). Because `pglBindFramebuffer` is the GL4ES wrapper, these expected logical-main restores raw-bind native FBO 0. They account for Run-64's transient native-zero bindings at invocations 478 and 480; they do not indicate a new owner or context loss. SDL later restores only `GL_DRAW_FRAMEBUFFER` to FBO 2, so the raw read binding can remain zero while GL4ES still reports logical zero.

The error sequence follows directly. Run 64's source `glReadPixels` calls against four-sample FBO 2 produce `GL_INVALID_OPERATION`; GLES 3 does not permit direct pixel reads from a multisampled framebuffer, so those checksum failures do not prove that scene pixels are absent. The ordinary SDL resolve then binds only DRAW=FBO 1 and assumes READ still names FBO 2. After a wrapper logical-zero restore has changed native READ/DRAW to incomplete native FBO 0, `glBlitFramebuffer` reads from FBO 0 and produces `GL_INVALID_FRAMEBUFFER_OPERATION`. The post-resolve audit observes that pending error. SDL then presents the still-valid but unchanged FBO 1, explaining the stable checksum, successful presentation, and stale menu image without a deadlock. FBO 1 itself is supported by its successful creation check, valid checksum, and repeated successful presentation; the failure is the implicit read-source contract.

### Architecture comparison and decision

| Option | Ownership model | Required behavior | Assessment |
| --- | --- | --- | --- |
| A - direct drawable | SDL owns one CAEAGLLayer-backed view FBO/renderbuffer/depth-stencil set; GL4ES logical zero maps explicitly to that live FBO | Force iOS GL4ES SDL MSAA to zero; install a context-scoped native-default-FBO mapping before renderer GL calls; present the view renderbuffer with no resolve | **Selected, Outcome A.** It removes the split read/draw ownership and the implicit resolve entirely. It uses the existing SDL view target and existing SysWM live-ID query, reduces memory/bandwidth, and needs one wrapper/embedder contract. The cost is loss of effective 4x MSAA and possible aliasing. |
| B - wrapper-aware MSAA | SDL retains FBO 2/RB 2 as the draw target and FBO 1/RB 1 as the present target; GL4ES logical zero maps to the live MSAA FBO | Add the same context-scoped mapping plus make SDL's one resolve explicit: bind READ=FBO 2, DRAW=FBO 1, blit once, and restore native read/draw plus logical state | Source-coherent but not the smallest reliable first repair. It preserves AA but keeps two owners, two native targets, sample/depth lifecycle, an explicit synchronization boundary, and raw-versus-wrapper state restoration. It adds failure modes after already requiring the core mapping that A needs. |
| C - GL4ES texture main FBO | GL4ES owns a third texture-backed main FBO; SDL still owns its view target and possibly MSAA objects | Enable/create/resize/delete the excluded GL4ES main-FBO architecture, then transfer its texture to SDL's target | Rejected. The pinned SDL/NOEGL build reports `usefb=0,usefbo=0` and excludes the GLX creators. Enabling it would introduce a third render-target lifecycle and a second transfer rather than repair the actual embedder-default contract. |

Outcome A is the structurally smallest reliable repair. Both A and B need a live, context-scoped mapping because neither SDL FBO 1 nor FBO 2 is native zero. A then deletes the entire MSAA resolve dependency: no split READ/DRAW default, no multisample read restriction, no blit compatibility requirement, no stale read binding, and no second color buffer. It changes only the iOS GL4ES presentation profile; Half-Life/Diffusion renderer FBOs, materials, shaders, menu callbacks, touch, gameplay, and non-iOS paths remain intact.

### Exact future mutation boundary - not implemented in Phase A

If and only if Phase B is later authorized, the repair must stay within this boundary:

- `ref/gl/gl_opengl.c`, `GL_SetupAttributes`: for `XASH_IOS && XASH_GL4ES`, request zero SDL multisample buffers/samples regardless of the persisted `gl_msaa_samples` value; retain the setting and all existing behavior elsewhere.
- `engine/ref_api.h`: add a versioned platform-to-renderer query for the current drawable framebuffer/renderbuffer and context/lifecycle identity, rather than exposing or hard-coding an observed numeric object ID.
- `engine/platform/sdl2/vid_sdl2.c`: implement that query from the live `SDL_SysWMinfo` UIKit fields after context creation/make-current; reject a missing, stale, non-UIKit, or zero drawable result. Re-query on context recreation and verify it after foreground/context restoration. No SDL source change is required for the basic direct-drawable identity because pinned SDL already exports it.
- `ref/gl/gl_opengl.c`, `GL_OnContextCreated` and shutdown/context-loss handling: install the live drawable mapping immediately after `initialize_gl4es` and before any renderer GL call; clear it before `close_gl4es`/SDL context destruction; refresh only on a proven context generation change. Reassert the mapping after context restoration without inventing a new owner.
- `scripts/ios/gl4es-drawable-bridge-ios.patch` (or one replacement patch with the same pinned-source policy): add a narrow public embedder setter and central helper that maps every logical-zero native bind path to the supplied live SDL framebuffer. It must cover `gl4es_glBindFramebuffer`, read/draw push/pop, readback helpers, and `gl4es_setCurrentFBO`; ordinary nonzero renderer FBO semantics remain unchanged. It must not enable `LIBGL_FB`, create `mainfbo_fbo`, or alias the SDL object as GL4ES-owned storage.
- `scripts/ios/sdl2-drawable-bridge-ios.patch` and `ref/gl/gl_context.c`: retire the failed texture-main-FBO transfer path and reduce the Bundle-64 audit to bounded acceptance evidence. SDL's normal no-MSAA swap must bind the live view renderbuffer and present exactly once; there must be no custom copy, blit, resolve, sentinel, or menu bypass.
- `scripts/ios/validate-ios-drawable-bridge.py` and `scripts/ios/verify_ipa.sh`: enforce zero iOS GL4ES MSAA, live-ID acquisition, all logical-zero mapping sites, context-scoped reset/refresh, absence of `LIBGL_FB`/main-FBO creation/hard-coded IDs/extra transfer, and the bounded marker contract.
- `Documentation/XASH3DIOS_PORTING_STATE.md`: record the later authorized implementation, build, and device outcome.

Required invariants for that future repair:

1. SDL remains the sole owner of the CAEAGLLayer view FBO, view color renderbuffer, and depth/stencil renderbuffer; GL4ES owns only the mapping from its logical zero to SDL's live object.
2. On iOS GL4ES the requested and effective sample counts are both zero. There is no MSAA FBO/color renderbuffer and exactly zero resolve/blit/copy operations in the presentation path.
3. Every GL4ES operation that means logical framebuffer zero binds the current live SDL view FBO for both read and draw. Nonzero Diffusion/renderer FBOs and their restoration remain unchanged.
4. The mapping is obtained after the EAGL context is current, installed before rendering, never hard-coded, cleared before context destruction, and refreshed before use after a real context recreation. Resize may reallocate storage under stable IDs; dimensions and completeness must be revalidated. Foreground restoration must reassert the current EAGL context and mapping.
5. GL4ES logical state and raw native read/draw bindings agree at renderer handoff and after each logical-main restore. SDL presentation may bind the view renderbuffer but must not leave a different framebuffer contract behind.
6. Viewport, scissor, color/depth/stencil masks, active renderer FBOs, menu/touch callbacks, audio, map progression, shaders, foliage, and all accepted Run-39 behavior remain enabled.

One bounded future acceptance gate, defined but **not requested or authorized here**: in a single later-authorized device run, prove policy `requested_samples=0 effective_samples=0`, no MSAA objects or resolve marker, the GL4ES logical-zero mapping equals SDL's live nonzero view FBO from the menu through the first active `ch1map0` frames, native read/draw bindings return to that same object after every sampled renderer-FBO restore, FBO completeness remains valid, and presentation succeeds without `GL_INVALID_FRAMEBUFFER_OPERATION`. Acceptance additionally requires the drawable checksum to change from the difficulty baseline by the first active-map frames and the visible 3-D scene to replace the stale menu while preserving the real menu, touch, audio, difficulty callback, map load, and gameplay-frame evidence. The known later map-transition termination and `glUniform4fv` issue remain separate; they cannot be bundled into this gate.

Why this satisfies Work Order 46 Phase A: it traces the complete custom-renderer-to-EAGL path and names raw, SDL, GL4ES, and EAGL ownership; reconciles GL4ES logical zero with native FBO 2 and transient native zero; explains both audited GL error classes; audits requested/effective MSAA and context/resize/background/destruction lifecycle; compares all three authorized architectures against the pinned build; selects one source-supported outcome; specifies the smallest future mutation boundary and invariants; and defines exactly one acceptance gate without changing behavior or starting Phase B.

Validation performed: Codebase Memory graph discovery and call tracing were followed by direct inspection of every cited repository and exact pinned/applied source path. The audited pins and local/remote branch head were verified. Renderer call mangling and proc loading, SDL raw-symbol linkage, EAGL context/view creation, MSAA clamp/allocation/resolve/resize/present/delete, UIKit foreground context restoration and SysWM live-object export, GL4ES compiled-source policy, logical-zero bookkeeping and every native-zero substitution helper, and Diffusion's main-FBO restore callers were read directly. The Run-64 checkpoint/error chronology was reconciled against those sources. Upstream history available in the pinned clones confirms SDL's implicit-bound-source resolve contract and GL4ES's longstanding zero-to-`mainfbo_fbo` design; neither pin provides an embedder-supplied nonzero-default-FBO contract. `git diff --check`, changed-file review, documentation-only commit inspection, remote-head verification, and both-ledger readback are required for publication. No source/patch/script/workflow/artifact behavior is changed or run.

Expected new log markers: none. Phase A is documentation-only. A future Phase-B marker set is deliberately not invented here beyond the acceptance invariants above.

Exact files changed by Work Order 46 Phase A: `Documentation/XASH3DIOS_PORTING_STATE.md` only.

Workflow/artifact/IPA/SHA-256: not run or produced; all are forbidden by this phase.

Structural cause: GL4ES and SDL have incompatible definitions of the default framebuffer. GL4ES logical zero falls through to native zero, while SDL's actual iOS draw/present objects are generated nonzero FBOs. SDL's GLES 3 MSAA swap assumes its MSAA object is still the native read framebuffer, but expected Diffusion logical-main restores can raw-bind native zero through GL4ES without updating the logical cache. The resolve then reads an incomplete framebuffer, leaves the valid view target stale, and successfully presents those stale pixels.

Remaining risks: direct rendering trades effective 4x MSAA for a simpler ownership contract and may reveal visible aliasing. The future wrapper hook must cover every logical-zero helper, not only public `glBindFramebuffer`; a first-frame gap, context-generation race, or stale resize identity would reproduce the defect. Rendering directly into the view FBO may expose an independent renderer assumption previously masked by MSAA. The known `glUniform4fv` active-extent issue and later `ch1map0` to `ch1map1` termination remain unresolved and explicitly outside this work order.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit. The exact commit is recorded in the authoritative Google Docs mirror and final handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 46 Phase A ends at **Outcome A** for orchestrator review. Do not implement the direct-drawable repair, modify SDL/GL4ES/renderer/gameplay code, build or publish a candidate, run GitHub Actions, retrieve or upload an IPA, use tempfile.org, contact Arjun, request evidence or device testing, or begin Phase B.

## Work Order 46 Phase B - bundle version 69 direct SDL drawable

Candidate/run and acceptance status: **bundle version 69, build-qualified direct-drawable candidate; not device-accepted**. Run 39 remains the accepted device baseline. Bundle 64 remains diagnostics-only evidence and was not rebuilt or proposed for another test. No device test, log, or other user evidence was requested.

Commits and exact pinned inputs:

- Behavioral implementation: `93881a0513c648ec5d20d1f96efb8f8a03347c00` (`fix(ios): render GL4ES logical zero into SDL drawable`).
- Bounded build fixes permitted by the Phase-B stop rules: `de230a982084afbfa6910b92ffeac8f34ab185e1` defines the framebuffer-completeness API token locally without changing runtime policy; `4caad99dbb7e0fdaed050dd21fad2095655ce6b0` forward-declares the versioned drawable state so the pre-existing `common.h -> system.h -> platform.h` include cycle can compile. Candidate head: `4caad99dbb7e0fdaed050dd21fad2095655ce6b0`.
- Exact source pins remain Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, GL4ES `81547d986798e876de8b434193920b606a72363f`, and Diffusion-MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`.

Workflow URL/ID and result:

- Sole qualifying candidate workflow: canonical push [iOS Proof of Life run 31819158442](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31819158442), bundle/run number 69, head `4caad99dbb7e0fdaed050dd21fad2095655ce6b0`, result `success`; unsigned arm64 IPA job `94827992981`. Checkout, pinned dependency installation and patching, engine/Half-Life/Diffusion/menu builds, IPA contract verification, and artifact upload all succeeded.
- Push run `31809914937` (bundle 65, behavioral head) passed policy/rejection validation and compiled the pinned GL4ES patch, then failed renderer compilation because `GL_FRAMEBUFFER_COMPLETE` was not visible in that translation unit. It uploaded no artifact and is not a candidate. Automatic PR duplicate `31809919200` was cancelled.
- Push run `31810459430` (bundle 67) compiled and linked `libref_gl4es.dylib`, then failed the engine build because the new platform prototype encountered its typedef before `ref_api.h` in the include cycle. It uploaded no artifact and is not a candidate. Automatic PR duplicate `31810464886` was cancelled.
- The bundle-69 open-PR duplicate `31819161529` was cancelled. All Build & Deploy Engine invocations created by these pushes were automatically skipped. Exactly one qualifying artifact was retained.

Artifact and IPA:

- Retained artifact `Xash3DiOS-arm64-unsigned`, ID `9226352131`, archive size 8,564,353 bytes: https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31819158442/artifacts/9226352131
- Actual IPA `xash3d-fwgs-ios-arm64.ipa`: 8,661,301 bytes; SHA-256 `2F99ABC90CDA21EAF7B9A3373C9633EF17BB1192EA1DB88EA698727A6224900A`.
- Tempfile delivery page: https://tempfile.org/81D5ufEaQwE/ ; direct download: https://tempfile.org/81D5ufEaQwE/download ; reported expiry `2026-08-16 16:40:08 UTC`. API metadata and security readback confirmed the exact filename, byte size, SHA-256, existence, and `safe`/no-warning scan result. The first local POST connection was terminated by the worker execution timeout before it returned any response or file ID; the documented bounded retry created this single confirmed publication object. No second confirmed tempfile object is known or reported.

Exact files changed:

- `engine/ref_api.h`: advances the renderer API and defines the version-3 direct-drawable state/action contract plus the platform query slot.
- `engine/client/dll_int/ref_common.c`: supplies the iOS platform drawable query through the renderer import table; non-iOS builds retain `NULL`.
- `engine/platform/platform.h`: declares the query and forward-declares its state type. This additional authorized integration file is necessary because platform/video entry points are declared here and the engine include cycle reaches it before `ref_api.h`.
- `engine/platform/sdl2/vid_sdl2.c`: dynamically queries the live UIKit drawable FBO/color renderbuffer, current EAGL-context identity, size, sample state, and context/resize generation through `SDL_SysWMinfo`; it registers the callback before swap and unregisters it before SDL context destruction.
- `ref/gl/gl_opengl.c`: forces requested iOS+GL4ES SDL samples to zero, installs the mapping immediately after `initialize_gl4es` and before renderer GL hints/calls, and clears it before `close_gl4es`.
- `ref/gl/gl_context.c`: retires the Bundle-60 texture transfer and broad Bundle-64 audit; revalidates/reasserts the live mapping at bounded lifecycle/swap points and emits only the authorized policy, register, logical-zero, lifecycle, present, and proof records.
- `scripts/ios/gl4es-drawable-bridge-ios.patch`: adds context-scoped external-default state and central logical-zero/native mapping helpers to the exact GL4ES pin, covering public binding, read/write helpers, read/draw push-pop, current-FBO state, save/restore, and audited fallback paths while leaving ordinary nonzero renderer FBO semantics unchanged.
- `scripts/ios/sdl2-drawable-bridge-ios.patch`: adds the version-3 direct-drawable callback to the exact SDL pin, keeps SDL as view-object owner, restores/reasserts lifecycle state, binds the view color renderbuffer, and performs exactly one normal presentation with the iOS+GL4ES active path at zero samples.
- `scripts/ios/validate-ios-drawable-bridge.py`: enforces the complete Work Order 46 direct-drawable contract and rejection fixtures.
- `scripts/ios/verify_ipa.sh`: verifies the new marker/API contract and rejects obsolete transfer/main-FBO diagnostics.
- `Documentation/XASH3DIOS_PORTING_STATE.md`: this durable report only in the following documentation-only `[skip ci]` commit.

Verified prior failure boundary: Run 64 proved that Diffusion and Xash continued through `ch1map0`, gameplay frames, foliage, shader 48, later `ch1map1`, and successful EAGL presentations while the view checksum and visible difficulty image remained stale. GL4ES logical-zero restores fell through to native FBO 0; SDL owned live MSAA FBO 2 and view FBO 1; SDL's GLES 3 resolve assumed FBO 2 was still READ, then attempted its blit from incomplete native FBO 0, yielding `GL_INVALID_FRAMEBUFFER_OPERATION` and presenting unchanged but valid FBO-1 pixels.

Structural cause: GL4ES and SDL had incompatible default-framebuffer ownership contracts. GL4ES logical zero mapped to native zero because the compiled SDL/NOEGL route has no GL4ES main FBO, while SDL's actual iOS drawable was a generated nonzero FBO. With SDL MSAA enabled, expected Diffusion logical-main restores could change raw read/draw bindings without changing GL4ES's logical cache, invalidating SDL's implicit resolve-source assumption.

Why the implementation satisfies the authorized invariants:

1. SDL remains sole owner of the CAEAGLLayer-backed view FBO, color renderbuffer, and depth/stencil storage; GL4ES stores only a context-scoped external-default identity.
2. `XASH_IOS && XASH_GL4ES` forces requested/effective samples to zero. The active direct path creates no SDL MSAA object and performs no resolve, blit, copy, sentinel, or post-render transfer.
3. A central GL4ES helper maps every audited meaning of logical framebuffer zero to the registered live SDL view FBO, including public binds, read/write helpers, read/draw push-pop, current-FBO and save/restore paths. Nonzero renderer FBO behavior is preserved.
4. The renderer proof records compare GL4ES logical current/read/draw zero with native read/draw equality to the live view FBO and validate completeness after initial registration and sampled restores; the validator rejects a public-bind-only hook or any remaining audited logical-zero-to-native-zero path.
5. Identity is queried dynamically only after the correct EAGL context is current, never hard-coded, installed before renderer GL use, revalidated for resize/context/foreground lifecycle, reasserted at swap, and cleared before destruction.
6. The implementation does not set `LIBGL_FB`, create/alias `mainfbo_fbo`, claim SDL storage, or retain the Bundle-60 transfer. The SDL no-MSAA path binds the live view renderbuffer and calls one normal `presentRenderbuffer`.
7. Diffusion gameplay, renderer FBOs, materials/shaders, real menu callbacks, touch, audio, difficulty callback, map load, foliage, viewport/scissor/masks, and non-iOS behavior were not disabled or bypassed.

Validation performed:

- Codebase Memory graph discovery/call tracing was followed by direct inspection of the exact repository and pinned/applied SDL and GL4ES sources.
- Both replacement patches applied cleanly with `--unidiff-zero` against SDL `5d249570393f7a37e037abf22cd6012a4cc56a71` and GL4ES `81547d986798e876de8b434193920b606a72363f` after the existing base patch.
- `python -m py_compile scripts/ios/validate-ios-drawable-bridge.py` passed. Validator positive/self-tests passed and explicitly rejected hard-coded IDs, nonzero MSAA, transfer/resolve/copy, `LIBGL_FB`/main-FBO policy, public-bind-only mapping, native-zero fallback, missing clear or foreground re-register, stale generations, Bundle-60 transfer, sentinel/menu bypass, and unbounded diagnostics. `git diff --check` passed.
- CI compiled and linked the complete arm64 engine plus Half-Life, Diffusion client/server/menu, SDL, and GL4ES targets and passed the IPA contract and artifact steps.
- Independent artifact readback verified `CFBundleVersion=69`, `CFBundleExecutable=xash`, thin 64-bit Mach-O arm64 headers for `xash`, `libref_gl4es.dylib`, and the client/server/menu modules, the embedded direct-drawable marker families, exact size, and SHA-256. Tempfile server-side readback matched the local hash and size.

Expected log markers:

```text
iOS direct drawable policy:
iOS direct drawable register:
iOS direct drawable logical-zero:
iOS direct drawable present:
iOS direct drawable lifecycle:
iOS direct drawable proof:
```

The policy must report `requested_samples=0 effective_samples=0 msaa_objects=0 resolve=disabled transfer=none`; registration and logical-zero records must identify the dynamic live nonzero view FBO and show logical/native agreement plus completeness; present must report `resolve=0 transfer=0 one_present=1`; bounded proof samples are two menu and three active-map samples with a hard maximum of 32 records and must show a checksum change from the menu baseline by first active `ch1map0` frames.

Remaining risks: this build is not device-accepted. Direct rendering intentionally trades the device's previous effective 4x MSAA for one-owner presentation and may expose aliasing. A device-only EAGL lifecycle race, resize-generation mismatch, or un-audited logical-zero helper could still violate the contract. The checksum/visible-scene acceptance condition remains unproven until orchestrator-authorized evidence. The known later `ch1map0` to `ch1map1` termination and `glUniform4fv` active-extent issue are unchanged and outside Work Order 46 Phase B.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit. Its exact hash is recorded in the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 46 Phase B implementation, structural/rejection validation, one qualifying bundle-69 candidate, one retained artifact, independent IPA verification, one confirmed tempfile.org publication, and both ledger reports are complete. Stop for orchestrator review. Do not contact Arjun, request evidence/logs/device testing, diagnose a future run, implement another renderer/gameplay change, or begin another phase or work order.

## Work Order 47 Phase A - corrupt 3-D output and transition-crash source audit

Candidate/run and acceptance status: **audit-only; Track-A Outcome B selected; no candidate and no device acceptance**. Bundle 69 is accepted only as the direct-drawable presentation baseline: it proves that live `ch1map0` pixels reach the CAEAGLLayer, but its corrupt scene is not playable. Run 39 remains the generally accepted device baseline. This phase changes no renderer, engine, GL4ES, SDL, Diffusion, menu, gameplay, patch, script, or workflow behavior. It creates no build, workflow, artifact, IPA, upload, runtime marker, evidence request, or device-test request.

### Authoritative inputs and exact sources

- Repository audit head and remote branch before this report: `846e52fc3e02a119bc156556c512cf3ca00898a9`; Bundle-69 candidate head: `4caad99dbb7e0fdaed050dd21fad2095655ce6b0`; direct-drawable behavioral commit: `93881a0513c648ec5d20d1f96efb8f8a03347c00`.
- Exact pins: Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`; MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`; engine executable `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`; SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`; GL4ES `81547d986798e876de8b434193920b606a72363f`.
- The final pre-report Google Docs readback remained at revision `AIroW36Lm_OtVWnwZYqJPCf0rWKi99CS_3uh2Fz73HwgrW3ng48sHdYlnZYqsl6ZTNnSwEZJH7P21cSPO3hOJmDkO8ZftYZiOpxs69ESYyc`. No complete Bundle-69 log or matching `.ips` had been appended. The authoritative device evidence is therefore the recorded Bundle-69 observation: live cutscene after about 20-30 seconds, stretched/exploded/duplicated/disconnected ribbon geometry, flickering or disappearing surfaces and textures, a mix of plausible and flat/incorrect materials, continued cutscene/audio, then a brief loading screen and hard termination at the later `ch1map0` to `ch1map1` boundary.
- The archived source-correlating device log available to this worker is `engine(20260811-181200).log`, 1,598 lines, 63,442 bytes, SHA-256 `5F7BFDDE516FC2A26D74220FCFA8AB660A5E748AA941E0FE925F467BD2B6ABE2`. It proves native `GL4ES_VERSION: OpenGL ES 3.0 Metal - 104.1`, a native extension list with no `GL_OES_element_index_uint`, 2,732 `ch1map0` surfaces, and loaded vertex-light data including 112,981 vertices for `truck_new.mdl` and 139,508 for `cars_pack.mdl`. Those model totals do not by themselves prove that one studio mesh has an index above 65,535; they do prove that Diffusion intentionally operates beyond a global 16-bit model-vertex budget.
- Codebase Memory graph discovery and call tracing preceded direct source inspection. Material findings were checked in the repository and exact pinned/applied trees, including `scripts/ios/gl4es-ios.patch`, `3rdparty/gl4es/wscript`, pinned GL4ES `src/glx/hardext.c`, `src/gl/drawing.c`, `src/gl/array.c`, `src/gl/uniform.c`, `src/gl/fpe.c`, and framebuffer/VAO code; Diffusion `client/render/{r_world.cpp,r_world.h,r_studio.cpp,r_studio.h,r_studiodecal.cpp,r_main.cpp,r_shader.cpp}`, `glsl/bmodelsolid_{vp,fp}.glsl`, and the generated iOS patch; regular renderer `ref/gl/gl_rsurf.c`; engine transition, client, model, sound, and host-state sources; and Diffusion changelevel/world/video-init sources.

### Track A evidence matrix

| Observed symptom | Audited path and invariant | Source finding | Classification |
| --- | --- | --- | --- |
| Stretched, exploded, duplicated, disconnected ribbon triangles | Diffusion world/studio `GL_UNSIGNED_INT` element buffers -> GL4ES draw translation -> native GLES 3 draw. Explicit 32-bit indices must reach a native ES3 context without narrowing. | The iOS build fixes `DEFAULT_ES=2` even though the live context reports ES3. `GetHardwareExtensions` recognizes core ES3 NPOT via the native version string in `scripts/ios/gl4es-ios.patch`, but pinned `hardext.c:332` sets `hardext.elementuint` only when the legacy `GL_OES_element_index_uint` string exists. That string is absent. Every non-intercepted uint draw therefore takes `copy_gl_array(... GL_UNSIGNED_INT ... GL_UNSIGNED_SHORT ...)`; `copy_gl_array` assigns each `GLuint` to `GLushort` without a range check or split. Values at and above 65,536 wrap to unrelated low vertices, which produces exactly long ribbon triangles rather than a blank draw. | **Primary, Outcome B.** This is the earliest source-level contract violation. |
| Large surfaces/textures flicker or disappear while some geometry remains plausible | `R_DrawBrushList`, dynamic-light and shadow lists rebuild visible batches each frame from absolute `firstvertex + local index` values into the monolithic world VBO. | `r_world.cpp` stores `tempElems` as `unsigned int`, tracks absolute `startv/endv`, and calls `pglDrawRangeElementsEXT(... GL_UNSIGNED_INT, tempElems)`. `world->numvertexes` is the sum of every surface edge/subdivision and is not constrained by the BSP source-lump `MAX_MAP_VERTS=65535`; the latter only sizes a scratch element budget (`MAX_MAP_ELEMS=MAX_MAP_VERTS*5`). Once narrowed, different visibility/material batches wrap different high absolute vertices onto low geometry, so appearance changes with the draw lists while low indices can remain correct. | **Primary B symptom match.** |
| Studio/vertex-lit scene is affected alongside world geometry | `MeshCreateBuffer` -> uint EBO -> `DrawMeshFromBuffer`. | Diffusion allocates `MAXARRAYVERTS=320000`, stores `unsigned int m_arrayelems`, uploads `sizeof(unsigned int)`, and draws each mesh as `GL_UNSIGNED_INT`; studio decals do the same. The 139,508 log record is a per-model accumulated vertex-light total, not proof that one mesh exceeds 65,535, so the report does not use it as a standalone causal proof. It does establish that a 16-bit-only wrapper policy is incompatible with the renderer's designed capacity. | **Supports B; per-mesh magnitude remains a rejection-fixture requirement.** |
| Regular Half-Life renderer is the working differential | Regular renderer VBO generation and index type. | `ref/gl/gl_rsurf.c:1972-1977` defaults to `unsigned short vboindex_t`, `VBOINDEX_MAX=USHRT_MAX`, and `GL_UNSIGNED_SHORT`. `R_GenerateVBO` explicitly closes an array and starts another when `array_len + surface vertices` would exceed `VBOINDEX_MAX` (`:2184`, `:2252`). It therefore never depends on the custom renderer's unsatisfied 32-bit-element contract. | **Explains custom-renderer-only failure; rejects blaming all GL4ES draws generically.** |
| Plausible textures/colors mixed with flat or incorrect material output; every audited frame has `0x0502` | Diffusion `R_DrawBrushList` -> `glUniform4fv(count=3)` -> GL4ES uniform reflection/cache/upload. | Shaders declare `u_BrushParams[3]`, but translated variants reflect only active extent 1 or 2. `GoUniformfv` rejects `count > m->size` with `GL_INVALID_OPERATION` before either cache copy or native upload. Element 0 controls fog, element 1 view origin/wave height, and element 2 underwater state. It can leave fog, reflection/view-vector, water, and underwater material parameters stale, but normal vertex position uses the independent model and MVP matrices; the rejected call cannot fabricate disconnected triangle topology. | **Real, causal only for narrower material/water defects; secondary after B.** |
| Possible transform, bone-array, location-remap, or matrix-transpose error | `R_SetupGL`/`R_RestoreGLState`, GL4ES FPE realization, linked uniforms, studio bones. | Diffusion builds and loads projection/modelview matrices through count-one matrix calls; explicit model matrices are count one with transpose false. GL4ES realizes built-in modelview/MVP/texture matrices and per-attribute size/type/normalization/stride plus real VBO identity. The shared animated layout uploads no more than the fixed 128-bone arrays proven by Run 41. No exact source path was found that transposes, overruns, or cross-program-remaps these values. | **Rejected as earliest cause.** |
| Possible stale EBO/VAO or cross-program state cache | VAO binding, `glDrawElementsCommon`, FPE element-buffer realization, renderer restoration. | The apparent stale-EBO hypothesis does not survive exact inspection: GLES2+/3 draws go through `fpe_glDrawElements`; it binds the real logical EBO when one exists and `realize_bufferIndex()` restores the desired zero index buffer for client-index draws. Diffusion restores viewport, projection/modelview, depth test/write, blend and cull at renderer handoff, and individual passes bind their programs, textures and buffers. No earlier state-cache violation with the screenshot's topology signature was found. | **Outcome C rejected.** |
| Live scene now reaches the screen after Bundle 69 | Direct-drawable implementation diff and accepted device gate. | Commit `93881a05` changes framebuffer-zero ownership, SDL drawable identity/lifecycle, zero-MSAA policy and presentation validation. It does not rewrite shaders, transforms, vertex layouts, element buffers, indices, VAO semantics, textures, or materials. Bundle 69 proves the destination FBO/presentation contract. | **Outcome D rejected; direct mapping must be preserved.** |
| About 20-30 seconds on the difficulty image before live 3-D | Shader compilation, texture decompression/upload, vertex-light cache and foliage construction. | Prior complete logs show finite forward progress through synchronous shader compilation and large model/foliage/cache construction, followed by active frames. No loop or retry path was found that makes the interval an indefinite deadlock. | **Bounded synchronous initialization; no optimization authorized.** |

### Track A decision and earliest violated invariant

**Selected outcome: B - source-supported vertex/index translation failure.** The earliest violated invariant is independent of any particular draw's maximum value: when the native context is OpenGL ES 3, a caller-supplied `GL_UNSIGNED_INT` element stream must remain 32-bit through wrapper capability discovery and draw submission. The current iOS GL4ES profile recognizes the native context as ES3 for core NPOT, yet leaves `hardext.elementuint` false solely because ES3 correctly omits the obsolete extension token. Pinned `gl4es_glDrawRangeElements` (`drawing.c:457-556`), `gl4es_glDrawElements` (`:561-666`) and the corresponding base-vertex, instanced and multidraw paths then narrow uint elements to ushort. Pinned `copy_gl_array` (`array.c:13-81`) performs the lossy assignment with no overflow check. The custom renderer deliberately emits uint absolute world indices and uint studio/decal EBOs; the regular renderer avoids this contract by splitting ushort arrays.

This finding explains the topology signature and the working differential without rolling back accepted presentation work or disabling complex models, foliage, materials, lighting, world surfaces, or the menu. The exact first offending Bundle-69 element value is not available because the complete Bundle-69 log was not in the authoritative ledger and Phase A cannot add instrumentation. That evidence limitation is retained: the causal claim rests on the proven wrapper invariant violation, the custom renderer's high-capacity uint design, the low-index-preserving/high-index-wrapping symptom signature, and the regular path's explicit 16-bit split—not on an invented per-mesh number.

The known `glUniform4fv` mismatch is **secondary and independently causal for material parameters**, not the structural cause of exploded geometry. `GoUniformfv` rejects before cache mutation, so it cannot corrupt adjacent uniforms. `u_BrushParams[0]` affects fog, `[1]` affects view origin and water wave height, and `[2]` affects underwater fragment behavior. A later repair must address it independently after the element-width invariant; combining both would destroy the ability to reject a partial fix.

### Minimum coherent future rendering boundary - defined, not implemented

No Phase B is started or authorized here. If an implementation phase is later authorized, the smallest structural boundary is:

1. In the exact pinned GL4ES capability discovery plus `scripts/ios/gl4es-ios.patch`, derive uint-element support from the live native context: native OpenGL ES 3.x enables `hardext.elementuint` as a core feature even when `GL_OES_element_index_uint` is absent; ES2 continues to require the extension. Because this project compiles GL4ES with `DEFAULT_ES=2` while SDL supplies an ES3 context, the check must use the already-read native `GL_VERSION`/equivalent live capability, not merely `hardext.esversion`.
2. Audit all element draw entry points—ordinary and range draws, base-vertex, instanced, multidraw, render-list/intercept routes, client pointers, and EBO offsets—so a supported native ES3 uint stream is never narrowed, copied into a ushort list, or submitted with the wrong type. If an intercept/render-list route cannot preserve uint, it must retain a source-proven non-lossy strategy; silently narrowing is forbidden.
3. Preserve Diffusion's uint world, studio and decal semantics and regular Half-Life's existing ushort split. Do not add a one-off `ch1map0` clamp, model exclusion, feature disable, hard-coded mesh split, or direct-drawable/MSAA/FBO change.
4. Keep the separate `u_BrushParams` active-extent contract outside this first topology repair and outside its acceptance gate.

Required rejection fixtures for any such later implementation:

- A mocked native ES3 context whose extension list omits `GL_OES_element_index_uint`; uint values `65535, 65536, 65537, 100000` must reach the native draw unchanged and with type `GL_UNSIGNED_INT`.
- ES2 without the extension must not falsely issue unsupported uint draws; ES2 with the extension must preserve uint.
- Client-index and EBO-offset paths must agree. Range, ordinary, base-vertex, instanced and multidraw entry points must all preserve the capability contract; a public-`glDrawElements`-only patch must fail validation.
- A Diffusion world fixture with absolute generated vertices above 65,535 and a studio-mesh fixture above 65,535 must preserve exact triangle indices; a fixture using only low indices must remain identical.
- The regular renderer's ushort array splitting must remain unchanged.
- Direct-drawable logical-zero mapping, zero-MSAA presentation, real menu/touch/audio/gameplay paths, shader/material/model features, and all accepted Run-39/Bundle-69 presentation behavior must remain enabled.

### Track B - independent cutscene-end/map-transition termination

The complete source path is:

```text
Diffusion CChangeLevel::ChangeLevelNow
  -> engine pfnChangeLevel / SV_QueueChangeLevel
  -> COM_ChangeLevel records ch1map1 + landmark to_map1
  -> COM_Frame STATE_CHANGELEVEL -> SV_ExecChangeLevel -> SV_ChangeLevel
  -> SaveGameState(true)
  -> SV_InactivateClients -> SV_FinalMessage -> SV_DeactivateServer
     -> game DLL ServerDeactivate, edict/physics/string cleanup
  -> SV_SpawnServer(ch1map1, to_map1)
     -> client slots/state, new BSP/world/model/collision and renderer data
  -> SaveFinish
  -> LoadGameState(ch1map1, true)
     -> missing save returns false
  -> normal fallback SV_SpawnEntities(ch1map1)
  -> LoadAdjacentEnts(ch1map0, to_map1)
  -> SV_ActivateServer(false)
     -> game DLL ServerActivate -> generic resources -> one settle frame
     -> baselines -> resource/consistency lists -> expected "Game started"
  -> local client svc_changing/serverdata/resource registration
     -> S_StopAllSounds / CL_ClearState as applicable
     -> client VidInit, renderer world release/recreate, R_NewMap
     -> new-map signon and active frame
```

The transition is not a single renderer call. `SV_DeactivateServer` runs the game DLL deactivation and releases server edicts, physics entities, strings and client frames. The client changing path stops channels and clears resource/effect/edict state; `CL_RegisterResources` installs the new world, clears the old renderer world, sets sky, calls `R_NewMap`, loads detail textures and frees unused models. Diffusion's renderer frees and recreates per-world cubemaps, world vertex/VBO/VAO, foliage, landscape, custom-FBO/postprocess and studio-video resources through its world-processing and video-init callbacks. Sound teardown (`S_StopAllSounds`) frees active channels, clears DSP/buffers, and rebuilds ambient channels. These owners were traced, but source alone does not prove a double free, use-after-free, resource leak, audio fault, or deliberate fatal path.

The missing `save/ch1map1.HL1` remains a handled fallback, not a cause: `LoadGameState` returns false and `SV_ChangeLevel` immediately calls `SV_SpawnEntities`. The strongest exact archived transition evidence remains the prior complete diagnostic log: it reaches `Spawn Server: ch1map1 [to_map1]`, reports 242 packed normals and eight cubemap boxes, returns from the missing-save read, and reaches both `ch1map0_unload.cfg` and `ch1map1_load.cfg` execution before EOF. It does not prove return from fallback `SV_SpawnEntities`, `LoadAdjacentEnts`, `SV_ActivateServer`, or a new `Game started`. Bundle 69 adds the lower-resolution behavioral fact that the cutscene completed, a loading screen appeared for about one or two seconds, and the app hard-terminated; without its complete engine log or `.ips`, it cannot move the exact function boundary.

Track-B terminal classification is therefore **unresolved**. Exception/crash, assertion, deliberate `Host_Error`, iOS watchdog, and jetsam remain separate. A complete Bundle-69 engine log could distinguish an engine fatal/assert marker and the last activation stage; a timestamp-matched `.ips` is the decisive minimum discriminator for exception type or termination reason, crashed thread/backtrace, watchdog/jetsam classification, memory footprint, and loaded images. This report identifies that gap but does not contact Arjun, request the files, or authorize instrumentation or testing.

The two tracks must remain separate. The index-width defect acts continuously in live `ch1map0` draw submission and matches the corrupt topology while the cutscene/audio continue. The later termination occurs only after changelevel begins and crosses save, server, world/resource, client and audio ownership boundaries. Fixing topology cannot establish server activation, and changing transition ownership cannot repair per-frame triangle indices. Their future rejection and acceptance gates therefore cannot be bundled.

### Validation, risks, durable state, and stop gate

Validation performed: Codebase Memory graph architecture/search/trace/snippet tools were used first; every material claim was then verified against direct exact source. Repository/remote heads and all pins were checked. The archived log's ES3 version, extension absence, map surface count and large vertex-light totals were reproduced with line-numbered `Select-String`; the file line count, size and SHA-256 were checked. GL4ES capability discovery, every draw family, lossy conversion, FPE EBO realization and uniform rejection were audited. Diffusion world/studio/decal generation and draw calls, transform/attribute/state restoration, regular-renderer ushort splitting, direct-drawable commit scope, and full transition/resource/audio paths were inspected. The authoritative Google Doc was re-read immediately before this report and contained no new Bundle-69 file evidence. Publication requires `git diff --check`, documentation-only changed-file inspection, `[skip ci]` commit/push, remote-head verification, and readback of both ledgers. No compilation, build, workflow, IPA, upload or runtime test is warranted or allowed.

Exact files changed by Work Order 47 Phase A: `Documentation/XASH3DIOS_PORTING_STATE.md` only.

Expected new log markers: none. Phase A is documentation-only.

Workflow/artifact/IPA/tempfile/SHA-256: none created or used; all are forbidden by this phase.

Remaining risks: the exact first Bundle-69 index above 65,535 is not logged, so any future implementation must include the high-index rejection fixtures and retain a bounded proof rather than infer success from compilation. GL4ES render-list/intercept paths contain separate uint TODOs and must not be overlooked. The secondary uniform defect can still leave material/water output wrong after topology is repaired. Startup remains synchronous and potentially slow. Track B remains OS-mechanism-unknown and source-bounded before proven new-server activation. None of these risks authorizes a patch, build, or test in Phase A.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit. Its exact hash is recorded in the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 47 Phase A ends at **Track-A Outcome B** and **Track-B unresolved evidence gap** for orchestrator review. Do not implement either repair, modify code, build, start a workflow, create/retrieve/upload an IPA, use tempfile.org, contact Arjun, request evidence or testing, begin Phase B, or create another work order.

## Work Order 47 Phase B - Bundle 71 native-ES3 32-bit element-index repair

Candidate/run and acceptance status: **Bundle 71 is build-qualified and awaiting orchestrator review; it is not device-accepted.** The candidate preserves Bundle 69's direct-drawable logical-zero mapping and zero-MSAA presentation architecture. Work Order 47 Phase B addresses only the proven element-index topology boundary. It does not change `glUniform4fv`/`u_BrushParams`, startup behavior, or the later `ch1map0` to `ch1map1` termination.

### Commits, workflow, and artifacts

- Behavioral and final build commit: `cc87b9ab09501ef3e7ace571786535707d54948e` (`fix(ios): preserve uint element indices on native ES3`). Exact GL4ES pin: `81547d986798e876de8b434193920b606a72363f`.
- Sole qualifying workflow: GitHub Actions run `31872797997`, bundle/run number `71`, `push`, successful, head `cc87b9ab09501ef3e7ace571786535707d54948e`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31872797997`. Job `94983900217` completed every step successfully.
- The automatic pull-request duplicate, run `31872799390` / number `72`, was cancelled immediately and produced no retained candidate. It is not Bundle 71 and is not offered for testing.
- Retained GitHub artifact: `Xash3DiOS-arm64-unsigned`, artifact ID `9243950326`, archive size `8,564,939` bytes, digest `sha256:58442bf8af7977a9b635bf0882dc1037ef5d3d32bbb55f53a9db1b475a4722af`, expires `2026-08-29T07:51:31Z`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31872797997/artifacts/9243950326`.
- Verified IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,662,214` bytes, SHA-256 `1A0DBE078050B853EB9C5E5A4A31972B6A07C3C376063C616EA43BA4DCEAC8B5`.
- One and only one tempfile.org upload of that verified byte-identical IPA: information page `https://tempfile.org/qDJUk1VciLj/`; direct download `https://tempfile.org/qDJUk1VciLj/download`; expiry `2026-08-17 08:16:18 UTC`. Tempfile metadata reports `8,662,214` bytes and a safe scan; its server-side SHA-256 equals the independently calculated IPA hash.

### Exact files changed by the behavioral candidate

- `.gitattributes`
- `scripts/gha/build_ios.sh`
- `scripts/ios/gl4es-uint-elements-ios.patch`
- `scripts/ios/validate-ios-uint-elements.py`
- `scripts/ios/verify_ipa.sh`

The subsequent durable-ledger publication changes only `Documentation/XASH3DIOS_PORTING_STATE.md`, uses `[skip ci]`, and does not create another qualifying candidate. Its exact commit is recorded in the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash.

### Verified failure boundary and structural cause

The earliest violated invariant was the pinned iOS GL4ES wrapper, not Diffusion's index generation or Bundle 69's presentation path. SDL supplies a live OpenGL ES 3 context, but the GL4ES iOS profile is compiled with `DEFAULT_ES=2`. Capability discovery previously enabled `hardext.elementuint` only when the legacy `GL_OES_element_index_uint` extension token appeared. Native ES3 exposes 32-bit element indices as core and need not advertise that ES2-era token, so `hardext.elementuint` remained false. Ordinary, range, base-vertex, instanced, multidraw, and intercept/render-list routes could then copy caller-supplied `GLuint` indices through `GLushort` storage. Values at and above 65,536 wrapped, matching Bundle 69's disconnected, stretched, exploded, and ribbon-like topology while low-index geometry and the direct drawable continued to work.

### Structural repair and complete route coverage

- `hardext.c` now parses the already-read live native `GL_VERSION`. Native ES 3.x enables uint elements as a core capability even without `GL_OES_element_index_uint`; ES2 still requires the extension. No unconditional enablement and no inference from compile-time `DEFAULT_ES` or stale wrapper profile state is used.
- Direct supported paths preserve `GL_UNSIGNED_INT` and the original client pointer or EBO byte offset. Unsupported ES2 paths never submit an unsupported native uint draw: they either take a proven non-lossy route or set `GL_INVALID_OPERATION` and reject before narrowing.
- `drawing.c` applies the same policy to ordinary, range, base-vertex, instanced, multidraw, intercept, client-index, and EBO-offset entry points. The audited multidraw intercept path also uses per-draw index sources/base vertices rather than a shadowed local source.
- Render-list/index accumulation is 32-bit end to end: list storage, append/merge, line and texgen helpers, GL state declarations, draw submission, and selection paths use `GLuint`. Native ES3 or supported ES2 submits `GL_UNSIGNED_INT`. An unsupported ES2 render list converts only after proving every value is at most 65,535; otherwise it rejects explicitly. No supported route copies through `GLushort`.
- Diffusion's existing uint world, studio, foliage, and decal semantics are unchanged. The regular Half-Life renderer's existing `GL_UNSIGNED_SHORT` split is unchanged. No map/model clamp, model exclusion, asset substitution, renderer disable, material shortcut, direct-drawable/FBO rollback, MSAA change, uniform change, or transition change was introduced.

### Validation and rejection results

- Exact pinned-source replay passed from clean trees: the existing base iOS GL4ES patch, Bundle 69 drawable bridge patch, and new uint-element patch all applied in order with `git apply --check` and then applied cleanly.
- The validator passed Python bytecode compilation and its full self-test. Positive fixtures prove exact values `65535`, `65536`, `65537`, and `100000` in ES3 without the legacy extension, ES2 with the extension, and all audited client/EBO, ordinary/range/base-vertex/instanced/multidraw/render-list/intercept routes. Diffusion world and studio semantic fixtures preserve high-index triangles; low-index semantics remain identical.
- Rejection fixtures fail closed for extension-only ES3 detection, unconditional capability enablement, any lossy `GLuint` to `GLushort` path, public-`glDrawElements`-only or otherwise incomplete route coverage, unsupported ES2 uint submission, marker removal, map/model-specific hacks, Bundle 69 direct-drawable/MSAA/FBO rollback, and bundled uniform or transition changes.
- `git diff --check` passed. The exact patched GL4ES source compiled all 70 translation units and linked successfully on the available MSVC toolchain. GitHub Actions repeated the policy/rejection validation, shader checks, exact patch application, and the complete arm64 engine plus Half-Life and Diffusion client/server/menu build.
- Independent IPA verification found bundle version `71`, minimum iOS `12.0`, executable `xash`, 13 Mach-O files and 11 dylibs. `xash`, `libref_gl4es.dylib`, and all Diffusion client/server/menu modules are thin 64-bit arm64. All four new uint-policy markers and all accepted Bundle 69 direct-drawable markers are present; legacy transfer/audit/sentinel markers are absent.

Expected bounded log markers:

```text
iOS uint element policy:
iOS uint element first use:
iOS uint element high index:
iOS uint element route summary:
```

The policy marker identifies the live native ES version and core-versus-extension decision. First-use/high-index/route-summary records are bounded and identify draw family, client-versus-EBO source, submitted type, and representative maximum index without per-frame flooding.

### Orchestrator-controlled acceptance gate, risks, and stop state

Single device test proposed **only for orchestrator approval; the worker has not contacted Arjun or requested a test**: install Bundle 71, use New Game -> Chapter 1 -> Medium, wait for live `ch1map0`, and judge only whether exploded, stretched, disconnected, or ribbon-like topology is gone. Preserve the complete `engine.log` for orchestrator review of the four bounded markers. Material/fog/water/color defects from the deliberately unchanged `u_BrushParams` mismatch and the later `ch1map1` termination are not failures of this topology gate.

Remaining risks: build and fixture evidence cannot establish device topology. Some material/water output may remain wrong because the known `glUniform4fv` active-extent mismatch is unchanged. Synchronous startup may remain slow. The later map transition may still terminate for its independently unresolved reason. The safe-rejection path for an actual ES2 device without the extension is intentionally fail-closed, not a claim that every uint workload can be rendered there.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. Behavioral candidate commit: `cc87b9ab09501ef3e7ace571786535707d54948e`. The exact documentation-only ledger commit is recorded in the authoritative Google Docs ledger and final handoff.

Stop state: Work Order 47 Phase B implementation, positive and rejection validation, exactly one qualifying successful Bundle 71 workflow, one retained GitHub artifact, independent IPA verification, exactly one tempfile.org upload, and both durable-ledger reports are complete. Stop for orchestrator review. Do not contact Arjun, request evidence or testing directly, claim device acceptance, implement the excluded uniform/transition/startup work, or begin another phase or work order.

## Work Order 48 Phase A - Bundle 71 failed-topology structural audit

Candidate/run and acceptance status: **audit-only; Outcome B selected; no candidate**. Bundle 71 is rejected at the device topology gate: all nine authoritative screenshots still show severe exploded, stretched, disconnected and ribbon-like scene geometry. It is build-qualified only and is not device-accepted. Bundle 69 remains the accepted direct-drawable presentation architecture, and Run 39 remains the accepted gameplay/menu baseline. This phase changes no engine, renderer, GL4ES, SDL, Diffusion, menu, gameplay, patch, validator, build or CI behavior. It creates no build, workflow, artifact, IPA, upload, marker, evidence request or device-test request.

### Authoritative evidence and audit inputs

- Repository and remote audit head before this report: `ce231df9662db97dc2355321d82fb58b0e679794`; Bundle-71 behavioral commit: `cc87b9ab09501ef3e7ace571786535707d54948e`; Bundle-69 direct-drawable candidate head: `4caad99dbb7e0fdaed050dd21fad2095655ce6b0`. Exact pins remain Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, GL4ES `81547d986798e876de8b434193920b606a72363f`, and Diffusion-MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`.
- The authoritative Google Docs ledger was read through its latest complete entry at revision `AIroW35rd_MdrfzT7yZ1Z6ItSAokSCds6hWEmObvjTBVnCS2WD19La4BWOrXmcDGIxKHnWz70PDqhIExwOdmU0vFUBNfMccaRN9NAP7roeo`, tab `t.0`, end index `284408`. Its nine screenshots and complete `engine(20260815-084517).log` findings are the device authority. The large video is not needed and no evidence was requested from Arjun.
- Authoritative log findings: no OOM, allocation failure, memory-pressure, Jetsam, texture eviction or failed texture-allocation record; the visible 20-30 second delay coincides with synchronous UberShader programs `#10` through `#59`, foliage generation and the render-gate opening; all four Bundle-71 uint markers are absent; material/capability warnings include `u_BrushParams` active extents of one or two with a three-`vec4` upload, absent texture arrays, absent `GL_EXT_gpu_shader4`, unavailable depth/shadow features, unsupported `depthCube`, and unsupported BC6H/BC7; transition processing reaches `Spawn Server: ch1map1 [to_map1]`, cubemap boxes, unload/load configuration, and StudioSolid/`CompileUberShader #60` before log EOF without a crash or memory discriminator.
- The retained Bundle-71 IPA was inspected without rebuilding it: `xash3d-fwgs-ios-arm64.ipa`, 8,662,214 bytes, SHA-256 `1a0dbe078050b853eb9c5e5a4a31972b6a07c3c376063c616ea43ba4dceac8b5`. Its extracted `xash` is 2,763,568 bytes, SHA-256 `9873f875893df11d30533f301215fcad1a45daf02d76aba2972e295a7d408ca0`; `bin/client_arm64.dylib` is 2,268,040 bytes, SHA-256 `2e99f788d3689c3dc16f2322e89b5ee31b763c3d585984ffe7a0c45a8679d527`; `libref_gl4es.dylib` is 1,721,096 bytes, SHA-256 `ead885e53373a12e40ea67c6c5a9a76aaecc9accc9f2bf91e38bdc23f91a8a6a`.
- Codebase Memory graph search, architecture, call tracing and function snippets preceded direct inspection of the repository and exact pinned/applied sources. The audit then covered Diffusion GL loading and all draw call sites, world/studio/decal vertex-index construction, VBO/VAO/EBO ownership, GL4ES lookup, capability discovery, draw translation, render lists, buffers, FPE/native submission, marker logging, uniform validation and feature fallbacks, plus the Bundle-71 binary's Mach-O ownership and marker strings.

### Track A - provenance, symbol ownership and the absent markers

The packaged call chain is structurally unambiguous:

```text
Diffusion client renderer
  R_InitExtensions / GL_CheckExtension
  -> gRenderfuncs.GL_GetProcAddress
  -> libref_gl4es R_GetProcAddress
  -> gl4es_GetProcAddress
  -> gl4es_glDrawRangeElements / gl4es_glDrawElements aliases
  -> GL4ES direct or render-list/intercept route
  -> native GLES glDrawElements obtained through GL4ES_GetProcAddress
  -> engine SDL_GL_GetProcAddress
```

`client/render/r_opengl.cpp` fills every `pgl*` slot only through `GL_GetProcAddress`, which is `gRenderfuncs.GL_GetProcAddress`. Under `XASH_GL4ES`, `ref/gl/gl_context.c:R_GetProcAddress` returns `gl4es_GetProcAddress(name)` rather than the engine's native resolver. The lookup table maps both core and `EXT` range names to `gl4es_glDrawRangeElements`, and ordinary draws to `gl4es_glDrawElements`. GL4ES's own native callback is separately installed by `ref/gl/gl_opengl.c` and reaches SDL only after wrapper translation.

The Bundle-71 Mach-O audit rejects a direct-native-GL bypass. `client_arm64.dylib` owns `gRenderfuncs` and the `pglDraw*` pointer variables but has no OpenGLES dependency or undefined direct GL draw import. `libref_gl4es.dylib` contains `R_GetProcAddress`, `GL4ES_GetProcAddress`, `gl4es_GetProcAddress`, `gl4es_glDrawRangeElements`, `gl4es_glDrawElements`, the other patched draw families, and `LogPrintf`; it has no direct OpenGLES framework dependency. The executable supplies the engine/SDL resolver. All four Bundle-71 marker strings are present in `libref_gl4es.dylib`. The behavioral commit and exact library hash therefore match the packaged wrapper; **Outcome C is rejected**.

The missing records do not prove that these symbols were bypassed. `scripts/ios/gl4es-uint-elements-ios.patch` emits the policy with `SHUT_LOGD` and the first-use/high-index/summary records with `LOGD`. On iOS, GL4ES `LogPrintf` writes `LIBGL: ` records with `printf`/`vprintf` to process stdout; it does not call the engine console logger used by `engine.log`. `SHUT_LOGD` is additionally suppressed when `LIBGL_NOBANNER` is active. As a reproducible cross-check, both archived device engine logs available to this worker contain `GL4ES_VERSION: OpenGL ES 3.0 Metal - 104.1` and extensive `CompileUberShader` activity but exactly zero lines beginning `LIBGL:` (139 and 41 engine-renderer evidence matches respectively). Thus all four missing Bundle-71 records share a sink mismatch; their absence cannot establish route inactivity, capability failure, or packaging failure.

### Track B - actual draw families, vertex/index pairing and Bundle 69 versus 71

Diffusion's affected renderer uses only two 32-bit entry families:

1. **World/brush client range route.** `r_world.cpp` builds a static `GLuint tempElems[MAX_MAP_ELEMS]` from absolute `mextrasurf_t::firstvertex` values. `R_DrawBrushList`, world dynamic-light lists and shadow lists bind `world->vertex_array_object`, whose attributes reference one monolithic `bvert_t` VBO, compute inclusive `startv`/`endv - 1`, and call `pglDrawRangeElementsEXT(GL_TRIANGLES, ..., GL_UNSIGNED_INT, tempElems)`. No element buffer is bound. The indices and range refer to the same absolute monolithic vertex space. The static client array remains valid for the synchronous direct call; any GL4ES deferred route copies it before return.
2. **Studio/decal routes.** Studio mesh creation uploads local `GLuint m_arrayelems` into a per-mesh EBO and pairs it with that mesh's VBO/VAO; draw uses range or ordinary `GL_UNSIGNED_INT` with byte offset zero. GL4ES retains a CPU mirror of the EBO as well as an optional native buffer, so its wrapper resolves the offset against the mirror before any client/deferred processing. Studio decals use client `GLuint` arrays paired with their generated client vertex arrays. Diffusion's other grass, weather and particle element calls are `GL_UNSIGNED_SHORT`. It does not call base-vertex, instanced or multidraw element APIs in this renderer.

Counts and modes are not silently reinterpreted on the affected path: all audited topology calls use triangles and counts generated as triangle multiples. Range normalization subtracts `start` only after the corresponding `[start, end]` vertex span is copied into a deferred list. Ordinary deferred draws normalize by the observed minimum and copy the matching vertex span. Render-list storage and native submission are 32-bit in Bundle 71. Default GL4ES initialization sets `maxbatch=0`, and this repository does not set `LIBGL_BATCH`; valid shader-backed triangle draws therefore select the direct route unless runtime state independently activates a list/intercept. The precise device subroute remains unlogged, which is one part of the Outcome-B discriminator.

Bundle 69's wrapper had a genuine lossy path: capability discovery could leave `hardext.elementuint` false on native ES3 without the legacy extension token, and deferred routes used 16-bit list storage. Bundle 71 corrects native-ES3 capability discovery and preserves uint storage/submission through every audited family. It does **not** change Diffusion index generation, vertex attributes, VAO/VBO pairing, draw counts, material selection or presentation. Because Bundle 71 produces the same severe topology, the old narrowing defect is not established as the complete active cause. The evidence permits three possibilities that cannot be distinguished from this `engine.log`: the affected draws never exceed 65,535; they traverse an unexpected runtime subroute/state pairing; or correct 32-bit submission exposes an independent vertex/index-state defect. Claiming any one now would be serial whack-a-mole.

The prior Work Order 47 cause is therefore reclassified as **a proven wrapper invariant defect but an unproven sole device cause**. It was reasonable to repair structurally, but Bundle 71's failed gate disproves device acceptance and requires a runtime pairing discriminator before another topology repair.

### Track C - material, capability and memory findings remain separate

- Diffusion always uploads three `vec4` values to `u_BrushParams`; translated programs report an active array extent of one or two. GL4ES `GoUniformfv` checks `count > m->size`, raises `GL_INVALID_OPERATION`, and returns before cache mutation or native upload. This can leave fog, view/wave or underwater material parameters stale, but it cannot overwrite adjacent uniform state or reconnect triangle indices. It is a real, separate material defect and not authorized for repair here.
- Missing `GL_EXT_texture_array` explicitly disables landscapes; missing `GL_EXT_gpu_shader4` disables omni-light shadows; absent depth/shadow support disables dynamic shadows; an unsupported depth cubemap disables that resource path. These are source-declared feature fallbacks. They can produce flat, missing or incorrectly lit materials but not exploded vertex connectivity.
- BC6H/BC7 upload returns false when BPTC support is absent. That can reject individual compressed textures, but the renderer contains no evidence that it changes element indices or vertex ownership.
- The authoritative log contains no OOM, allocation failure, memory-pressure, Jetsam, texture eviction or failed texture-allocation marker. Memory pressure is rejected as the present topology explanation. Texture/material warnings are not promoted to allocation failures.

### Track D - latency and transition boundary

The 20-30 second startup is forward progress, not a freeze: the log serially advances through at least 50 synchronous UberShader programs (`#10` through `#59`), foliage work and the render-gate opening. No topology conclusion follows from that compilation latency, and startup optimization remains a separate future track.

The later transition is also separate. The log reaches `Spawn Server: ch1map1 [to_map1]`, creates cubemap boxes, executes old-map unload/new-map load configuration, and advances to StudioSolid/`CompileUberShader #60` before ending. It provides no crash, assertion, watchdog, Jetsam or allocation discriminator. A timestamp-matched iOS incident report would distinguish exception/backtrace, watchdog and memory termination mechanisms, but this phase neither requests that evidence nor changes the transition path.

### Proof-gate decision - Outcome B

**Outcome B is selected: the active route is narrowed and packaging is proven, but one runtime discriminator is missing.** Outcome A is not established because no exact high index, direct/deferred choice, native element binding or submitted pointer/type pairing from an affected device draw reached `engine.log`. Outcome C is rejected by the binary ownership, exact hashes and embedded marker strings.

If and only if a later phase explicitly authorizes it, the single bounded diagnostics-only candidate must do all of the following without changing draw results:

1. Route records into the engine console sink, not GL4ES stdout. Install a small iOS-only GL4ES diagnostic callback from `libref_gl4es` to `gEngfuncs.Con_Printf`; do not change capability, indices, vertex data, draw order, error state or presentation.
2. Emit one ownership record after Diffusion resolves `glDrawRangeElements`, `glDrawRangeElementsEXT` and `glDrawElements`, including returned pointer and `dladdr` image/symbol, proving the live function owners.
3. Emit at most one first-use record for each affected world-client, studio-EBO and studio-decal-client family, plus the first high-index record and one final summary; hard cap all records at 16. Each record must contain route, direct/deferred/intercept state, mode/count, incoming type, start/end where applicable, client-versus-EBO source, EBO byte offset/CPU-mirror/native-buffer identity, input min/max, normalized min/max when copied, actual native submitted type and pointer-versus-offset, logical VAO, position-attribute buffer/stride/offset, and the copied vertex span. Do not call or consume `glGetError` for diagnostics.
4. Preserve Bundle 71's uint policy and Bundle 69's direct-drawable architecture byte-for-behavior. Rejection validation must fail marker-only stdout logging, per-draw flooding, missing client or EBO coverage, any index/vertex mutation, any material/uniform/startup/transition change, and any FBO/MSAA/presentation change.
5. The diagnostic interpretation is predetermined: `(a)` an affected maximum at or below 65,535 proves Bundle 71 was non-operative for that draw; `(b)` a high input that reaches native `GL_UNSIGNED_INT` with the matching vertex span proves the repaired invariant is active and shifts the next audit to vertex/VAO state without undoing it; `(c)` a mismatch between input, normalized or native submission identifies the exact missing route/state boundary. No screenshot-only success claim is allowed.

The explicit later-phase stop gate is: build and publish at most one diagnostics-only candidate only when separately authorized, append both ledgers, and stop for orchestrator review before contacting Arjun, requesting a device run, interpreting new evidence or implementing a renderer repair. This Work Order 48 Phase A does not authorize that candidate.

### Validation, report fields and stop state

Structural cause: **unresolved at the complete topology level**. Bundle 69's uint narrowing was real, but Bundle 71 proves it was incomplete, inactive for the affected index magnitudes, bypassed by runtime state, or accompanied by another vertex/index-state defect. The current evidence does not distinguish those branches. The absent markers are explained by their stdout sink, not by a proven route bypass.

Why this work satisfies Work Order 48 Phase A: it proves candidate provenance and wrapper ownership, traces every Diffusion 32-bit draw family through GL4ES to native GLES, pairs each index source with its vertex storage and lifetime, compares Bundle 69 and 71 at the changed invariant, rejects unsupported material/memory/latency/transition conflation, selects exactly one authorized proof-gate outcome, and specifies one bounded non-mutating discriminator for a later separately authorized phase.

Validation performed: Google Docs title/tab/revision/end-index verification and full latest-entry read; Codebase Memory-first architecture/search/call tracing; exact source and pin inspection; all Diffusion element-call enumeration; world/studio/decal construction and lifetime audit; GL4ES direct/deferred/intercept/render-list/capability/buffer/FPE/native-submission audit; uniform and feature-fallback inspection; Bundle-69/71 patch comparison; retained IPA size/hash readback; extracted Mach-O dependency/symbol/marker inspection; and two archived engine-log sink cross-checks. Publication validation additionally requires `git diff --check`, documentation-only changed-file inspection, `[skip ci]` commit/push, remote-head verification, clean worktree verification, and readback of both durable ledgers.

Workflow URL/ID and result: none; forbidden. Artifact/IPA/upload: none created, retrieved, published or uploaded; forbidden. The retained Bundle-71 IPA was read only for provenance. Tempfile.org was not used.

Expected new log markers: none. This phase is documentation-only. The future diagnostic names above are a boundary specification, not implemented markers.

Exact files changed by Work Order 48 Phase A: `Documentation/XASH3DIOS_PORTING_STATE.md` only.

Remaining risks: the device's exact world/studio maximum indices and direct/deferred state remain unknown; correct uint submission may coexist with a VAO/attribute/buffer-state defect; the uniform active-extent mismatch can independently corrupt material appearance; capability fallbacks can hide content; synchronous shader compilation remains slow; and the later map-transition termination mechanism remains unresolved. None authorizes another patch or test in this phase.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit. Its exact hash is recorded in the authoritative Google Docs mirror and final handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 48 Phase A ends at **Outcome B** for orchestrator review. Treat Bundle 71 as a failed topology candidate. Do not modify code, build, start a workflow, create/retrieve/upload an IPA, use tempfile.org, contact Arjun, request evidence or a device test, implement the bounded diagnostic candidate, repair topology/material/startup/transition behavior, or begin another phase or work order.

## Work Order 48 Phase B - Bundle 75 bounded ingress-to-native index-stream pairing

Candidate/run and acceptance status: **Bundle 75 is build-qualified diagnostics-only and awaiting orchestrator review; it is not device-accepted.** Bundle 71 remains rejected at the topology gate. Bundle 69's direct-drawable zero-MSAA presentation architecture and Bundle 71's native-ES3 uint-element repair are preserved byte-for-behavior. This candidate makes no gameplay, renderer-output, index, vertex, VAO/VBO/EBO, shader, material, uniform, texture, startup, transition, framebuffer, MSAA, presentation, menu, touch, audio, launch-argument, map, model or asset repair.

### Commits, workflows, retained artifact and tempfile publication

- Diagnostics implementation commit: `0c75669d892944ff2b49ee8da360f8e8905cf01c` (`diag(ios): pair index streams through native draw`). Final candidate commit: `ac0b030fb672630ce76e765176dcee63ddd4417e` (`fix(ios): preserve drawable validation ordering`). The second commit only places logger install/clear outside the exact ordering strings enforced by the accepted direct-drawable validator; it does not alter runtime order relative to context initialization or destruction.
- Retained qualifying workflow: GitHub Actions `push` run `31883710344`, bundle/run number `75`, successful, head `ac0b030fb672630ce76e765176dcee63ddd4417e`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31883710344`. Job `95009746716` completed build, IPA verification and artifact upload successfully.
- The first push run `31882507292` / bundle 73 failed before compilation because the accepted drawable validator requires literal adjacency around `initialize_gl4es` and `close_gl4es`; its automatic PR twin `31882509829` also completed without an accepted candidate. The final automatic PR twin `31883711515` / bundle 76 completed before cancellation could be issued. Its artifact `9246745059` was immediately deleted and readback confirms zero retained artifacts. It is not offered as a candidate. Only Bundle 75 is retained.
- Retained GitHub artifact: `Xash3DiOS-arm64-unsigned`, artifact ID `9246753251`, archive size `8,571,751` bytes, digest `sha256:786d4f92c23263bf7d122f79263bfa4eef70372eb1b59730b3c988f6ecaa69ee`, expires `2026-08-29T12:12:02Z`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31883710344/artifacts/9246753251`.
- Verified IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,668,802` bytes, SHA-256 `97F931D4EA889BDEF66D6052B2FE4F259C28873CF5858FD357AF24F7E6203311`.
- Exactly one tempfile.org upload: information page `https://tempfile.org/ZNvLN9dyzMC/`; direct download `https://tempfile.org/ZNvLN9dyzMC/download`; expiry `2026-08-17 12:22:51 UTC`. Tempfile metadata reports the same filename and size, no security warning, and the downloaded server readback has the exact local SHA-256 above.

### Exact files changed

- `ref/gl/gl_context.c`: records the three Diffusion-resolved draw entry pointers and their `dladdr` image/symbol ownership in one engine-console line. Diffusion's source-supported core-to-EXT alias is queried only for ownership when the client aliases EXT locally.
- `ref/gl/gl_opengl.c`: installs and clears a bounded, guarded `libref_gl4es` diagnostic callback that writes complete fixed-buffer records through `gEngfuncs.Con_Printf` into `engine.log`.
- `ref/gl/gl_rmain.c`: supplies copied frame/map/phase context immediately before the custom Diffusion renderer callback.
- `scripts/ios/gl4es-index-trace-ios.patch`: adds the fixed-cap trace implementation to the exact GL4ES pin; samples affected wrapper ingress, direct/intercept/deferred capture, render-list append/merge identity, and native egress without modifying submitted rendering data or GL state.
- `scripts/ios/validate-ios-index-trace.py`: enforces positive coverage and rejects stdout-only logging, flooding, missing families, lost IDs, missing deferred/replay/append coverage, allocations, error-queue changes, index mutation, uniform/material expansion and drawable/FBO/MSAA/presentation changes.
- `scripts/gha/build_ios.sh`: applies the trace patch after the unchanged Bundle-71 uint patch and runs its self-test validator.
- `scripts/ios/verify_ipa.sh`: requires all eight index-trace marker families in the packaged renderer.
- `Documentation/XASH3DIOS_PORTING_STATE.md`: this durable worker report only in the following documentation-only `[skip ci]` commit.

### Verified failure boundary and unresolved structural cause

Run/Bundle 71 proved that severe exploded, stretched, disconnected and ribbon-like topology survives the structural uint-element repair. Phase A proved that Diffusion's world-client range draws, studio EBO draws and studio-decal client draws resolve through packaged `libref_gl4es`, but Bundle-71 diagnostics wrote only to process stdout and therefore did not reach `engine.log`. The exact live affected maximum index, direct/deferred/intercept selection, native element binding/pointer pairing, normalized copy, render-list replay and position-buffer/VAO pairing remained unobserved. The complete topology cause therefore remains **unresolved**; this candidate does not promote the suspected direct studio-EBO pointer/offset pairing or any other branch into a repair without device evidence.

The new invariant is a monotonic trace ID created at every affected uint wrapper ingress. A maximum of five sampled IDs covers the first use of each of the three source-supported families, the first high index and the first deferred/intercept route. For each sample, the logger records mode/count/type/range/base, client versus EBO source, logical and native EBO identities, offset or pointer, CPU-mirror-valid min/max and FNV-1a checksum, logical VAO, position attribute enable/type/component count/stride/offset/logical/native buffer/size/highest legal vertex, copied vertex span and normalized data. Deferred/render-list fields preserve the originating ID and segment through append/merge and native replay. Native records compare width, count, min/max, checksum, offset/base/range, EBO/client semantics and vertex pairing. The first mismatch emits exactly one `first divergence`; matching high data proves Bundle 71 active; a completed 64-ingress window emits one covered/uncovered summary.

### Why this satisfies Work Order 48 Phase B without changing rendering

The logging bridge is iOS+GL4ES-only, formats into a fixed 1,024-byte stack buffer, uses no diagnostic allocation, has a reentrancy guard, copies map/phase text, retains no game pointer, does not call `glGetError`, and never changes error-queue semantics or GL state. Trace computation reads wrapper-owned CPU mirrors or live client data only inside the synchronous ingress/native call. `renderlist_t` receives three diagnostics-only scalar fields; they do not participate in compatibility, batching, transforms, storage, draw order or submission. All added native hooks execute immediately before the pre-existing draw with the same arguments.

The GL4ES logger reserves 15 lines and the engine ownership record is exactly one line, proving a hard global maximum of 16 records. Silent counters continue only through the 64-ingress window. The exact SHA-256 values of `gl4es-uint-elements-ios.patch`, `gl4es-drawable-bridge-ios.patch` and `sdl2-drawable-bridge-ios.patch` remain respectively `57CBB4B8899EB182A71BEE9E9FBA1FE29334E541B3AEB4CB4BA6EE327DF5F5FE`, `F9E521FABF164801341C222ED802F2BE24439B4E526094F122997CA147485CB1` and `49B867A0F01B488E7BF6A85575B0363E6D1325CAC1EF0249E2B421A0E13F7826`.

### Validation performed

- The latest authoritative Google Docs entry and complete repository ledger were read before modification. Codebase Memory graph search, call tracing and source snippets preceded direct inspection of `R_GetProcAddress`, `GL4ES_GetProcAddress`, `R_RenderFrame`, `Con_Printf`, exact applied GL4ES sources and every affected Diffusion draw family.
- Exact pin replay passed from clean GL4ES `81547d986798e876de8b434193920b606a72363f`: base iOS patch, Bundle-69 drawable patch, unchanged Bundle-71 uint patch and new trace patch each passed `git apply --check` and applied in order.
- `validate-ios-index-trace.py` passed Python bytecode compilation, positive validation and all mutation/rejection self-tests. Existing uint and direct-drawable validators passed their complete positive and rejection suites. `git diff --check` passed.
- CI compiled and linked the full arm64 engine, Half-Life, Diffusion client/server/menu, SDL and GL4ES targets; all workflow policy validators, shader validation, IPA contract checks and artifact upload steps passed.
- Independent artifact readback verified `CFBundleVersion=75`, `CFBundleExecutable=xash`, minimum iOS `12.0`, 163 packaged files, 11 dylibs, and thin 64-bit arm64 Mach-O headers for `xash`, `libref_gl4es.dylib` and Diffusion client/server/menu. All eight trace markers are embedded in `libref_gl4es.dylib`. Local artifact and tempfile readback size/hash match exactly.

Expected bounded `engine.log` markers:

```text
iOS index trace logger:
iOS index trace policy:
iOS index trace ownership:
iOS index trace ingress:
iOS index trace deferred:
iOS index trace native:
iOS index trace first divergence:
iOS index trace summary:
```

Remaining risks: Bundle 75 has not been run on device, so it cannot yet identify the first live divergence or prove a matching high-index submission. A bounded window may not encounter studio decals or a high index; the summary reports either gap explicitly. If every sampled maximum is at or below 65,535, Bundle 71 was non-operative for those samples. If high data reaches native `GL_UNSIGNED_INT` with matching count/checksum/span and no mismatch, the next authorized audit boundary is vertex/VAO state, not an undo of the uint repair. The independent `glUniform4fv` active-extent material issue, synchronous startup latency and later changelevel termination remain unchanged and out of scope.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit. Its exact hash is recorded in the authoritative Google Docs ledger and final worker handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 48 Phase B implementation, positive/rejection validation, retained Bundle-75 qualifying workflow/artifact, independent IPA verification, exactly one tempfile.org publication and both durable-ledger reports are complete. Stop for orchestrator review. Do not contact Arjun, request logs/evidence/device testing, interpret future device evidence, implement a topology/material/startup/transition repair, or begin another phase or work order.

## Work Order 49 Phase A - Bundle 75 complete topology path and telemetry-failure audit

Candidate/run and acceptance status: **audit-only; Outcome B selected; no candidate**. Bundle 75 failed its complete diagnostic-coverage gate and remains diagnostics-only, build-qualified and not device-accepted. Bundle 69's direct-drawable presentation architecture and Bundle 71's native-ES3 32-bit element-index invariant remain required. This phase changes no engine, renderer, GL4ES, SDL, Diffusion, menu, gameplay, patch, validator, build or CI behavior. It creates no build, workflow, artifact, IPA, upload, marker, evidence request or device-test request.

### Authority, source pins and exact evidence boundary

- The audit began at the exact fetched remote `agent/ios-proof-of-life` head `90fa97a62df34c23c3016f3aae244e5681c246b3`, with a clean worktree. The authoritative Google Docs ledger was read through Work Order 49 Phase A at revision `AIroW35grWrlzhaTIG4x3uODGOEmyeI3LyejVBRic27ikIyXR1cDbbyFhSABmJHxpsWEmgeEr9QNoWsLXvWhae9aU8mkwjOzXW2n_LQRbG8`, tab `t.0`, end index `331553`. The repository ledger was also read completely before analysis.
- Exact applied trees were inspected, not inferred from patch intent: Diffusion `14d156bf3a6993c172697fac83a937836c3b5561` in `build/wo44-diffusion-applytest` and GL4ES `81547d986798e876de8b434193920b606a72363f` in `build/wo48b-gl4es`, each with the retained iOS patch stack applied.
- The authoritative Bundle 75 log has 1,653 lines and 70,461 bytes. It contains exactly the following index-trace marker counts:

| Marker family | Count |
| --- | ---: |
| `iOS index trace logger:` | 1 |
| `iOS index trace policy:` | 1 |
| `iOS index trace ownership:` | 1 |
| `iOS index trace ingress:` | 1 |
| `iOS index trace deferred:` | 0 |
| `iOS index trace native:` | 1 |
| `iOS index trace first divergence:` | 0 |
| `iOS index trace summary:` | 0 |
| Total trace-related engine-log lines | 5 |

- Trace ID 1 is preserved exactly as the sole ingress/native pair: direct world-client `glDrawRangeElements`, count 18, ingress and native `GL_UNSIGNED_INT`, start/end and min/max `2818/2825`, FNV-1a checksum `f0758dc7` at both boundaries, `match=1`, logical/native position buffer `1`, position stride `100`, position-buffer size `1,135,200` bytes and highest legal vertex `11,351`. It proves that one small world batch was internally consistent and drawable; it does not prove any affected studio draw or the native attribute state used by one.
- The log contains no studio-EBO, studio-decal-client, deferred/replay, high-index, first-divergence or summary record. It continues through model/foliage work and ends during first-active-frame BmodelSolid `CompileUberShader #48`. The device evidence still shows severe exploded/disconnected large models and ribbon-like geometry, followed later by a black loading screen. There is no OOM, allocation failure, texture eviction, Jetsam or failed-GL-texture discriminator.

### Why Bundle 75 captured only the safe world pair

The missing records are not explained by the documented caps. `indextrace.c` allows 64 eligible uint ingresses, five sampled trace IDs and 15 GL4ES callback lines, reserving the final GL line for the summary; the ownership line is emitted outside that counter. Bundle 75 used only four GL4ES callback lines plus the ownership line. Every wrapper call increments its monotonic ID, but eligibility requires `GL_UNSIGNED_INT`, a resolved index address and a positive count. Eligible calls increment a silent ingress count; a record is emitted only for the first observed family, first high index or first deferred/intercept route. The summary is deliberately withheld until ingress 64. Therefore the missing summary proves the observed log never completed a 64-ingress window; the line cap did not truncate it. It does **not** prove that the sole logged record was the sole wrapper call.

The family classifier reads live logical GL4ES state: an element buffer means `studio-ebo`; no element buffer plus a position buffer means `world-client`; neither means `studio-decal-client`. Diffusion explicitly binds each studio mesh's VAO and IBO before its uint draw, so a reached, correctly represented studio mesh would be eligible and would create the first studio-family sample inside the window. Core and EXT `glDrawRangeElements` names and ordinary `glDrawElements` all resolve to instrumented GL4ES wrappers; the ownership record rejects a separate Diffusion-to-native draw bypass. Source alone cannot prove whether the affected device call had not yet reached wrapper ingress, whether its live logical state differed from the source-expected EBO state, or whether logging ceased first.

Shader ordering supplies the observed delay boundary. `AddMeshToDrawList` calls `ChooseStudioProgram` before it stores the mesh in the draw queue; shader selection can synchronously enter `GL_UberShaderForSolidStudio`/`GL_UberShaderForDlightStudio` and `CompileUberShader`. `DrawMeshFromBuffer`, VAO/IBO binding and wrapper ingress occur only after that call returns and the queued mesh is later drained. An engine log that ends in `CompileUberShader #48` can therefore lack the later studio ingress without implying an index-route bypass.

The engine sink did not lose an already-emitted user-space tail. Bundle 75's callback calls `gEngfuncs.Con_Printf`; the engine path is `Con_Printf -> Con_Printfv -> Sys_Print -> Sys_PrintLog`. `Sys_PrintLog` writes each message to the raw log descriptor through `Sys_WriteLogfile` and immediately calls `Sys_FlushLogfile`, which calls `fflush` on the companion stream. The callback is installed after GL4ES initialization and cleared only during GL shutdown immediately before context destruction; shader compilation does not clear it. Thus absent markers were not sitting in an engine stdio buffer. They were not emitted before the recorded logging boundary, or execution/log ownership ended before those calls.

Bundle 75 also did not observe the full native attribute boundary it claimed to correlate. Its `ios_index_trace_native` call in `glDrawElementsCommon` executes before `fpe_glDrawElements`. The latter then calls `realize_glenv`, realizes the program's vertex attributes and native array-buffer bindings, maps a logical EBO CPU-mirror pointer back to a native byte offset when applicable, calls `realize_bufferIndex`, and only then invokes native `gles_glDrawElements`. The Bundle 75 native line therefore checks the selected index payload and ingress-captured position metadata, but it cannot prove the post-realization native position buffer/type/stride/offset actually submitted. That unobserved interval is the narrowest remaining topology-bearing boundary.

### Complete topology-bearing source chain

**Studio large-model route.** `CreateMeshCacheVL` resets `m_nNumLightVerts` once for the complete vertex-light cache, calls `CreateMeshCache`, and compares the final aggregate with `dml->numverts`. `CreateMeshCache` walks every unique submodel and every mesh. `MeshCreateBuffer` resets `m_nNumArrayVerts` and `m_nNumArrayElems` for each `mstudiomesh_t`, expands strip/fan commands into duplicated local vertices, and writes local uint indices whose domain is exactly that mesh's `0..numVerts-1`. It increments `m_nNumLightVerts` for every expanded vertex across all meshes/submodels. Consequently the reported `truck_new.mdl` 112,981 and `cars_pack.mdl` 139,508 values are aggregate duplicated vertex-light-cache totals, not single draw-addressable domains and not proof of an index above 65,535 in any one draw.

Each mesh owns a VBO, VAO and EBO. Upload selects one packed studio vertex layout: position is always three `GL_FLOAT` components at offset zero; the actual packed strides are 60 bytes (`svert_v0_t`), 88 (`svert_v1_t`), 64 (`svert_v2_t`) or 96 (`svert_v3_t`). Attribute offsets use `offsetof` and the same `sizeof` used for VBO upload. Bone IDs use four `GL_BYTE` components and weights use four `GL_UNSIGNED_BYTE` components through the float generic-attribute API with normalization false, matching the renderer's shader-facing convention. The local `unsigned int` element array is uploaded while that VAO is bound. `DrawMeshFromBuffer` rebinds both `mesh->vao` and `mesh->ibo`, then submits range `0..mesh->numVerts-1`, uint count `mesh->numElems`, EBO byte offset zero; its fallback ordinary draw has the same local domain. There is no studio base vertex, global aggregate offset or cross-mesh index append.

GL4ES retains logical buffer objects with CPU mirrors and optional real native buffers. Binding the Diffusion VAO restores its logical attribute descriptors and EBO pointer. The range wrapper resolves offset zero against the EBO mirror, preserves uint indices, and either: (a) sends the direct path through `glDrawElementsCommon`/FPE; or (b) copies exactly the declared vertex span, subtracts the range start (zero for studio), owns 32-bit normalized indices in a render list, and replays them through a render-list VBO/client submission. Append/merge reallocates list-owned arrays rather than retaining the caller's EBO pointer. On the direct FPE path, `realize_glenv` maps each enabled logical attribute to its stored real buffer and relative pointer, then the EBO mirror pointer is converted back to the real EBO offset immediately before native draw. The source chain is internally coherent, but Bundle 75 captured neither an affected studio instance nor the post-realization native attribute state, so device-time adherence is unresolved.

**World/brush route.** World loading creates one monolithic `bvert_t` VBO/VAO for world and brush surfaces. Position is three floats at offset zero with stride `sizeof(bvert_t)`; Bundle 75 measured that stride as 100 bytes. Draw lists append absolute `firstvertex`-based uint indices to a synchronous client `tempElems` array, track the global minimum and exclusive maximum, and submit `glDrawRangeElements(startv, endv - 1, ..., GL_UNSIGNED_INT, tempElems)` with no EBO. Trace ID 1 is exactly this family and proves one range, one client index payload and one logical/native position-buffer identity were safe. It does not establish that every later world batch is safe or explain studio-model explosions. Apparent world ribbons can be malformed studio geometry stretched across the scene; the evidence does not yet prove a corrupt brush batch.

**Studio decal route.** Decals concatenate generated pose-space client vertices and local per-decal uint indices, adding a CPU `vertexOffset` as batches are concatenated. They bind no EBO and submit a client uint range/ordinary draw. This is a separate family from the per-mesh studio EBO path and was not observed in Bundle 75.

**Desktop and Android comparison.** The audited Diffusion construction, upload, VAO/EBO pairing and draw files contain no iOS or Android conditional around these paths. Desktop OpenGL consumes the same per-mesh local domains and packed descriptors directly, without GL4ES's logical-to-native realization layer. A GL4ES-based Android/GLES build uses the same Diffusion source and the same wrapper algorithms; no source-supported Android-only base, stride, pointer or index workaround exists to transplant. The iOS-only difference material to this audit is the retained GL4ES bridge/capability/profile and its diagnostic placement, not a different model producer.

### Proof-gate decision - Outcome B

**Outcome B is selected: one runtime discriminator remains.** Source proves that the 112,981/139,508 diagnostics are aggregate totals and proves a coherent per-mesh producer invariant, but it cannot separate these final device branches: (1) the affected studio draw never reached the wrapper before the recorded termination/log boundary; (2) it reached with unexpected logical VAO/EBO state and escaped the event-triggered family sample; (3) direct FPE realization paired correct uint indices with a wrong native attribute buffer/stride/offset; or (4) an unobserved deferred/replay route changed the vertex/index pairing. Outcome A is not established because no complete affected producer-to-post-realization-native invariant failure is source-proven. Outcome C is not selected because the ID-1 index pair is trustworthy and non-mutating; the instrumentation is incomplete for the intended topology question, not evidence-corrupting.

The minimal separately authorized future boundary, if any, is one diagnostics-only design rather than larger counters:

1. At studio cache creation, compute and retain in a fixed bounded diagnostic record the per-mesh `numVerts`, `numElems`, local min/max/checksum, selected packed layout, VAO/VBO/EBO handles and uploaded byte sizes. Select structurally (for example, first vertex-lit model whose aggregate cache exceeds 65,535), never by hard-coded model name.
2. In `AddMeshToDrawList`, emit one synchronously flushed `producer-plan` record **before** `ChooseStudioProgram`. It survives termination during shader compilation and proves whether the affected mesh reached the pre-shader boundary.
3. Immediately before `DrawMeshFromBuffer`, arm a stable diagnostic token for that exact mesh. At GL4ES ingress, consume the token and record logical EBO/VAO plus every enabled program-relevant attribute, resolved indices, range/base and buffer bounds.
4. Carry the same token through direct or render-list ownership. For the direct path, record egress only inside `fpe_glDrawElements`, after `realize_glenv` and `realize_bufferIndex` and immediately before native `gles_glDrawElements`; capture the realized `gleshard` attribute buffer/type/components/normalized/integer/stride/pointer and actual native EBO/offset. For deferred replay, capture the list-owned vertex span/index segment and post-realization native state at the equivalent point.
5. Emit one completion/absence summary through the engine sink with fixed storage and a hard global line cap. Do not call `glGetError`, allocate per draw, alter GL state, change ordering or mutate vertex/index data.

One run would then distinguish: pre-shader record only (draw blocked before dispatch); producer plus ingress but no post-realization egress (wrapper/FPE boundary); full matching pair (topology cause lies outside index/base/attribute pairing); or the first exact mismatched buffer/base/stride/type/pointer/lifetime field. No candidate or device test is authorized in this phase.

### Competing-hypothesis matrix

| Hypothesis | Strongest supporting evidence | Strongest falsifying evidence / remaining discriminator | Phase-A disposition |
| --- | --- | --- | --- |
| Correct uint indices paired with wrong vertex buffer/VAO/attribute state | Severe connected-to-distant-point geometry is consistent with wrong position fetch; Bundle 75 never sampled affected studio or post-`realize_glenv` native attributes. | Per-mesh source rebinds VAO+IBO and stores exact packed descriptors; ID 1 has a safe world position buffer. Needs the paired post-realization studio record. | Leading unresolved branch. |
| Lost or wrong base/range transformation | A wrong copied span or normalization would produce ribbons; GL4ES has distinct direct/deferred range logic. | Studio range is local `0..numVerts-1` with base zero; direct path does not normalize; ID 1's world range matches. Only an affected deferred record can revive it. | Possible only on an unobserved deferred route. |
| EBO byte offset misclassified as client pointer, or reverse | Direct studio crosses logical EBO mirror pointer to native EBO-offset conversion, a topology-critical boundary. | Diffusion explicitly rebinds the mesh IBO and GL4ES logical VAO stores it; source conversion is coherent. No live studio EBO pair exists. | Unresolved. |
| Deferred/render-list replay uses stale buffer identity | Lists copy/normalize vertex/index data and may append/merge/reallocate before replay. | Ownership is list-local and Bundle 71 keeps uint storage; default batching is off and no deferred marker appeared. Runtime route is still unproved. | Lower-probability unresolved branch. |
| Vertex structure/stride/layout mismatch | Four packed studio layouts and scene-wide stretching make a device-time stride mismatch plausible. | Upload byte size, attribute stride and offsets all use the same `sizeof`/`offsetof`; position is float3 offset zero across layouts and desktop uses the same definitions. | Not source-proven; needs realized native attributes. |
| Invalid attribute type/normalization/integer-vs-float translation | Bone IDs/weights use byte types through generic float attributes, adding a GL-to-GLES translation seam. | Position, the topology-bearing attribute, is always float3; GL4ES retains type/normalization and the shaders use the generic convention. | Weak for topology, still record all used attributes. |
| Asset/model loader corruption before GL4ES | Very large vertex-light caches and a historical disabled TBN assertion warrant producer verification. | CRC and aggregate vertex-light counts match; each mesh is rebuilt into bounded local arrays and the same producer works on desktop. | Possible but unsupported; pre-upload checksum closes it. |
| Uniform/material/capability fallback or memory pressure | Known `glUniform4fv` errors, missing features/material warnings and later black loading exist. | These paths do not rewrite index/vertex ownership; the log has no OOM/Jetsam/allocation/texture-eviction evidence. | Rejected as the current topology explanation; separate tracks. |

### Validation, files, risks and stop state

Why this satisfies Work Order 49 Phase A: it records every expected Bundle 75 marker count and the decisive ID-1 values; proves why record/line caps and engine buffering did not explain the missing families; traces shader ordering and callback lifetime; audits the full studio/world/decal producer, ownership, direct/deferred/replay and native-realization path; separates logical from realized native VAO state; compares source-equivalent desktop/Android paths; evaluates all eight required hypotheses; selects exactly one proof-gate outcome; and specifies one termination-surviving, one-run discriminator without implementing it.

Validation performed: authoritative Google Docs and repository-ledger full reads; Codebase Memory-first architecture, symbol search, call tracing and source-snippet retrieval; exact fetched remote-head/worktree verification; exact Diffusion and GL4ES pin/applied-tree inspection; complete affected draw-call enumeration; studio aggregate/local-domain construction audit; packed attribute/VBO/VAO/EBO lifetime audit; world global-domain and decal client-domain audit; GL4ES eligibility/cap/classification/direct/deferred/render-list/FPE/native audit; engine console/raw-FD/flush and callback-lifetime trace; desktop/Android conditional search; and documentation diff/readback checks. Publication validation additionally includes `git diff --check`, documentation-only changed-file inspection, one `[skip ci]` commit/push, remote-head and clean-worktree verification, zero-workflow readback, and readback of both durable ledgers.

Exact files changed by Work Order 49 Phase A: `Documentation/XASH3DIOS_PORTING_STATE.md` only. Workflow URL/ID/result: none; forbidden. Artifact/IPA/tempfile.org: none created, retrieved, published or uploaded; forbidden. Expected new log markers: none; the future diagnostic labels above are an unimplemented boundary specification, not runtime output.

Remaining risks: the affected studio mesh's actual local maximum and checksum are unknown; its device-time logical and realized native attribute state is unknown; direct versus deferred selection is unknown; correct topology pairing may still leave the separate uniform/material defect, synchronous shader latency and later transition termination; and apparent world ribbons have not been attributed conclusively to brush versus stretched studio geometry. None authorizes a patch, build or test here.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit. Its exact hash is recorded in the authoritative Google Docs mirror and final handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 49 Phase A ends at **Outcome B** for orchestrator review. Do not modify runtime code, build, start or dispatch Actions, create/retrieve/upload an IPA, use tempfile.org, contact Arjun, request evidence or a device test, implement the future discriminator, begin Phase B, or begin any other work order.

## Work Order 49 Phase B - Bundle 77 producer-to-post-realization topology discriminator

Candidate/run and acceptance status: **Outcome A. Bundle 77 is build-qualified diagnostics-only and awaiting orchestrator review; it is not device-accepted.** It implements only the authorized bounded topology discriminator. It does not repair or alter renderer output, presentation, gameplay, menus, touch, audio, shaders, materials, uniforms, loading, transitions, draw ordering, batching, GL state, vertex/index data or timing. Bundle 69's direct-drawable zero-MSAA architecture and Bundle 71's native-ES3 uint-index preservation remain frozen and validated.

### Commits, workflow, artifact and publication

- Diagnostics implementation commit: `f8a02cdc7380854368c353663a691fba3416d9ec` (`feat(ios): add WO49 realized-topology discriminator`).
- Retained qualifying workflow: successful GitHub Actions push run `31903385948`, run/bundle number `77`, job `95057449870`, head `f8a02cdc7380854368c353663a691fba3416d9ec`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31903385948`.
- The automatic pull-request twin `31903389585` was canceled and has zero artifacts. It is not a candidate. No manual dispatch or retry was created; the push run is the sole qualifying candidate workflow.
- Retained GitHub artifact: `Xash3DiOS-arm64-unsigned`, artifact ID `9251744156`, archive size `8,583,864` bytes, archive digest `sha256:afb7aa8255fa8724c752d17a300aa79827184d75f4b4d62729d0326675de7f18`, expiry `2026-08-29T19:19:45Z`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31903385948/artifacts/9251744156`.
- Verified IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,679,931` bytes, SHA-256 `A8A5131EC77D471F2CB581126981E5BD9EB4B680CD5A932D7A213D3ACDEF1976`. Independent extraction reports `CFBundleVersion=77`, `MinimumOSVersion=12.0`, file sharing enabled, and 13 of 13 Mach-O binaries as thin arm64.
- Exactly one tempfile.org upload: information page `https://tempfile.org/pG6NHEGSpkL/`; direct download `https://tempfile.org/pG6NHEGSpkL/download`; expiry `2026-08-17T19:22:05.325Z`. API metadata reports the exact filename and `8,679,931` bytes; security readback reports `safe`, no warning or suspicious pattern, and SHA-256 `a8a5131ec77d471f2cb581126981e5bd9eb4b680cd5a932d7a213d3acdef1976`.

### Exact instrumentation boundary and behavior

The structurally eligible event is the first actually submitted vertex-lit Diffusion studio mesh whose owning vertex-light cache has more than 65,535 aggregate vertices. No model, path, aggregate/local count, shader number, frame, pointer or framebuffer is hard-coded. After all `AddMeshToDrawList` eligibility returns and immediately before `ChooseStudioProgram`, Diffusion emits one producer record through the installed GL4ES callback. The engine bridge calls `gEngfuncs.Con_Printf`; `Sys_PrintLog` writes and calls `Sys_FlushLogfile` on every message, so the producer record is durably visible before synchronous shader compilation. Stable monotonic tokens are capped at four and deduplicated by mesh identity, permitting at least two distinct earliest eligible meshes when execution reaches them.

The producer records frame/map and producer/model/cache/instance/mesh identities; aggregate and local vertex/element counts; mode/type/source; local index min/max/FNV checksum; base/range; one of the four packed studio layouts, full stride and every shader-relevant attribute descriptor; logical VAO/VBO/EBO, allocation sizes and upload offsets; full vertex, position and index checksums; and highest legal local/packed address. The token is carried through the draw queue and `DrawMeshFromBuffer`, then armed before Diffusion binds the mesh VAO/EBO and enters either range or ordinary uint draw.

At GL4ES ingress, the paired record captures logical VAO/VBO/EBO and native-mirror identities, client-pointer versus EBO-offset classification, mode/type/count/range/base, resolved index min/max/checksum, mirrored full-vertex and position checksums, and every producer-declared logical attribute with enable, buffer, type/count, normalized/integer state, stride, offset, divisor, allocation size and calculated highest byte/bounds result. Direct, intercept, deferred and list routes preserve the same token. Fixed per-list arrays retain token and index/vertex segment offsets/counts through append/merge; the route record is delayed until replay so copied/normalized/rebased/appended ownership reflects the final list state. Missing ingress, route or replay emits a reason-coded absence.

The native record is inside `fpe_glDrawElements` after `realize_glenv` and `realize_bufferIndex` and immediately before the actual `gles_glDrawElements` call. Render-list replay sets its token/owned segment immediately before the same FPE/native boundary. It captures GL4ES's native-VAO policy, actual array/EBO binding, EBO size and pointer/offset classification, actual draw and paired segment counts/type/min/max/checksum, all active realized attributes and every computed highest referenced byte/bounds result. Producer, ingress, route and realized fields are compared in deterministic order; only the first mismatch per token is emitted. An index checksum by itself can never yield `match=1` because logical/native attributes, buffers, data checksums, range/base/source and bounds are also required.

The complete topology cause remains **explicitly unresolved pending device evidence**. The candidate is designed to discriminate the leading wrong realized VBO/attribute branch, wrong VAO/EBO/source classification, lost range/base transformation, stale deferred/list ownership, pre-GL4ES producer corruption, or a complete producer-to-native match. No one of those branches has been promoted into a renderer repair.

### Validation and rejection results

- Exact applied-tree patch checks passed against Diffusion `14d156bf3a6993c172697fac83a937836c3b5561` and GL4ES `81547d986798e876de8b434193920b606a72363f`; MainUI remains pinned at `8c68de2f2325a0130953719efc3ae413eb24e01a`.
- Python compilation and WO49 positive/self-test validation passed in full and GL4ES-only modes. Existing drawable, uint-element, Bundle-75 index-trace and Diffusion iOS renderer-policy validators also passed. `git diff --check` passed.
- Synthetic fixtures detect wrong native VAO/VBO, wrong stride/offset, disabled or missing position, wrong EBO or client/offset classification, lost base/range, stale list storage, and accept a full match.
- Adversarial source mutations are rejected for a native hook before realization, missing direct activation, missing replay, index-only comparison, omitted bounds, token cap above four, hard-coded model/count, producer after shader selection, per-draw allocation, `glGetError`, pixel readback, and loss of the engine sink.
- The sole retained macOS run successfully applied all pinned patches, ran all positive/rejection suites, built arm64 GL4ES and the complete engine/Half-Life/Diffusion client/server/menu graph with `XASH_IOS=1`, passed mobile shader validation, passed packaged marker/API checks, and passed the IPA contract. Independent local extraction reconfirmed bundle version, marker presence, file size/hash and the 13-file arm64 inventory.

Expected engine.log markers are exactly: `WO49 topology policy:`, `WO49 topology producer:`, `WO49 topology ingress:`, `WO49 topology route:`, `WO49 topology realized:`, `WO49 topology mismatch:`, `WO49 topology absence:`, and `WO49 topology summary:`. The summary is terminal and bounded; it reports each token's furthest completed stage and reason/match state even when no token reaches native submission.

### Files, risks, durability and stop state

Exact repository files changed by Work Order 49 Phase B implementation: `scripts/ios/diffusion-wo49-topology-ios.patch`, `scripts/ios/gl4es-wo49-topology-ios.patch`, `scripts/ios/validate-ios-wo49-topology.py`, `scripts/gha/build_ios.sh`, `scripts/ios/builddiffusion.sh`, and `scripts/ios/verify_ipa.sh`. This report additionally changes `Documentation/XASH3DIOS_PORTING_STATE.md`. The Diffusion patch touches only `engine/studio.h`, `client/render/r_studio.h`, and `client/render/r_studio.cpp`; the GL4ES patch touches only `src/gl/indextrace.h`, `src/gl/indextrace.c`, `src/gl/gl_lookup.c`, `src/gl/list.h`, `src/gl/drawing.c`, `src/gl/list.c`, `src/gl/listdraw.c`, and `src/gl/fpe.c`.

Remaining risks: the device's first eligible studio token, direct versus deferred/list route and first mismatching field are not yet observed; a complete topology match would shift attention without fixing the separate `glUniform4fv` active-extent defect, capability/material fallbacks, synchronous shader latency or later transition termination; default native VAO is an architectural GL4ES emulation invariant rather than a separate GLES VAO object. None authorizes a renderer repair, user contact, evidence request, device-test request or another phase.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 49 Phase B implementation, positive/rejection validation, one retained Bundle-77 qualifying workflow/artifact, independent IPA verification, exactly one tempfile.org upload and both durable-ledger reports are complete. Stop for orchestrator review. Do not contact Arjun, ask for logs/evidence/testing, request a device test, interpret future device evidence, implement a renderer/gameplay repair, or begin another phase or work order.

## Work Order 49 Phase D - Bundle 77 comparator and studio transform audit

Candidate/run and acceptance status: **Outcome C. The single Bundle 77 Phase C device evidence set is accepted as an audit input, but Bundle 77 remains diagnostics-only and is not a device-accepted gameplay candidate.** The evidence proves that the sampled `truck_new.mdl` draw topology survives unchanged from Diffusion's producer through GL4ES's native draw boundary. The four reported `attribute-enabled` mismatches are comparator false positives. The severe visible deformation remains real, but the exact position-transform cause is unresolved because Bundle 77 did not correlate a token to its shader program or capture position-bearing matrix/bone/uniform values. No code, diagnostic, build, workflow, IPA, upload or device-test action is authorized or performed in this phase.

### Accepted evidence and verified boundary

The authoritative evidence is the complete 2,187-line `engine(20260816-073124).log` attachment, 98,670 bytes, SHA-256 `A983018802C7AD5C150963FD9ACDE2A23D76CAC032A36FDDD808B7AF7427364B`, plus the two accepted Phase C screenshots: `Photo-2.jpg`, 127,108 bytes, SHA-256 `A185E394C0A202A6F11DF7FBE7EFF15E57BCA06260D9ACF6956ABDE52C04D161`, and `Photo-3.jpg`, 117,056 bytes, SHA-256 `054D99CAC395C04802C65867E870A5A6D487593CC749350F676F5A56F9ACA4A3`. The screenshots show a normally presented gameplay scene containing recognizable terrain, foliage and background geometry together with severe repeated vertical ribbons, exploded strips and distorted bands. They rule out the old stale-menu/presentation boundary but do not identify which model or shader produced each pixel. There is no screenshot-proven one-bone studio control using the same program and uniform path.

All four bounded tokens are frame-54, direct-route, fixed-owned, actually submitted vertex-lit meshes from `models/bmec/cars/truck_new.mdl` on `maps/ch1map0.bsp`. Every producer, wrapper-ingress, route and post-`realize_glenv` native record agrees on `GL_TRIANGLES`, `GL_UNSIGNED_INT`, zero base, local range, count, min/max, FNV checksum, EBO identity/size, VBO identity/size, layout 1, 88-byte stride, every enabled attribute descriptor and position checksum. The direct route performs no copy, normalization, rebase, append or replay. This moves the verified failure boundary past index construction, EBO ownership, wrapper classification, uint preservation, range/base handling, position-VBO selection and native attribute realization, to **position transformation after the correct local position stream is presented to the linked native program**.

| Token | Indices / EBO | Position VBO and checksum | Linked and draw-enabled array attributes | Re-evaluated bounds | Route | Phase D classification |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 3,162 uint; 0..1,777; `e8ad3e72`; EBO 1051 / 12,648 B | VBO 1050 / 156,464 B; `b761109f` | a0,a1,a2,a3,a4,a10,a11 | all fetched arrays valid; a7 disabled and irrelevant | direct, fixed-owned | complete sampled topology match |
| 2 | 4,362 uint; 0..2,649; `0098309d`; EBO 1053 / 17,448 B | VBO 1052 / 233,200 B; `152ed4f8` | a0,a1,a2,a3,a4,a10,a11 | all fetched arrays valid; a7 disabled and irrelevant | direct, fixed-owned | complete sampled topology match |
| 3 | 36 uint; 0..17; `cf852f75`; EBO 1055 / 144 B | VBO 1054 / 1,584 B; `1b55d5dc` | a0,a1,a2,a3,a4,a10,a11 | all fetched arrays valid; even stale a7 happens to be in bounds | direct, fixed-owned | complete sampled topology match; disproves a7 bounds as mismatch trigger |
| 4 | 19,797 uint; 0..9,684; `9f0b4cb8`; EBO 1057 / 79,188 B | VBO 1056 / 852,280 B; `7499bbfa` | a0,a1,a2,a3,a4,a10,a11 | all fetched arrays valid; a7 disabled and irrelevant | direct, fixed-owned | complete sampled topology match |

The 112,981 figure is the owning vertex-light cache aggregate, not any mesh's local index domain. The observed local maxima are 1,777, 2,649, 17 and 9,684, so none approaches 65,536. Bundle 71's uint repair remains a required structural invariant, but it is non-discriminating for these four draws and is not their remaining failure cause.

### Comparator false-positive proof

The exact implementation is `ios_wo49_realize_one` in the applied Bundle 77 `src/gl/indextrace.c`, sourced by `scripts/ios/gl4es-wo49-topology-ios.patch`. It loops upward through every location for which the linked native `program->va_size[index]` is nonzero, obtains the realized mirror at `glstate->gleshard->vertexattrib[index]`, and looks for a producer/ingress record at the same index. Location a7 is the first reflected location not present in layout 1. For a7, `logical == NULL` and `native_attr->enabled == 0`; nevertheless the comparator calls:

```text
ios_wo49_mismatch(record, "attribute-enabled", 1,
    logical ? logical->enabled : 0, native_attr->enabled)
```

The printed operands `producer=1 ingress=0 realized=0` therefore mean **hard-coded expected one, no captured logical attribute, disabled realized array**. They do not report a producer field, and the message omits the responsible slot. The same loop calculates a highest byte and globally clears `bounds_ok` for every reflected location even when its array is disabled. That is why stale a7 state (`buffer=962`, `GL_BYTE`, stride 60, offset 56) makes tokens 1, 2 and 4 print `bounds_ok=0`; token 3 still prints the same mismatch with a7 accidentally in bounds, proving that bounds did not trigger the first mismatch.

The only topology-bearing attribute bounds are those the linked program reflects **and** the draw enables for array fetch. In GL4ES `realize_glenv`, an enabled attribute is realized with `gles_glVertexAttribPointer` or, only when its recorded `integer` flag is true, `gles_glVertexAttribIPointer`. A disabled attribute instead disables the native array and sends the current generic constant through `gles_glVertexAttrib4fv`; no buffer vertex is fetched. Consequently a7's stale buffer descriptor cannot invalidate bounds. For the sampled `MAXSTUDIOBONES 1` rigid branch, the shader constructs the bone matrix from `u_BoneQuaternion[0]` and `u_BonePosition[0]`; it does not use a per-vertex bone index for position. The later `native-active-attribute-unexpected` check would also misclassify this disabled, producer-absent slot had the hard-coded enabled check not already consumed the one-mismatch budget. **No comparator source change is made or authorized.**

### Studio attributes, packing and native realization

Diffusion binds stable attribute locations before link: a0 position, a1 tangent, a2 binormal, a3 normal, a4 texture coordinate 0, a7 bone indexes, a8 bone weights, a10 vertex-light color and a11 vertex-light vectors. `tnbasis.h` declares and uses a1/a2/a3; `studiosolid_vp.glsl` declares and uses a0/a4 and, for `STUDIO_VERTEX_LIGHTING`, a10/a11. Bundle 77 layout 1 is the one-bone vertex-light `svert_v1_t`: float3 position at byte 0, normal at 12, tangent at 24, binormal at 36, float2 texture coordinate at 48, four packed light floats at 56 and four packed deluxe/light-vector floats at 72, total 88 bytes. `UploadBufferVLight` uses the same `sizeof`/`offsetof` values for upload and VAO setup.

All seven enabled sampled attributes are floating-point inputs with `normalized=0` and `integer=0`. GL4ES therefore realizes them with native `glVertexAttribPointer`, preserving component width, type, normalization, stride, offset and VBO. Integer-pointer conversion is not involved. Bone index/weight arrays use generic byte attributes only in layouts that contain them; layout 1 contains neither, and the rigid shader branch does not require them for position. The producer/ingress/realized data establish no genuine consumed-attribute mismatch.

### Complete rigid studio position-transform and uniform path

The source-level position path for the sampled model class is:

1. `StudioSetupBones` evaluates the sequence/controllers/IK into local `m_pbones`. With no pose-to-bone weighting path, each bone's quaternion and origin are copied into `m_studioquat` and `m_studiopos`. The sampled shader define and layout prove the rigid, one-bone branch; `num_bones` is one.
2. `DrawStudioMeshes` calls `R_TransformForEntity(m_protationmatrix)`. That sets `objectMatrix`, computes `modelviewMatrix = worldviewMatrix * objectMatrix`, selects `GL_MODELVIEW`, converts the engine matrix to a 16-float GL array and calls `glLoadMatrixf`. Projection was loaded separately from `RI->projectionMatrix` by 3-D frame setup.
3. GL4ES stores those model-view and projection matrices, dirties its cached MVP, and computes `projection * modelview` in `getMVPMat`. Shader conversion replaces legacy `gl_ModelViewMatrix` and `gl_ModelViewProjectionMatrix` with `_gl4es_...` uniforms. `builtin_CheckUniform` records their reflected native locations, and `realize_glenv` forwards both as count-one `glUniformMatrix4fv(..., GL_FALSE, value)` calls before the native draw.
4. On each shader change, Diffusion uploads `u_StudioParams` as three vec4 values, `u_GammaTable` as 64 vec4 values for vertex lighting, and `u_MeshParams` as three vec3 values. On entity/model change it uploads one `u_BoneQuaternion` vec4, one `u_BonePosition` vec3 and two `u_StudioLighting` vec4 values.
5. In `studiosolid_vp.glsl`, the rigid branch builds `boneMatrix = Mat4FromOriginQuat(u_BoneQuaternion[0], u_BonePosition[0])`, computes `worldpos = boneMatrix * vec4(attr_Position, 1)`, then computes clip position as `_gl4es_ModelViewProjectionMatrix * worldpos`. Mesh, studio-lighting and gamma arrays do not feed `gl_Position`. Only the separately compiled `STUDIO_SWAY_FOLIAGE` variant first modifies local x/y using `u_FoliageSwayHeight` and `u_StudioParams[0].w`.

GL4ES obtains each native active uniform's name, type, extent and location from `glGetActiveUniform`/`glGetUniformLocation`, creates one `uniform_t` entry per element, and records native `id`, reflected `size`, type and cache extent. `glGetUniformLocation` exposed to Diffusion returns that tracked location. `glUniform3fv`/`glUniform4fv` enter `GoUniformfv`, which rejects a missing location, wrong vector width, non-float type or `count > reflected size`; otherwise it updates the exact cache slice and forwards the same native location/count/value to `gles_glUniform3fv` or `gles_glUniform4fv`. Matrix built-ins use the analogous count/type/extent validation in `GoUniformMatrix4fv` before native forwarding.

For the relevant reflected programs, the log itself is authoritative because `GL_ShowProgramUniforms` prints native active-uniform reflection, not source declarations. StudioSolid #49 (`MAXSTUDIOBONES 1`, `STUDIO_VERTEX_LIGHTING`) reports `u_BonePosition[128]`, `u_BoneQuaternion[128]`, `u_MeshParams[3]`, `u_StudioParams[3]`, `u_StudioLighting[2]`, `u_GammaTable[64]` and the two count-one matrix uniforms. The application counts of 1, 1, 3, 3, 2, 64 and 1 respectively are within those active extents and use the correct float widths. StudioSolid #50 and #51 report the same extents; #51 additionally reflects scalar float `u_FoliageSwayHeight`.

Two real but insufficiently correlated uniform defects are kept explicit rather than generalized:

- StudioSolid #52 (`STUDIO_ADDITIVE`) reflects `u_StudioParams` with extent one while `DrawStudioMeshes` still submits three vec4 values. GL4ES must reject that one named upload with `GL_INVALID_OPERATION` before cache/native mutation. The array controls view/fog/material terms in that variant, not its rigid `gl_Position`, so this does not establish the severe geometry cause.
- For a material with nonzero foliage height, `DrawStudioMeshes` calls integer `pglUniform1iARB` for the shader's scalar **float** `u_FoliageSwayHeight`. GL4ES `GoUniformiv` must reject the type mismatch. This is position-bearing only in StudioSolid #51, but Bundle 77 records the producer before shader selection and never stores `hProgram`/options in its token, so none of the four tokens can be proven to use #51. Even if one does, the shader's bounded 2.5%-of-z sway does not by source alone explain the scene-wide ribbon topology. It is a source-proven defect and a candidate explanation for one GL error, not an authorized repair or an established Bundle 77 cause.

The earlier `glUniform4fv` active-extent defect therefore remains **variant- and uniform-specific**. It is proven for brush `u_BrushParams` and additive studio `u_StudioParams`, but it is not present for the position-bearing bone arrays or matrix uploads of #49-#51. The log captures neither application values, GL4ES cache contents nor native forwarded values for the bone or matrix uniforms, so source coherence cannot prove runtime equality.

### Controls and competing hypotheses

| Hypothesis | Phase D evidence | Disposition |
| --- | --- | --- |
| Comparator-reported attribute enable/bounds mismatch | Source proves the first failing slot is disabled a7 with fabricated producer operand; token 3 mismatches even when its stale descriptor is in bounds. | **Proven diagnostic false positive.** |
| Uint/index/EBO/base/range/route corruption | All four local streams, checksums, bindings, ranges and direct native submissions match; maxima are below 65,536. | Rejected for sampled draws. Preserve Bundle 71 invariant. |
| Wrong fetched position/TBN/texture/light attribute descriptor | All linked-and-enabled arrays match type/count/stride/offset/buffer and are in bounds. | Rejected for sampled draws. |
| Disabled a7 stale state | GL4ES supplies a generic constant and fetches no a7 buffer; rigid position branch uses bone 0 directly. | Irrelevant to sampled topology and bounds. |
| Bad application bone pose or entity/model-view/projection values | These are exactly the remaining common inputs to rigid clip position, but their values were not logged. | Leading unresolved transform branch. |
| GL4ES uniform location/cache/native forwarding mismatch for bone or matrix values | Source path is coherent and reflected extents/counts match, but Bundle 77 captured none of the values or forwarding decisions. | Unresolved; requires one paired value trace. |
| Foliage height integer-to-float upload defect | Exact source mismatch; #51 is compiled for a material during the relevant interval. Token-to-program linkage and runtime effect are absent. | Proven separate defect, not established as the severe topology cause. |
| Additive `u_StudioParams` active-extent rejection | Exact #52 extent/count mismatch, but this uniform does not form rigid clip position. | Proven separate material/view/fog defect. |
| Texture/material/capability fallback | Can change shading or missing content, not the now-matched position/index fetch. | Separate, not the present geometry boundary. |
| Shader compilation latency or later ch1map1 termination | Log continues through shader compilation and gameplay presentation; later map transition remains unclassified. | Separate tracks. |

The visible world/foliage background is not a valid rigid-studio control: it uses different producers, shaders and uniforms, and the screenshots cannot assign the ribbons to a specific token. No logged correct one-bone `StudioSolid` draw with captured transform values exists for a same-path comparison.

### Proof-gate decision - Outcome C and one future discriminator

**Outcome C is selected: sampled topology matches, but the exact studio transform cause remains unresolved.** Outcome A is rejected because there is no genuine consumed-attribute topology mismatch. Outcome B is not established because the two source-proven uniform defects are either non-position-bearing for the affected variant or not correlated to any sampled token, while the position-bearing bone and matrix values were not observed. Outcome D is rejected because the evidence is internally consistent once disabled a7 is excluded from fetch/bounds validity.

If and only if a later work order authorizes it, the tight one-run discriminator is one structurally selected Bundle-77-style rigid vertex-lit token, extended without rendering mutation to pair exactly one draw across these stages:

1. After `ChooseStudioProgram`, record token, linked program handle/name, complete option set, material foliage height and whether the position shader contains the rigid or sway branch.
2. Immediately before the draw, record finite/range checks and hashes for one local position sample plus `m_studioquat[0]`, `m_studiopos[0]`, engine model-view, projection and CPU-computed MVP. Compute and record the same shader-side rigid clip result on CPU for a bounded vertex sample.
3. At GL4ES reflection/cache/realization, record only the position-bearing names: `_gl4es_ModelViewMatrix`, `_gl4es_ModelViewProjectionMatrix`, `u_BoneQuaternion[0]`, `u_BonePosition[0]`, and, only for the sway variant, `u_FoliageSwayHeight` and `u_StudioParams[0]`. Include logical and native location, reflected type/extent, submitted function/type/count, accepted-versus-rejected decision and value hash. Do not consume `glGetError`.
4. Immediately before the one native draw, compare application values, GL4ES cached values and values passed to native GLES, then emit one terminal first-divergence or full-match record. Retain fixed storage, no per-draw allocation, no GL-state mutation and a hard one-token/one-record-per-stage cap.

That single run would distinguish bad engine bone/matrix construction, wrong uniform function/count/extent, GL4ES location/cache/native forwarding divergence, the exact foliage variant mismatch, or a complete input match that moves the boundary into translated shader/native execution. It does not prescribe a repair.

### Required worker report and stop state

Structural cause: **unresolved at the position-transform boundary.** The reported Bundle 77 comparator mismatch is structurally explained as a disabled-a7 false positive; the topology stream itself matches. The remaining common position inputs are rigid bone quaternion/origin and GL4ES's model-view/MVP transport, with an uncorrelated float foliage-height upload defect on one compiled variant.

Why this satisfies Work Order 49 Phase D: it reads and classifies every accepted Bundle 77 token and both screenshots; proves the exact comparator operands and slot; re-evaluates bounds using linked-and-enabled fetch semantics; maps all sampled attribute locations; traces the complete Diffusion rigid position, matrix, bone and auxiliary uniform paths through GL4ES reflection/cache/type/extent checks to native GLES; revisits `glUniform4fv` per named variant; separates material, latency and transition tracks; selects exactly one authorized outcome; and defines one bounded future discriminator without implementing it.

Validation performed: complete accepted-log read and SHA-256; original-resolution screenshot inspection; exact Bundle 77 implementation commit and pinned applied-tree inspection; Codebase Memory-first search followed by source fallback for the unindexed pinned work trees; producer/ingress/route/native token reconciliation; comparator control-flow and operand audit; enabled-fetch/bounds audit; Diffusion attribute binding and `svert_v1_t` packing audit; shader preprocessor/rigid/sway branch audit; bone production and upload-count audit; engine matrix-load trace; GL4ES shader conversion, reflection, uniform cache/type/extent, matrix realization, native pointer and generic-attribute trace; active-uniform reflection cross-check against StudioSolid #49-#52; and documentation-only diff/readback validation. Publication verification additionally requires `git diff --check`, one `[skip ci]` documentation commit/push, remote-head equality, clean worktree, no new workflow and readback of both ledgers.

Workflow URL/ID and result: none for Phase D; forbidden. The existing Bundle 77 workflow remains historical evidence only. IPA/artifact/tempfile.org: none created, retrieved, published or uploaded; forbidden. Expected new log markers: none; this phase changes no executable source. Single device test requested: none; forbidden.

Exact files changed by Work Order 49 Phase D: `Documentation/XASH3DIOS_PORTING_STATE.md` only. No runtime, diagnostic, build, workflow or artifact file is changed.

Remaining risks: Bundle 77 does not map tokens to program/options; the actual bone quaternion/origin, model-view/projection/MVP values and GL4ES/native uniform bytes are unknown; the exact visible ownership of the screenshot ribbons is unknown; the foliage float/int upload and additive active-extent defect remain real but causally unproven; material fallbacks, shader latency and the later ch1map1 termination remain separate; and no device-accepted gameplay candidate exists.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This Phase D report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a commit cannot contain its own hash.

Stop state: Work Order 49 Phase D ends at **Outcome C** for orchestrator review. Do not change comparator/runtime/diagnostic code, build, start or dispatch a workflow, create/retrieve/upload an IPA, use tempfile.org, contact Arjun, request evidence or a device test, repair foliage/uniform/renderer behavior, implement the future discriminator, or begin another phase or work order.

## Work Order 49 Phase E - Bundle 79 one-token studio-transform discriminator

Candidate/run and acceptance status: **Outcome A. Bundle 79 is build-qualified diagnostics-only and awaiting orchestrator review; it is not device-accepted.** The implementation proof gate and complete CI validation passed. This candidate records one rigid vertex-lit transform path without changing rendering behavior. It does not claim that the renderer cause is fixed, and no device test is requested.

### Commits, workflow, artifact and publication

- Diagnostics implementation commit: `5a55a313d35834a2de001d78ea5b21cf044327a4` (`Add WO49 transform-path discriminator`).
- Sole retained qualifying workflow: successful GitHub Actions push run `31940875844`, run/bundle number `79`, job `95149762643`, head `5a55a313d35834a2de001d78ea5b21cf044327a4`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31940875844`.
- The automatic pull-request twin `31940877510` (run 80) was canceled and retained no artifact. It is not a candidate. No manual dispatch, retry or second qualifying artifact was created.
- Retained GitHub artifact: `Xash3DiOS-arm64-unsigned`, artifact ID `9262049612`, archive size `8,593,067` bytes, expiry `2026-08-30T10:14:40Z`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31940875844/artifacts/9262049612`.
- Verified IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,689,575` bytes, SHA-256 `f0178c2069aa7c91367e2232d13545375976418b1c87d19df23bc3b52f473f69`.
- Exactly one tempfile.org upload: information page `https://tempfile.org/zq9FMzUYvQc/`; direct download `https://tempfile.org/zq9FMzUYvQc/download`; expiry `2026-08-17T10:16:51.878Z`. Metadata/security readback reports the exact filename and size, `safe`, no warning or suspicious pattern, and the same SHA-256. A separate download of that published URL independently reproduced the exact size and hash.

### Verified boundary, structural finding and diagnostic behavior

The accepted Phase-D evidence moves the verified failure boundary past local index construction, EBO ownership, uint preservation, range/base handling, position-VBO selection and realized native attribute state. For the four sampled `models/bmec/cars/truck_new.mdl` draws, the remaining verified boundary is **position transformation after the correct local position stream reaches the linked native program**. Bundle 79 deliberately does not reopen the disabled-a7 comparator false positive or the already matched topology path.

The visual deformation's structural cause remains **explicitly unresolved pending this diagnostic's device evidence**. Source inspection found one important transport boundary that this candidate now distinguishes rather than repairs: `gl4es_glUseProgram` changes the logical program, while native `gles_glUseProgram` can be delayed until `realize_glenv`; Diffusion submits the bone uniforms immediately after the logical bind; `GoUniformfv` forwards accepted values immediately; and a same-parent realization path does not necessarily replay them through `fpe_SyncUniforms` after the native bind. This is a source-proven architectural risk and exact observation point, not proof that it caused the Bundle-77 deformation.

Diffusion deterministically claims only the first eligible rigid vertex-lit `truck_new.mdl` draw on `maps/ch1map0.bsp`, using fixed storage and a one-token, one-program, one-draw, one-frame/generation and one-terminal cap. It records map/model, token/frame/generation, chosen program handle and options hash, rigid/sway identity, one EBO-referenced local vertex/index, bone quaternion/origin element zero, complete model-view/projection/MVP values and hashes, and the CPU clip result computed with the selected shader's exact rigid semantics. Sway values and CPU sway math are required only if that selected shader consumes the sway branch.

The same token enters GL4ES before the application's position-bearing uploads. For model-view, MVP, `u_BoneQuaternion[0]`, `u_BonePosition[0]` and conditional sway inputs, fixed records retain reflected name/type/extent, logical and native locations, application entry point/count/hash, cache width/count/hash, and immediately pre-native function/count/hash. The selected translated vertex source is represented by a stable hash plus rigid/MVP branch flags, not an unbounded source dump. A post-native-`glUseProgram` realization hook and the hook immediately before the real native draw capture the realized program and required transform state. The terminal result is withheld until every field required by the selected shader exists, then emits exactly one of `application-source-transform-mismatch`, `GL4ES-reflection/cache-mismatch`, `GL4ES-native-forward-mismatch`, `full-application-to-native-transform-match`, or `incomplete/absent-evidence` with the first missing field.

Why this satisfies Work Order 49 Phase E: it follows precisely one structurally selected rigid vertex-lit draw from the Diffusion producer and CPU clip calculation through selected-program identity, native reflection, GL4ES cache and native-call forwarding to the immediately pre-draw state. It conditionally includes sway only when consumed, ignores disabled stale attributes, keeps terminal completeness strict, and adds no GL query, allocation, state mutation, rebind, retry, sleep, synthetic draw, source-shader change, uniform fix or rendering repair. Bundle 69's direct-drawable architecture, Bundle 71's uint-index invariant, the real Diffusion menu/callback/map path, and all unrelated behavior are preserved.

### Validation and rejection results

- The accepted patch chain plus the two new patches applied cleanly to exact pins: Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, GL4ES `81547d986798e876de8b434193920b606a72363f`, and unchanged MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`.
- Source proof places the GL4ES application record immediately before the real native uniform call, the realization record after native `gles_glUseProgram` and before uniform synchronization, and the native record after `realize_glenv`/`realize_bufferIndex` immediately before the real native draw. The terminal completeness mask prevents a match classification before all selected-shader fields exist.
- `scripts/ios/validate-ios-wo49-transform.py` passed Python compilation, positive fixtures and self-tests in full applied-tree and GL4ES-only modes. Fixtures classify application/source, reflection/cache and native-forward mutations at the correct boundary, accept a complete match, require conditional sway only for a sway program, and classify missing data as incomplete rather than full-match.
- Rejection mutations passed for a cap above one, lost pre-realization program observation, a missing terminal-required field, stale-attribute dependency, `glGetError`, added GL mutation, multiple token claims, a bone-weighted selector and producer capture after bone upload. Existing WO49 topology, Bundle-75 index-trace, uint-element and Diffusion iOS policy validators also passed.
- `git diff --check`, patch replay and all build-policy checks passed. The retained macOS CI job built arm64 GL4ES plus the complete engine, Half-Life and Diffusion client/server/menu graph with `XASH_IOS=1`; packaged marker/API and IPA contract validation passed.
- Independent extraction verified `CFBundleVersion=79`, `MinimumOSVersion=12.0`, file sharing enabled, all inspected Mach-O headers as thin arm64, all seven transform marker families in `libref_gl4es.dylib`, and the begin/finish bridge API in both the renderer and Diffusion client.

Expected engine.log markers are exactly: `WO49 transform policy:`, `WO49 transform producer:`, `WO49 transform clip:`, `WO49 transform program:`, `WO49 transform uniform:`, `WO49 transform native:`, and `WO49 transform terminal:`. Output is bounded to the one selected token and one terminal classification.

### Exact files, risks, durability and stop state

Exact implementation files changed: `scripts/gha/build_ios.sh`, `scripts/ios/builddiffusion.sh`, `scripts/ios/diffusion-wo49-transform-ios.patch`, `scripts/ios/gl4es-wo49-transform-ios.patch`, `scripts/ios/validate-ios-wo49-topology.py`, `scripts/ios/validate-ios-wo49-transform.py`, and `scripts/ios/verify_ipa.sh`. This report additionally changes `Documentation/XASH3DIOS_PORTING_STATE.md`. The Diffusion patch affects `engine/studio.h`, `client/render/r_studio.h` and `client/render/r_studio.cpp`; the GL4ES patch affects `src/gl/indextrace.h`, `src/gl/indextrace.c`, `src/gl/uniform.c`, `src/gl/fpe.c` and `src/gl/gl_lookup.c` in the exact pinned build trees.

Single device test requested: none. Phase E explicitly forbids worker contact with Arjun and leaves any later device authorization to the orchestrator.

Remaining risks: no device log has yet shown which terminal classification Bundle 79 produces; the selected token may end incomplete if the exact qualifying draw is not reached; a full application-to-native match would move the boundary into translated/native shader execution without repairing it; the source-observed native-program timing risk is not yet causally established; the separate additive `u_StudioParams` extent violation, foliage float/int upload defect, material/color issues, synchronous shader compilation and later transition termination remain intentionally unmodified; and no device-accepted gameplay candidate exists.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit. Its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 49 Phase E implementation, proof-gate validation, one retained Bundle-79 qualifying workflow/artifact, independent IPA and tempfile readback verification, and both durable-ledger reports are complete. Stop for orchestrator review. Do not request a device test, contact Arjun, ask for logs or evidence, claim a renderer fix, implement a repair, or begin Phase F or any later work order.

## Work Order 49 Phase F - Bundle 81 per-unit texture-realization repair

Candidate/run and acceptance status: **Outcome A. Bundle 81 is build-qualified and awaiting orchestrator review; it is not device-accepted.** Bundle 79 is treated as the failed visual/material input specified by the work order and is not being retested. Phase F proves and repairs one general GL4ES texture-realization defect shared by the audited world/brush and studio draw routes. Bundle 69's direct-drawable architecture, Bundle 71's native-ES3 uint-element invariant, the real Diffusion menu/touch/callback path and all unrelated behavior remain preserved.

### Commit, workflow, artifact and publication

- Implementation commit: `3ff32128a58aed4ad9be571be28f12960ac5ca5c` (`Fix GL4ES per-unit texture realization`).
- Sole retained qualifying workflow: successful GitHub Actions push run `31945009553`, run/bundle number `81`, job `95159557155`, head `3ff32128a58aed4ad9be571be28f12960ac5ca5c`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31945009553`.
- The automatic pull-request twin `31945011577` (run 82) was canceled and is not a candidate. No manual dispatch, retry or second qualifying artifact was created.
- Retained GitHub artifact: `Xash3DiOS-arm64-unsigned`, artifact ID `9263095304`, archive size `8,591,380` bytes, archive digest `sha256:6e94026aeaaf93318bed3c93f999d5cb833b7f80f6a56bd8abc752bf69d5c5d7`, expiry `2026-08-30T11:46:54Z`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31945009553/artifacts/9263095304`.
- Verified IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,689,744` bytes, SHA-256 `A7460886B8D1968A6AC04312660C6E76F0E84F8E0D7999473387047B63BABDA5`.
- Exactly one tempfile.org upload: information page `https://tempfile.org/QFfv3SPoVNs/`; direct download `https://tempfile.org/QFfv3SPoVNs/download`; expiry `2026-08-17T11:50:46.893Z`. API metadata and security readback report the exact filename/size/hash, `safe`, no warning and no suspicious pattern. A separate download reproduces the exact size and SHA-256.

### Verified failure boundary and structural cause

Bundle 79 establishes that the direct-drawable/presentation path works, the sampled rigid studio local position/index stream reaches the intended native program, and the sampled application, GL4ES cache and native transform values match. Its screenshots nevertheless show missing ground, stretched geometry, tan materials, unrelated vehicle/tire imagery on other surfaces and frame-to-frame flicker. The Phase F audit moves the common failure boundary to **logical texture state being converted into native bindings immediately before draw**, after Diffusion has selected its material, sampler unit, target and texture object but before the shared native submission paths consume those bindings.

The exact pinned GL4ES source stores enabled texture-target bits per logical unit in `glstate->enable.texture[unit]`, and `glEnable`/`glDisable` mutate the slot for the active unit. Deferred bindings are also stored per unit and per target in `glstate->texture.bound[unit][target]`. However, `realize_textures()` iterated all changed units while selecting every iteration's target from `glstate->enable.texture[glstate->texture.active]`. It then indexed `bound[i][tgt]` with that aliased target. This is the sole outlier among the audited per-unit state consumers and remains present in upstream GL4ES; it is not introduced by an earlier iOS patch.

The error is structurally causal for the accepted visual class. Diffusion's world route binds color/lightmap/deluxe or cubemap/screen/normal/layer/interior/depth inputs across units 0-6. The studio route binds color/normal/cubemap/interior or blend/colormask inputs across units 0-5. Both correctly select a texture unit, enable that unit's target and bind its object. If the final active unit is a cubemap, the defective realization loop treats pending 2D units as cubemaps; cubemaps are immediately bound and skipped by the deferred 2D binding block, so the correct native 2D object is not installed and a prior object's imagery can be reused. If the final active unit is 2D, those binds may realize correctly. That draw-dependent final-active-target behavior explains cross-object texture reuse and flicker without reopening the already matched uint topology, transform transport or drawable presentation paths.

The general repair changes only the selector in `realize_textures()` from the current active unit to the loop unit: `glstate->enable.texture[i]`. One once-only stable marker, `WO49 texture policy: target-source=per-unit route=all-realize_textures`, describes the packaged policy. Direct drawing, deferred/render-list drawing, blit drawing and all non-draw realization callers already converge on this single function, so the invariant applies to every audited GL4ES route without per-route workarounds, hard-coded texture IDs, material substitutions, retries, feature disabling or draw-order changes.

### Complete audit and out-of-scope findings

- Program/options and sampler assignment: Diffusion chooses coherent world/studio variants and assigns sampler uniforms using its unit-index enum (`0`, `1`, and so on), not OpenGL `GL_TEXTURE0` enum values. No program-key or shader-source repair is justified by Bundle 79.
- Material/texture producer: `GL_Bind` selects the requested unit, derives the target from texture metadata, toggles the old/new target for that unit and submits the target/object. World and studio callers bind the expected material maps. The producer state is per-unit and coherent; corruption enters at realization.
- Logical/native binding: GL4ES defers 1D/2D/3D/rectangle bindings per unit while cubemaps bind immediately. The old cross-unit target alias can therefore suppress or misselect the deferred native binding; the repair restores the recorded unit/target/object invariant.
- UVs and texture matrices: world VBO/VAO texture coordinates and studio packed texture coordinates use stable descriptors already covered by the accepted topology path. The respective texture matrices are explicitly loaded or reset. No evidence correlates Bundle 79 with a UV producer change.
- Texture uploads: Diffusion's load/allocation/process/upload chain supplies target, dimensions, format/type and compressed/raw data; its bounds checks and GL4ES metadata tracking were audited. The accepted evidence contains no upload-payload discriminator and does not justify format conversion or asset replacement.
- Fixed-function state: blend, depth, cull, color/depth masks and active program state are set per route. None assigns another object's texture to a surface, and no correlated failure was found.
- `u_StudioParams` active extent and the foliage integer-to-float submission remain source-proven defects, but neither explains unrelated texture reuse across both world and studio routes. They remain deliberately unmodified, as do the separate capability/asset warnings, shader latency, memory policy and later map-transition boundary.

### Validation, exact files and stop state

Why the fix addresses the structural cause: each iteration now derives target priority from the same unit whose per-target binding is read and whose native active unit/object is realized. A two-unit positive fixture proves that a pending unit-0 2D object is realized even when the final active unit is a cubemap; the former active-unit policy is rejected because it suppresses that bind. Reverse and three-target fixtures prove the rule is genuinely per-unit rather than hard-coded to unit zero or 2D.

Validation performed: authoritative-ledger and accepted Bundle 79 evidence read; Codebase Memory-first architecture/symbol/call-path inspection followed by exact pinned source inspection; full Diffusion world/studio material, unit, target, sampler, UV/matrix, uniform, texture-upload and fixed-state trace; GL4ES logical bind, enable, deferred target/object, direct/deferred/list/blit and native realization trace; upstream-source control; exact patch-chain replay against GL4ES `81547d986798e876de8b434193920b606a72363f`; exact Diffusion policy replay against `14d156bf3a6993c172697fac83a937836c3b5561`; positive fixtures and rejection mutations for active-unit alias, unit-zero alias, active binding alias, absent marker and missing direct/list/blit realization routes; existing uint-element, index-trace, topology, transform and Diffusion iOS policy suites; and `git diff --check`.

The sole retained macOS run applied all exact pins including unchanged MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, passed the new positive/rejection suite, retained the shared animated-model/one-bone-rigid shader policy, built the complete engine/Half-Life/Diffusion client/server/menu/SDL/GL4ES graph with `XASH_IOS=1`, passed the IPA contract and uploaded one artifact. Independent artifact inspection verifies `CFBundleVersion=81`, `MinimumOSVersion=12.0`, file sharing enabled, the policy marker present, and 13 of 13 Mach-O files thin arm64.

Exact implementation files changed: `scripts/ios/gl4es-wo49-texture-unit-ios.patch`, `scripts/ios/validate-ios-wo49-texture-unit.py`, `scripts/gha/build_ios.sh`, and `scripts/ios/verify_ipa.sh`. This report additionally changes `Documentation/XASH3DIOS_PORTING_STATE.md`. The runtime patch changes only exact pinned GL4ES `src/gl/texture_params.c`.

Expected new engine.log marker: `WO49 texture policy: target-source=per-unit route=all-realize_textures`. Existing Bundle 69, 71, 77 and 79 marker/API contracts remain packaged. Single device test requested: **none**. This worker does not request a Bundle 79 retest or any Bundle 81 test; only the orchestrator may authorize later device action.

Remaining risks: Bundle 81 has not been device-tested or accepted; the per-unit repair may expose separate material/UV/upload or uniform defects after stale native binding is removed; missing assets/capability fallbacks may still omit surfaces; the additive studio extent and foliage type defects remain; shader compilation latency and the later transition boundary remain separate; and no device evidence yet proves the repaired output. None authorizes an additional patch, workflow, upload, user contact or test request.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit after the qualifying build; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash.

Stop state: Work Order 49 Phase F Outcome A implementation, validation, sole retained Bundle-81 workflow/artifact, independent IPA/tempfile readback and both durable-ledger updates are complete. **Stop for orchestrator review.** Do not contact Arjun, request evidence or testing, request a Bundle 79 retest, interpret Bundle 81 device behavior, modify code, run another workflow, create another artifact/upload, or begin Phase G or any later phase.

## Work Order 50 Phase A - consolidated landscape and material-state audit

Candidate/run and acceptance status: **Outcome C; audit only. No candidate, build, workflow, IPA, upload, or device-test request was authorized or produced.** Bundle 81 remains not fully device-accepted, but its per-unit texture-target repair is device-supported and retained. Bundle 69 direct-drawable presentation, Bundle 71 native-ES3 uint indices, the real Diffusion menu/touch/callback/map route, and all other previously accepted fixes remain unchanged.

### Verified boundaries and decision

The two Bundle-81 visual classes have independent source-proven boundaries:

1. **Missing road/ground/landscape: capability/architecture boundary.** Diffusion checks the literal `GL_EXT_texture_array` capability before loading landscapes. The pinned GL4ES does not advertise that extension and, more importantly, has no distinct texture-array target state, array allocation/upload implementation, `sampler2DArray` reflection, or `texture2DArray` shader-conversion route. Its exported 3D aliases call 2D operations while discarding the caller's depth/z semantics. This is Work Order 50 classification **A5: the required implementation is genuinely absent**, not an extension-string-only A1/A4 defect.
2. **Flat tan/yellow or flickering studio materials: application-producer cache lifetime.** Diffusion's studio renderer retains member-level texture/material cache values across draws, while every studio draw ends with engine `GL_CleanUpTextureUnits(0)`. Cleanup invalidates the engine's actual logical texture bindings but does not invalidate Diffusion's private `cached_texture`, `cached_normalmap`, `cached_cubemap`, or related material cache. A later draw with the same shader and base texture number can therefore skip the required `GL_Bind` calls after cleanup or intervening world/postprocess work. Bundle 81 correctly realizes every bind it receives; this remaining defect is above GL4ES and can prevent a bind from being issued at all. The cache key also uses the base `iTexnum`, not every selected animated/monitor/drone frame texture identity, so dynamic sources can be skipped independently.

Outcome C is selected because the pinned GL4ES architecture genuinely cannot transport the landscape array resource. The independent yellow-material audit nevertheless proves a separate, bounded general studio cache-lifetime defect plus two narrower uniform defects. Phase A documents their ownership boundaries only; it does not authorize any repair.

### Landscape capability and dispatch table

| Stage | Exact source behavior | Classification |
| --- | --- | --- |
| Diffusion application check | `client/render/r_opengl.cpp` requires literal `GL_EXT_texture_array`; failure emits `Warning: GL_EXT_texture_array not supported. Landscapes will be unavailable.` | Correctly detects that the wrapper exposes no usable route; changing only this check would be unsafe. |
| Engine capability gate | `ref/gl/gl_opengl.c` requires the extension plus 3D texture functions; `GL_LoadTextureArray` in `ref/gl/gl_image.c` returns texture 0 when `GL_TEXTURE_ARRAY_EXT` support is absent. | Allocation is rejected before layer upload. |
| GL4ES advertisement | `BuildExtensionsList` in pinned `src/gl/getter.c` contains no `GL_EXT_texture_array` entry or live-context conditional addition. | Not advertised. |
| GL4ES entry points | Core/EXT `glTexImage3D`, `glTexSubImage3D`, and copy aliases are exported and found by `gl_lookup.c`, but pinned `texture_3d.c` forwards them to 2D calls and drops depth/z behavior. | Alias exists; array semantics do not. This rules out A2 as the complete explanation. |
| GL4ES target/object state | `texture.h`, `what_target`, `to_target`, bind/enable logic, and Bundle-81 `realize_textures` know 1D, 2D, 3D, rectangle, and cube targets only. `GL_TEXTURE_2D_ARRAY` falls into non-array behavior; no per-object layer lifecycle exists. | Native array object cannot be represented or realized. |
| GL4ES shader/reflection | Pinned shader conversion has no `sampler2DArray`/`texture2DArray` handling, emits the ESSL-100 path, and program reflection classifies 2D and cube samplers only. | Array shader cannot be converted, reflected, or bound correctly. |
| Native context | The accepted Bundle-71 proof establishes the live native GLES3 path and 32-bit element-index support. GL4ES performs live-context hardware discovery during initialization, but never turns that capability into the complete array route above. | Native capability alone is insufficient; wrapper transport is missing. |
| Actual Diffusion use | No diffuse array object is returned, landscape faces are not mapped as `SURF_LANDSCAPE`, and terrain array shader/draw submission is never reached. | First blocking boundary is application capability/allocation through absent GL4ES architecture, before native array upload/draw. |

Initialization timing is not the defect by itself. GL4ES initializes the native library/context capability record before its lazy extension string is consumed, and parses texture-related configuration, but there is no conditional implementation to enable. Advertising the name or aliasing the enum without target storage, allocation/upload, sampler reflection, and an ESSL-300-compatible shader route would move the failure downstream and violate the structural gate.

### Landscape resource and draw-family table

| Resource/path | Target, format, layers and upload | Sampler/shader use | Draw/material family and observed boundary |
| --- | --- | --- | --- |
| Landscape index/height map | Ordinary 2D image loaded by `LoadHeightMap`; pixels are retained for face classification. | 2D height/index sampler in the terrain-capable brush shader. | Loads independently, but cannot activate multilayer faces without a diffuse array. |
| Landscape diffuse layers | Individual layer materials are resolved, then `LOAD_TEXTURE_ARRAY` requests one layered diffuse object. `GL_LoadTextureArray` returns 0 at the capability gate. | Terrain GLSL declares `sampler2DArray` and calls `texture2DArray`; the solid path binds the diffuse array on its terrain material unit. | Affects lightmapped/solid world and brush landscape faces, including road/ground faces assigned to the same BSP landscape group. |
| Landscape normal layers | Optional normal maps are assembled as a second array. | Terrain normal-array sampling is used by the terrain-capable solid/dynamic-light variants on their assigned normal-array unit. | Same landscape surface families; also unreachable without the diffuse array. |
| Face classification | `R_LoadLandscapes` parses `maps/<map>_land.txt`, loads index/diffuse/layer metadata, calls `LoadTerrainLayers`, then currently marks the terrain record valid without checking its false return. `Mod_MappingLandscapes` later refuses to set `SURF_LANDSCAPE` when `gl_diffuse_id == 0`. | Successful mapping would add the terrain options to the brush shader key. | The unchecked return is a general bookkeeping defect, but the downstream guard prevents array shader/draw use; it is not a compatibility implementation. |
| Solid/lightmapped terrain | Would bind the diffuse array, index/height map, optional normal array, lightmap/deluxe and other canonical material inputs. | `BmodelSolid` terrain/multilayer variants consume the array samplers and landscape coordinates. | Unreachable on this architecture. |
| Projected/omni dynamic-light terrain | Reuses the same terrain arrays with dynamic-light inputs. | `BmodelDlight` terrain/multilayer variants consume the same layered resources. | Unreachable on this architecture. |
| Grass/foliage | Grass separately consults texture-array capability for an optimized family, but is not the road/ground landscape face mapper. | Separate vegetation shaders and draw path. | Capability may affect vegetation behavior, but it does not explain the landscape face gate or all yellow objects. |

No separate road renderer was found. Roads and terrain are ordinary BSP world/brush surfaces associated with landscape face information and therefore share the same array allocation, face mapping, shader-key, sampler, and draw path. Once the diffuse array is zero, those surfaces retain the non-landscape/base BSP path; depending on the authored assets and surrounding visibility, the device can show missing road/ground or sky/void beneath vehicles.

### Smallest future landscape compatibility boundary (not implemented)

The smallest structurally complete path is a GL4ES GLES3 array passthrough, not an extension-string workaround or asset substitution:

- after live native GLES3 capability discovery, add a distinct `GL_TEXTURE_2D_ARRAY` target through texture-object creation, per-unit enable/bind state, allocation, layer upload/subupload, deletion, queries, and Bundle-81's per-unit realization invariant;
- load and call the native GLES3 3D allocation/subimage entry points with preserved target, depth, z offset, internal format, mip, and layer limits;
- add `GL_SAMPLER_2D_ARRAY` program reflection and sampler-unit handling;
- translate the desktop `sampler2DArray`/`texture2DArray` shader route through a coherent ESSL-300-compatible vertex/fragment pipeline, including attributes/varyings and fragment output syntax, rather than inserting one unsupported token into the ESSL-100 converter;
- advertise `GL_EXT_texture_array` only when that entire live-context route is available; and
- make Diffusion mark a terrain record valid only when `LoadTerrainLayers` succeeds, so metadata matches resource lifetime.

Atlas emulation is larger and riskier because it must rewrite shader coordinates and handle mip filtering, layer boundaries, wrap modes and bleed. No source evidence justifies asset downscaling, substitution, disabling landscape, or bypassing Diffusion's material classification.

### Yellow-material hypothesis matrix

| Hypothesis | Source/evidence result | Scope/judgment |
| --- | --- | --- |
| Intentional yellow/debug output | The terrain shader contains a yellow-ish layer-debug palette helper, but no production caller was found, and the landscape array route never reaches that shader. Frustum yellow is explicit debug geometry. | Rejected as the general Bundle-81 material result. |
| Stable fallback or missing texture | Default/white/gray/fallback textures exist for missing assets, fullbright/lightmap policy, or explicit material fallback. They are deterministic absent state variation. | Can explain an individual stable material, not cross-frame loss/recovery by itself. |
| Residual Bundle-81 per-unit target alias | The fixed `realize_textures()` now selects target and object from the same unit on all audited realization callers. No contrary source evidence was found for an issued 2D bind. | Bundle 81's restored cliff/building textures are positive device evidence that this repair is valid and must be preserved. |
| Studio producer skips texture binds | Member texture/material caches survive `GL_CleanUpTextureUnits(0)`, even though cleanup invalidates engine bindings. Same shader/base texture can suppress base, normal, interior/blend or cubemap binds; dynamic texture identity is incompletely keyed. | **Source-proven general studio material-state defect; best structural explanation for intermittent flat/wrong/flickering studio materials.** Boundary is before engine `GL_Bind` and GL4ES. |
| `u_StudioParams` over-count | Producer always uploads three vec4s, while optimized additive variants can expose only one or two active elements. Pinned GL4ES rejects `count > active size` with `GL_INVALID_OPERATION` before cache/native mutation. | Proven subset defect affecting additive studio view/chrome/fog parameters; not a complete explanation for broad diffuse texture loss. |
| `u_FoliageSwayHeight` type mismatch | Packaged iOS shader declares float. Solid studio foliage still uses the integer uniform call; dlight/depth use float calls. | Proven vegetation-specific vertex-sway defect, not a general material-color path. |
| Shader-cache key omission | Material option keys cover the broad static variant features, but studio bind caching keys base texture number rather than every actual animated/monitor/drone selected object. | Contributes to dynamic studio texture staleness; no evidence that compiled shader programs themselves alias unrelated option sets. |
| Failed native upload/format | Audited loaders carry texture metadata and bounds; accepted evidence contains no allocation/upload error discriminator for the yellow objects. | Unproven for this class; array upload absence is Track A, not the existing 2D studio route. |
| Memory pressure | Bundle-81 log has no OOM, allocation failure, memory warning, or Jetsam discriminator. | Unsupported. Do not introduce memory limits, purges, or downscaling. |

The representative studio path is: material load and optional maps/animation -> shader option/cache selection -> `DrawStudioMeshes` producer values -> base/animated/monitor/drone texture selection plus normal/cubemap/interior/blend/colormask units -> engine `GL_Bind` target/object bookkeeping -> GL4ES logical deferred state -> Bundle-81 per-unit native realization -> draw. The proven first divergence is the application producer's decision to skip some `GL_Bind` calls using a stale private cache after engine cleanup; it is not GL4ES re-aliasing a bind that was actually submitted.

### Per-variant `u_StudioParams` audit

The source declarations reserve `u_StudioParams[3]`; index 0 carries view origin and real time, index 1 carries view-right data for chrome, and index 2 carries fog data for non-additive variants. `DrawStudioMeshes` unconditionally calls `pglUniform4fvARB(location, 3, ...)`. Native link optimization changes the active extent by variant, and pinned GL4ES rejects an over-count rather than partially applying it.

| Studio solid variant | Declared extent | Native active extent | Producer call/count | Error semantics and downstream scope |
| --- | --- | --- | --- | --- |
| Non-additive, with or without chrome | 3 vec4 | 3 (fog keeps trailing element active) | `glUniform4fv`, count 3 | Valid; indices 0-2 reach native state. |
| Additive without chrome | 3 vec4 | 1 (observed scalar/base location in accepted shader evidence) | `glUniform4fv`, count 3 | GL4ES `GoUniformfv` rejects count greater than reflected size with `GL_INVALID_OPERATION`; view/realtime update can remain stale. |
| Additive with chrome | 3 vec4 | 2 | `glUniform4fv`, count 3 | Same rejection; view/realtime and chrome/view-right update can remain stale. |

This is a bounded subset defect. It can affect additive studio view/chrome/fog-derived rendering and explains a recurring GL error, but it does not issue, select, or bind the diffuse texture and cannot alone explain broad non-additive or world material flicker.

### Competing-hypothesis rejection matrix

| Competing explanation | Bundle-81/source discriminator | Result |
| --- | --- | --- |
| Bundle-81 repair is wrong or should be reverted | Cliffs and buildings retain correct textures after the repair; exact source now preserves per-unit target/object selection. | Rejected; partial success is affirmative evidence. Preserve it. |
| Landscape is another manifestation of the old unit-target alias | The device log emits the explicit extension failure; allocation returns zero before landscape mapping and shaders. | Rejected. Distinct capability/architecture class. |
| Advertising one extension string is sufficient | Target state, layered upload semantics, array sampler reflection, and shader conversion are all absent. | Rejected as a downstream whack-a-mole change. |
| Missing landscape assets alone | The first deterministic boundary occurs before layer use because capability is absent. Asset warnings may be secondary but do not remove the architecture gate. | Not the primary cause. |
| Yellow is the terrain debug palette | Landscape faces never reach the terrain shader, and the helper is not on a production call path. | Rejected. |
| Yellow is remaining GL4ES cross-unit aliasing | No new source defect exists for issued 2D binds after Bundle 81; the device improved. Diffusion can skip issuing binds after its private cache outlives cleanup. | Rejected for the fixed route; application cache lifetime is the stronger remaining boundary. |
| `u_StudioParams` explains every yellow object | Only additive optimized variants reject the count; it does not control diffuse sampler binding. | Proven subset, rejected as complete cause. |
| Foliage uniform explains every visual class | Mismatch is confined to solid foliage sway position. | Proven subset, rejected as general material/landscape cause. |
| Resource pressure causes material loss | No OOM/allocation/Jetsam/memory-warning evidence exists; landscape failure is deterministic during capability setup. | Unsupported. |
| Startup shader compilation is the visual failure | `GL_FindUberShader` compiles/link variants synchronously on first use, so it can delay first presentation, but accepted frames continue and the visual classes persist. | Separate performance track, not the landscape/material-state cause. |

### Performance/memory classification, validation and future evidence

Startup delay remains consistent with synchronous, on-demand `GL_FindUberShader` compilation/linking and the accepted sequence of `CompileUberShader` markers. The existing evidence does not establish memory pressure: it contains no OOM, failed allocation, memory warning, Jetsam, or termination discriminator. A future evidence review could distinguish the classes by correlating timestamp gaps around compile markers and continued frame markers against explicit allocation failures, iOS memory-warning callbacks, or Jetsam/termination records, but Phase A requests no evidence and authorizes no test.

Validation performed: newest authoritative Google Docs ledger and complete Bundle-81 evidence/constraints read; Codebase Memory-first architecture, symbol and caller/callee trace; exact-source inspection of pinned Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, GL4ES `81547d986798e876de8b434193920b606a72363f`, engine executable `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, and unchanged MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`; applied iOS patch inspection including Bundle-81 and shader policy; end-to-end capability, allocation/upload, mapping, shader/sampler, material, bind/cache, realization and draw trace; accepted-log/source comparison; and competing-hypothesis rejection. No runtime/source/build-policy file was edited and no build was run.

Expected new log markers: **none**; this phase adds no instrumentation or runtime change. Exact file changed: `Documentation/XASH3DIOS_PORTING_STATE.md` only. Workflow/artifact/IPA/tempfile: **none**. Single device test requested: **none**.

Remaining risks: the landscape compatibility path requires a coherent GLES3 shader and texture-array architecture, not a bounded one-line alias; a future studio-cache repair must invalidate/re-key all material texture families without regressing animation or Bundle-81 realization; the additive `u_StudioParams` and foliage-call defects remain independently real; missing assets could remain after capability is added; shader compilation latency and the later ch1map0-to-ch1map1 termination remain separate; and no repair or candidate is authorized by this audit.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a commit cannot contain its own hash.

Stop state: Work Order 50 Phase A Outcome C source audit and durable report are complete. **Stop for orchestrator review.** Do not modify renderer/runtime code, build, start GitHub Actions, create an IPA/artifact/upload, contact Arjun, request evidence/testing, or begin Phase B or any later phase.

## Work Order 50 Phase B - Outcome B architectural proof gate

Candidate/run and acceptance status: **Outcome B. No candidate was built or published.** The required complete GLES3 texture-array route cannot be bounded inside the exact pinned GL4ES architecture while satisfying Work Order 50's native proof, lifecycle, shader-conversion, preservation, and all-or-nothing requirements. The separately bounded studio cache, `u_StudioParams`, and foliage repairs are deliberately not implemented because Phase B forbids a partial or studio-only candidate.

### Authorization and preserved baseline

The complete authoritative Google Docs ledger was read through its newest entry, `WORK ORDER 50 PHASE B - CONSOLIDATED TEXTURE-ARRAY AND MATERIAL-STATE STRUCTURAL REPAIR`. The authorized scope was one coherent repair containing all four proven classes: complete native GLES3 texture arrays through GL4ES; studio texture-cache invalidation and actual-object keying; exact per-variant `u_StudioParams` counts; and the solid foliage float upload. The gate permits Outcome A only after the entire route passes native/source proof, otherwise Outcome B requires stopping before a build.

The audit began from clean branch `agent/ios-proof-of-life` at `f7a5b4bae2c22ae616827dbb22d00386f78d2f81`. Exact source pins were verified directly: engine/executable `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, Diffusion MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, and GL4ES `81547d986798e876de8b434193920b606a72363f`. Bundle 69 direct-drawable presentation, Bundle 71 native GLES3 uint indices, Bundle 81 per-unit target selection, the real Diffusion menu/touch/callback/map path, and all unrelated accepted behavior remain byte-for-byte unchanged.

### Exact first unbounded boundary

The first unavoidable boundary is **GL4ES program conversion/linking**, owned by `src/gl/shaderconv.c::ConvertShader`, before a terrain program can reflect or sample an array:

- Diffusion `client/render/r_shader.cpp::GL_ProcessShader` generates `#version 130` source. Terrain-capable `BmodelSolid` and `BmodelDlight` fragments combine `sampler2DArray`/`texture2DArray` with legacy `attribute`, `varying`, `gl_FragColor`, `texture2D`, `texture2DProj`, and `textureCube` constructs.
- Pinned `ConvertShader` unconditionally selects `GLESHeader[0]`, emitting `#version 100`. Its only higher-version selection block is compiled out under `#if 0` with the source comment that higher GLSL support "requires much more work." Even if enabled unchanged, it recognizes only source version `120`, not Diffusion's `130`.
- The dormant ESSL-300 header defines `varying` as `out` for both stages. Fragment varyings must be `in`; it also supplies no declared fragment output for `gl_FragColor` and no ESSL-300 conversion for the legacy texture lookup family. Therefore it is incomplete scaffolding, not a hidden usable array path.
- `ConvertShader` is the common 833-line translator used by every linked application program, with fixed-function builtin insertion, varying accounting, matrix rewriting, shader-key needs, and program redo compatibility. A source-name or Diffusion-only textual exception would not establish a coherent GL4ES capability and would violate the required unsupported-combination rejection contract.

This boundary alone prevents the required ESSL-300 conversion, native link, and native sample fixture. It is not repairable by extension advertisement, enum aliases, or a local sampler token replacement.

### Additional architecture that would have to change as one subsystem

The source audit confirms that reaching the first boundary would still leave multiple coupled, currently absent facilities:

| Ownership | Exact pinned state | Required architectural change |
| --- | --- | --- |
| `src/gl/texture.h`, `state.h`, `stack.[ch]` | `ENABLED_TEXTURE_LAST` contains 1D/2D/3D/rectangle/cube only; bound and saved state are dimensioned by that enum. | Add a distinct array object/target through creation, saved state, queries, push/pop, cleanup, deletion, and restoration. |
| `src/gl/texture_3d.c`, `gles.h`, `loader.[ch]` | Exported core/EXT 3D entry points are stubs that forward to 2D and discard depth/zoffset; no native `glTexImage3D`/`glTexSubImage3D` loader signatures exist. | Add verified native GLES3 ABI loading plus full allocation/subupload/error/unpack semantics. |
| `src/gl/texture_params.c`, `glstate.[ch]`, `blit.c` | Bundle 81 correctly picks each loop unit, but the actual native cache remains one `actual_tex2d` value per unit and realization always calls native `GL_TEXTURE_2D`. | Introduce target-aware actual bindings and extend every direct/list/blit/cleanup/restoration route without regressing Bundle 81. |
| `src/gl/program.[ch]`, `uniform.c`, `fpe.c` | Reflection and uniform-type handling recognize only `GL_SAMPLER_2D` and `GL_SAMPLER_CUBE`; texture-unit routing assumes those enum-to-target cases. | Add array sampler reflection, type validation, unit assignment, FBO conflict handling, cache, sync, and native realization. |
| `src/glx/hardext.[ch]`, `src/gl/init.c` | The NOEGL iOS build tests a singleton current context; `hardext.esversion` remains the ES2 backend selection and only special cases individual ES3 core features. No array capability/limits or reset lifecycle exists. | Add post-current-context entry-point/limit discovery and an explicit reset/re-establish contract. |
| SDL/GL4ES lifecycle bridge | SDL owns EAGL context creation, currentness, resize, foreground/background, and destruction; GL4ES has no array-capability lifecycle callback. | Add a cross-component lifecycle API while preserving Bundle 69 drawable ownership and invalidating all target/program capability state safely. |
| Native proof infrastructure | Existing iOS validators are deterministic source/model fixtures. The workflow cross-compiles an iPhoneOS arm64 payload but has no simulator/device GLES3 array execution harness. | Create and validate a real current-context allocation/subupload/mixed-unit/link/sample/readback harness before any candidate build. |

The engine side already routes multilayer images through `ref/gl/gl_image.c::{GL_LoadTextureArray,GL_UploadTexture,GL_TextureImageRAW}`; Diffusion already provides the terrain layer data and array sampler declarations. Those consumers do not remove the missing GL4ES translator, object, loader, reflection, native-state, and lifecycle ownership.

### Why Outcome A cannot satisfy the local/source proof

Work Order 50 requires, before a candidate build, deterministic native proof of layer 0, layer 1 and highest-layer content; nonzero-layer subupload; mip behavior; mixed 2D/cube/array units; cleanup/rebind; native array reflection/link/sample; and context invalidation/re-establishment. The repository has no executable iOS simulator/device harness for those operations, and the current Windows worker cannot execute the iPhoneOS arm64 OpenGLES payload. Static Python models cannot prove native EAGL allocation, link or sampling and therefore cannot be represented as satisfying the gate.

Adding only the bounded studio repairs would leave the required array route and landscape visual gate unresolved. Building that subset, advertising the extension, or producing a diagnostics candidate is explicitly forbidden. No runtime, patch, shader, build-policy, workflow, validator, IPA, or upload file is changed.

### Smallest defensible architectural alternative

Treat GLES3 texture arrays as a separately owned renderer subsystem before another gameplay candidate: first adopt or develop a GL4ES baseline where ESSL-300 stage conversion, true array objects/uploads, array sampler reflection/routing, target-aware native binding caches, context lifecycle, and a simulator/device conformance harness are first-class and validated together. Only after that subsystem passes the Work Order 50 array fixtures should it be integrated with the preserved Bundle 69/71/81 patch stack and the three bounded Diffusion studio fixes in one candidate. Patching the pinned ES2-oriented translator in-place without that conformance project is not a bounded porting repair.

This alternative does not authorize a GL_TEXTURE_2D fallback, atlas, asset substitution, terrain disable, source-name shader exception, string-only advertisement, or partial studio IPA.

### Proof-gate validation and publication state

Validation performed: full authoritative-ledger read and newest-order check; Codebase Memory-first architecture, symbol, caller/callee and ownership inspection; exact applied-tree inspection at all five pins; Diffusion terrain source generation, shader family and resource path trace; GL4ES target/object, upload stub, native loader, extension discovery, program conversion, reflection, uniform, realization, stack/state and context-lifecycle trace; established workflow/native-test capability audit; and competing Outcome-A proof requirements checked one by one. The source/apply trees were read only.

Candidate/bundle: none. Behavioral/build commit: none. Workflow URL/ID/result: none. Duplicate workflow disposition: none. GitHub artifact: none. IPA filename/size/SHA-256: none. tempfile page/direct URL/expiry: none. Expected runtime markers: none, because no executable changed.

Exact file changed by this Outcome-B handoff: `Documentation/XASH3DIOS_PORTING_STATE.md` only. This report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a commit cannot contain its own hash.

Remaining independent risks: Bundle 81 remains only partially device-accepted; landscape remains unavailable; the studio private-cache lifetime/key defect, exact 1/2/3 `u_StudioParams` producer counts, and solid foliage float upload remain source-proven but intentionally unfixed; synchronous shader compilation latency and the later ch1map0-to-ch1map1 termination remain separate; and no gameplay candidate is accepted.

Stop state: **Work Order 50 Phase B stops at Outcome B before implementation or build.** Do not contact Arjun, request evidence or device testing, publish a partial IPA, implement a studio-only subset, advertise texture arrays partially, or begin Phase C or any later phase. Stop for orchestrator review.

## Work Order 51 Phase A - Outcome B architecture selection

Candidate/run and acceptance status: **Outcome B; audit complete, no candidate.** A complete Diffusion terrain route remains migration-scale under every audited architecture. The three independent material-state defects are source-proven, bounded, and suitable for one future consolidated candidate, but that candidate requires explicit Phase B authorization.

### Authorization, baseline and accepted boundary

The authoritative Google Docs ledger was read through its newest complete entry, `WORK ORDER 51 PHASE A - TERRAIN ARCHITECTURE SELECTION AND MATERIAL-STATE SEPARABILITY AUDIT`, before this audit. Work Order 50 Phase B's accepted boundary remains controlling: the exact pinned GL4ES cannot acquire coherent Diffusion GLSL-130 `sampler2DArray` support through a bounded converter patch. This phase therefore compares complete architectures; it does not reopen isolated `ConvertShader` edits.

The audit began from clean `agent/ios-proof-of-life` commit `2bcefe584073c445a0666d30dc511f2992fb69cf`. Immutable project pins remain engine/executable `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, and GL4ES `81547d986798e876de8b434193920b606a72363f`. Bundle 69 direct-drawable ownership, Bundle 71 native GLES3 32-bit indices, Bundle 81 per-unit target selection, and the accepted Diffusion menu/touch/callback/map path were read only and remain unchanged.

The terrain semantics that an architecture must preserve are concrete. Diffusion accepts up to 16 landscape materials. `LoadHeightMap` packs four material weights per RGBA layer, giving up to four layers in the weight-map array. `LoadTerrainLayers` creates diffuse and, when complete, normal-map arrays. Engine `GL_LoadTextureArray` enforces compatible inputs, resamples raw layers to one size, retains all mips, marks the result multilayer, and routes it through three-dimensional allocation/subupload. Terrain solid and dynamic-light shaders select all 16 diffuse/normal layers and four weight layers while sharing existing lightmap and material units. A complete replacement must preserve those layer, mip, filtering, repeat, normal/specular, dynamic-light, mixed-target, reflection, context and presentation semantics.

### Required architecture comparison

| Route | First structural boundary | Semantic/proof result | Bundle compatibility, rollback and maintenance | Decision |
| --- | --- | --- | --- | --- |
| Diffusion-side atlas or multiple samplers at the existing five pins | Up to 16 diffuse, 16 normal and four weight textures must coexist with existing material/lightmap units; the GLES3 minimum fragment-unit budget cannot represent that as one equivalent pass. An atlas instead owns new packing, coordinate, derivative, gutter and mip policy. | Multipass changes lighting, blending and ordering. An atlas must generate every mip with per-layer gutters, preserve repeat without cross-layer bleed, and avoid `fract`-induced derivative discontinuities. The pinned ESSL-100 route has no proven complete gradient-based substitute. Runtime conversion could be deterministic/reversible, but no existing packer, cache lifecycle or visual conformance suite proves it. Offline asset mutation is outside the accepted source/pin policy. | It can theoretically preserve Bundle 69/71/81, but it couples engine upload/cache policy to all Diffusion terrain shader families and introduces a long-lived port-specific renderer subsystem. A safe rollback is possible only after that subsystem is isolated and conformance-tested. | **Not bounded for a gameplay Phase B.** Retain only as a migration research branch, not an IPA diagnostic. |
| Proven GL4ES fork migration | Exact current Android lineage: `sandstranger/com.mobilerpgpack.phone` `983964fefe89ab0402f74415512536aa89cea680`, with NG-GL4ES submodule `sandstranger/NG-GL4ES` `204c496068da3e5717b6163efd3d35ac56492676` and legacy GL4ES `cbc1d8599bbe4c4e106d4aee9818ecb3144a5160`. Comparison heads are Sisah2 Openmw3 `72d0029baf1de0b6a85244680316132a4c244164` and current Duron27 Openmw3 `e176d7395689c61c7cf242b89f1e50854baef922`; the previously recorded Duron27 `8eca1a14` is no longer resolvable and cannot serve as a pin. | The exact NG fork has genuine GLES3 `glTexImage3D`, subupload and storage entry points plus a glslang/SPIR-V/SPIRV-Cross shader route. It still maps `GL_TEXTURE_2D_ARRAY` through 2D/default target state, lacks array-sampler reflection/uniform routing, and contains application-specific final-source fixups. Its manual init creates and probes a separate EGL pbuffer once; it does not prove re-probe/reset against the later SDL-owned drawable context. No immutable lineage supplies Diffusion's complete layer/mip/mixed-target/reflection/context fixtures. | It is useful differential evidence but cannot be dropped under the accepted patches. It changes shader conversion, native loader, target state, cache, initialization and lifecycle ownership together. Preserving Bundle 69 requires removing or redesigning fork EGL ownership; Bundle 71/81 must be revalidated route by route. Rollback is clean only as a separately pinned translator migration. | **Migration candidate, not proven terrain solution.** First require an immutable fork and conformance milestone; do not produce a terrain IPA yet. |
| Native GLES3 backend in Xash/Diffusion at the existing engine and Diffusion pins | Xash `GL_InitExtensionsGLES` explicitly lacks texture arrays/3D textures, and `gl2_shim` documents fixed-function, client-array, quad and matrix limits. Engine and Diffusion still use immediate mode, desktop matrix/fixed state, legacy shader builtins and desktop/ARB dynamic entry points across world, studio, sprites, effects and UI. | A real backend must replace the complete engine and custom-renderer GL contract, emit/link ESSL-300 shaders, implement arrays and mixed targets, and own current-context capability/lifecycle validation. This can ultimately provide exact native semantics, but no bounded adapter or native conformance harness currently covers all consumers. | Direct drawable ownership can be preserved by design, and legacy GL4ES can be retained as a rollback backend. However, the development and maintenance boundary is a whole renderer backend rather than a terrain repair; every Bundle repair becomes a porting invariant to re-prove. | **Architecturally clean long-term option, but migration-scale.** Not a bounded Phase B. |
| Complete the pinned GL4ES control route at `81547d986798e876de8b434193920b606a72363f` | Accepted Work Order 50 proof: ESSL-100-only active conversion; incomplete dormant ESSL-300 header; no distinct array target/object state, native 3D ABI/realization, array sampler reflection/routing, context lifecycle contract or native proof harness. | Closing every layer requires a coherent translator/backend subsystem and native simulator/device tests for allocation, nonzero-layer subupload, mips, mixed targets, reflection, sampling and context recreation. Extension advertisement, enum aliases, source-name exceptions and 2D fallback all fail rejection fixtures. | It could retain the current patch stack, but the change surface and maintenance burden are equivalent to creating a new GL4ES backend generation. Partial rollback is unsafe because target, program and lifecycle state are coupled. | **Rejected as bounded control.** Work Order 50's accepted boundary stands. |

No route closes every required semantic layer with an immutable, testable, rollback-safe implementation small enough for the next gameplay candidate. This is not a claim that terrain is impossible; it is a proof that terrain needs an explicit migration program before it can satisfy the established one-candidate gate.

### OpenMW/NG-GL4ES differential

The current Android lineage was inspected at the exact commits above rather than relying on mutable branch names. Its application initializes NG-GL4ES manually for a GLES-300 target before launching the engine and packages both NG and legacy translators. NG compiles with `DEFAULT_ES=3`, glslang, SPIR-V Tools and SPIRV-Cross. Shader source can pass through legacy-to-3XX rewriting, SPIR-V translation and final ad-hoc ESSL fixups before native `glShaderSource`; cache hits can bypass conversion. That is materially more capable than the pinned GL4ES converter, but it is not a general completeness proof.

The positive differential is true native 3D allocation/subupload/storage loading. The negative differential is decisive for this workload: no distinct 2D-array target in the core target map, no `GL_SAMPLER_2D_ARRAY` program-reflection or uniform-type route, and no established mixed-unit cleanup/restore invariant. Initialization also probes capabilities in its own EGL pbuffer and retains a one-time tested state, whereas Bundle 69 requires SDL to own the drawable/current context. A migration must therefore specify source-before conversion, converted source, final native source, cache identity, array object state, reflected uniform types, per-unit realization, context loss/recreation and presentation ownership; merely adopting the converter files or compile flags is not sufficient.

### Separate terrain migration roadmap

Terrain moves to a separate renderer-migration roadmap, with no diagnostic IPA authorized:

1. Freeze one immutable candidate architecture and exact dependency graph. The initial comparison should use the exact NG lineage above and a native GLES3 backend skeleton, but selection must be driven by conformance rather than fork name.
2. Add an executable GLES3 conformance harness before Xash integration. It must prove layer 0, layer 1 and highest-layer upload/sample, nonzero-layer subupload, mip/filter/repeat behavior, mixed 2D/cube/array units, sampler reflection and wrong-type rejection, cleanup/rebind, context loss/re-establishment and SDL-owned presentation.
3. Integrate the winning target/program/lifecycle subsystem behind a rollbackable backend boundary, then replay the exact engine, Diffusion, MainUI, SDL and accepted Bundle 69/71/81 pins and validators.
4. Integrate Diffusion's weight/diffuse/normal terrain families and establish deterministic visual fixtures for all 16 materials, dynamic light, normal/specular, mips and transitions before authorizing one device candidate.

### Material-state separability and future Phase B plan

The three material defects are independent of the terrain capability boundary and of each other at the native API level. They live in the pinned Diffusion producer/cache path and can be repaired without changing GL4ES target realization, shader conversion, array advertisement, drawable ownership or index handling:

| Defect | Exact ownership and invariant | Bounded repair contract |
| --- | --- | --- |
| Stale studio texture cache after `GL_CleanUpTextureUnits(0)` | `CStudioModelRenderer` keeps base, normal, cubemap and related member cache identities after engine cleanup invalidates/binds away those units. Cache equality can suppress the next required application `GL_Bind`; dynamic animation, monitor/entity-screen and drone choices are not fully represented by `iTexnum`. | Invalidate the studio material cache at every audited pass cleanup (`DrawStudioMeshes` and `DrawLightForMeshList`, plus any source-proven sibling) so the next pass must bind. Within a pass, key the skip decision by the actual selected texture object/mode for base and dependent maps, preserving sorted-mesh reuse and forced special-skin behavior. No per-draw global flush. |
| `u_StudioParams` over-count | Shader variants expose exact active extents: additive/no chrome 1, additive/chrome 2, non-additive 3. The producer always uploads 3, and pinned GL4ES correctly rejects an over-count. | Carry the exact shader-variant extent in `glsl_program_t` when `GL_UberShaderForSolidStudio` establishes additive/chrome directives, and upload that exact 1/2/3 count. Do not truncate, clamp or coerce in GL4ES. |
| Foliage uniform type mismatch | The packaged iOS shader declares `u_FoliageSwayHeight` as float; the solid studio producer uses `glUniform1i` while its dlight/depth siblings use `glUniform1f`. | Change only the solid producer to `glUniform1f` with an explicit float value; retain the shader's float declaration and reject a mutated integer call. |

The single actionable future Phase B, if explicitly authorized, is **one consolidated material-state repair candidate with no terrain changes**. Its implementation should be carried through `scripts/ios/diffusion-ios.patch` against exact Diffusion pin `14d156bf3a6993c172697fac83a937836c3b5561`; the existing float declaration in `scripts/ios/diffusion-shaders-ios.patch` must remain validated. Add a deterministic validator that positively proves cleanup/rebind and same-pass reuse for repeated, animated, monitor/entity, drone, base, normal, cubemap, interior, blend and colormask selections; proves uniform counts 1/2/3 for the three studio variant classes; and proves the foliage float declaration/call pair. Mutation/rejection fixtures must restore the stale cache, restore unconditional count 3, use the wrong variant count, or restore `glUniform1i`, and must fail.

Before any future candidate, replay both Diffusion patches at the exact pin, compile every relevant client/server/menu target with `XASH_IOS=1`, run the new positive and rejection fixtures, and rerun every Bundle 69, 71 and 81 preservation validator. Only after those local gates pass may that future order authorize at most one qualifying CI workflow and one IPA. The repair must be one rollbackable material-state commit and must not change terrain, extension strings, GL4ES shader conversion, object/target realization, direct-drawable presentation, uint indices, assets, menu/touch/callback behavior or transition/latency code.

### Validation and stop gate

Validation performed: complete newest-ledger read and authority check; Codebase Memory-first architecture/symbol/caller-callee audit followed by exact-source inspection; terrain producer-to-engine-array-to-shader/draw trace; all four architecture routes compared against layer/mip/filter/mixed-target/reflection/context/presentation, deterministic asset-conversion, CI conformance, Bundle preservation, rollback and maintenance requirements; exact current OpenMW/NG lineage, flags, initialization, source-conversion, array upload, target/reflection and drawable ownership differential; and full material-cache/uniform-producer trace. No runtime, patch, shader, validator, workflow or build-policy file was modified. No build, CI run, artifact, IPA, upload, evidence request, user contact or device-test request occurred.

Expected new log markers: **none**. Workflow URL/ID/result: **none**. IPA/artifact/tempfile filename, link, size and SHA-256: **none**. Exact file changed: `Documentation/XASH3DIOS_PORTING_STATE.md` only. This report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a commit cannot contain its own hash.

Remaining risks: terrain stays unavailable until a migration route passes native conformance; current NG-GL4ES branch history is mutable and the old `8eca1a14` comparison is not presently reproducible; the three material defects remain unfixed pending authorization; a future cache repair must cover every actual selected-object family without sacrificing within-pass reuse; shader compilation latency and the later transition termination remain separate; and Bundle 81 is not a generally accepted gameplay candidate.

Stop state: **Work Order 51 Phase A Outcome B is complete. Stop for orchestrator review.** Do not implement or begin Phase B, build, run CI, create or upload an IPA, contact Arjun, request evidence/testing, or reopen terrain with a narrower diagnostic patch.

## Work Order 51 Phase B - Bundle 85 consolidated material-state repair

Candidate/run and acceptance status: **Outcome A, Bundle 85 is build-qualified and published but is not device-tested or device-accepted.** This worker does not request a device test. The accepted Bundle 69 direct-drawable architecture, Bundle 71 native-ES3 32-bit index invariant, Bundle 81 per-texture-unit target realization, Diffusion menu/touch/callback/map behavior, exact source pins, and unrelated user changes are preserved. Terrain/texture arrays, GL4ES shader conversion, transition behavior, and shader-compilation latency remain outside this candidate.

### Candidate, commits, workflow, artifact, and publication

- Final behavioral/build commit: `c7f18b6e234a0efc4e6de7f5e1c2b6d71327352a` (`Repair Diffusion studio material-state invariants`). Exact pins remain engine/executable `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, and GL4ES `81547d986798e876de8b434193920b606a72363f`.
- Sole retained qualifying workflow: GitHub Actions push run `31958083850`, successful, head `c7f18b6e234a0efc4e6de7f5e1c2b6d71327352a`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31958083850`. The automatic pull-request twin `31958085306` was canceled and produced no retained candidate. Skipped `Build & Deploy Engine` runs are not candidates.
- Disclosed prequalification failure: push run `31957328896` at superseded SHA `ad5b9f3933587bceb651aab3436fef4f00f57e626` stopped before Diffusion compilation because two non-semantic end-of-file newline hunks did not apply on Linux; it produced no IPA/artifact. Its PR twin `31957332861` was canceled. Removing only those EOF hunks, replaying from the exact pin, and amending the same behavioral unit produced the final commit above; runtime semantics did not change.
- Retained GitHub artifact: `Xash3DiOS-arm64-unsigned`, artifact ID `9266557105`, archive size `8,592,491` bytes, archive digest `sha256:2e70331aa05cd3ebb454dbfd1ce823964ccfd3e42cadb6013764d84f622e2bed`, expiry `2026-08-30T16:21:07Z`: `https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31958083850/artifacts/9266557105`.
- Verified IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,690,958` bytes, SHA-256 `89109695341BFE8E92C8E024982D8B15423812022BCF58E274E09D0EA40A1168`.
- Exactly one tempfile.org upload of that verified IPA: information page `https://tempfile.org/Qpb2BedypS9/`; direct download `https://tempfile.org/Qpb2BedypS9/download`; expiry `2026-08-17T16:27:00.301Z`. Upload and metadata readback report the exact filename and `8,690,958` bytes; the security endpoint reports `safe`, no warning and no suspicious patterns, with server SHA-256 `89109695341bfe8e92c8e024982d8b15423812022bcf58e274e09d0ea40a1168`. Direct-URL headers independently report HTTP 200, the exact filename/content length, and the same expiry.

### Verified failure boundary and structural cause

The first material-state divergence is in pinned Diffusion's studio producer, before engine `GL_Bind` and before GL4ES. `DrawStudioMeshes`, `RenderDynLightList`, and `DrawStudioMeshesShadow` end authoritative passes with `GL_CleanUpTextureUnits(0)`, which invalidates engine texture-unit state, while `CStudioModelRenderer` previously retained private member cache identities. The next sorted draw could therefore treat a material as already bound and suppress the application `GL_Bind` that Bundle 81 correctly realizes. The old base key was only material `iTexnum`; it did not represent the selected white/fallback/animated frame/monitor entity/drone object or selection mode. Dependent normal, cubemap, interior/blend, and colormask identities likewise lacked a complete post-cleanup lifetime invariant.

Two independent uniform producer defects are confirmed at the same application boundary. Solid studio variants have exact linked `u_StudioParams` vec4 extents of 1 for additive/no-chrome, 2 for additive/chrome, and 3 for non-additive, but the producer unconditionally submitted count 3; pinned GL4ES correctly rejects an over-count rather than truncating it. The packaged foliage shader declares `u_FoliageSwayHeight` as float, but solid studio used the integer upload API while dynamic-light and depth siblings already used float.

### Structural repair and why it satisfies the order

Diffusion now owns an explicit studio material-cache epoch. Every audited authoritative cleanup immediately invalidates all base and dependent identities, forcing the next complete bind while retaining unchanged same-pass reuse. Base decisions are keyed by material, actual selected object, and selection mode across base, white, fallback, animated, monitor/entity-screen, and drone routes; the engine-owned colormap remap remains intentionally forced because its actual object is not observable at this layer. Normal, cubemap object/owner, interior-versus-blend auxiliary object/material, and colormask identities are independently represented. Shader switches use the same centralized reset. No brute-force per-draw texture flushing and no GL4ES, SDL, drawable, index, menu, terrain, asset, or transition mutation was introduced.

Solid-studio shader metadata now derives the exact 1/2/3 extent from the same additive/chrome directives that construct the variant, reflects the linked active `GL_FLOAT_VEC4` array extent after link, and rejects a program unless producer metadata, linked extent, and upload count agree. `DrawStudioMeshes` uploads only that exact count. There is no GL4ES clamp, name-based inference, or coercion. Solid foliage now uses `pglUniform1fARB` with an explicit float value, matching the unchanged float shader declaration and its dynamic-light/depth siblings.

### Exact files and validation

Behavioral files changed:

- `scripts/ios/diffusion-wo51-material-state-ios.patch`
- `scripts/ios/validate-ios-material-state.py`
- `scripts/ios/builddiffusion.sh`
- `scripts/ios/verify_ipa.sh`

This durable report additionally changes `Documentation/XASH3DIOS_PORTING_STATE.md`. The runtime patch changes only pinned Diffusion `client/render/r_shader.cpp`, `client/render/r_shader.h`, `client/render/r_studio.cpp`, and `client/render/r_studio.h` during the iOS build.

Validation performed: complete authoritative-ledger authority check; Codebase Memory-first symbol/call-path inspection followed by exact source inspection; complete cleanup-to-next-bind and solid/dlight/depth uniform trace; clean exact-pin patch replay in CI order; deterministic positive fixtures proving first complete rebind, unchanged same-pass reuse, actual object/mode changes, auxiliary mode changes, cubemap owner changes and cleanup epochs; rejection mutations for stale cleanup, incomplete object/mode keys, missing animation, unconditional count 3, wrong counts for each 1/2/3 class, missing linked-extent rejection, integer foliage declaration/call, and GL4ES coercion; Diffusion policy plus Bundle 69 direct-drawable, Bundle 71 uint-index/index-trace, Bundle 81 per-unit texture-target, WO49 topology, and WO49 transform positive/rejection suites; Python syntax and `git diff --check`.

The successful macOS workflow reapplied every exact pin, installed the GLES shader validator, passed all preservation and WO51 positive/rejection gates, retained the shared animated-model/one-bone-rigid shader policy, built the complete engine, Half-Life client/server, Diffusion client/server/menu, MainUI, SDL, and GL4ES graph with `XASH_IOS=1`, then passed the IPA contract and artifact upload. Independent extraction verifies `CFBundleVersion=85`, `MinimumOSVersion=12.0`, file sharing enabled, all five new markers, 13 of 13 Mach-O files thin arm64, and 11 game dylibs.

Expected new engine.log marker prefixes:

- `iOS material-state policy:`
- `iOS studio texture cache epoch:`
- `iOS studio params exact count:`
- `iOS foliage uniform type:`
- `iOS material-state terminal:`

Single device test requested: **none**. Only the orchestrator may authorize any Bundle 85 device action.

Remaining risks: Bundle 85 is build-qualified, not device-accepted; device evidence may reveal a separate material, asset, lighting, or presentation defect after the three proven producer defects are removed. Landscape remains unsupported pending the separate renderer-migration roadmap. Synchronous shader compilation latency and the later map-transition crash/termination remain independent and unchanged. None authorizes a follow-up patch, workflow, artifact, upload, user contact, or test request.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. Behavioral commit is `c7f18b6e234a0efc4e6de7f5e1c2b6d71327352a`. This complete report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash.

Stop state: **Work Order 51 Phase B Outcome A implementation, validation, sole retained Bundle-85 workflow/artifact, independent IPA verification, exactly one tempfile.org upload, and both durable-ledger updates are complete. Stop for orchestrator review.** Do not contact Arjun, request logs/evidence/device testing, claim device acceptance, modify code, start another workflow, create another artifact/upload, or begin Phase C or any later work order.

## Work Order 52 Phase A - scene-stable yellow material failure audit

Candidate/run and acceptance status: **Outcome B, audit-only; no candidate/run was created.** Bundle 85 is device-tested partial progress, not accepted: cliffs/buildings remain textured and the prior frame-to-frame flicker is no longer reproduced, but some studio models or model parts remain flat tan/yellow for an entire scene and can become correctly textured after a scene transition. Terrain/road remains the separately classified unsupported texture-array path and is excluded from this finding.

### Authority, evidence, and verified boundary

The authoritative Google Docs ledger was read through `WORK ORDER 52 PHASE A - SCENE-STABLE YELLOW MATERIAL FAILURE AUDIT`, and the complete linked `Xash3DiOS Bundle 85 engine log 20260816-171453` was read as 2,034 indexed paragraphs. The audit began from clean `agent/ios-proof-of-life` at `e95a2c4817e26f3f35c5acca44232ba9207265ae`, whose behavioral parent remains Bundle-85 commit `c7f18b6e234a0efc4e6de7f5e1c2b6d71327352a`.

Accepted device evidence establishes the boundary after correct drawable presentation and stable scene rendering: affected cars, trucks, props, or model parts are visible with valid silhouettes but a flat tan/yellow material for the whole scene; correctly textured cliffs and other models coexist; no within-scene flicker is reported; and the same player car can be correct after a later scene transition. This is a subset studio/material-readiness or binding failure, not a whole-frame presentation failure. The log confirms all three Bundle-85 policy markers, continued `StudioSolid`/`Bmodel` shader progress, and a later `ch1map1` transition.

The log contains no `GL_OUT_OF_MEMORY`, allocation-failure, Jetsam, memory-pressure, texture-eviction, or purgeable-resource marker. The missing `models/bmec/cars/sedan_volkswagen_passat.mdl` and `models/bmec2/truck.mdl` errors are permanent data-pack omissions and cannot explain an already visible model that changes from flat tan to textured after transition. The audited and rendered `models/bmec/cars/truck_new.mdl` is a different, present asset.

### Flat-tan producer evidence table

| Plausible producer | Exact source/log evidence | Finding |
| --- | --- | --- |
| iOS presentation/debug sentinel or literal tan output | Bundle 69 owns the drawable; the earlier yellow sentinel is not in the normal studio fragment path. No production literal tan/yellow output exists in `studiosolid_fp.glsl` or `studiodlight_fp.glsl`. | Rejected. It cannot preserve per-model silhouettes alongside correct scene content. |
| Engine default/error texture | `R_CreateBuiltinTextures` creates `*default` as a magenta/black 16x16 checkerboard. `TryReloadingAnimation` can substitute it only after an animation reload failure. | Rejected as the observed flat tan. A visible checkerboard is not the screenshot result. |
| White texture/debug-lightmap route | `DrawStudioMeshes` selects `tr.whiteTexture` only when `r_lightmap` is enabled and `r_fullbright` is not. White sampled through studio lighting/render color can look tan. | Source-capable but not supported by the subset evidence: this global debug condition would affect the studio family coherently, not only stable individual model parts, and the log has no state discriminator. |
| `u_RenderColor` or color-mask path | Both studio fragment shaders sample `u_ColorMap` first. `u_RenderColor` then multiplies diffuse color globally or through `u_ColorMask`; it does not independently replace a detailed diffuse sample with a flat color. `u_MeshParams[2].y` can mix a `u_BlendTexture` for cars. | A tan render color can explain the hue only if the sampled base/blend/mask input is already uniform or wrong. It is not a standalone first cause. Its exact value remains required evidence. |
| Missing/zero/wrong `u_ColorMap` sampler or unit-0 object | `GL_InitSolidStudioUniforms` reflects `u_ColorMap` and assigns unit 0. `DrawStudioMeshes` selects base/white/colormap/monitor/fallback/animated/drone, calls engine `GL_Bind`, GL4ES defers the logical bind, Bundle 81 realizes the selected per-unit object, then the native draw samples it. | Leading unresolved boundary. A wrong uniform-color 2D object, native binding 0/incomplete object, or sampler/unit mismatch directly produces a stable silhouette and can be reset at transition. Bundle-85 log does not record this chain. |
| Diffusion fallback/material-load failure | `LoadStudioMaterials` synchronously prefers an external texture, falls back to the embedded studio texture, stores `gl_diffuse_id`, then loads optional fallback, animation, blend, mask, interior, and material settings. Explicit fallback is deterministic; permanent missing model files cannot later render correctly. | General permanent asset/load failure rejected for a later-correct asset. Animated/fallback selection remains possible only until the selected object for an affected material is captured. |
| Shader compile/link failure or error material | `ChooseStudioProgram` returns zero on selection/compile failure and `AddMeshToDrawList` omits the mesh; it does not draw a tan replacement. The complete log continues through programs 15-60 without a studio compile/link error. | Rejected for visible silhouettes. A wrong-but-successful variant remains possible and requires the material-to-program correlation absent from the log. |
| Fullbright, additive, alpha-rescaling, chrome, blend, or colormask variant | Every audited `StudioSolid`/`StudioDlight` variant still samples `u_ColorMap`; optional blend/mask paths add more texture/state dependencies. The log compiles blend variants 45-47 before gameplay, rigid/vertex-lit/alpha/sway/additive variants 49-52 in `ch1map0`, fullbright/colormask and related variants 53-59 later, and alpha-rescaling program 60 after the `ch1map1` transition. | No option family is tied to an affected object/material in this log. Variant presence alone cannot choose a repair. |
| Texture-not-ready, deleted, or stale native realization | Diffusion texture loading is synchronous, but GL4ES holds separate logical bound objects and `actual_tex2d` native realization state. Bundle 81 fixes the cross-unit target source, not proof of a particular affected draw's object completeness or immediate native binding. | Structurally compatible with scene stability and transition recovery, but unproven without producer-to-native identity evidence. |
| Memory pressure/eviction | No OOM, allocation failure, OS/Jetsam, memory warning, explicit texture deletion/eviction, or purgeable lifecycle appears in the complete log. Recovery occurs at a deterministic transition. | Rejected on present evidence. Do not downscale, purge, or impose memory workarounds. |

### Source-level material lifecycle and call graph

The exact pinned build remains Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, executable/engine `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, GL4ES `81547d986798e876de8b434193920b606a72363f`, and the accepted iOS patch stack.

Initial resource/material production:

`engine Mod_StudioLoadTextures -> R_StudioLoadTexture -> GL_LoadTexture` creates each embedded or external studio texture synchronously and leaves a valid texture index or `tr.defaultTexture`. Diffusion `HUD_ProcessModelData -> R_ProcessStudioData -> CStudioModelRenderer::ProcessUserData(create) -> CreateMeshCache(unique) -> LoadStudioMaterials` copies studio texture metadata to `mstudiomaterial_t`, chooses external-versus-embedded `gl_diffuse_id`, loads material settings and optional maps/animation, and precaches solid/dynamic-light shader families. `CreateInstance/ClearInstanceData -> UpdateInstanceMaterials` copies the model material array to the entity instance, invalidates shader sequences, and invokes `TryReloadingAnimation` for animation metadata.

Affected draw production and native consumption:

`StudioDrawModel -> AddBodyPartToDrawList -> AddMeshToDrawList -> ChooseStudioProgram -> GL_UberShaderForSolidStudio/GL_FindUberShader` selects a successful variant. `DrawStudioMeshes` recovers the model material and diffuse ID, derives the actual mode/object across base, white, colormap, monitor, explicit fallback, animation, and drone, then handles normal, cubemap, interior/blend, and colormask dependencies. Bundle 85 keys those actual identities and forces a complete next bind after every authoritative `GL_CleanUpTextureUnits(0)` epoch. The path continues through Diffusion `GL_Bind` and its engine-side target/object cache, GL4ES `gl4es_glBindTexture` logical per-unit state, `realize_textures(drawing=1)` with Bundle-81 per-unit target selection, reflected `u_ColorMap = unit 0`, and the immediate native `fpe_glDrawElements`/GLES draw.

The first bad boundary cannot be placed more narrowly from Bundle-85 evidence. It is between Diffusion's selected material object and the native texture/sampler state consumed by the affected draw. No current record names the affected entity/model/material, selected object/mode, shader and sampler, GL4ES logical object/glname, or immediate native binding in one token chain.

Transition comparison:

`HUD_ProcessEntData(allocate) -> Mod_PrepareModelInstances` invalidates entity model handles before new-map loading; the release side calls `Mod_ThrowModelInstances -> DestroyAllModelInstances`. `Mod_LoadWorld` resets material/world bookkeeping and initializes map-specific animations/materials. `R_NewMap -> g_StudioRenderer.VidInit -> ResetRenderCache` starts a fresh studio material-cache epoch. Recreated entity instances call `UpdateInstanceMaterials`, which recopies model materials and can reload purged animations. Shaders are normally retained unless the 90-percent program threshold forces a flush, while additional successful variants can compile on demand; Bundle 85 shows program 60 after the `ch1map1` transition.

Therefore transition recovery is real but not uniquely diagnostic: cache epoch reset, instance recreation, animation/material refresh, new logical/native binds, and a later shader variant all occur at or near the same transition. Source cannot identify one minimal repairing event without the affected material's before/after token chain.

### Outcome B one-run discriminator specification (not implemented)

One bounded producer-to-native audit should assign a shared token to the first draw of every unique `(map generation, entity, model, skin, bodypart/mesh, material)` studio identity, plus the first reappearance of that identity after a map-generation change. Cap the table deterministically (for example 256 identities), emit at most one record per stage per token, never mutate GL state or drain the error queue, and finish with a completeness/overflow summary. A single device run would capture:

1. Producer/material: map generation/name, frame, entity/index/model/model-handle, skin/body/mesh/material indices and names, material flags, `gl_diffuse_id`, selected texture mode and intended object, fallback/animation/monitor/drone decision, auxiliary blend/interior/mask/normal/cubemap objects, animation slot/readiness, and texture width/height/target/format/flags.
2. Shader/uniforms: program index/logical and realized handles, options hash/directives, linked `u_ColorMap` type/extent/location and sampler value, optional unit-4/unit-5 sampler metadata, `u_RenderColor`, `u_MeshParams` including blend amount, and studio lighting/fullbright/additive state.
3. Diffusion bind boundary: engine active unit, cached target/index/object before and after each relevant `GL_Bind`, whether the call issued or returned as equal, and the cleanup/material-cache epochs.
4. GL4ES/native boundary: logical unit/target/object and `glname`, per-unit enabled target, `bound_changed`, `actual_tex2d`, realized program/sampler value, then immediately before the native draw the native active unit, `GL_TEXTURE_BINDING_2D`, texture level-0 width/height/format/completeness-relevant sampler parameters for units 0/4/5 as applicable, all keyed to the same token.
5. Transition event: ordered markers for `Mod_PrepareModelInstances`, `DestroyAllModelInstances`, world/material/animation reset or reload, `R_NewMap`, `VidInit` epoch, shader creation/reuse, and the first matching post-transition material token.

Terminal classification must compare intended object -> Diffusion issued bind -> GL4ES logical/glname -> immediate native binding -> reflected sampler/unit. The first unequal or absent field chooses the repair boundary; if all texture/sampler fields match, the recorded color/blend/lighting uniforms and shader options reject the binding theory and identify a producer/material-authoring variant instead. This is one consolidated discriminator, not multiple micro-builds, and it is sufficient to choose or reject a repair in one authorized device run. Phase A does not implement or build it.

### Validation, risks, and stop gate

Validation performed: current authoritative ledger revision and complete Work Order 52 Phase A read; complete linked 2,034-paragraph Bundle-85 log read and event/pattern audit; Codebase Memory-first architecture, symbol, code-snippet, and caller/callee traces followed by exact pinned-source/patch inspection; full material acquisition, shader selection/reflection, producer cache, engine bind, GL4ES logical/realized state, draw, and scene-transition lifecycle trace; exact comparison of programs 15-60; positive and rejection rerun of `validate-ios-material-state.py` against the exact applied Diffusion source; clean-branch and `git diff --check` validation. No runtime, patch, shader, validator, workflow, or build-policy file changed. No build or CI run occurred.

Exact file changed: `Documentation/XASH3DIOS_PORTING_STATE.md` only. Workflow URL/ID/result: **none**. Artifact/IPA/tempfile filename, link, size, and SHA-256: **none**. Expected runtime/log marker: **none**. Device test requested: **none**.

Remaining risks: the screenshots do not provide machine-readable model/material identity; multiple transition events remain correlated; blend/colormask and render-color state could be valid authored behavior for some parts; an affected texture may be correct at the Diffusion producer but incomplete or different at native draw; and program 60's timing does not identify its material. Terrain arrays, shader-compilation latency, and later transition termination remain independent. None authorizes a repair or diagnostics candidate.

Durable ledger path and commit: `Documentation/XASH3DIOS_PORTING_STATE.md`. This audit is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a commit cannot contain its own hash.

Stop state: **Work Order 52 Phase A Outcome B audit and both-ledger reporting are complete. Stop for orchestrator review.** Do not implement the discriminator, modify runtime code, build, start GitHub Actions, create an IPA/artifact/upload, contact Arjun, request evidence/testing, or begin Phase B or any later work order.
