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

## Work Order 52 Phase B - diagnostics implementation stopped at failed build gate

Candidate/run and acceptance status: **rejected before artifact publication; no device candidate exists.** The authorized producer-to-native discriminator was implemented and passed its source, exact-pin, positive, rejection, and preservation gates, but the sole corrected publication run failed while compiling GL4ES. IPA contract verification and upload never ran. Bundle 85 remains partial progress and is still not accepted.

### Authority, preserved boundary, and implementation

The authoritative Google Docs ledger was read completely through `WORK ORDER 52 PHASE B - ONE-RUN STUDIO MATERIAL/SAMPLER DISCRIMINATOR`, then reread immediately before this report; no newer authorization exists. The work remained diagnostics-only. Bundle 69 direct-drawable ownership, Bundle 71 native GLES3 uint indices, Bundle 81 per-unit texture-target selection, Bundle 85 material-state fixes, Diffusion menu/touch/callback behavior, terrain exclusions, and every unrelated source path were preserved.

Implementation commit `6ac650fd97838b5d9bac2777ecc01c6b90ac34ab` adds one fixed-cap token chain across Diffusion material production, shader/uniform metadata, engine `GL_Bind`, GL4ES logical binding and draw-route ownership, post-realization immediate pre-native shadow state, scene transitions, one of six terminal classifiers, and completeness accounting. It caps selection at 256 identities, units at 6, and render-list tokens at 32; deep-copies names into fixed storage; emits at most one record per stage/token through the existing engine-console sink; does not query or mutate GL state, drain errors, allocate dynamically, alter draw order, or change renderer policy. Commit `00ae2fb2df900e314f6392ed427a03259223c831` makes the 32-token list cap self-contained in `list.h` after the first compile attempt proved that the initial declaration was not visible there, and adds the matching rejection mutation.

The intended diagnostic boundary is unchanged from Phase A: the unresolved device defect remains between Diffusion's selected studio material object and the native texture/sampler/program state consumed by the affected draw. The implementation was designed to classify producer selection, bind/cache suppression, GL4ES logical-to-native realization, sampler/program routing, captured color/material/shader state, or an explicitly missing/overflowed stage. It does not claim or implement a renderer repair.

### Validation and exact build boundary

Local/source validation completed: Python compilation; exact Diffusion `14d156bf3a6993c172697fac83a937836c3b5561` and GL4ES `81547d986798e876de8b434193920b606a72363f` patch reversibility/replay checks; full WO52 positive fixtures and rejection mutations for early/missing hooks, route loss, unbounded storage, stdout, state mutation, error draining, stale attribute queries, sampler-type omission, unsupported claims, and the header-visibility defect; Diffusion shared-animated/rigid-one-bone policy; Bundle 69 drawable, Bundle 71 uint/index-trace, Bundle 81 per-unit target, WO49 topology/transform, and Bundle 85 material-state positive/rejection suites; and staged `git diff --check`.

The first push workflow, [31971603395](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31971603395), failed without an artifact because `src/gl/list.h` used `IOS_WO52_MATERIAL_LIST_CAP` before that header could see its declaration. Its automatic PR duplicate [31971605149](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/31971605149) was cancelled; the general C/C++ workflows were policy-skipped. The bounded header fix and rejection fixture were then published in `00ae2fb2df900e314f6392ed427a03259223c831`.

The corrected push workflow, [32007677554](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32007677554), also failed in `Build engine, Half-Life, and Diffusion modules` before contract verification or artifact upload. The first authoritative boundary is GL4ES `src/gl/indextrace.c`: calls to the existing static engine-log helper `ios_wo49_emit` at lines 370 and 391 precede its declaration, followed by `static declaration of 'ios_wo49_emit' follows non-static declaration` at line 595 under Clang's C99 implicit-declaration error. Its automatic PR duplicate [32007682782](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32007682782) was cancelled; the general C/C++ workflows were policy-skipped. This is a diagnostics implementation declaration-order defect, not evidence about the yellow-material renderer cause.

No third workflow, follow-up compile patch, renderer repair, IPA, GitHub artifact, tempfile.org upload, device contact, evidence request, or test request is authorized or created. IPA filename, byte size, SHA-256, GitHub artifact link, tempfile information/direct link, and expiry are all **none** because no IPA exists. Thin-arm64 and packaged-marker verification could not run.

### Exact files changed and expected markers

Behavioral/diagnostic commits changed:

- `ref/gl/gl_backend.c`
- `scripts/gha/build_ios.sh`
- `scripts/ios/builddiffusion.sh`
- `scripts/ios/verify_ipa.sh`
- `scripts/ios/diffusion-wo52-material-trace-ios.patch`
- `scripts/ios/gl4es-wo52-material-trace-ios.patch`
- `scripts/ios/validate-ios-wo52-material-trace.py`

This report additionally changes `Documentation/XASH3DIOS_PORTING_STATE.md`. The unbuilt marker contract is `WO52 material trace policy:`, `producer:`, `shader:`, `bind:`, `gl4es:`, `native:`, `transition:`, `terminal:`, and `summary:`. These strings exist in source and packaging checks but are **not expected from any installable IPA**, because no IPA was produced.

Structural cause: the scene-stable yellow material cause remains unresolved; the authorized discriminator did not reach an executable artifact. The concrete stop cause is the GL4ES diagnostic helper declaration order above. Why the change addresses the work order: the source design spans every required producer/cache/route/native/transition stage with bounded non-mutating instrumentation and deterministic terminal results, but it does **not** satisfy the full build/publication gate and therefore cannot be represented as a qualified candidate.

Remaining risks: the current branch head contains an uncompiled diagnostics patch; no runtime behavior or marker has been validated on device; the true material divergence remains unknown; terrain arrays, shader compilation latency, and later map-transition termination remain independent. A future correction requires a new explicit orchestrator authorization. If a later authorized device run of a build-qualified discriminator still cannot classify the first divergence, end micro-diagnostic iterations and move to a broader renderer capture or native conformance harness as Work Order 52 requires.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash.

Stop state: **Work Order 52 Phase B is stopped at a failed full-build gate. No candidate or artifact is accepted or available. Stop for orchestrator review.** Do not contact Arjun, request logs/evidence/testing, start another workflow, upload anything, fix the declaration order, implement a renderer repair, or begin another phase without a new explicit work order.

## Work Order 52 Phase B Correction - declaration fixed; single build stopped at Diffusion patch replay

Candidate/run and acceptance status: **rejected before artifact publication; no installable candidate exists.** The authorized declaration-order correction passed its local compile and unchanged validation gates, but the one qualifying workflow failed later while applying the existing Diffusion WO52 patch. The failure gate therefore prohibits a retry, follow-up fix, IPA, upload, or device-test request.

### Correction, scope, and verified boundary

Starting exactly from branch head `72ef44bce54231dfedb3568c6e49595fd90539ba`, commit `383aa252bbef347cbd697da87305c543f4ec5580` changes only `scripts/ios/gl4es-wo52-material-trace-ios.patch`. It adds the exact matching forward declaration `static void ios_wo49_emit(const char *format, ...);` before the first WO52 call in generated GL4ES `src/gl/indextrace.c`. The existing definition, signature, emitted fields, token/cap policy, engine-console sink, diagnostic routes, runtime behavior, and every renderer/gameplay policy remain unchanged.

The original authoritative boundary is resolved: exact GL4ES pin `81547d986798e876de8b434193920b606a72363f` replayed through the complete accepted iOS patch stack, and the affected translation unit compiled locally under Clang C11 with implicit-function declarations treated as errors. There is no longer an implicit declaration or static/non-static conflict for `ios_wo49_emit`.

The one qualifying push workflow, [32010810711](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32010810711), passed the drawable, uint-index, index-trace, WO49 topology/transform/texture-unit, and WO52 validators, configured and built the engine, and completed the Half-Life client/server build. It then failed in `scripts/ios/builddiffusion.sh` while applying the unchanged `scripts/ios/diffusion-wo52-material-trace-ios.patch`: `error: patch failed: client/render/r_shader.cpp:3263`, followed by `error: client/render/r_shader.cpp: patch does not apply`. This is the first authoritative new build error. It is a separate Diffusion patch-replay defect and was not modified because the correction order explicitly forbids speculative later fixes after the single workflow.

The automatic pull-request duplicate [32010815714](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32010815714) was cancelled. The general C/C++ push and pull-request workflows [32010810636](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32010810636) and [32010815705](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32010815705) were policy-skipped and are not qualifying candidates.

### Validation performed

- Exact branch/head and single-file diff inspection; generated/patched source inspection in both GL4ES working copies.
- Exact pinned GL4ES replay through `gl4es-ios`, drawable bridge, uint elements, index trace, WO49 topology, WO49 transform, WO49 texture unit, and corrected WO52 material trace patches.
- Real Clang `-fsyntax-only -std=gnu11 -Werror=implicit-function-declaration` compile of the replayed `src/gl/indextrace.c`; only two pre-existing Windows CRT `strncpy` deprecation warnings remained.
- Unchanged positive and rejection suites: drawable bridge; uint elements; index trace; WO49 topology; WO49 transform; WO49 texture unit; Bundle 85 material state; WO52 material trace; Diffusion shared-animated/rigid-one-bone policy; Python compilation; `git diff --check`.
- Full macOS Actions log inspected through the exact first Diffusion patch-application failure.

### Artifact, markers, risks, and stop state

IPA filename/link, GitHub artifact, tempfile.org object, byte size, bundle version, thin-arm64 inventory, packaged marker verification, and SHA-256 are all **none** because the build failed before `Verify IPA contract` and `Upload unsigned IPA`.

Expected source-only marker contract remains unchanged: `WO52 material trace policy:`, `producer:`, `shader:`, `bind:`, `gl4es:`, `native:`, `transition:`, `terminal:`, and `summary:`. No marker is claimed from an IPA because no IPA was created.

Structural cause: the authorized GL4ES declaration-order defect is fixed. The material-rendering cause remains unresolved because the discriminator still has no executable artifact. The current publication blocker is the unchanged WO52 Diffusion patch's EOF/context hunk at `client/render/r_shader.cpp:3263` not applying after the preceding pinned patch stack on the macOS runner; its repair was outside this correction's one-workflow authority.

Remaining risks: the WO52 diagnostics are still not packaged or device-validated; the exact Diffusion patch-replay mismatch requires a new explicit authorization before any edit or build; the true studio material divergence, terrain arrays, shader latency, and later map-transition termination remain independent.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in a documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger because a Git commit cannot contain its own hash.

Stop state: **Work Order 52 Phase B Correction is stopped at its single-workflow failure gate.** Do not retry, change the Diffusion patch, create/upload an IPA, contact Arjun, request evidence/testing, implement a renderer repair, or begin another phase. Await orchestrator review.

## Work Order 52 Phase C - complete build stack normalized; Bundle 94 diagnostics candidate produced

Outcome and candidate/acceptance status: **Outcome A. Bundle version 94 is a build-qualified, diagnostics-only WO52 candidate; it is not device-accepted.** The complete deterministic WO52 chain now replays, compiles, links, packages, passes the IPA contract, and publishes exactly one retained GitHub artifact and one tempfile.org object. This order makes no renderer or gameplay repair and requests no device test.

### Commits, exact pins, and production patch order

- Starting clean remote head: `9785d6c15151d8788e08b3c56e670a1dace5ffba`.
- Build-normalization candidate commit: `9cb19028af9a1769b45d75fb4f53fee5031d62f3`.
- One authorized CI-specific verifier correction: `5c38946ff99e6398825ee665fbc100284c82ba2f`.
- Exact source revisions: Xash3D `9785d6c15151d8788e08b3c56e670a1dace5ffba`; GL4ES `81547d986798e876de8b434193920b606a72363f`; NanoGL `7f654d2de2680c7f6007aef5159ed63247741620`; SDL `5d249570393f7a37e037abf22cd6012a4cc56a71` (`2.32.10`); Half-Life SDK `079f2387eb59e4a045647d9057240628130f0058`; Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`; Diffusion MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`; Diffusion executable `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`.
- NanoGL production order: `nanogl-large-primitive.patch`.
- SDL production order: `sdl2-drawable-bridge-ios.patch`.
- GL4ES production order: `gl4es-ios.patch`, `gl4es-drawable-bridge-ios.patch`, `gl4es-uint-elements-ios.patch`, `gl4es-index-trace-ios.patch`, `gl4es-wo49-topology-ios.patch`, `gl4es-wo49-transform-ios.patch`, `gl4es-wo49-texture-unit-ios.patch`, `gl4es-wo52-material-trace-ios.patch`.
- Diffusion production order: `diffusion-ios.patch`, `diffusion-shaders-ios.patch`, `diffusion-wo49-topology-ios.patch`, `diffusion-wo49-transform-ios.patch`, `diffusion-wo51-material-state-ios.patch`, `diffusion-wo52-material-trace-ios.patch`.

The deterministic defects were build-chain defects only. `scripts/ios/diffusion-wo52-material-trace-ios.patch` was regenerated against the exact post-WO51 source state: its stale `r_shader.cpp` base blob was corrected and a no-op EOF-newline hunk was removed. All six resulting Diffusion WO52 files are semantically identical, ignoring host EOL representation, to the previously intended fully applied diagnostic source. `scripts/gha/deps_ios.sh` now fetches, detaches, and verifies the exact Half-Life SDK commit instead of cloning a moving branch.

The first qualifying workflow proved a packaging-only ownership error after all builds succeeded: `verify_ipa.sh` searched the `xash` executable for `gl4es_iOSWO52EngineBind`, although its consumer is `ref/gl/gl_backend.c` and is packaged in `libref_gl4es.dylib`. The permitted CI-specific correction checks the correct binary and extends the unchanged WO52 validator with a rejection fixture that rejects the former wrong-binary assertion. It changes no packaged runtime behavior.

### Exact files changed

- `scripts/gha/deps_ios.sh`
- `scripts/ios/diffusion-wo52-material-trace-ios.patch`
- `scripts/ios/verify_ipa.sh`
- `scripts/ios/validate-ios-wo52-material-trace.py`
- `Documentation/XASH3DIOS_PORTING_STATE.md`

No engine, renderer, GL4ES runtime patch, Diffusion diagnostic body, shader, material, texture, terrain, sampler, uniform, index, transform, presentation, gameplay, menu, touch, transition, lifecycle, MSAA, timing, or asset-policy source changed.

### Local proof and CI result

Fresh exact-pin trees replayed the full NanoGL, SDL, GL4ES, and Diffusion production stacks with no rejects or skipped WO52 patch. All 14 modified GL4ES C translation units compiled under Clang GNU C11 with implicit declarations, incompatible pointers, integer conversion, and return-type failures promoted to errors. All four modified Diffusion C++ translation units (`r_misc.cpp`, `r_shader.cpp`, `r_studio.cpp`, `r_world.cpp`) compiled under Clang GNU C++17 with `XASH_IOS=1`. The NanoGL batch test compiled, linked, and passed.

The drawable bridge, uint-elements, index-trace, WO49 topology, WO49 transform, WO49 texture-unit, WO51 material-state, WO52 material-trace, and Diffusion iOS policy positive/rejection suites all passed. Python compilation and `git diff --check` passed. The final WO52 verifier self-test specifically rejects checking the engine-bind consumer in `ENGINE_STRINGS`.

Host Windows could not exercise Apple Objective-C/Objective-C++, iPhoneOS linking, or the GL4ES-translated shader gate. Its strongest attempted full builds were bounded by host/toolchain prerequisites: Diffusion Waf configuration requires Unix `libm`; the engine host configuration lacked initialized recursive submodules in the restricted Windows Git helper; Half-Life CMake could not complete the host RC/lld toolchain probe. The macOS workflow then covered those unavailable gates and successfully built the SDL arm64 framework, engine, Half-Life client/server, Diffusion client/server/menu, GL4ES renderer, translated mobile shaders, and IPA.

- First qualifier: [workflow 32021080139](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32021080139), commit `9cb19028af9a1769b45d75fb4f53fee5031d62f3`: engine/Half-Life/Diffusion build succeeded; failed only at the incorrect IPA bridge-owner assertion; no artifact retained.
- Final permitted qualifier: [workflow 32355333619](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32355333619), commit `5c38946ff99e6398825ee665fbc100284c82ba2f`: **success**, including IPA contract and upload.
- Duplicate handling: both candidate pushes used `[skip ci]`; no automatic qualifying duplicate or duplicate artifact was created. No third workflow was run.

### Artifact, IPA, marker, and architecture verification

- Retained GitHub artifact: `Xash3DiOS-arm64-unsigned`, ID `9401577451`, [artifact page](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32355333619/artifacts/9401577451), archive size `8,605,889` bytes, GitHub archive digest `fdb01fb1cc3aef2cd71d45d887cf566698370605ae2b430f4cfab208efaf0acd`.
- IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,705,206` bytes, SHA-256 `2D93C13E913F908BA81E22420A950D502893BC7F2827A270D39CA31204BD0E47`, `CFBundleVersion=94`, `CFBundleExecutable=xash`.
- Exactly one tempfile.org object: [information page](https://tempfile.org/NUyct1xEmKb/); [direct IPA download](https://tempfile.org/NUyct1xEmKb/download); expiry `2026-08-22T09:51:06.122Z`. API and direct-header readback report the exact filename and byte size; the server security endpoint reports the same SHA-256, `safe`, no warning, and no suspicious pattern.
- Independent Mach-O header inspection verified thin 64-bit arm64 (`CFFAEDFE`, CPU `0C000001`) for `xash`, `libref_gl4es.dylib`, SDL2, and the Diffusion client/server/menu dylibs.
- The packaged GL4ES renderer contains `gl4es_iOSWO52EngineBind` and every unchanged expected marker: `WO52 material trace policy:`, `producer:`, `shader:`, `bind:`, `gl4es:`, `native:`, `transition:`, `terminal:`, and `summary:`. The Diffusion client contains the accepted canonical-material/shared-animated-layout/on-demand-shader marker.

### Structural boundary, semantic preservation, risks, and stop state

Verified boundary: Work Order 52 Phase C resolved the deterministic patch/application/dependency/package-verifier chain. It does not resolve or reinterpret the device-visible scene-stable material divergence. Structural cause of the former build blocker was stale Diffusion patch context plus a moving Half-Life dependency; the first CI-only failure was an artifact-owner assertion against the wrong Mach-O image. The normalized patch produces the exact same WO52 diagnostic program and the final verifier checks the image that actually owns the bridge.

Remaining risks: Bundle 94 has not been run on an iPhone and is not accepted; the actual producer-to-native material divergence remains unresolved until orchestrator-authorized device evidence exists. Terrain arrays, shader latency, and later map-transition termination remain independent. The tempfile object is temporary; the retained GitHub artifact expires under the workflow retention policy.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in a documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash. Repository-ledger and Google Docs readbacks are required before handoff.

Stop state: **Work Order 52 Phase C Outcome A is complete at the orchestrator-review gate.** Do not contact Arjun, request evidence or device testing, claim device acceptance, modify runtime behavior, start another workflow, create another artifact or tempfile object, begin Phase D, Work Order 53, or any later phase. Await orchestrator review.

## Work Order 52 Phase D - inactive-sampler location-zero alias repaired; Bundle 96 produced

Selected work order and outcome: **WORK ORDER 52 PHASE D — PROVE AND REPAIR INACTIVE-SAMPLER LOCATION-ZERO ALIAS; Outcome A.** Bundle version 96 is one build-qualified structural-repair candidate. It is not device-accepted. Bundle 94 is decisive evidence and must not be retested.

### Verified boundary and structural cause

The complete accepted Bundle-94 evidence places the first bad material-uniform boundary inside the studio renderer before the affected native draw. All 118 audited tokens whose optional unit-2 sampler was recorded at location zero corrupted native `u_MeshParams`; all 138 tokens without that alias preserved it. Ordinary unit-0 diffuse sampling remained correct. Representative corrupt values such as `[-2785.5, -2588, -446]` are cubemap box/origin data, not mesh parameters.

Exact pinned-source inspection proves the ownership defect. Diffusion `GL_CreateUberShader` zero-initializes each `glsl_program_t`. The iOS canonical shader policy deliberately rejects optional `REFLECTION_CUBEMAP`, `BUMP`, `INTERIOR`, `SPECULAR`, and `EMBOSS` directives, so their inactive uniforms are not reflected or assigned. The studio shader builder nevertheless derived `SHADER_USE_CUBEMAPS` and related runtime status from the requested material feature instead of the directives actually admitted to the shader. The zero-filled inactive `u_Cubemap` field was therefore treated as a valid location. `DrawStudioMeshes` later issued `glUniform3fv(location=0, count=3, cubemap_params)`, overwriting the real active `u_MeshParams` vec3 array at location zero. The corrupted values then reached the GL4ES/native draw and produced the stable tan/yellow material substitution.

The GL4ES ownership/lifetime audit independently confirms the invariant already implemented there: a missing uniform lookup begins and remains `-1`, active reflected locations retain their real location including zero, uploads to location `-1` are no-ops, type and extent are checked, relink clears and rebuilds reflection/cache state, variant/FPE mapping uses exact uniform names, and program destruction releases uniform/cache state. No GL4ES behavioral fallback or hardcoded location repair is justified.

### Structural repair and exact files changed

Implementation commit `5cf496cef94a61b44404b2d790981d3b065d98a2` changes exactly:

- `scripts/gha/build_ios.sh`
- `scripts/ios/builddiffusion.sh`
- `scripts/ios/diffusion-wo52-inactive-sampler-ios.patch`
- `scripts/ios/gl4es-wo52-trace-cap-ios.patch`
- `scripts/ios/validate-ios-inactive-sampler.py`
- `scripts/ios/validate-ios-wo52-material-trace.py`
- `scripts/ios/verify_ipa.sh`

The Diffusion patch initializes every conditional solid-studio sampler/location field to `-1`, including cubemap box/sampler/reflect/fresnel, interior, blend, and colormask fields; it applies the corresponding `-1` invariant to dynamic-light conditional fields. A single `GL_AssignSamplerUnit` owner preserves every valid location, including active location zero, and makes a negative location an explicitly logged no-op before any GL upload. Every solid- and dynamic-light studio sampler assignment uses that owner.

Runtime feature/status flags are now derived from the directives actually admitted to the compiled variant, not the material features merely requested before iOS canonical filtering. Thus a requested but filtered cubemap leaves its optional locations at `-1`, does not set the runtime cubemap flag, and cannot reach the conditional unit-2 bind or vec3 upload. The admitted desktop/optional-feature path remains intact. The existing WO52 diagnostic stream is capped from 256 to 16 records and labels the repair without changing draw state. Bundle 69 direct-drawable ownership, Bundle 71 native GLES3 uint indices, Bundle 81 per-unit texture-target selection, Bundle 85 material fixes, menu/touch/callback behavior, and all unrelated renderer/gameplay behavior are preserved.

### Validation performed

- Replayed the exact Diffusion pin `14d156bf3a6993c172697fac83a937836c3b5561` and GL4ES pin `81547d986798e876de8b434193920b606a72363f` through the accepted production patch order; the new patches pass forward/reverse application checks.
- Ran the new executable source/lifecycle harness with self-tests. It proves: active location zero remains writable; an inactive sampler stores/returns `-1`; negative uploads are no-ops; unit-0 diffuse remains intact; optional units 1/2 are assigned only when admitted; and the invariant survives first link, cache hit, relink, variant switch, invalidation, and destroy/recreate.
- Rejection fixtures fail on default-zero optional storage, absent-sampler upload through zero, hardcoded locations, request/admission mismatch, disabling all active cubemaps/materials, incorrect GL4ES missing-location behavior, negative-location writes, stale relink state, and uncapped WO52 diagnostics.
- Passed the full WO52 material-trace, WO51 material-state, Diffusion mobile shader policy, WO49 topology/transform, drawable bridge, native GLES3 uint-elements, index-trace, GL4ES-only topology/transform/texture-unit, and WO52 GL4ES-only positive and rejection suites; Python compilation and `git diff --check` passed.
- The local Windows host has no Bash/Apple linker, so the complete arm64 compile/link/package proof was delegated to the sole macOS Actions run. It successfully built the engine, Half-Life client/server, Diffusion client/server/menu, GL4ES renderer, translated mobile shaders, and IPA; `Verify IPA contract` passed.
- Independent artifact inspection confirmed `CFBundleVersion=96`, `CFBundleExecutable=xash`, `CFBundleIdentifier=su.xash.engine`, `iPhoneOS`, `UIRequiredDeviceCapabilities=arm64`, and thin 64-bit arm64 Mach-O headers (`CFFAEDFE`, CPU bytes `0C000001`) for `xash` and every packaged dylib. The Diffusion client contains all three Phase-D markers below.
- The separately downloaded tempfile object reproduced the exact local filename, size, and SHA-256. Tempfile metadata reports no warning or suspicious pattern; its security result is `safe` and reports the same hash.

### Candidate, CI, IPA, and publication

- Candidate/build status: **Bundle 96, build-qualified Outcome A candidate; not device-accepted.**
- Workflow: [iOS Proof of Life run 32376179206](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32376179206), exact head `5cf496cef94a61b44404b2d790981d3b065d98a2`, **success**. Build, IPA-contract, and artifact-upload steps all succeeded. Exactly one qualifying workflow and one artifact were produced. Automatically triggered generic workflow `32376179291` was policy-skipped and produced no artifact.
- GitHub artifact: `Xash3DiOS-arm64-unsigned`, ID `9409330973`, [artifact page](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32376179206/artifacts/9409330973), archive size `8,608,730` bytes, GitHub archive digest `7ecd1233cd8a1fb7b36fcebc63ad49ec6c27430ef39be692ab9a69521778b7fc`.
- IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,705,975` bytes, SHA-256 `F97A58069297F5017EEAF18E2E435BE399BB9C29D40E3AB98997A819E4E25807`.
- Exactly one tempfile.org object: [information page](https://tempfile.org/LbqPTYCCqAR/); [direct IPA download](https://tempfile.org/LbqPTYCCqAR/download); expiry `2026-08-22T13:56:23.737Z`.

Expected new runtime markers:

- `iOS inactive sampler policy: active location 0 preserved; missing=-1; negative uploads skipped`
- `iOS inactive sampler rejection: program=%s sampler=%s unit=%d location=%d upload=skipped`
- `iOS material uniform proof: requested cubemap omitted by canonical profile; runtime status inactive; conditional locations=-1; draw uploads skipped`

Why this addresses the cause: the repair is placed at both owners of the invalid state. Conditional location storage has the GL-defined missing value from construction onward, and runtime optional-feature status is based on shader admission. The guarded sampler assignment then preserves valid location zero while rejecting only missing locations. This prevents cubemap data from being uploaded through location zero without disabling materials, cubemaps that are actually compiled, unit-0 diffuse sampling, or any unrelated rendering path.

Remaining risks: Bundle 96 has not been device-tested and is not accepted. Device evidence must confirm the 118/118 alias/corruption split disappears and the previously tan/yellow studio materials render normally. Terrain texture arrays, shader-start latency, and later `ch1map1` transition behavior remain separate and are not claimed fixed. The 16-record diagnostic cap is intentionally bounded; it may omit later nonessential records but retains the stable policy/proof markers. GitHub and tempfile retention are finite.

Single device test the orchestrator may choose to relay: install only Bundle 96; launch with `-dev 2 -log -game diffusion -ref gl4es`; choose New Game -> Chapter 1 -> Medium once; wait up to two minutes without extra menu actions; capture one screenshot of the first stable gameplay view, one screenshot after moving/turning enough to show several studio materials, and return the complete resulting `engine.log`. Do not retest Bundle 94.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit after the implementation commit. Its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a commit cannot contain its own hash. Both ledgers are read back after publication.

Stop state: **Work Order 52 Phase D Outcome A implementation, validation, the sole qualifying Bundle-96 workflow/artifact, independent IPA verification, exactly one tempfile.org upload, and both durable-ledger reports are complete. Stop for orchestrator review.** Do not contact Arjun, request evidence or testing directly, claim device acceptance, start another workflow, create another artifact/upload, implement a further repair, begin Phase E, Work Order 53, or any later phase.

## Work Order 53 Phase A - landscape route source-proven; ch1map1 termination requires iOS evidence

Selected work order and outcome: **WORK ORDER 53 PHASE A — LANDSCAPE CAPABILITY AND CH1MAP1 TRANSITION ROOT-CAUSE AUDIT. Track A is Outcome A; Track B is Outcome C.** This phase is complete at its audit-only proof gate. No runtime or diagnostic source changed, no build or workflow ran, and no candidate, IPA, artifact, or tempfile.org object exists.

### Baseline, scope, and preserved invariants

- Audited clean branch head `6ab4b5e61335f98ad2154669c36e98588284d347`, which is also the fetched remote head. Bundle 96 implementation commit `5cf496cef94a61b44404b2d790981d3b065d98a2` and repository-ledger commit `6ab4b5e61335f98ad2154669c36e98588284d347` remain the accepted subsystem baseline.
- Exact pinned revisions inspected: Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, Diffusion MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, Diffusion executable `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, GL4ES `81547d986798e876de8b434193920b606a72363f`, and SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, plus the current Xash3D engine/ref source.
- The authoritative Bundle-96 screenshots and complete `engine(20260820-163844).log` findings were treated as the device baseline. Bundle 96 remains accepted only for the inactive-sampler/admitted-directive studio-material repair. Its active-location-zero, missing-location-minus-one, conditional-upload, canonical-material, direct-drawable, native uint-index, per-unit texture-target, menu, touch, and gameplay behavior was not changed or reinterpreted.
- Exact files changed by Phase A: `Documentation/XASH3DIOS_PORTING_STATE.md` only. The Google Docs ledger receives the same report. There is no renderer, GL4ES, SDL, Diffusion, engine, shader, gameplay, diagnostic, workflow, or packaging change.

### Track A — Outcome A: the backend route is incomplete, not merely hidden by a legacy token check

Verified failure boundary: Diffusion disables landscapes in `client/render/r_opengl.cpp::GL_InitExtensions` when `GL_CheckExtension("GL_EXT_texture_array", ...)` cannot find that literal token in the GL4ES-provided `GL_EXTENSIONS` string. The check does not treat an ES3 core version as an alternative. That predicate is desktop/legacy-token-only, but changing it would cross into a second, source-proven failure: the pinned GL4ES implementation cannot carry Diffusion's array resources and `sampler2DArray` shaders to native GLES3.

Evidence chain and exact owners:

1. Diffusion `client/render/r_opengl.cpp::GL_CheckExtension` tests extension-style names only by literal substring. `GL_InitExtensions` registers `GL_EXT_texture_array` as `R_TEXTURE_ARRAY_EXT`; its false branch emits `Landscapes will be unavailable`. Diffusion terrain source then gates `GLSL_ALLOW_TEXTURE_ARRAY`, loads/creates arrays in `client/render/r_misc.cpp`, and declares `sampler2DArray` in the bmodel/terrain shader sources.
2. The engine GL renderer has a coherent desktop-side producer route: `ref/gl/gl_image.c::GL_LoadTextureArray` packs layers, marks `IMAGE_MULTILAYER`, chooses `GL_TEXTURE_2D_ARRAY_EXT`, and uploads via `pglTexImage3D`/`pglTexSubImage3D`; `GL_CreateTextureArray` enforces the renderer capability before using that route. This proves the intended allocation → upload boundary and also proves that the application needs more than an enum or warning override.
3. GL4ES discovers the live native version and native extension string in `src/glx/hardext.c` only after a context is current. Bundle 71 uses the native ES-major result for the separately proven uint-index invariant, but `hardext_t` contains no texture-array capability, maximum-layer, or native array-entry-point contract. Its configured `esversion` remains the GL4ES backend mode, not a complete declaration of every live ES3 core feature.
4. `src/gl/getter.c::BuildExtensionsList` synthesizes the desktop extension string and deliberately does not advertise `GL_EXT_texture_array`. This is consistent with the implementation. `src/gl/texture.h::map_tex_target`, `what_target`, and `to_target`, the enabled-target enum, per-unit binding state, and texture realization code have no distinct 2D-array target. Unknown array targets cannot acquire independent object/binding/parameter state.
5. `src/gl/texture_3d.c` labels its implementation as 3D stubs. `gl4es_glTexImage3D` and `gl4es_glTexSubImage3D` discard array/3D depth semantics through the 2D route; storage handles only level zero; copy discards the z layer. The native GLES3 `glTexImage3D`/`glTexSubImage3D` entry points are not owned as a complete route.
6. The shader side is independently incomplete. `src/gl/shaderconv.c` rewrites emulated 3D samplers as `sampler2D`; `src/gl/fpe_shader.c` only models 2D, rectangle, emulated 3D, cube, and stream categories; `src/gl/uniform.c` and `src/gl/program.c` recognize only 2D/cube sampler routing. There is no `sampler2DArray` translation/reflection, layer-coordinate preservation, texture-unit type, or ESSL 300 array-sampling route.
7. The Android/native-GLES control does not create an alternate pinned implementation: the platform changes context/bootstrap mechanics, while the same GL4ES target, upload, state, and shader-conversion sources remain. A native ES3 context can support arrays, but this wrapper does not expose that capability coherently on either iOS or Android merely because the native version is ES3.

Structural cause: there are two adjacent facts, not one interchangeable defect. Diffusion's capability predicate is legacy-token-only, while GL4ES correctly withholds that token because its texture-array subsystem is absent. The Bundle-96 log's native `OpenGL ES 3.0 Metal` line proves potential driver capability, not wrapper correctness. Advertising the token, accepting ES3 alone, adding enum aliases, forwarding only `glTexImage3D`, or mapping arrays onto 2D/3D would let the application enter a route whose binding, parameters, layers, shader type, reflection, and draw semantics remain wrong.

Rejected hypotheses and approaches: memory pressure is not supported as the landscape-disable cause; the warning is emitted deterministically during capability initialization. Asset absence is downstream of the disabled route, not the cause of this warning. A token spoof, version-only predicate, source-name exception, 2D fallback, layer-zero sampling, or upload-only forwarding is rejected because each violates the verified whole-route invariant. The accepted Bundle-96 sampler repair is unrelated and remains untouched.

Minimal future repair boundary: a future authorized Phase B must begin at the renderer-wrapper architecture, not at the warning. Before Diffusion may enable landscapes, one selected route must prove all of these together: post-current-context native ES3/core discovery; layer limits; a distinct array target and per-unit binding/parameter/object lifecycle; the native 3D allocation/subimage and any actually used compressed/immutable operations; exact layer preservation; `sampler2DArray` parsing, reflection, unit routing, and ESSL-300-compatible translation; relink/context-loss cleanup; and an offscreen native conformance harness that uploads distinguishable layers and verifies layer-selecting draws. Only after that proof may GL4ES advertise a compatibility token or Diffusion accept a core-capability contract. This is the smallest structural boundary, but it is migration-scale rather than a one-line repair. No diagnostic candidate is justified in Phase A.

Why Outcome A satisfies the order: source inspection distinguishes the competing explanations without runtime instrumentation. The warning is reached through a narrow predicate, but the correct repair cannot end there because the complete consumer route is demonstrably missing.

### Track B — Outcome C: engine.log narrows the span but cannot classify the termination

Verified transition path and boundary:

1. `engine/server/sv_save.c::SV_ChangeLevel` saves the old level state, inactivates clients, and calls `SV_DeactivateServer`; `engine/server/sv_init.c::SV_DeactivateServer` queues `maps/ch1map0_unload.cfg`. `SV_SpawnServer` queues `maps/ch1map1_load.cfg`, prints `Spawn Server: ch1map1 [to_map1]`, loads `maps/ch1map1.bsp`, creates the new server/world state, and returns before entity spawn or activation.
2. `LoadGameState("ch1map1", true)` calls `LoadSaveData`, whose `save/ch1map1.HL1` open may fail. `SV_ChangeLevel` explicitly handles false by calling `SV_SpawnEntities("ch1map1")`. The file is the serialized state of a previously visited destination level; it is not a required map asset on first arrival. The Bundle-96 path proceeds through the documented fallback, so the missing file is rejected as the proven fault.
3. `SV_SpawnEntities` calls `SV_LoadFromFile`, which parses BSP entities and invokes the game DLL's `pfnSpawn`. Model precache proceeds through `pfnPrecacheModel` → `Mod_ForName` → `Mod_LoadModel` → `Mod_LoadStudioModel` → engine `ref/gl/gl_context.c::Mod_ProcessRenderData` → Diffusion `HUD_ProcessModelData`/`R_ProcessStudioData` → `CStudioModelRenderer::ProcessUserData` → `CreateMeshCache`/`LoadStudioMaterials` → `GL_UberShaderForSolidStudio` → `GL_FindUberShader` → `GL_CreateUberShader`.
4. In `client/render/r_shader.cpp::GL_CreateUberShader`, the `CompileUberShader #60: StudioSolid` line is after both shader-stage loads/compiles, `GL_LinkProgram`, and the solid-studio uniform initializer. Therefore the final line proves that shader #60 compile, link, and uniform registration returned. It does not prove that all post-link bookkeeping or the enclosing model/entity spawn returned.
5. Immediately after the marker, the synchronous source path conditionally appends `shaders_unlisted.log` when developer/precompile state enables it; conditionally queries/extracts/saves a program binary when `R_BINARY_SHADER_EXT` is active; increments/registers the program; returns through the remaining material, mesh-cache, model-load, and game-entity spawn work; and only then can `SV_SpawnEntities` return to `SV_ChangeLevel`.
6. `SV_ActivateServer(false)` is textually after that return. It would call the game DLL's server activation, run settling physics, build baselines/resources, print `Game started`, and set `ss_active`. None of those markers occurs. If activation completed, the normal frame path would later continue through `Host_Frame`/`Host_ClientFrame` → `SCR_UpdateScreen` → `V_RenderView`/`GL_RenderFrame` and Diffusion's custom renderer for the first `ch1map1` client frame. The accepted log reaches neither activation nor that frame.

The tightest proven failure boundary is therefore: **after successful shader-60 compile/link/uniform initialization, within the remaining synchronous fresh-entity/model-realization span, and before `SV_ActivateServer` can report success.** Owners still live in that span include Diffusion shader/material/mesh-cache code, GL4ES/native program-binary calls when enabled, engine filesystem/model allocation and render-data callbacks, and the game DLL's remaining entity-spawn work.

Rejected classifications: shader-60 compile/link failure is contradicted by marker placement. The missing `.HL1` is an explicit optional fallback. There is no source or log evidence of a recursive changelevel, assertion, in-process signal/backtrace, GL error tied to termination, or reached first-frame/presentation path. The existing record also contains no resident-memory trajectory, Jetsam reason, watchdog code, exception type, faulting thread, or termination namespace. Static ownership cannot distinguish an application crash in any remaining owner from an iOS watchdog, Jetsam, external termination, or an alive-but-stalled process. Texture arrays, Bundle-96 sampler state, presentation, MSAA, topology, and startup shader latency are independent and do not classify this event.

Mandatory external discriminator: before any transition code change, retrieve the complete timestamp-matched iOS diagnostic for process `xash` / bundle `su.xash.engine`. Preferred routes are Xcode's connected-device **Devices and Simulators → View Device Logs**, or the iPhone's **Settings → Privacy & Security → Analytics & Improvements → Analytics Data** export. Match the incident to the `engine(20260820-163844).log` reproduction interval and return the full `.ips`, not a screenshot or excerpt. Check for an app crash/watchdog report named for `xash` and for a `JetsamEvent` covering the same interval. Correlate timestamp, process/bundle identity, incident identifier, exception/termination namespace and code, triggered-thread backtrace, and binary UUID; for Jetsam, also preserve reason, memory-status snapshot, process row, and page/footprint fields. If neither report exists, a Mac device-console capture spanning the exact disappearance is the next external evidence, because it can distinguish an alive process from OS termination.

Smallest later discriminator, only if the external record proves the app remained alive and the orchestrator separately authorizes instrumentation: one transition ID with monotonic timestamps at the complete remaining boundary—post-shader-marker return, post-program-binary branch, material loop exit, mesh-cache/model callback exit, `SV_SpawnEntities` exit, `SV_ActivateServer` entry/exit, and first client render entry. The terminal summary must name the last completed and next pending checkpoint. Instrumenting only shader #60 would repeat the already-settled boundary and is forbidden.

Proposed minimal Phase B scope: first classify and symbolicate the timestamp-matched iOS report against the retained Bundle-96 binary/archive. A crash stack permits a source audit of the named owner; a watchdog report requires main-thread stack/duration analysis; a Jetsam report requires subsystem memory accounting. No runtime mutation is responsible until that classification exists. If external evidence instead proves no termination, only the single end-to-end discriminator above becomes eligible under a new order.

Anti-whack-a-mole rationale: the accepted evidence spans multiple synchronous owners after a successful shader link. Changing the last visible call would confuse log position with causation. OS-level termination evidence is the only non-speculative way to select the next subsystem, just as the complete texture-array invariant—not an extension token—is the only safe landscape repair boundary.

### Validation, publication, and stop state

- Used the codebase knowledge graph first for `SV_ChangeLevel`, `SV_SpawnServer`, `LoadGameState`, `SV_SpawnEntities`, `SV_LoadFromFile`, `pfnPrecacheModel`, `Mod_LoadModel`, `Mod_LoadStudioModel`, `SV_ActivateServer`, `Host_Frame`, `SCR_UpdateScreen`, and render-frame ownership; inspected the exact source bodies and the applied pinned Diffusion/GL4ES trees for ignored external sources.
- Reproduced the landscape owner inventory with bounded `rg` searches covering the warning, array producers, engine upload target, GL4ES extension builder, target mapping/state, 3D stubs, shader conversion, sampler reflection, and platform guards. Read the authoritative Work Order 53 and Bundle-96 acceptance evidence from the connected Google Doc through a file-backed trusted read.
- Re-fetched the remote branch and verified local/remote head equality and a clean starting tree. No source, patch, configuration, workflow, or dependency file changed. No build was required or authorized. Final documentation validation includes `git diff --check`, exact one-file diff inspection, both-ledger readback, and remote commit verification.
- Candidate/build status: **none; audit-only**. Workflow ID/URL/result: **none; no workflow authorized or started**. IPA filename, size, SHA-256, GitHub artifact, and tempfile.org link: **none**. Expected new runtime markers: **none**; Bundle-96 markers and behavior remain unchanged.

Remaining risks: Track A's future repair boundary is broad enough to require an explicit architecture choice and native conformance proof. Track B's exact terminating owner remains unresolved until the timestamp-matched iOS report is obtained and symbolicated. The engine log alone cannot support a repair. No device test is requested by this worker; the only evidence request the orchestrator may later relay is the complete already-produced timestamp-matched `.ips`/`JetsamEvent` (or exact-interval device console if neither exists), without rerunning Bundle 94 or Bundle 96.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit; its exact commit is mirrored into the authoritative Google Docs ledger after publication because a Git commit cannot contain its own hash. Both ledgers are read back after the Google Docs append.

Stop state: **Work Order 53 Phase A is complete at the orchestrator-review gate: Track A Outcome A, Track B Outcome C.** Do not implement either repair, add diagnostics, build, run CI, produce/upload an IPA, contact Arjun, request a new device test, begin Phase B, Work Order 54, or any later phase without a new explicit orchestrator-authored work order.

## Work Order 53 Phase B - Outcome B at the complete-route proof gate

Selected work order and outcome: **WORK ORDER 53 PHASE B — COMPLETE GLES3 TEXTURE-ARRAY PATH FOR DIFFUSION LANDSCAPES. Outcome B.** The full source-to-native texture-array route cannot be completed and proven safely inside the authorized branch, exact pins, existing external-context architecture, and single-qualifying-workflow gate. No partial feature advertisement, runtime change, diagnostic change, build, workflow, artifact, IPA, or tempfile.org object was produced.

### Authority, baseline, and preserved invariants

- The authoritative Google Docs ledger was read through its newest complete entry and Work Order 53 Phase B was confirmed as the first uncompleted work order after the accepted Phase A report.
- The audit began from a clean local and fetched remote `agent/ios-proof-of-life` head at `7ca216f6c4a7dc01051c3485d717dab75db63791`. Bundle 96's implementation commit remains `5cf496cef94a61b44404b2d790981d3b065d98a2` and is preserved exactly.
- Exact source pins remain GL4ES `81547d986798e876de8b434193920b606a72363f`, Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, executable/engine `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, and Half-Life SDK `079f2387eb59e4a045647d9057240628130f0058`.
- Bundle 69 direct-drawable ownership, Bundle 71 native-ES3 uint elements, Bundle 81 per-unit target-source selection, Bundle 96 inactive-sampler handling, canonical studio materials, Diffusion menu/touch/gameplay behavior, and Track B transition quarantine are unchanged.

### Exact Outcome-B boundary

The first complete-route proof failure is not the legacy extension string. It is the coupled **GLSL-130-to-native-ESSL-300 program route plus native current-context conformance requirement**:

1. Applied pinned Diffusion still emits `#version 130` in `client/render/r_shader.cpp::GL_ProcessShader`. Terrain-enabled bmodel programs mix `sampler2DArray`/`texture2DArray` with legacy `attribute`, `varying`, `gl_FragColor`, `texture2D`, `texture2DProj`, and `textureCube` syntax.
2. Applied pinned GL4ES `src/gl/shaderconv.c::ConvertShader` always selects `GLESHeader[0]`, which emits ESSL 100. Its higher-version branch remains compiled out with the source warning that higher GLSL requires substantially more work. The dormant ESSL-300 header maps `varying` to `out` for both stages, provides no fragment input/output repair, does not translate the legacy lookup family, and does not admit Diffusion's GLSL 130 source. It therefore cannot compile a coherent native array-sampler program.
3. `src/gl/program.c` and `src/gl/uniform.c` classify, cache, initialize, and route only `GL_SAMPLER_2D` and `GL_SAMPLER_CUBE`. `GL_SAMPLER_2D_ARRAY` has no cache size, integer-uniform classification, texture-unit type, reflection route, or required-target realization.
4. The iOS workflow cross-compiles an iPhoneOS arm64 payload and packages an IPA. It has no iOS Simulator/device execution job, XCTest/EAGL conformance target, `simctl` launch, or offscreen array upload/sample/readback test. Consequently the required multiple-layer, nonzero-mip, subimage, sampler-coordinate, delete/rebind, and context-recreation invariants cannot be proven by the sole qualifying workflow. A successful compile would not satisfy the order's native proof gate.

Every downstream route remains incomplete as well:

- `src/gl/texture.h` has no distinct array member in `texture_enabled_t`. `what_target(GL_TEXTURE_2D_ARRAY)` falls through to `ENABLED_TEX2D`; `to_target`, enable masks, saved state, and `texture_state_t::bound` therefore cannot preserve an array target independently.
- Applied Bundle-81 `realize_textures` correctly derives a target per unit, but all non-cube targets still share `glstate->actual_tex2d` and are natively rebound with `gles_glBindTexture(GL_TEXTURE_2D, ...)`. An array object would alias 2D cache/state rather than retain its native target.
- `src/gl/texture_3d.c` explicitly implements “3d stubs.” `gl4es_glTexImage3D` and `gl4es_glTexSubImage3D` call 2D wrappers, discard the supplied target/depth/z-offset semantics, and `glTexStorage3D` allocates only level zero through that same stub. This contradicts the engine's proven multilayer/mipmap producer contract in `ref/gl/gl_image.c`.
- `hardext_t` has no texture-array capability, maximum-layer value, native 3D-entry-point admission, or generation-scoped reset state. The NOEGL/NO_LOADER iOS build probes the SDL-owned current context only through the existing singleton initialization path; the direct-drawable lifecycle bridge exposes presentation generations but no renderer-wrapper array capability invalidation/re-probe contract.
- `BuildExtensionsList` correctly omits `GL_EXT_texture_array`. Diffusion's literal token check is narrow, but changing it or advertising the token before the complete route exists would enter invalid object, upload, shader, reflection, and draw semantics.

Structural cause: the exact pinned GL4ES is an ES2-oriented desktop-compatibility translator whose texture object model, native binding cache, upload ABI, shader conversion, reflection, and lifecycle ownership all lack arrays. Native `OpenGL ES 3.0 Metal` capability is necessary but not sufficient. The required repair is a separately testable renderer-wrapper migration, not an additive enum or upload function.

### Why no implementation or candidate is responsible

Work Order 53 Phase B permits Outcome A only when every route is present and proven, and explicitly requires Outcome B when the complete route cannot be implemented safely. Adding only `GL_TEXTURE_2D_ARRAY`, forwarding only `glTexImage3D`, accepting ES3 in Diffusion, translating only `sampler2DArray`, or advertising the legacy token would each leave independently proven contract violations. A source-name shader exception, 2D flattening, layer-zero fallback, atlas, or GLES2 downgrade is likewise forbidden.

Completing the route would require one coordinated subsystem across at least capability/lifecycle discovery, texture object and push/pop state, target-aware native caches, 3D allocation/subupload and pixel-store/PBO conversion, program/uniform/fixed-pipeline sampler classification, full stage-correct ESSL-300 translation, Diffusion admission, context teardown/recreation, engine-log markers, and an executable native EAGL conformance harness. Implementing that migration without a runnable prequalification harness and then relying on the only authorized workflow to discover Apple/native defects would violate the one-candidate proof gate rather than prove it.

No Track B transition, crash, save fallback, server activation, shader-latency, gameplay, menu, touch, drawable, index, sampler-location, material, or asset behavior was touched.

### Validation, publication, and stop state

- Used Codebase Memory first for engine texture-array producers, capability owners, and renderer entry points, then inspected the ignored pinned GL4ES and Diffusion sources directly.
- Fetched and verified the clean remote branch. Cloned exact pinned GL4ES and Diffusion audit trees. The complete current GL4ES iOS patch order replayed cleanly: base iOS, direct drawable, uint elements, index trace, WO49 topology, WO49 transform, WO49 texture-unit, WO52 material trace, and WO52 trace cap. Relevant current Diffusion client patches and exact terrain consumers were inspected at their pin.
- Reconfirmed the engine allocation/upload consumer, Diffusion admission and terrain shader families, GL4ES target/state, upload stubs, shader converter, reflection/uniform routing, hardext lifecycle, build defines, and the sole iOS workflow's execution surface.
- Candidate/build status: **none; Outcome B before build**. Workflow ID/URL/result: **none; no workflow authorized after proof failure and none started**. Artifact and IPA filename/link/size/SHA-256: **none**. tempfile.org link/expiry: **none**. Expected new runtime markers: **none**, because no executable changed.
- Exact repository file changed by Phase B: `Documentation/XASH3DIOS_PORTING_STATE.md` only. The authoritative Google Docs ledger receives this same report. The repository report is published in one documentation-only `[skip ci]` commit and both ledgers are read back.

Remaining risks: landscapes remain unavailable. A future order would need to authorize a renderer-wrapper migration and a native simulator/device conformance milestone before any gameplay candidate; merely expanding workflow count would not remove the architectural work. Bundle 96 remains only the current device baseline for its accepted inactive-sampler subsystem. The `ch1map1` termination remains quarantined pending external iOS termination evidence.

Stop state: **Work Order 53 Phase B is complete at Outcome B and the orchestrator-review gate.** Do not implement or publish a partial texture-array route, build, run CI, create/upload an IPA, request device testing or evidence, contact Arjun, modify Track B, begin Work Order 54, or start any later phase without a new explicit orchestrator-authored work order.

## Work Order 54 Phase A - Outcome B: no complete Diffusion-side terrain fallback fits the proven limits

Selected work order and outcome: **WORK ORDER 54 PHASE A — SELECT A COMPLETE DIFFUSION-SIDE TERRAIN FALLBACK. Outcome B.** No application-side route based only on the already-proven `GL_TEXTURE_2D`, `sampler2D`, and ESSL-100 primitives preserves Diffusion's complete shipped terrain contract within portable GLES3/GL4ES limits. This phase is audit-only: no runtime source, patch, build configuration, workflow, artifact, IPA, tempfile.org object, or device-test request was created.

### Authority, baseline, and preserved invariants

- The authoritative Google Docs ledger was read through its newest complete entry. Work Order 54 Phase A was the first explicit work order without a later matching completion report; no later amendment or authorization was present before this report.
- The audit began from clean local and fetched remote `agent/ios-proof-of-life` at `0184bd0fa55f79bc6f5af22e437670b9bf1da841`. Bundle 96's implementation remains `5cf496cef94a61b44404b2d790981d3b065d98a2`.
- Exact pins remain executable/engine `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, GL4ES `81547d986798e876de8b434193920b606a72363f`, and Half-Life SDK `079f2387eb59e4a045647d9057240628130f0058`.
- Work Order 53 Phase B Outcome B is binding. No partial array implementation, ESSL-300 fragment, extension advertisement, capability-token spoof, or layer-zero substitution is revived. Bundle 69 direct-drawable ownership, Bundle 71 native-ES3 uint indices, Bundle 81 per-unit texture-target selection, Bundle 96 inactive-sampler repair, canonical materials, menu/touch/gameplay behavior, and the quarantined `ch1map1` transition track are unchanged.

### Complete audited terrain contract and lifecycle

The producer-to-consumer route is structural, not a single texture lookup:

1. `client/render/r_misc.cpp::R_LoadLandscapes` parses `maps/<map>_land.txt`, accepts `layer0` through `layer15`, and records a fundamental `MAX_LANDSCAPE_LAYERS` limit of 16. `LoadHeightMap` retains and expands the source index image, derives the active layer weights with a wrapped `FILTER_SIZE=2` neighborhood, keeps one CPU byte per index-map texel for terrain/foliage consumers, and packs four weights per RGBA slice. The weight representation therefore requires `ceil(N/4)`, up to four slices. It is created clamped with alpha.
2. `LoadTerrainLayers` loads every diffuse material to retain `DynlightScale`, `GlossScale`, `GlossSmoothness`, and `EmbossScale`; creates one diffuse array; and creates a normal array only when every layer supplies a normal map. The engine array loader requires common format/type/mip encoding, resamples raw layers to the first layer's dimensions when necessary, preserves the entire source mip chain, and uploads every layer at every mip. Diffuse and normal layers retain repeat semantics; the weight array is clamped. Filtering, trilinear mip selection, anisotropy where supported, and pixel-store/upload conversion remain engine-owned.
3. The solid and dynamic-light terrain shader families compile exact `TERRAIN_NUM_LAYERS` variants. `glsl/terrain.h` samples up to four weight slices and fixed integral diffuse/normal layers 0 through 15. Weighted diffuse, weighted-and-renormalized normals, and weighted per-layer material parameters feed the ordinary alpha, lightmap/deluxe, dynamic-light, projection/shadow, specular, emboss, reflection, fog, and lighting paths. `glsl/specular.h` can add one diffuse lookup per layer; `glsl/emboss.h` can add nine per layer and depends on texture dimensions. The theoretical 16-layer feature combination can therefore require four weight, 16 diffuse, 16 normal, 16 gloss-source, and 144 emboss-source fetches before unrelated lighting/shadow lookups, although feature variants omit unused groups.
4. Solid programs currently assign array color, normal, and weight samplers to units 0, 4, and 5 while lightmap/deluxe/screen/cubemap resources occupy other variants. Dynamic-light programs use array color, weight, and normal units 0, 5, and 6 while projection, shadow, depth, and optional interior resources occupy other units. This coexistence is part of the terrain contract, not spare capacity.
5. Landscapes load before world materials in `Mod_LoadWorld`, participate in surface mapping and shader selection, and are freed by `Mod_FreeWorld`/`R_FreeLandscapes` on map unload. That destructor releases CPU index data, diffuse and normal arrays, the global diffuse image, and the weight array. A replacement must rebuild deterministically across map changes and renderer/context generations; the existing application retains asset names and the index CPU image, but it does not retain a complete application-owned CPU copy of every diffuse/normal mip for an atlas rebuild.

No shipped map, texture, `_land.txt`, PK3, or WAD manifest is present in the pinned source or packaged application repository, so a smaller asset bound cannot be proven locally. The runtime-generated `client/render/r_shaderlist.h` contains 45 observed terrain entries: 8 for two layers, 17 for three, and 20 for four; observed maximum 4. That file is historical shader-cache evidence, not an authoritative manifest for the user-supplied `res0.pk3`, `res1.pk3`, and `res2.pk3`, and cannot narrow the accepted 1–16 source contract. Theoretical maximum 16 is therefore the required completeness bound.

The portable hardware envelope is also exact. Khronos OpenGL ES 3.0.6 tables 6.28 and 6.32 guarantee `GL_MAX_TEXTURE_SIZE >= 2048` and only 16 fragment texture image units; table 6.33 guarantees 15 varying vectors. The pinned GL4ES has `MAX_TEX=16`, queries the native fragment-unit and varying limits, and clamps the exposed fragment-unit count to that same 16. Bundle-85's phone reported larger texture dimensions but still 16 fragment units; those device values are observations, not admissible portable assumptions. GL4ES exposes explicit fragment gradients/LOD only when optional `GL_EXT_shader_texture_lod` is present and not disabled, so an ESSL-100 fallback cannot require that extension.

### Candidate matrix and exact blockers

| Candidate | Capacity and budget | Correctness/lifecycle result | Decision |
| --- | --- | --- | --- |
| Independent `sampler2D` bank with static ESSL-100 variants | For `N=16`, diffuse plus `ceil(N/4)` weight samplers already needs 20 fragment units. Adding the optional-but-shipped normal path raises the terrain-only lower bound to 36 before lightmap, deluxe, projection, shadow, screen, reflection, or depth samplers. Even with no other sampler, 16 units cap diffuse-plus-weights at 12 layers and diffuse-plus-normal-plus-weights at 7. Static ESSL-100 selection needs at least one exact layer-count family per solid/dlight feature combination; the existing cache already records 45 variants for only counts 2–4. | Individual 2D objects could preserve each layer's mips, repeat/clamp, filtering, deletion, reload, and total texel memory, but they cannot bind the complete 16-layer contract in one fragment program. Dynamic sampler-array indexing is not a portable ESSL-100 escape. | Rejected numerically. It is incomplete before ancillary terrain lighting is counted. |
| Deterministic 2D atlases for diffuse, normal, and weights | A square 4-by-4 atlas is the best dimension bound for 16 equal layers. Against the guaranteed 2048 texture size it admits at most 512-by-512 source layers before any per-mip gutter. The current array contract independently admits a 2048-by-2048 layer and resamples peer layers to it. A 2-by-2 weight atlas has the same class of bound for its four slices. Base texel memory is array-equivalent, but every mip needs repeated-edge gutters and startup repacking; a persistent rebuild cache adds CPU memory. | Diffuse/normal coordinates intentionally repeat. Applying `fract` inside a tile makes implicit derivatives discontinuous at every wrap. Exact trilinear/anisotropic LOD across tile edges requires original-coordinate gradients and per-mip repeated gutters, but explicit fragment gradients/LOD are optional in ESSL 100/this GL4ES path. Fixed gutters cannot preserve arbitrary anisotropic footprints. Deep mips collapse tiles/gutters, `textureSize`-based emboss needs replacement dimensions, and context recreation needs retained/reloaded source mip data. No shipped manifest proves safe layer dimensions or restricted wrap/filter/aniso use. | Rejected numerically and semantically. It cannot represent every legal source size or guarantee seam-, wrap-, mip-, and anisotropy-equivalent sampling. |
| Semantically equivalent multipass terrain | A naive route requires up to 16 layer draws plus resolution; grouping remains limited by the same sampler budget. It multiplies brush submissions and overdraw, with no source-level bounded performance proof. A truly equivalent route needs intermediate color/normal/material accumulation surfaces and a final lighting resolve. | Additive per-layer color is not equivalent to the current program: normals are summed then normalized; gloss/smoothness/emboss/dynamic-light scales are weighted before nonlinear lighting; combined alpha controls discard; shadows, lightmaps/deluxe, specular, fog, and reflections are applied with order-dependent state. Reapplying these per layer overcounts or changes them. Preserving them requires a new deferred-like accumulation renderer, new FBO formats, blend/depth ownership, and context lifecycle—not a proven 2D compatibility path. | Rejected semantically. The simple route changes pixels; the correct route is a new renderer subsystem with unproven memory/performance limits. |
| Existing Diffusion compatibility/history route | Source and bounded history searches found no non-array landscape renderer, cvar, low-feature terrain path, or complete compatibility implementation. `sampler2DArray` exists from the initial shader import; the later terrain change only adjusted conditionals. | The global `indexmap.gl_diffuse_id` and ordinary surface texture are mapping/material auxiliaries. `Mod_MappingLandscapes` refuses to mark the surface as landscape when the diffuse array was not created. Binding the global image or layer zero would remove shipped layer blending, normals, and material behavior. | Rejected as nonexistent. The apparent single-texture fallback is exactly the forbidden flat/global or layer-zero degradation. |

Flat terrain, layer-zero-only sampling, landscape disablement, removed geometry, hard-coded `ch1map0`, map/asset-name exceptions, screenshots as proof, desktop behavior changes, partial arrays, and token spoofing remain explicitly rejected.

### Selected larger alternative and future proof surface

Because every application-only alternative fails a numeric or semantic invariant, the smallest responsible larger alternative remains the **separately testable GL4ES texture-array migration identified by Work Order 53 Phase B**, not a native whole-renderer rewrite and not a Diffusion terrain approximation. It preserves Diffusion's existing assets, array layer identity, mips, repeat/clamp/filter behavior, shader weighting, solid/dlight integration, material parameters, and map lifecycle. Its larger implementation surface must be authorized separately and must include all of these together:

- Native current-context capability discovery and generation-scoped reset in `src/glx/hardext.[ch]`, including the real ES3 array-layer limit and 3D entry points without changing SDL/direct-drawable presentation ownership.
- A distinct array target/object/binding/parameter/cache identity in GL4ES texture and state owners (`src/gl/texture*`, `glstate`, save/restore, per-unit realization), with native `glTexImage3D`, `glTexSubImage3D`, mip, format/type, pixel-store/PBO, delete/unbind, relink, background/foreground, and context-recreation semantics. Array objects must never alias the accepted 2D cache.
- `GL_SAMPLER_2D_ARRAY` reflection, uniform classification, sampler-unit routing, program relink/destruction, and fixed-pipeline/variant cache ownership in `src/gl/program.c`, `uniform.c`, and related program state.
- A complete stage-correct ESSL-300 converter in `src/gl/shaderconv.c`: Diffusion GLSL-130 admission; vertex outputs/fragment inputs; explicit fragment output; legacy lookup conversion; array samplers/lookups; precision; directives; and coherent cache identity. No source-name exception or terrain-only token rewrite is admissible.
- Diffusion admission only after the renderer route is proven. Its landscape producers, shaders, material weighting, and desktop path should remain unchanged except for a capability predicate that reflects the complete core route rather than a legacy extension string.

The proof plan must precede any gameplay candidate. A native offscreen ES3 harness must allocate and subupdate distinguishable 16-layer diffuse and normal arrays plus four weight layers; exercise nonzero mips, repeat and clamp, nearest/linear/trilinear state, nonzero layer selection, high-layer non-aliasing, delete/rebind, map-style teardown/reload, and context destruction/recreation; compile/link both solid- and dynamic-light-shaped translated programs; draw/read back every layer and representative blends; and run under the same current-context ownership used by the app. Positive fixtures must then replay exact pins and all accepted patch-policy suites, compile affected units, build arm64 engine/Half-Life/Diffusion, and verify the IPA contract. Rejection and mutation fixtures must fail on capability-only advertisement, 2D/array target aliasing, flattened depth, lost z-offset/mip, missing array sampler reflection, stage-wrong ESSL-300 I/O, legacy lookup leakage, high-layer aliasing, stale context generations, partial lifecycle cleanup, or desktop-path mutation. Only after those gates may one later orchestrator-authorized gameplay candidate exist.

### Validation, publication, risks, and stop state

- Used Codebase Memory first for engine array producers and their call ownership, then inspected the ignored exact-pin Diffusion and GL4ES audit trees directly where the graph had no coverage.
- Reproduced the full producer/upload/bind/shader/free lifecycle; exact layer/unit/fetch budgets; the 45-entry observed shader-list distribution; source/history fallback absence; and the pinned GL4ES unit, varying, texture-size, shader-LOD, and target behavior. Cross-checked portable limits against the Khronos OpenGL ES 3.0.6 specification rather than treating one iPhone as the contract.
- Desktop isolation is preserved because no source changed. Proposed future admission is iOS/renderer-capability bounded and leaves Diffusion's desktop array route intact.
- Candidate/build status: **none; Outcome B before implementation/build**. Workflow ID/URL/result: **none; no workflow authorized or started**. IPA filename, size, SHA-256, GitHub artifact, and tempfile.org link: **none**. Expected new runtime markers: **none**, because no executable changed.
- Exact repository file changed: `Documentation/XASH3DIOS_PORTING_STATE.md` only. This report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash. Both ledgers are read back after publication.

Verified boundary: landscapes remain blocked at the complete texture-array contract. Structural cause: Diffusion's accepted terrain semantics require an array-like 16-layer representation with coherent layer selection inside one lighting program; portable 2D-only alternatives either exceed the 16-unit fragment budget or change mip/wrap/filter, nonlinear material/normal/lighting, size, lifecycle, or performance semantics. The remaining discriminator is architectural, not runtime: only a complete renderer-wrapper array route can retain the contract without altering Diffusion content.

Remaining risks: the recommended GL4ES migration is subsystem-scale and still lacks the required runnable native conformance target. No future implementation is authorized by this report. Bundle 96 remains the device baseline for its accepted inactive-sampler subsystem; landscapes remain unavailable; the `ch1map1` termination remains separately quarantined pending its external iOS termination record.

Stop state: **Work Order 54 Phase A is complete at Outcome B and the orchestrator-review gate.** Do not begin Phase B, Work Order 55, a renderer migration, transition work, runtime diagnostics, a build, workflow, IPA, upload, or device test; do not contact Arjun or request evidence/testing. Await a new explicit orchestrator-authored work order.

## Work Order 55 Phase A - Outcome B: no source-complete, bounded GL4ES array foundation is available to backport

Selected work order and outcome: **WORK ORDER 55 PHASE A — IMPLEMENT AND PROVE THE COMPLETE GL4ES TEXTURE-ARRAY FOUNDATION. Outcome B.** The mandatory provenance and closure audit found no source-complete, ABI-compatible implementation that can be boundedly backported into the pinned GL4ES tree. A partial object, upload, shader, reflection, or lifecycle route would violate this order's no-partial-success gate. No runtime source, patch, harness, build configuration, workflow, artifact, IPA, tempfile.org object, or device-test request was created.

### Authority, baseline, and preserved invariants

- The authoritative Google Docs ledger was read through its newest complete entry. Work Order 55 Phase A was the newest orchestrator-authored work order without a later matching worker report. Its reusable activation prompt is not a separate authorization.
- The audit began from clean local and fetched remote `agent/ios-proof-of-life` at the exact required commit `c1ab22505a832f90dc41a82d9e78ad99e5098303`.
- Exact pins remain executable/engine `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`, GL4ES `81547d986798e876de8b434193920b606a72363f`, Half-Life SDK `079f2387eb59e4a045647d9057240628130f0058`, and NanoGL `7f654d2de2680c7f6007aef5159ed63247741620`.
- Bundle 96's inactive-sampler repair, Bundle 69 direct-drawable ownership, Bundle 71 native-ES3 uint-index behavior, Bundle 81 per-unit target selection, canonical materials, Diffusion menu/touch/gameplay behavior, desktop rendering, and the quarantined `ch1map1` transition track are unchanged.
- The texture-array capability remains disabled and unadvertised to Diffusion. No `GL_TEXTURE_2D_ARRAY` object, `sampler2DArray` shader, token spoof, layer-zero substitute, sampler bank, atlas, multipass route, map exception, or terrain admission was added.

### Provenance matrix

| Source | Exact revision and relevant surface | Audited result | Backport decision |
| --- | --- | --- | --- |
| Pinned/current upstream GL4ES, `ptitSeb/gl4es` | `81547d986798e876de8b434193920b606a72363f` (also current upstream `master` during this audit); MIT; `src/gl/texture_3d.c`, `texture_compressed.c`, `texture.h`, `texture_params.c`, `program.c`, `shaderconv.c`, `hardext.[ch]`, `glstate.c`, `init.c` | Array enums/prototypes occur only in imported headers. `glTexImage3D` and `glTexSubImage3D` call 2D wrappers and discard depth/z; compressed 3D calls likewise flatten. `map_tex_target` maps 3D to 2D and has no array target. There is one shared `actual_tex2d` native cache. Reflection classifies only `GL_SAMPLER_2D` and `GL_SAMPLER_CUBE`. The GLSL-120/ESSL-300 selection block is compiled out with `#if 0`. Hardware discovery tests whether GLSL 300 compiles but does not resolve 3D entry points or query array-layer limits. In the static build, `close_gl4es` does not restore the `inited` guard, so a full destroy/reinitialize cycle cannot rebuild capability state. | Rejected: this is the exact incomplete architecture the order requires replacing, not a source for the missing implementation. Repository history contains no `sampler2DArray` implementation and no post-header `GL_TEXTURE_2D_ARRAY` implementation commit. |
| Archived Android OpenMW integration, `xyzz/openmw-android` | `bfd613230ebe57170cbe4966aa8938d54afa6efa`; `buildscripts/CMakeLists.txt` pins GL4ES `v1.1.4`; local patches are `shared-library.patch`, `gamma.patch`, and `keyword-usage.patch` | The integration proves a conventional Android EGL/shared-library deployment only. Its three GL4ES patches do not implement texture arrays, ESSL-300 conversion, external current-context discovery, or context-generation lifecycle. | Rejected: no relevant source-complete array or lifecycle technique exists to backport. |
| NG-GL4ES public branch, `Sisah2/NG-GL4ES` | `b5bc4268c8fafb04fc0b79d6c1306ca5ed642fa9`; MIT | Its VGPU translator contains generic `sampler2DArray` helper text and broader modern GLSL machinery, but the public texture route retains the upstream 3D flattening stubs and has no distinct array object/binding/reflection route. Importing VGPU would replace a large shader subsystem and would not close object or lifecycle semantics. | Rejected: incomplete for arrays and an unbounded/wholesale fork migration. |
| NG-GL4ES OpenMW3 branch | `72d0029baf1de0b6a85244680316132a4c244164`; `src/gl/texture_3d.c`, `texture_compressed.c`, `texture.h`, `texture_params.c`, `program.[ch]`, `shaderconv.c`, `vgpu/shaderconv.c`, `init.c` | This is the only audited branch with native uncompressed `glTexImage3D`, nonzero-z `glTexSubImage3D`, unpack-image-height handling, and a general forward GLSL converter. It is still not an array foundation: `GL_TEXTURE_2D_ARRAY` is absent from `what_target`, `to_target`, `map_tex_target`, bind/realization, save/restore, and native-cache ownership, so an array target falls through to the 2D object slot while the bind switch does not bind it. Compressed 3D still logs and calls 2D functions, discarding depth/z. Program reflection/state still has only 1D/2D/3D/cube fields and does not classify `GL_SAMPLER_2D_ARRAY`. Its static `inited` lifecycle guard has the same reinitialization defect. The branch is a broad fork with generated wrappers and VGPU infrastructure not ABI-matched to the pinned tree. | Rejected: useful isolated techniques exist, but the source as a whole fails the exact array identity, compressed upload, reflection, cache, and lifecycle gates. Backporting only its passing fragments would knowingly publish a partial route; importing the whole fork is explicitly forbidden. |

The searches are reproducible with `git log -S GL_TEXTURE_2D_ARRAY`, `git log -S sampler2DArray`, and `git grep` over the exact refs above. In upstream, `GL_TEXTURE_2D_ARRAY` history is limited to imported header commits and `sampler2DArray` has no implementation history. On OpenMW3, direct source inspection confirms that the apparent native 3D work does not add array-target state and that compressed 3D remains a 2D fallback.

### Required closure matrix and exact blocker

| Required closure | Pinned/current stack | Best audited external source | Proof-gate result |
| --- | --- | --- | --- |
| Capability after a real current EAGL ES3 context; array limits and native 3D entry points; generation reset | Current-context ordering exists in Xash/SDL and GL4ES tests GLSL 300, but no array capability/limit/function set exists; static close/reinitialize is stale | OpenMW Android adds no technique; OpenMW3 retains stale static initialization and no array capability contract | **Fail** |
| Distinct array object/target/per-unit binding/native cache/save-restore/delete/error semantics, never aliasing 2D | No array slot; 3D maps to 2D; one `actual_tex2d` cache | OpenMW3 still has no array slot and falls through to the 2D slot | **Fail** |
| Mutable/immutable, compressed/uncompressed 3D allocation/subupload, z/mip/depth, format/type, pixel-store/PBO, filters/wrap/aniso, high layers | Native wrappers flatten depth/z | OpenMW3 improves uncompressed 3D and unpack rows/images, but compressed paths flatten and no array/high-layer ownership exists | **Fail** |
| General stage-correct GLSL-130 to ESSL-300 conversion with array lookup and coherent cache identity | ESSL-300 selection is disabled; converter is ESSL-100-oriented | OpenMW3 VGPU is broad and modern but cannot be isolated as an ABI-verified bounded backport; it does not supply object/reflection closure | **Fail** |
| `GL_SAMPLER_2D_ARRAY` reflection, active-uniform cache, unit routing, relink/destruction | Only sampler2D/cube are classified; FPE routing indexes existing target slots | OpenMW3 remains without array classification/routing | **Fail** |
| Context destroy/recreate, resize, background/foreground, map teardown/reload, relink/destruction | GL object cleanup exists, but static GL4ES cannot fully reinitialize; no array generation exists | No audited source supplies the missing generation model | **Fail** |
| Standalone native iOS harness using the same GL4ES/EAGL path, with 16+16+4 data, high layer/mips/subupdate/readback/lifecycle and 2D/cube regression | No harness target exists | No audited source provides such a harness | **Fail** |

The irreducible Phase-A blocker is therefore not a single missing token or callable native function. There is no coherent source unit to backport that simultaneously owns array object identity, native upload semantics, shader conversion, reflection/unit routing, and context generations. The only source with some native 3D and ESSL-300 techniques still fails four mandatory subsystems and is a large incompatible fork. Closing those gaps would require designing and integrating a new GL4ES subsystem plus a new native harness rather than applying source-complete, ABI-verified pieces. Treating its uncompressed upload or translator alone as success would immediately trigger the order's rejection fixtures for 2D/array aliasing, compressed depth/z loss, missing reflection, stale lifecycle generation, and harness bypass.

Under Work Order 55's binding rules—no partial success, no premature advertisement, no wholesale fork migration, and backport only source-complete ABI-verified pieces—the proof gate requires **Outcome B before implementation or publication**. This outcome does not say a complete foundation is impossible in a future, separately authorized architecture project; it says the currently authorized bounded backport cannot be completed from the audited sources without violating its own safety constraints.

### Harness matrix, validation, and publication status

| Native harness requirement | Expected proof | Observed in Phase A |
| --- | --- | --- |
| Same EAGL/current-context/GL4ES initialization and lifecycle | Capability becomes true only after the real context; generation changes and stale objects are rejected | No source-complete harness or array generation exists; not runnable |
| 16 diffuse + 16 normal + 4 weight layers; base/nonzero mips; nonzero-z update; layer 15 | Distinct checksums for every layer/mip and no high-layer alias | No complete object/upload route; not runnable |
| Repeat/clamp; nearest/linear/trilinear; anisotropy when supported | Readback/checksum matrix matches expected samples | No complete route; not runnable |
| Representative solid/dlight GLSL-130 through ESSL-300, array reflection and unit routing | Both stages compile/link; sampler reflects and samples intended unit/layer | Reflection and bounded converter closure absent; not runnable |
| Delete/rebind, map-style teardown/reload, resize, background/foreground, full recreation | All resources rebuild in the new generation without stale cache state | Static reinitialization and array generation absent; not runnable |
| 2D/cube/ESSL-100 regression | Existing checksums and routes remain unchanged | Existing accepted source stack is unchanged; no new array implementation to regress it |

Positive WO55 host fixtures, mutation/rejection fixtures, exact-pin affected-unit compilation, arm64 harness build, native checksums, and terminal success markers were not created or claimed because the mandatory provenance/closure precondition failed. Running or publishing a partial fixture set would misrepresent Outcome A. Baseline read-only validation was still performed: the exact GL4ES pin was cloned, the complete accepted iOS patch order replayed, and the existing uint-element, index-trace, WO49 topology, WO49 transform, WO49 texture-unit, and WO52 material-trace positive/rejection suites passed. The drawable validator could not run locally because the SDL dependency tree is intentionally absent on this no-build outcome; no dependency fetch or build was authorized after the blocker. Source/history inspections above are the decisive WO55 rejection results.

Candidate/run and acceptance status: **none; Outcome B before implementation/build**. Implementation commit: **none**. Workflow ID/URL/result: **none; no workflow started**. Harness artifact/IPA filename, link, size, SHA-256, GitHub artifact, and tempfile.org link: **none**. Expected new runtime markers: **none**, because no executable or harness changed. Exact repository file changed: `Documentation/XASH3DIOS_PORTING_STATE.md` only. The authoritative Google Docs ledger receives this same report. The repository report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the Google Docs ledger and final handoff because a Git commit cannot contain its own hash.

Verified failure boundary: the pre-implementation provenance/closure gate fails before any safe array capability can exist. Structural cause: the pinned GL4ES architecture aliases legacy 3D state to 2D, disables its unfinished ESSL-300 route, omits array sampler reflection, and cannot rebuild static-generation state; no audited upstream/OpenMW fork closes those requirements as one bounded compatible implementation. Why no fix was applied: any available subset would be a forbidden partial renderer route, while the only broader translator source requires a prohibited wholesale fork migration and still lacks object/reflection/compressed/lifecycle closure.

Remaining risks: Diffusion landscapes remain unavailable; the complete GL4ES array foundation and native conformance target do not yet exist; Bundle 96 remains only the current device baseline for the accepted inactive-sampler subsystem; `ch1map1` termination remains independently quarantined. No device evidence is requested by this outcome.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. Repository and Google Docs readbacks are required before handoff.

Stop state: **Work Order 55 Phase A is complete at Outcome B and the orchestrator-review gate.** Do not implement a partial array path, build, run CI, create or upload any IPA, advertise arrays to Diffusion, contact Arjun, request evidence/testing, begin Phase B, invent Work Order 56, or start any later phase. Await a new explicit orchestrator-authored work order.

## Work Order 56 Phase A - Outcome A: first-party GL4ES texture-array foundation build-qualified

Selected work order and outcome: **WORK ORDER 56 PHASE A — FIRST-PARTY GL4ES TEXTURE-ARRAY FOUNDATION AND ON-DEVICE CONFORMANCE GATE. Outcome A.** The complete first-party array route and deterministic `-gl4es_texture_array_selftest` harness satisfy the source, rejection-fixture, full arm64 build, mobile-shader, IPA-contract, and publication gates. Bundle version 105 is a build-qualified self-test-only candidate. It is **not device-accepted**, Diffusion terrain admission remains disabled, and no device test is requested by this report.

### Starting state, commits, and preserved scope

- Starting ledger/baseline commit: `faf345eebf6d9b15e0d786ce9e1823506db16d33`.
- Primary implementation commit: `239dfc204fe0e47e326371b0d68cdfd9fe38ca3a`.
- Compile/link corrections: `efbe47bb09cb28221df538f2cb1edee29231cf0c`, `c64845938ac6401f3c56fc242e885ecf5b181b8c`, and `ee8a515844f9ea3c2793140e5d367b0a7a8d73e0`.
- Final shader-route correction and candidate commit: `9f7e799763045cd88621fe89c2a4a0202cb510ff`.
- The exact GL4ES pin remains `81547d986798e876de8b434193920b606a72363f`; Diffusion remains `14d156bf3a6993c172697fac83a937836c3b5561`. Bundle 96's direct-drawable, uint-index, topology, transform, texture-unit, material, and inactive-sampler repairs remain in the production patch order. No gameplay, menu, presentation, timing, or `ch1map1` transition code changed.
- `GL_EXT_texture_array` is not advertised and Diffusion terrain is not admitted. The only published launch route is the pre-game self-test mode.

### Architecture-closure matrix

| Required route | Implemented closure | Proof |
| --- | --- | --- |
| Distinct object identity and per-unit state | Adds `ENABLED_TEXTURE_ARRAY`, `TU_ARRAY`, a separate array object slot and `actual_texarray` cache, target-specific bind/delete/rebind/query handling, and no 2-D/cache alias | Positive validator plus target-alias and wrong-unit rejection fixtures |
| Live-context native GLES3 capability | Resolves `glTexImage3D`, `glTexSubImage3D`, and `glTexStorage3D` only from the live current context; requires native ES3 and records `GL_MAX_ARRAY_TEXTURE_LAYERS` | Exact-pin source replay, capability checks, and arm64 build |
| Mutable/immutable upload | Preserves width, height, depth, z offset, mip, unpack/PBO offset, immutable levels, and array metadata through native 3-D calls | Lost-depth and lost-z mutation fixtures; harness image/storage/subimage cases |
| Compressed upload | DXT array image and subimage paths decompress every requested layer into RGBA8 while retaining depth, layer offset, mip, and update extent; no layer-zero fallback | Compressed-route source checks, layer-zero rejection, and harness DXT image/subimage case |
| Stage-correct ESSL 300 | Selects the array route from an explicit terrain/self-test program or active post-preprocessor array use; emits stage-correct `in`/`out`, fragment output, array permission, sampler precision, modern texture/projection mappings, and omits legacy numeric-overload helpers that collide with ESSL 300 | All four unsanitized pinned solid/dlight terrain jobs and all 354 CI shader variants compile; ESSL-100 fallback and raw-inactive-token mutations are rejected |
| Reflection and unit routing | Classifies `GL_SAMPLER_2D_ARRAY` as `TU_ARRAY`, retains active-uniform metadata, and realizes the sampler against the selected texture unit without 2-D/cube collision | Sampler-misclassification and wrong-unit rejection fixtures; harness active-uniform inspection |
| Context/lifecycle ownership | Resets array state and hardware-extension discovery on GL4ES close/reinitialize, preserves external-current-context ordering, and exercises delete/recreate/current-generation ownership | Lifecycle-removal rejection fixture, source replay, IPA markers, and harness lifecycle phase |
| Native self-test harness | Runs before game/Diffusion initialization, covers mutable/immutable/compressed paths, units/bindings/aliasing, delete/recreate, GL4ES shader conversion/reflection, four layer quadrants, readback/checksum, and explicit terminal PASS/FAIL | Self-test-bypass and layer-zero mutations are rejected; harness and all seven markers are present in the verified arm64 IPA |

### Failed-run evidence and verified correction boundary

The inherited implementation had four sequential macOS build boundaries, each preserved in Actions history. Run [32412260088](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32412260088) first failed because the harness used undeclared `GL_TEXTURE0` through `GL_TEXTURE3`. Run [32413452984](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32413452984) advanced to arm64 link and exposed that direct ARB shader entry points were not linked through the GL4ES core export route. Run [32414573392](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32414573392) then exposed the existing GL4ES `glGetProgramiv` ABI's unsigned output pointer. Those boundaries were corrected by the three narrow harness commits above.

The final inherited failure, [32416455836](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32416455836), passed the Work Order 56 source/rejection validator and built the engine, then failed the Diffusion mobile-shader gate: 158 of 354 variants failed, beginning with ordinary `bmodeldlight_fp.glsl`, at `float requires declaration of default precision qualifier` and `clamp redefinition`. The verified structural cause was pre-preprocessor substring routing: inactive `sampler2DArray`/`BMODEL_MULTI_LAYERS` text selected ESSL 300 for ordinary shaders, and the ESSL-300 branch still injected legacy ESSL-100 numeric overload helpers before precision declarations. The final correction selects generic array use from post-preprocessor source, keeps explicit paired vertex/fragment terrain/self-test routing, omits the legacy overload helpers only for ESSL 300, supplies opaque-sampler precision and `texture2DProj` mapping, and activates the guarded terrain helper definitions without advertising the extension. This is the first incomplete inherited step and the only runtime correction made by the replacement worker.

### Validation and qualification

- Inspected clean/local/remote branch heads, the inherited two-file diff, all implementation commits, and every active/recent failed workflow before editing. No qualifying workflow was already running.
- Read the repository ledger completely through Work Order 55 and the authoritative Google Doc completely through the full Work Order 56 authorization.
- Replayed the entire accepted GL4ES patch stack plus the Work Order 56 patch on a fresh exact-pin clone; `git apply --check`, positive validation, applied-source `git diff --check`, and all ten mutation/rejection fixtures passed. The added fixture rejects selection from raw inactive array tokens.
- Compiled the real patched GL4ES converter locally and validated the four required unsanitized pinned terrain jobs: `bmodelsolid_vp`, `bmodelsolid_fp`, `bmodeldlight_vp`, and `bmodeldlight_fp`.
- Passed the retained drawable, uint-element, index-trace, WO49 topology, WO49 transform, WO49 texture-unit, WO51 material-state, WO52 material-trace, inactive-sampler, and Diffusion shared-animated/rigid-one-bone positive/rejection suites.
- Qualification workflow [32450973853](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32450973853) completed `success` on candidate `9f7e7997`. It replayed exact pins, passed every validator, compiled all 354 translated GL4ES mobile shader variants, built the arm64 engine plus Half-Life and Diffusion client/server/menu, verified all required thin-arm64 Mach-O files and embedded markers, packaged Bundle 105, passed the IPA contract, and uploaded exactly one retained artifact. The automatic pull-request copy is not the qualifying candidate and no manual duplicate was launched.

### Artifact and IPA

- GitHub artifact: [`Xash3DiOS-arm64-unsigned`](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32450973853/artifacts/9435734500), ID `9435734500`, 8,614,116-byte artifact ZIP, SHA-256 `7cffe7db01389b27e0361f9c2018da6487f070b0fb7c3109a584dccf37bd52b8`, retained for 14 days by the workflow.
- IPA: `Xash3DiOS-WO56-9f7e7997-arm64-selftest-unsigned.ipa`, 8,711,204 bytes, SHA-256 `cee7394d25064341cf2fed8dcff6aa69f955217cd3eede50240f6bda5158b3b2`.
- Tempfile page: https://tempfile.org/BHHRZLnPmHp/ ; direct download: https://tempfile.org/BHHRZLnPmHp/download . Tempfile independently reports the same byte size and SHA-256 with risk level `safe`; the object has a 48-hour retention window.

### Exact repository files changed

- `engine/client/cl_main.c`
- `engine/platform/ios/launchdialog.m`
- `ref/gl/gl_local.h`
- `ref/gl/gl_opengl.c`
- `ref/gl/gl_texture_array_selftest.c`
- `scripts/gha/build_ios.sh`
- `scripts/ios/gl4es-wo56-texture-array-ios.patch`
- `scripts/ios/validate-diffusion-mobile-shaders.py`
- `scripts/ios/validate-ios-texture-array.py`
- `scripts/ios/verify_ipa.sh`
- `Documentation/XASH3DIOS_PORTING_STATE.md` (this outcome report only)

### Expected runtime markers

- `iOS texture array selftest policy:`
- `iOS texture array selftest object:`
- `iOS texture array selftest upload:`
- `iOS texture array selftest shader:`
- `iOS texture array selftest sample:`
- `iOS texture array selftest lifecycle:`
- `iOS texture array selftest terminal:`

The terminal success form is `iOS texture array selftest terminal: PASS failures=0 diffusion_started=0`. Any `FAIL`, nonzero failure count, missing stage marker, mismatched checksum/result, or evidence that Diffusion started rejects the candidate.

Remaining risks: build and packaging qualification do not prove on-device array sampling, native DXT decompression results, drawable readback checksums, or lifecycle behavior on a real EAGL context. The self-test IPA therefore remains not device-accepted. Terrain capability remains deliberately unadvertised and Diffusion landscapes remain unavailable until a later orchestrator-authorized admission phase. The independently quarantined `ch1map1` termination is unchanged.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. This report is published in one documentation-only `[skip ci]` commit; its exact hash is mirrored into the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash. Repository and Google Docs readbacks are required before handoff.

Stop state: **Work Order 56 Phase A is complete at Outcome A and the orchestrator-review gate.** Do not request or run a device test, advertise texture arrays to Diffusion, admit terrain, begin Work Order 56 Phase B, start another workflow, create another candidate, contact Arjun, or begin any later work order. Await explicit orchestrator review.

## Work Order 56 Phase C - Outcome A: filesystem-independent self-test boot build-qualified

Selected work order and outcome: **WORK ORDER 56 PHASE C — FILESYSTEM-INDEPENDENT SELF-TEST BOOT CORRECTION. Outcome A.** The locked iOS texture-array self-test now arms at the earliest parsed-command-line boundary, bypasses only normal game-data validation, creates the existing video/EAGL/GL4ES renderer route, dispatches the existing conformance harness exactly once, and exits through a bounded terminal result. Bundle 109 is a build-qualified self-test candidate. It is **not device-accepted**; no Arjun evidence or device test is requested, and no later phase is started.

### Prior failure boundary, source audit, and structural correction

The authoritative Phase B device result for Bundle 105 (`9f7e799763045cd88621fe89c2a4a0202cb510ff`) showed that the locked arguments were intact, but normal host/filesystem startup selected `valve`, failed in `FS_LoadGameInfo(valve)`, and emitted none of the expected self-test markers. Bundle 105 is not retested. The verified structural cause was boot ordering: `Host_InitCommon` parsed the flag but required normal game-directory validation before `Host_Main` could reach `CL_Init`; the previous dispatch inside client/video initialization was therefore unreachable on a data-free install.

The safe boundary is after base filesystem/platform setup but before `FS_LoadGameInfo` and before module, network, server, client-DLL, menu, game-DLL, map, Valve, or Diffusion startup. The correction arms a private iOS mode immediately after `Sys_ParseCommandLine`, emits `iOS texture array selftest boot: armed`, completes only the base services needed by the iOS video path, emits `filesystem-independent`, and returns before game-info loading. `Host_Main` then invokes `CL_Init` before normal subsystem registration; `VID_Init` creates the native context, the requested GL4ES renderer reaches its current-context initialization, emits `renderer-ready` and `dispatched`, and calls the unchanged self-test. The self-test has a one-dispatch guard. Successful self-test renderer initialization skips unrelated built-in image, screen, world, model, and TriAPI initialization. Requested-renderer failure emits a bounded terminal FAIL and quits instead of falling back to normal startup. Self-test shutdown skips the image teardown that was never initialized and does not write a normal game config. Without the flag, the existing filesystem validation, renderer fallback, launcher, game selection, Diffusion arguments/data path, and shutdown path are unchanged.

The locked launch arguments remain exactly `-dev 2 -log -ref gl4es -gl4es_texture_array_selftest`. There is no `valve` folder workaround, no `-game diffusion`, no terrain admission, no real-game texture-array activation, and no shader, material, presentation, gameplay, touch, save-data, external-folder, timing, or `ch1map1` change.

### Commits, candidate, and failed qualification evidence

- Starting repository-ledger baseline: `9cf4cf1fea8e1aa8e83b9f110452582302b3877f`.
- Boot/dispatch implementation: `273b8b10390a1822c1d17daadb09b93c594cf7d4`.
- CI full-history correction for the authorized baseline scope proof: `5a7f3dd2aabbe2928b0ccf9ea2b116baf43c3b4f`.
- Final committed-range scope correction and build-qualified candidate: `a96c03c79f49ae71ae50011da3b9360d0e88fbac`.
- Repository-ledger commit: this documentation-only `[skip ci]` reporting commit; its immutable hash is mirrored into the authoritative Google Docs ledger and worker handoff because a Git commit cannot contain its own hash.

Two nonqualifying manual correction runs stopped before compilation, packaging, or artifact creation and are retained as failure evidence. [Run 32458085432](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32458085432) reached the new validator but could not resolve the authorized baseline because the workflow checkout was shallow; the narrow correction set `fetch-depth: 0`. [Run 32458955881](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32458955881) passed every retained validator, then the new scope proof falsely counted the workflow's own dependency checkout, applied-submodule patches, generated SDL/Half-Life state, and build-number plist mutation as committed Phase C source changes. The narrow correction compares the immutable baseline-to-`HEAD` committed range, which still rejects any out-of-scope candidate commit while excluding CI workspace setup. Neither failed run produced an artifact or candidate IPA.

Exactly one qualifying workflow was launched for the final candidate after confirming that `[skip ci]` had created no automatic duplicate. [Run 32459314753](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32459314753), job `96702858668`, completed `success` on candidate `a96c03c79f49ae71ae50011da3b9360d0e88fbac`. It produced Bundle 109, built the engine plus Half-Life and Diffusion modules, passed the IPA contract, verified 13 thin-arm64 Mach-O files and 11 game dylibs, and uploaded exactly one retained artifact.

Candidate status: **build-qualified, not device-accepted**. Acceptance status: **Outcome A proof and publication gates complete; runtime/device acceptance remains solely for a later orchestrator decision.**

### Validation and rejection proof

- Re-audited clean/local/remote heads, recent commits, uncommitted state, and active/recent Actions before editing; no qualifying workflow was running.
- Read the repository ledger through its latest entry and the authoritative Google Docs ledger through the complete Phase B result and Phase C authorization. The authoritative ledger was newer, not contradictory: it supplied the missing Phase B device evidence and Phase C work order.
- Used the codebase graph first to trace `Host_InitCommon`, `Host_Main`, `CL_Init`, `VID_Init`, renderer initialization, current-context GL4ES initialization, and the existing self-test dispatch; literal/source inspection then established the exact early-return and normal-path boundaries.
- Replayed the complete accepted iOS GL4ES patch stack, including the Work Order 56 patch, onto a fresh ignored clone of exact pin `81547d986798e876de8b434193920b606a72363f`; patch checks and applied-source `git diff --check` passed.
- Passed the retained drawable, uint-element, index-trace, WO49 topology, WO49 transform, WO49 texture-unit, WO52 material-trace, and WO56 texture-array positive/rejection validators. Passed the new filesystem-independent boot validator's positive path and mutation fixtures covering early arming, filesystem bypass, locked arguments, ordinary-launch/Diffusion preservation, renderer-failure terminal behavior, dispatch, one-run guarding, IPA markers, and committed scope.
- Passed Python compilation and repository `git diff --check`. The final CI independently repeated the validators, full exact-pin arm64 build, IPA inspection, embedded-marker verification, and thin-arm64 inspection.
- Negative boundary proof is structural and mutation-enforced: the flagged route returns before `FS_LoadGameInfo`, cannot search for `valve`, cannot load menu/client/server/game DLLs or maps, cannot emit `Couldn't find game directory`, and cannot fall through from renderer failure to normal game startup. The unflagged route retains normal validation and failure behavior; Diffusion's established launch path remains unchanged.

### Artifact and IPA publication

- GitHub artifact: [`Xash3DiOS-arm64-unsigned`](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32459314753/artifacts/9438462527), ID `9438462527`, artifact ZIP size 8,611,795 bytes, SHA-256 `26f9c03fd7efa3aff261e8f802c55234c134d70f87efd5c428b5cb54feb5dbfb`.
- IPA: `Xash3DiOS-WO56C-bundle109-a96c03c7-arm64-unsigned.ipa`, 8,711,557 bytes, SHA-256 `3ebeff5fe9542dd10afa04323f3cfc286acf8d759338b2937e202fd019863073`.
- Tempfile information page: https://tempfile.org/56gwQPHtkrX/ ; direct IPA: https://tempfile.org/56gwQPHtkrX/download . The object uses the authorized 48-hour retention. Tempfile independently reports the exact filename and byte count with no security warning; a fresh direct-download round trip reproduced the same size and SHA-256.

### Exact repository files changed

- `.github/workflows/ios-proof-of-life.yml`
- `engine/client/dll_int/ref_common.c`
- `engine/common/host.c`
- `ref/gl/gl_opengl.c`
- `ref/gl/gl_texture_array_selftest.c`
- `scripts/gha/build_ios.sh`
- `scripts/ios/validate-ios-selftest-boot.py`
- `scripts/ios/verify_ipa.sh`
- `Documentation/XASH3DIOS_PORTING_STATE.md` (this Outcome A report only)

### Expected runtime markers and stop state

The ordered boot markers are:

- `iOS texture array selftest boot: armed`
- `iOS texture array selftest boot: filesystem-independent`
- `iOS texture array selftest boot: renderer-ready`
- `iOS texture array selftest boot: dispatched`

They are followed by the existing bounded harness markers `policy:`, `object:`, `upload:`, `shader:`, `sample:`, `lifecycle:`, and `terminal:`. The successful terminal form remains `iOS texture array selftest terminal: PASS failures=0 diffusion_started=0`. Any absent/duplicated/out-of-order boot or stage marker, `FS_LoadGameInfo`/`valve`/DLL-load/game-directory evidence, normal-startup fallback, terminal FAIL, nonzero failures, or nonzero `diffusion_started` rejects the candidate.

Remaining risks: the new data-free boot route, native EAGL/GL4ES initialization, array sampling/readback, compressed upload, and lifecycle behavior are build-proven but not yet exercised on a physical device. Bundle 109 is therefore not accepted for runtime use. Diffusion texture-array terrain remains deliberately disabled, ordinary game behavior is only regression-fixture/build checked in this phase, the independent `ch1map1` termination remains quarantined, and the tempfile object expires after 48 hours.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. Both durable ledgers are read back after publication.

Stop state: **Work Order 56 Phase C is complete at Outcome A and the orchestrator-review gate.** Do not ask Arjun for evidence or a device test, retest Bundle 105, start another workflow, create another candidate, advertise texture arrays to Diffusion, admit terrain, change normal game startup, begin a later phase or work order, or perform any additional implementation without a new explicit orchestrator-authored work order.

## Work Order 56 Phase E - Outcome A: complete filesystem-independent renderer contract build-qualified

Selected work order and outcome: **WORK ORDER 56 PHASE E — COMPLETE THE FILESYSTEM-INDEPENDENT RENDERER CONTRACT BOOTSTRAP. Outcome A.** The complete renderer prerequisite contract is now source-inventoried, shared with ordinary startup, runtime-checked before renderer readiness, mutation-enforced, arm64 build-qualified, IPA-verified, and published. Bundle 112 is a build-qualified self-test candidate. It is **not device-accepted**; no Arjun contact or device evidence is requested, Bundle 109 must not be retested, and no later phase or work order is started.

### Device failure boundary and structural cause

The authoritative Phase D evidence for Bundle 109, candidate `a96c03c79f49ae71ae50011da3b9360d0e88fbac`, proves that the Phase C boot repair worked: the log emitted `iOS texture array selftest boot: armed` and `filesystem-independent`, then began renderer loading without game data. The terminal boundary moved past the earlier missing-`valve` condition and stopped before `renderer-ready`, `dispatched`, or any harness terminal marker at `Host_ErrorInit: Error: engine didn't gave us r_showhull cvar pointer`. The earlier game-directory line was therefore nonterminal for the self-test route. Bundle 109 is rejected and is not retested.

Pinned source and call-path inspection proves this was not a one-variable defect. `ref/common/ref_context.c::GetRefAPI` retrieves the complete `ENGINE_SHARED_CVAR_LIST` before renderer initialization. The Phase C reduced path already creates 25 of those 27 cvars through `CL_InitLocal`, `V_Init`, and engine `R_Init`, but it returns from normal `Host_Main` ordering before `host_allow_materials` registration and before `Mod_Init` registers `r_showhull`. `r_showhull` is merely the first absent entry reached in macro order; `host_allow_materials` would fail later. The complete pre-`renderer-ready` contract is 57 runtime items: 27 shared cvars, 22 non-null renderer-import callbacks, five engine parameters, and three renderer-global/video-state items. The machine-readable inventory records each cvar's symbol, default, flags, owner, normal initializer, and first consumer and records the provider/consumer contract for callbacks, parameters, and globals.

### Implementation and preserved behavior

- Implementation commit: `7a17296881e843c27748aafc942ec00084be8a7d` (`ios: initialize complete selftest renderer contract`).
- Qualification-only correction commit: `35de5b04786d8ed4be91915dae50ee18e0da3886` (`ci: ignore checkout gitlinks in Phase E scope`). This is the final Bundle-112 candidate SHA.
- Repository-ledger commit: the documentation-only `[skip ci]` commit containing this report; its immutable hash is mirrored into the authoritative Google Docs ledger and final worker handoff because a commit cannot contain its own hash.

`Host_InitRendererContract` is one shared idempotent owner used by both the filesystem-independent self-test and ordinary `Host_Main`. It registers the original static `host_allow_materials` and `r_showhull` objects, accepts an already registered object only when ownership is identical, and bounds missing/ownership failure. `Mod_Init` no longer performs a second `r_showhull` registration. The ordinary path therefore retains the same defaults, flags, object owners, and downstream behavior while establishing both renderer prerequisites earlier through the same initializer. The self-test still performs no game-data, module, map, server, menu, Valve, or Diffusion initialization.

Before loading the renderer, engine `R_Init` validates and emits all 55 engine-owned items: the 27 cvars in the exact shared-macro order, 22 renderer imports, four non-null pointer parameters, scalar `PARM_CONNSTATE`, and owned `refState`. After video/context setup and before `initialize_gl4es`, the renderer validates `refState.desktopBitsPixel` and drawable width/height, emits the remaining two items, and emits `complete count=57`. Invalid state emits the named missing marker and bounded terminal FAIL; renderer-side failures cross `Host_Error` and cannot fall through to GL4ES initialization or hide behind a later marker.

### Validation, correction, and qualification evidence

- Re-audited clean worktree, local/remote branch equality at starting head `5b5cb89f1d9ec9c6b2291003c815c0019d065e1d`, recent commits, uncommitted state, and active/recent Actions. No qualifying workflow was active before the candidate push. Read the repository ledger through Phase C and the authoritative Google Doc through the complete Phase D evidence and Phase E authorization; the ledgers were additive and nonconflicting.
- Used the project code graph first, then exact literal/source inspection, to trace `Host_InitCommon`, `Host_Main`, `CL_InitLocal`, `VID_Init`, engine `R_Init`, `R_LoadRenderer`, renderer `GetRefAPI`, `GL_InitCommands`, renderer `R_Init`, `GL_SetupAttributes`, and `GL_OnContextCreated`. The audit covered every cvar/import/parameter/global consumed before `renderer-ready` and found no broader game-filesystem or game-module prerequisite.
- `scripts/ios/wo56e-renderer-contract.json` is the machine-readable 57-item source inventory. `scripts/ios/validate-ios-renderer-contract.py --self-test` passed its positive proof and rejected removal of either missing cvar, duplicate registration, wrong default, wrong flags, post-renderer ordering, filesystem leakage, missing bounded terminal, wrong complete count, missing IPA proof, and incomplete callback inventory. The retained Phase C filesystem-independent validator and rejection fixtures also passed; Python execution and `git diff --check` passed.
- Initial run [32469370518](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32469370518) is preserved as nonqualifying failure evidence. It passed every retained validator and stopped in the new Phase E validator before compilation because committed-scope validation also counted checked-out gitlink directories `SDL/` and `hlsdk/` as untracked Phase E files. It skipped IPA verification/upload and produced no artifact. The narrow correction qualifies the immutable baseline-to-candidate committed path set and does not alter implementation or contract semantics. Automatically triggered PR duplicate [32469374427](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32469374427) was cancelled.
- Final qualification workflow [32470512686](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32470512686), job `96736111071`, completed **success** on exact head `35de5b04786d8ed4be91915dae50ee18e0da3886`. Its build step passed the texture-array, filesystem-independent boot, and 57-item renderer-contract validators and all retained suites; it built the engine plus Half-Life and Diffusion client/server/menu for iPhoneOS arm64. IPA verification passed every required embedded marker and reported Bundle 112, minimum iOS 12.0, 13 thin-arm64 Mach-O files, and 11 game dylibs. The upload step produced exactly one retained artifact. Automatically triggered PR duplicate [32470517284](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32470517284) was cancelled; no manual duplicate was launched.

Candidate status: **Bundle 112 build-qualified, not device-accepted.** Acceptance status: **Phase E Outcome A source, rejection, full-build, IPA-contract, publication, and durable-reporting gates complete; runtime/device acceptance remains solely for a later orchestrator-authored decision.**

### Artifact and IPA publication

- GitHub artifact: [`Xash3DiOS-arm64-unsigned`](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32470512686/artifacts/9442496203), ID `9442496203`, archive size `8,616,682` bytes, archive SHA-256 `1746129ca8f90b0907977218029d46c0e8c65d7ed0b60691f650bb8335dfc9ca`, retained by GitHub for 14 days.
- IPA: `Xash3DiOS-WO56E-bundle112-35de5b04-arm64-unsigned.ipa`, `8,713,373` bytes, SHA-256 `b6daf675750bce5b3698abbeca4e53bb1b362b1fef214514586cbaf743066138`.
- Exactly one tempfile.org object: [information page](https://tempfile.org/i8Dqr3VUHED/); [direct IPA download](https://tempfile.org/i8Dqr3VUHED/download); 48-hour expiry. Tempfile metadata reports the exact filename and byte count, no warning or suspicious pattern, risk level `safe`, and the same SHA-256. A fresh direct-download round trip reproduced the exact byte count and SHA-256.

### Exact repository files changed

- `engine/client/dll_int/ref_common.c`
- `engine/common/host.c`
- `engine/common/model.c`
- `ref/gl/gl_opengl.c`
- `scripts/gha/build_ios.sh`
- `scripts/ios/validate-ios-renderer-contract.py`
- `scripts/ios/validate-ios-selftest-boot.py`
- `scripts/ios/verify_ipa.sh`
- `scripts/ios/wo56e-renderer-contract.json`
- `Documentation/XASH3DIOS_PORTING_STATE.md` (this Outcome A report only)

### Expected runtime markers, rejection boundary, and risks

Expected successful order is: `boot: armed`; `boot: filesystem-independent`; `contract: begin`; 55 engine items as `contract: item name=<name> source=shared`; the two renderer/video items `global.refState.desktopBitsPixel` and `global.refState.drawableSize`; `contract: complete count=57`; `boot: renderer-ready`; `boot: dispatched`; then the existing bounded `policy:`, `object:`, `upload:`, `shader:`, `sample:`, `lifecycle:`, and `terminal:` harness markers. The successful terminal remains `iOS texture array selftest terminal: PASS failures=0 diffusion_started=0`.

Any `contract: missing name=<name> reason=<reason>`, duplicate/wrong owner, wrong default or flags, missing or reordered item, count other than 57, filesystem/game/module evidence, marker after renderer readiness instead of before it, fallthrough after a failure, terminal FAIL, nonzero failure count, or nonzero `diffusion_started` rejects Bundle 112. The prior `r_showhull` pointer failure must be absent.

Remaining risks: full arm64 compilation and IPA structure do not prove the shared 57-item contract, native EAGL/GL4ES initialization, array sampling/readback, compressed upload, or lifecycle behavior on a physical device. Bundle 112 is therefore not runtime/device-accepted. Ordinary startup preservation is source-, ownership-, fixture-, and build-proven but has no new device regression run in this phase. Texture-array terrain remains deliberately unadvertised, Diffusion landscape admission remains disabled, and the independent `ch1map1` transition issue remains quarantined. GitHub and tempfile retention are finite.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. Both durable ledgers are read back after publication.

Stop state: **Work Order 56 Phase E is complete at Outcome A and the orchestrator-review gate.** Do not contact Arjun, request device evidence or testing, retest Bundle 109, start another workflow, create another candidate or upload, advertise texture arrays to Diffusion, admit terrain, change unrelated startup/rendering behavior, begin a later phase or work order, or perform additional implementation without a new explicit orchestrator-authored work order.

## 2026-08-21 — Work Order 56 Phase G Revised Outcome A worker report (Bundle 114)

Selected order and supersession: **WORK ORDER 56 PHASE G — REVISED: NORMAL DIFFUSION BOOTSTRAP TEXTURE-ARRAY SELF-TEST, Outcome A.** This revised order supersedes the withdrawn game-information-independent Phase G. The implementation does not add a no-game video descriptor, synthetic title/icon fallback, fabricated `gameinfo_t`, special no-game filesystem mode, or renderer-without-game-info route. Phase F Outcome C is adopted as the verified predecessor boundary: rejected Bundle 112 reached video initialization with the complete shared contract, then failed because its diagnostic bypass deliberately returned before `FS_LoadGameInfo` while ordinary SDL/iOS video consumes real game information.

Candidate/run and acceptance status: **Bundle 114 is build-qualified diagnostics-only evidence; it is not device-accepted.** Implementation commit: `281eb237d0d9f5387814b3fdfa740524aeac459a`. The repository-ledger commit is this report's documentation-only `[skip ci]` commit; its exact hash is recorded in the authoritative Google Docs report and final handoff because a commit cannot contain its own hash.

### Verified boundary, structural cause, and implementation

The source-proven startup path is: command-line parsing and self-test arming in `Host_InitCommon` -> ordinary `FS_Init` -> ordinary `FS_LoadGameInfo` selecting external `diffusion` -> exact real `GI->gamefolder` validation and `gameinfo-ready` marker -> ordinary post-filesystem initialization -> the flagged pre-module branch in `Host_Main` -> shared idempotent renderer-contract initialization -> `CL_Init` -> `CL_InitLocal` -> `VID_Init` -> renderer loading -> SDL window and iOS EAGL context creation -> `GL_OnContextCreated` -> validation of `global.refState.desktopBitsPixel` and `global.refState.drawableSize` -> `initialize_gl4es()` -> existing texture-array harness dispatch. `CL_Init` retains its flagged `Sys_Quit` immediately after `VID_Init` and before `CL_LoadProgs`; `Sys_Quit` enters guarded `Host_ShutdownWithReason`, and renderer shutdown remains partial-init-safe and idempotent.

The earliest safe dispatch remains the existing call in `GL_OnContextCreated`, immediately after `initialize_gl4es()` and direct-drawable context setup. At that boundary the EAGL context is current, GL4ES is initialized, both video globals are valid, and no Diffusion client/server/menu module, map, terrain, cutscene, or gameplay has begun. The harness source and all GL4ES texture-array semantics are unchanged.

The structural defect in Bundle 112 was the flagged pre-`FS_LoadGameInfo` early return, not the shared renderer contract or harness. Phase G removes only that inaccurate `filesystem-independent` return and marker. The locked launcher now uses exactly `-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest`. After ordinary game information is loaded, the route rejects any non-Diffusion `GI` through a bounded terminal failure and emits `iOS texture array selftest boot: gameinfo-ready game=diffusion`. There is no Valve substitution, fake metadata, fallback title/icon, terrain admission, Diffusion shader change, or gameplay fallthrough.

Unflagged Half-Life and Diffusion startup remains on the ordinary path: the new game-info check and early diagnostic branch are both guarded by `host_ios_texture_array_selftest`; normal `Host_InitRendererContract`, `Mod_Init`, networking, `SV_Init`, `CL_Init`, real title/icon behavior, `CL_LoadProgs`, and ordinary shutdown remain in their prior order. The complete Phase E contract remains exactly 57 shared items: 55 engine-owned items plus `global.refState.desktopBitsPixel` and `global.refState.drawableSize`.

### Validation and rejection evidence

- `python -m py_compile` passed for both Phase G/renderer-contract validators. `validate-ios-selftest-boot.py --self-test` passed its positive proof and mutation suite; `validate-ios-renderer-contract.py --self-test` passed the complete 57-item source/runtime inventory. Direct mutation checks additionally rejected a post-game-info fallback icon and moving harness dispatch after client-module admission.
- Required rejection coverage passed for missing `-game diffusion`, Valve substitution, pre-game-info return/marker, fake game information, fallback title/icon, pre-context and post-module dispatch, duplicate dispatch, missing terminal shutdown/game fallthrough, normal-launch hijack, contract count/order corruption, and removal of packaged-game-data rejection. The retained contract validator rejects missing/wrong-owner/default/flags/items and wrong count/order.
- The exact pinned GL4ES stack replayed cleanly at `81547d986798e876de8b434193920b606a72363f`. Retained positive and mutation suites passed for direct drawable ownership/presentation, native ES3 uint indices, index tracing, WO49 topology and transform discriminators, per-unit texture realization, WO52 material tracing, and the native texture-array harness. The pinned SDL drawable patch replayed and its lifecycle/generation/sentinel/menu-bypass rejection suite passed at `5d249570393f7a37e037abf22cd6012a4cc56a71`.
- `git diff --check` passed. The qualifying macOS/iPhoneOS build compiled and linked the engine plus Half-Life and Diffusion client/server/menu targets for arm64, ran all retained validators and rejection fixtures, passed the IPA contract, and uploaded the artifact. The ordinary unflagged route is source-, guard-, order-, and full-build-proven; no proprietary device data was used in CI.
- Independent IPA inspection found 13 Mach-O binaries, all thin arm64 (`MH_MAGIC_64`, CPU `0x0100000C`), the exact locked argument string and `gameinfo-ready` marker, and zero packaged `.bsp`, `.wad`, `.pak`, `.vpk`, `.mdl`, `.spr`, `.dem`, `.wav`, or `.mp3` game assets.

### Workflow, artifact, and IPA publication

- Sole qualifying workflow: [32479302024](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32479302024), push event, attempt 1, **success**, job `96762051888`, exact head `281eb237d0d9f5387814b3fdfa740524aeac459a`. Automatic pull-request duplicate [32479305662](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32479305662) was cancelled and did not qualify. No manual duplicate was launched.
- GitHub artifact: [`Xash3DiOS-arm64-unsigned`](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32479302024/artifacts/9445586940), ID `9445586940`, archive size `8,616,755` bytes, retained until `2026-09-04T11:59:09Z`.
- Exact unsigned IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,713,395` bytes, SHA-256 `B5D44CD65C64B65229F89F40444E01AA462F97C408064B2C8E9FC560414E0CFA`.
- Exactly one tempfile.org object: [information page](https://tempfile.org/qcEc6EdNF1v/); [direct IPA download](https://tempfile.org/qcEc6EdNF1v/download); expiry `2026-08-23T12:02:09.959Z`. API metadata/security readback reports the exact filename, byte count and SHA-256, `safe` risk, no warning, and no suspicious pattern. A fresh direct-download round trip reproduced the exact size and SHA-256.

### Exact files changed, expected markers, and risks

Runtime/qualification commit files: `engine/common/host.c`, `engine/platform/ios/launchdialog.m`, `scripts/ios/validate-ios-renderer-contract.py`, `scripts/ios/validate-ios-selftest-boot.py`, and `scripts/ios/verify_ipa.sh`. The durable-report commit changes `Documentation/XASH3DIOS_PORTING_STATE.md` and adds that required ledger path to the Phase G validator's allowed committed scope; it does not change runtime or validation semantics.

Expected successful runtime order: `iOS texture array selftest boot: armed`; `iOS texture array selftest boot: gameinfo-ready game=diffusion`; `iOS texture array selftest contract: begin`; exactly 55 engine-owned `source=shared` item markers; `global.refState.desktopBitsPixel`; `global.refState.drawableSize`; `iOS texture array selftest contract: complete count=57`; `iOS texture array selftest boot: renderer-ready`; `iOS texture array selftest boot: dispatched`; then the unchanged `policy`, `object`, `upload`, `shader`, `sample`, `lifecycle`, and terminal stages. The only successful terminal remains `iOS texture array selftest terminal: PASS failures=0 diffusion_started=0`. No `filesystem-independent`, `CL_LoadProgs`, module, map, terrain, cutscene, or gameplay marker may appear in the diagnostic execution around the terminal.

Remaining risks: build and static inspection cannot prove real external Diffusion game-info availability, physical-device EAGL/GL4ES behavior, the harness terminal, or teardown timing. A missing external `diffusion/gameinfo` prerequisite will fail before renderer dispatch by design. Bundle 114 is therefore not device-accepted. Diffusion texture-array terrain remains unadvertised and disabled, Bundle 112 remains rejected without retest, and the quarantined `ch1map1` transition and unrelated touch/gameplay work remain out of scope.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. Repository and Google Docs reports are read back after publication.

Stop state: **Revised Work Order 56 Phase G Outcome A is complete at the orchestrator-review gate.** Do not contact Arjun, request device evidence or testing, retest Bundle 112, start another workflow/candidate/upload, launch Diffusion gameplay, enable terrain, advertise arrays to Diffusion, alter `ch1map1`, begin a later phase, or perform additional implementation without a new explicit orchestrator-authored work order.

## 2026-08-21 — Work Order 56 Phase I Outcome A worker report (Bundle 116)

Selected order and outcome: **WORK ORDER 56 PHASE I — COMPLETE THE NATIVE ARRAY SAMPLING/READBACK CORRECTION, Outcome A.** The complete call-level audit established one immediate, source-proven GL4ES error origin and one additional native-ES3-invalid vertex-input route that the first error could mask. Both are corrected coherently at their owners. Bundle 116 is a build-qualified diagnostics candidate, **not device-accepted**. No device test or evidence is requested by this report, and no later phase is begun.

### Adopted Phase H evidence and exact boundary

The authoritative raw Bundle 114 log is `1-engine.log`, SHA-256 `2A0A70CC3005795626ADF1597E656FBE30FEBEFBF0EACE0D9342BD09399FB32B`. It proves one bounded launch on candidate prefix `281eb237`: normal Diffusion game-information bootstrap; all 57 renderer-contract items; `renderer-ready` and one dispatch; mutable, immutable and compressed uploads PASS; array-object identity PASS; shader translation/reflection PASS; lifecycle PASS; then sampling/readback `GL_INVALID_OPERATION` (`0x0502`), checksum `a915906d`, and `terminal: FAIL failures=1 diffusion_started=0`, followed by clean intentional shutdown. This was not a hard crash. Bundle 114 is rejected and is not retested.

The checksum is FNV-1a-32 over the exact 16 expected readback bytes, in quadrant order: red RGBA, green RGBA, magenta RGBA, yellow RGBA. Recomputing that stream yields `0xA915906D`, exactly matching the device log. The native array object, both draw calls, layer selection, drawable readback, quadrant order, and pixel contents therefore succeeded. The failure was an API-state error recorded during the sampling stage, not failed sampling or presentation.

### Complete provenance audit and structural cause

| Sequence | Owner/call | State/invariant | Phase H attribution | Phase I proof/correction |
| --- | --- | --- | --- | --- |
| 0 | Stage entry | Drain prior errors after the last successful shader/reflection operation | Object-routing drain was clean, so the later error is bounded to sampling | Explicit `stage-entry` immediate attribution rejects stale errors |
| 1 | SDL drawable FBO query/check | External default framebuffer, native draw/read FBO identity, complete drawable, audited size | Correct pixels prove drawable route worked but did not identify its state | Explicit owner/object/registered FBO/status/size marker before sampling |
| 2 | Viewport/scissor | Full 4×4 viewport; scissor cannot clip quadrants | Readback contained all four exact quadrants | Disable and restore scissor; set and restore viewport |
| 3 | Program and sampler uniform | Reflected `GL_SAMPLER_2D_ARRAY`, sampler unit 0 | First uninstrumented operation able to emit the observed wrapper error | Immediate per-call error marker; GL4ES uniform classification repaired |
| 4 | Texture unit/array bind | Unit 0, native array object, no 2-D alias | Object identity and exact layers passed | Immediate active-unit/bind attribution and state restoration |
| 5 | Vertex/index/attribute state | ES3-valid buffer-backed attributes | CPU client pointer existed in the old harness and is invalid in Apple GLES3 | Quad is uploaded to a native VBO; attribute pointer is a buffer offset |
| 6 | Draw/synchronization | Two triangle-strip draws, layer uniform 0 then 1, finish before read | Exact four-color result proves both draws and layer selection worked | Immediate attribution after each uniform/draw/finish call |
| 7 | Read-buffer/pack/readback | External default read FBO; supported RGBA/UNSIGNED_BYTE; pack alignment 1 | Exact 16-byte checksum proves read succeeded | Explicit read-FBO, pack, `glReadPixels`, buffer-size and checksum contract |
| 8 | Restoration/continuation | Restore program, buffers, attributes, texture bindings/unit, viewport, scissor, pack, clear state; continue lifecycle | Lifecycle PASS and clean terminal shutdown | Immediate cleanup attribution plus retained one-dispatch/lifecycle guards |

The exact observed `0x0502` origin is `gl4es_glUniform1i(u_Array, 0)`. GL4ES already reflected `GL_SAMPLER_2D_ARRAY` and routed it through `TU_ARRAY`, but `src/gl/uniform.c` omitted that type from all three uniform classification helpers: `uniformsize`, `is_uniform_int`, and `n_uniform`. `GoUniformiv` consequently saw an incompatible size/class and deterministically called `errorShim(GL_INVALID_OPERATION)`. The native sampler default is already zero, which explains why the rejected uniform update left the program able to draw the exact expected pixels. The prior clean error drain and new stage-entry drain exclude a stale earlier error.

The full route audit also proved that the old harness passed a CPU address to `glVertexAttribPointer`. Client-side vertex arrays are invalid in native OpenGL ES 3 on iOS, so that call could generate a second native `0x0502` hidden by the first shim error. This was not claimed as the origin of the logged checksum result; it is the second invalid operation on the same audited route and is removed by the required complete correction. No production terrain or gameplay path is enabled.

### Implementation, commits, and exact files

- Implementation/candidate commit: `bc4b2b7181b3111053f14ff86e8ff634718acf30` (`ios: complete native array sampling contract`).
- Repository-ledger commit: this documentation-only `[skip ci]` commit. Its immutable hash is mirrored into the authoritative Google Docs ledger and final handoff because a Git commit cannot contain its own hash.
- Exact GL4ES pin remains `81547d986798e876de8b434193920b606a72363f`.
- Runtime/contract files changed: `ref/gl/gl_texture_array_selftest.c`, `scripts/ios/gl4es-wo56-texture-array-ios.patch`, `scripts/ios/validate-ios-renderer-contract.py`, `scripts/ios/validate-ios-selftest-boot.py`, `scripts/ios/validate-ios-texture-array.py`, `scripts/ios/verify_ipa.sh`, and new `scripts/ios/wo56i-sampling-readback-contract.json`.
- Durable-report file: `Documentation/XASH3DIOS_PORTING_STATE.md` only in the reporting commit.

The GL4ES patch adds `GL_SAMPLER_2D_ARRAY` to all three uniform helpers. The harness adds direct-drawable FBO proof, a stale-error boundary, immediate sequence/call/owner/object/framebuffer/error/result attribution, a VBO-backed quad, explicit scissor/viewport/pack ownership and restoration, exact checksum constant `0xA915906D`, and complete cleanup. The JSON contract records every sampling/readback call, valid state, expected error and restoration obligation. Bundle 114's normal Diffusion bootstrap, 57-item contract, single dispatch, direct-drawable architecture, every preceding PASS stage, locked arguments, bounded terminal shutdown, unadvertised/disabled terrain, and quarantined `ch1map1` track are preserved.

### Validation, workflow, artifact, and IPA

- Python compilation and JSON parsing passed; repository and applied-source `git diff --check` passed.
- The complete accepted patch stack, ending in the Phase I patch, replayed cleanly against a fresh exact-pin GL4ES clone. `validate-ios-texture-array.py --self-test`, `validate-ios-selftest-boot.py --self-test`, and `validate-ios-renderer-contract.py --self-test` passed.
- Retained drawable, uint-element, index-trace, WO49 topology, WO49 transform, texture-unit, and WO52 material-trace suites passed.
- Mutation fixtures rejected stale attribution; missing/incomplete/wrong framebuffer; target, level, read/draw-buffer and sample defects; wrong sampler unit/type; missing array bind; wrong layer; client vertex storage; wrong viewport; unsupported read format/type; bad pack/buffer size; missing finish; checksum weakening; skipped read; 2-D/atlas/layer-zero/CPU fallbacks; state leakage; and missing continuation.
- The local SDL checkout is intentionally CI-owned and was absent locally; the qualifying workflow replayed its retained checks. No local clang was available, so the single qualifying macOS/iPhoneOS workflow supplied compilation and link proof.
- Sole retained qualifying workflow: [32489923843](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32489923843), job `96794910555`, push event, attempt 1, **success** in 4m56s on exact candidate commit `bc4b2b7181b3111053f14ff86e8ff634718acf30`. It replayed exact pins, passed all validators, built the engine plus Half-Life and Diffusion client/server/menu targets for iPhoneOS arm64, passed the IPA contract, and uploaded one artifact. Automatic PR duplicate `32489927380` was cancelled. Automatic Build & Deploy Engine runs `32489924024` and `32489927404` skipped and did not qualify.
- GitHub artifact: [`Xash3DiOS-arm64-unsigned`](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32489923843/artifacts/9449473335), ID `9449473335`, ZIP size `8,616,958` bytes, SHA-256 `dacfb9d82bce5c3f777b2c77b38fa038d24655260c0438d199a6b596479355d2`.
- Exact unsigned IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 116, `8,716,506` bytes, SHA-256 `4FD8D67DDAEBF1986AC795164B7CD20BA782319B9F29200C9EA76F1A4BA73806`. Independent extraction verified all required contents, 13 thin-arm64 Mach-O files, the new attribution/contract markers in `libref_gl4es.dylib`, and no proprietary game assets.
- Exactly one tempfile.org object: [information page](https://tempfile.org/FQBk1nBoC51/); [direct IPA download](https://tempfile.org/FQBk1nBoC51/download); 48-hour expiry. Metadata/security readback reports the exact filename, byte count and SHA-256, risk `safe`, no warning and no suspicious patterns. A fresh direct-download round trip reproduced the exact byte count and SHA-256.

### Expected markers, remaining risks, and stop state

New stable markers include `iOS texture array selftest sampling-fbo: owner=sdl-view ... result=PASS`, immediate `iOS texture array selftest sampling-call: seq=<n> call=<name> owner=<owner> object=<id> framebuffer=<id> error=0x0000 result=PASS`, and `iOS texture array selftest sampling-contract: schema=1 expected_checksum=a915906d error_origin=gl4es-uniform-type-cache vertex_source=vbo framebuffer=external-default attribution=immediate`. The existing sample checksum must remain `a915906d`; every immediate call must report `0x0000`; the terminal success form remains `iOS texture array selftest terminal: PASS failures=0 diffusion_started=0`.

Remaining risks: source, mutation, full-build and packaged-marker proof cannot establish physical-device error-free execution. Bundle 116 is therefore not device-accepted. Texture-array terrain remains deliberately unadvertised and disabled; no gameplay launch occurred; Bundle 114 remains rejected without retest; and the independent `ch1map1` issue remains quarantined. GitHub and tempfile retention are finite.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. Both repository and authoritative Google Docs reports are read back after publication.

Stop state: **Work Order 56 Phase I is complete at Outcome A and the orchestrator-review gate.** Do not contact Arjun, request evidence or device testing, retest Bundle 114, start another workflow/candidate/upload, launch gameplay, enable or advertise Diffusion terrain, alter `ch1map1`, begin a later phase, or perform additional implementation without a new explicit orchestrator-authored work order.

## 2026-08-21 — Work Order 56 Phase I acceptance and Phase J device-evidence order

Orchestrator decision: **Work Order 56 Phase I Outcome A is accepted.** The source-proven `GL_SAMPLER_2D_ARRAY` uniform-classification defect, VBO correction, exact `a915906d` checksum derivation, complete validator/rejection suite, exact-pin replay, successful arm64 build, artifact identity, and durable two-ledger worker report are accepted as build-qualified diagnostics evidence. This acceptance does not device-accept Bundle 116, admit terrain, or qualify gameplay.

Selected next boundary: **WORK ORDER 56 PHASE J — BUNDLE 116 NORMAL-BOOTSTRAP DEVICE ACCEPTANCE.** This is a device-evidence-only continuation of WO-056, not a new implementation phase. The existing worker may request exactly one physical-device evidence package from Arjun, validate it, update both durable ledgers, and report. No new candidate, workflow, artifact, upload, patch, instrumentation, source edit, or game-data change is authorized.

### Exact candidate and objective

- Candidate commit: `bc4b2b7181b3111053f14ff86e8ff634718acf30`.
- Workflow: `32489923843`, success; artifact `Xash3DiOS-arm64-unsigned`, ID `9449473335`.
- Exact IPA: `xash3d-fwgs-ios-arm64.ipa`, `8,716,506` bytes, SHA-256 `4FD8D67DDAEBF1986AC795164B7CD20BA782319B9F29200C9EA76F1A4BA73806`.
- Locked arguments remain `-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest`.
- Objective: determine whether the corrected normal-bootstrap native array sampling/readback contract passes once on Apple GLES3 while retaining the exact prior checksum and bounded pre-gameplay shutdown.

### Authorized procedure and required evidence

Verify the exact IPA identity before installation. Preserve the device's existing authorized external Diffusion data; do not delete, replace, add, or package game data. Install Bundle 116 over the existing test installation, launch the diagnostic route exactly once, do not click Start or enter gameplay, and export the complete new engine log. Record device model, iOS version, whether the app visibly closed after the terminal marker, and the log filename, byte count, and SHA-256. If the process terminates without a complete terminal marker, include the matching iOS `.ips` report if one exists. Do not infer a hard crash merely because the bounded harness intentionally closes the app.

Outcome A requires one complete log proving normal Diffusion game information, all 57 contract items, one renderer dispatch, every retained policy/object/upload/shader/lifecycle PASS stage, `sampling-fbo ... result=PASS`, every immediate sampling call with `error=0x0000 result=PASS`, the exact sampling contract, checksum `a915906d`, terminal `PASS failures=0 diffusion_started=0`, and bounded intentional shutdown. Outcome A device-accepts only the native texture-array conformance harness. Terrain remains disabled and unadvertised; gameplay and `ch1map1` remain outside the result.

Outcome B applies when a complete run reaches the harness but records a nonzero immediate error, framebuffer failure, different checksum, missing retained PASS stage, terminal FAIL, nonzero failure count, nonzero `diffusion_started`, module/map/terrain/gameplay admission, or a matching iOS crash report. Preserve the exact first failing call and all later bounded evidence; do not patch, rebuild, or rerun.

Outcome C is inconclusive: wrong IPA identity, unavailable external Diffusion game information, installation/log-export failure, a truncated log before the decisive boundary without a matching `.ips`, or evidence not attributable to one Bundle 116 launch. Do not reinterpret it as renderer failure and do not rerun without review.

The authoritative Google Docs ledger was updated under revision guard and verified by readback at revision `AIroW37HusfW5RcASaQXlFaFbLG6Gn6MQSQKue4vM5AcoplbZxyRyXtBUv4dHDYxPXkic431rdzCcxaXlSDz3IUyB9P73Jr-36zbyq1Cbi8`.

Stop state: **Work Order 56 Phase J is active and awaiting exactly one Bundle 116 physical-device evidence package.** No source, patch, validator, CI, workflow, artifact, IPA, game-data, renderer, terrain, menu, input, gameplay, or `ch1map1` change is authorized. Do not test Bundle 114 or begin another phase.

## 2026-08-21 — Work Order 56 Phase J Outcome A device report (Bundle 116)

Selected outcome: **WORK ORDER 56 PHASE J — BUNDLE 116 NORMAL-BOOTSTRAP DEVICE ACCEPTANCE, Outcome A.** The sole authorized Bundle 116 run passes the complete bounded native texture-array conformance contract on an iPhone 16 Pro Max running iOS 26.6. Bundle 116 is device-accepted for this harness only. Production Diffusion terrain remains disabled and `GL_EXT_texture_array` remains unadvertised; gameplay and the quarantined `ch1map1` transition remain outside the result.

### Evidence identity and observed close

- Exact candidate: implementation `bc4b2b7181b3111053f14ff86e8ff634718acf30`; the log identifies `bc4b2b71-dirty`, `agent/ios-proof-of-life`, `apple-arm64`, and the locked arguments `-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest`.
- Device: iPhone 16 Pro Max, iOS 26.6; log-reported `Apple A18 Pro GPU`; drawable `2868x1320`.
- Complete evidence log: `1-engine.log`, `23,255` bytes, `254` lines, SHA-256 `139B15982FEC0B4D34146B3F99A39D4758B36D77925394403B214BE9F5544FF5`.
- The engine started at `20:55:04` and stopped at `20:55:05`. The user described the app as hard-crashing about one second after clicking Start. The complete log disproves a crash: the bounded diagnostic had already armed, completed, emitted its successful terminal, deliberately invoked host shutdown with reason `iOS texture array selftest complete`, ran `CL_Shutdown()`, cleared the direct-drawable context lifecycle, unlinked engine state, and emitted `Stopped with reason "iOS texture array selftest complete"`. No `.ips` is required.

### Qualified runtime contract

- Real Diffusion game information loaded. All 57 shared renderer-contract items completed, followed by `renderer-ready` and one `dispatched` marker.
- Mutable, immutable and compressed array uploads reported PASS. Array object identity, four distinct units/layers, alias rejection and delete/recreate reported PASS. GLSL-130 to ESSL-300 translation and `sampler2DArray` reflection reported PASS.
- The direct-drawable framebuffer was registered and complete at native draw/read framebuffer `1/1`, status `0x8cd5`, size `2868x1320`, samples `0`.
- Every immediate sampling and cleanup attribution from `seq=1` through `seq=51` reported `error=0x0000 result=PASS`. This includes the corrected `glUniform1i(u_Array)` at sequence 12 and the VBO-backed `glVertexAttribPointer(0,VBO)` at sequence 20.
- Four quadrant readbacks from layers `0,1,2,3` produced exact checksum `a915906d` and PASS. Lifecycle delete/recreate and context ownership reported PASS.
- Exact terminal: `iOS texture array selftest terminal: PASS failures=0 diffusion_started=0`.
- No `CL_LoadProgs`, client/server/menu module, map, terrain, cutscene, or gameplay admission occurred. The log's early `FS_LoadProgs: filesystem_stdio successfully loaded` is the filesystem plugin and is not client-game admission.
- The later `GL_EXT_texture_array - failed` capability check is expected and preserved: production Diffusion advertisement remains deliberately disabled. It does not contradict the native array harness PASS.

### Conclusion, qualification boundary, and stop state

Bundle 116 now qualifies native iOS/Apple-GLES3 texture-array object identity, mutable/immutable/compressed upload, ESSL-300 translation/reflection, sampler update, VBO-backed submission, four-layer sampling, direct-drawable readback, exact pixels, cleanup/restoration, lifecycle, and bounded normal-bootstrap shutdown. The Phase H `GL_INVALID_OPERATION` boundary is closed on device.

This result does not qualify or authorize production `GL_EXT_texture_array` advertisement, the real Diffusion terrain shader/material path, ordinary gameplay, or `ch1map1`. The first unqualified boundary is production terrain admission using the now-qualified native array capability.

The authoritative Google Docs ledger was updated under revision guard and verified by readback at revision `AIroW35eAHEQsIjng7koSVYL26SxH_LPplNTY2_pP2hkjH5sDD-v7Sa_DztjVI28T3Rh0oHuQNk1fdRkpHFvUX0cTfPZNGDFprZXSl-CK-o`.

Stop state: **Work Order 56 Phase J is complete at Outcome A and the orchestrator-review gate.** The one-run authorization is consumed. Do not rerun, rebuild, patch, enable or advertise terrain, launch a gameplay experiment, modify `ch1map1`, or begin another phase without a new explicit orchestrator order.

## 2026-08-21 — Work Order 56 Phase J acceptance and Phase K production-admission order

Orchestrator decision: **Work Order 56 Phase J Outcome A is accepted.** Bundle 116, candidate `bc4b2b7181b3111053f14ff86e8ff634718acf30`, passed the complete bounded native texture-array conformance contract on iPhone 16 Pro Max / iOS 26.6. The native Apple GLES3/GL4ES object, upload, shader translation/reflection, sampler, VBO draw, four-layer sample, direct-drawable readback, exact `a915906d` checksum, cleanup, lifecycle, and intentional shutdown contracts are qualified. This does not qualify production terrain, gameplay, or `ch1map1`.

Selected next boundary: **WORK ORDER 56 PHASE K — CONDITIONAL PRODUCTION TEXTURE-ARRAY ADMISSION.** This remains a continuation of WO-056. It authorizes the preserved worker to audit and implement one complete guarded production route, validate it, build at most one qualifying candidate, update both ledgers, and stop before any device test.

### Baseline, objective, and first incomplete action

- Branch/control baseline: `agent/ios-proof-of-life` at Phase J record `cc02ebaa192abb3a11ce5ea520649a096a68ed44`; qualified implementation baseline `bc4b2b7181b3111053f14ff86e8ff634718acf30`.
- Latest qualified CI remains workflow `32489923843`, artifact `9449473335`, Bundle 116 IPA SHA-256 `4FD8D67DDAEBF1986AC795164B7CD20BA782319B9F29200C9EA76F1A4BA73806`. No relevant workflow was active when Phase K was issued.
- Objective: admit the proven capability into the real engine and Diffusion production route only when the complete GL4ES/native ES3 provider, entry-point, limit, engine, Diffusion, loader, sampler, target, and terrain-shader contract is true.
- First incomplete action: audit the exact end-to-end production admission path and produce the source-proven capability/provenance table required by the Phase K order before or with one coherent implementation.

### Required complete route

The audit must cover the GL4ES extension-string/capability provider and negative cases; required native ES3 array procedures and limits; engine `GL_CheckExtension`, `GL_TEXTURE_ARRAY_EXT`, callback exports, `GL_MAX_ARRAY_TEXTURE_LAYERS_EXT`, target/create/load paths; Diffusion `R_TEXTURE_ARRAY_EXT`, `GLSL_ALLOW_TEXTURE_ARRAY`, `LOAD_TEXTURE_ARRAY`, `LoadTerrainLayers`, diffuse and normal layer arrays, targets, units, samplers, cleanup; and terrain GLSL `sampler2DArray`, `texture2DArray`, `TERRAIN_NUM_LAYERS`, and `BMODEL_MULTI_LAYERS` behavior.

The current iOS Diffusion shader patch filters `MULTI_LAYERS`. Phase K must prove and preserve the complete production shader/material contract; merely appending `GL_EXT_texture_array` while leaving the consumer disabled is rejected. Engine and Diffusion must agree on capability, and unsupported contexts/backends, missing procedures, or invalid/insufficient limits must remain unadvertised. Record this as `scripts/ios/wo56k-production-array-admission-contract.json` or a semantically equivalent machine-readable contract named in the report.

### Scope, prohibitions, validation, and outcomes

After the audit establishes one bounded route, implement only the minimum coherent production admission at the responsible owners. Retain exact GL4ES/SDL pins and all accepted drawable, uint-index, per-unit target, material/inactive-sampler, array uniform/VBO, normal-bootstrap, renderer-contract, lifecycle, and diagnostic-harness behavior.

Do not spoof or unconditionally advertise the extension; add a cvar/argument/environment force-enable; use CPU, 2-D, atlas, multi-texture, or layer-zero fallback; strip terrain or `MULTI_LAYERS` semantics to compile; change gameplay, input, menus, data, maps, unrelated shaders, or `ch1map1`; create a probe-only IPA or serial partial candidates; or request/run device or gameplay testing.

Positive and mutation coverage must reject unsupported providers, missing procedures, bad limits, engine/Diffusion disagreement, absent callbacks, wrong target/unit/sampler, missing array loader paths, lost shader defines, false-positive support, fallbacks, and normal-startup changes. Retain all prior validators, replay exact pins, run Python/JSON and `git diff --check`, build affected units, and perform full iPhoneOS arm64 engine/Half-Life/Diffusion plus IPA qualification.

- **Outcome A:** one coherent conditional admission passes every source, mutation, pinned-replay, full-build, and IPA gate. Retain exactly one qualifying run/artifact and verify IPA identity/hash. This is build-qualified only, not terrain/device-accepted. Update/read back both ledgers and stop.
- **Outcome B:** the audit finds a broader renderer/shader/material migration. Make no partial advertisement or runtime candidate/build. Record the exact boundary and stop.
- **Outcome C:** the capability cannot be safely discriminated or engine/Diffusion agreement cannot be proven. Make no runtime change/build; record the missing evidence and stop.

Complete authority, rejection fixtures, reporting fields, and stop conditions are materialized in `WorkOrders/WO-056.md`; `Documentation/CURRENT_STATE.md`, `Decisions/DEC-006.md`, and `Evidence/WO-056/manifest.md` form the current ControlPlane checkpoint.

The authoritative Google Docs ledger was appended under revision guard and verified by readback at revision `AIroW37mgJWSAdh9os0FJ0VzXL-r36Dj5xAz9EfzGMg_oXINPkRe-WWO3uZKluW6OOn4DguV3EyefcmwR0ZwOd7v-shLklDwN20hf5dbH84`.

Stop state: **Work Order 56 Phase K is active.** The preserved worker may read and implement the published order, create at most one qualifying build candidate, update both ledgers, and report at orchestrator review. No Phase K device test or later phase is authorized.

## 2026-08-21 — Work Order 56 Phase K Outcome A worker report (Bundle 124)

Selected order and outcome: **WORK ORDER 56 PHASE K — CONDITIONAL PRODUCTION TEXTURE-ARRAY ADMISSION, Outcome A.** The audit established one complete conditional native-ES3/GL4ES-to-Diffusion production route. Bundle 124 is build-qualified only; production terrain has not been device- or gameplay-accepted. No device test or user evidence is requested, and no later phase is begun.

### Baseline, verified boundary, and structural cause

- Control-plane baseline: `b3531a8dbed396aed22aca109b9cab64939305f6`; qualified implementation baseline: `bc4b2b7181b3111053f14ff86e8ff634718acf30`; accepted prerequisite: Bundle 116's physical-device native array conformance PASS.
- Verified first unqualified boundary: after the complete Bundle 116 native array harness passed, production startup still logged `GL_EXT_texture_array - failed`; therefore the real engine/Diffusion landscape route remained unavailable even though its native primitives were qualified.
- Structural cause: the pinned GL4ES extension provider never conditionally exposed the qualified route; the engine gate lacked a complete production proc/limit agreement; Diffusion lacked an independent callback/limit agreement and loader failure closure; and the iOS shader policy stripped `MULTI_LAYERS` plus related terrain directives, so merely exposing the token would have created a false-positive capability whose consumer stayed disabled or whose source/cache key diverged.
- The machine-readable invariant is `scripts/ios/wo56k-production-array-admission-contract.json` (schema 1, seven provenance stages, nine GL4ES operation routes, minimum 16 layers, explicit negative cases and forbidden fallbacks).

### Complete production capability/provenance contract

| Stage | Owner and input | Qualified output | False/failure behavior |
| --- | --- | --- | --- |
| Native provider | GL4ES `GetHardwareExtensions`: live ES major >= 3, live `glTexImage3D`/`glTexSubImage3D`/`glTexStorage3D`, `GL_MAX_ARRAY_TEXTURE_LAYERS >= 16`, live ESSL-300 compile | `hardext.texture_array`, `hardext.maxarraylayers`, `hardext.glsl300es` | Unsupported context/provider, missing proc, insufficient limit, or missing ESSL-300 leaves the route false |
| GL4ES exposure | `BuildExtensionsList`: native predicate plus compiled `gl4es_texture_array_available()` | Exactly one conditional `GL_EXT_texture_array` token | Token omitted; no spoof, cvar, argument, or environment override |
| Engine gate | `GL_InitExtensions`/`GL_CheckExtension`: token, mutable and compressed 3-D upload procs, live layer limit | `GL_TEXTURE_ARRAY_EXT`, `max_2d_texture_layers`, stable engine marker | On disagreement or fewer than 16 layers, extension bit cleared and maximum zeroed |
| Engine loader/export | `R_FillRenderAPI`, `GL_SetTextureTarget`, `GL_CreateTextureArray`, `GL_LoadTextureArray` | `IMAGE_MULTILAYER` maps to `GL_TEXTURE_2D_ARRAY_EXT`; both callbacks exported | Creation/load returns zero; no 2-D, atlas, CPU, or layer-zero fallback |
| Diffusion gate | Its `GL_InitExtensions`: token, at least 16 layers, both array callbacks | `R_TEXTURE_ARRAY_EXT`, agreed maximum, stable admission marker | Gate cleared; `R_LoadLandscapes` performs no array work |
| Landscape loader | `R_LoadLandscapes`, `LoadHeightMap`, `LoadTerrainLayers`: weight, diffuse, and complete optional normal layer sets | Valid weight/diffuse/normal array objects, at most `MAX_LANDSCAPE_LAYERS` | Terrain remains invalid and every partially created array is released |
| Terrain shader/material | Solid/dlight bmodel builders and processor: `GLSL_ALLOW_TEXTURE_ARRAY 1`, `TERRAIN_NUM_LAYERS`, `BMODEL_MULTI_LAYERS`, bump/specular/emboss directives | Real `sampler2DArray`/`texture2DArray` variants; solid units diffuse/normal/weights = 0/4/5, dlight = 0/6/5 | Terrain variants are not admitted without the complete gate and objects; unrelated mobile filtering remains unchanged |

The exact all-required predicate is: live native ES3+ context; all three provider procedures; at least 16 array layers; working ESSL 300; compiled GL4ES object/upload/sampler/translation/realization/lifecycle routes; engine mutable plus compressed 3-D upload procedures and retained engine bit; Diffusion token/limit/two-callback agreement; and terrain cache keys plus emitted source retaining the complete multi-layer feature family. Any false term keeps the provider unadvertised or clears a downstream gate. The native operations are wrapper-owned lifecycle and per-unit array identity/cache; native-forwarded mutable, subimage and immutable upload; per-layer DXT decode followed by native array upload for compressed layers; `TU_ARRAY` reflection/uniform and realization; existing qualified draw routes; live limit query; and stage-correct ESSL-300 translation.

### Implementation, commits, and files

- Coherent implementation commit: `c063202dc0c0111304e2d0a82a2506f1457f1454` (`ios: admit qualified production texture arrays`).
- Bounded qualification corrections: `12a80912c8c18870cad71e6116fbfeda2e26e2c3` normalizes the terrain macro to `#define GLSL_ALLOW_TEXTURE_ARRAY 1`; `38d429b189efc9a46e1a47f8463bf04797641fd6` supplies the GLES token `GL_MAX_ARRAY_TEXTURE_LAYERS_EXT` when the pinned Diffusion headers omit it; `976c38f3d99d7ef6eaf348188fabf4fe4e722be9` verifies the engine gate marker in its actual `libref_gl4es.dylib` owner and adds a wrong-binary rejection fixture. None changes the admission predicate or broadens runtime scope.
- Runtime/build files: `ref/gl/gl_opengl.c`, `scripts/gha/build_ios.sh`, `scripts/ios/builddiffusion.sh`, new `scripts/ios/gl4es-wo56-production-array-admission-ios.patch`, and new `scripts/ios/diffusion-wo56-production-array-admission-ios.patch`.
- Contract/qualification files: new `scripts/ios/wo56k-production-array-admission-contract.json`, new `scripts/ios/validate-ios-production-array-admission.py`, `scripts/ios/validate-diffusion-mobile-shaders.py`, `scripts/ios/validate-ios-renderer-contract.py`, `scripts/ios/validate-ios-selftest-boot.py`, `scripts/ios/validate-ios-texture-array.py`, and `scripts/ios/verify_ipa.sh`.
- Durable-report file: `Documentation/XASH3DIOS_PORTING_STATE.md` only in the final documentation commit.

### Validation, rejection proof, and CI

- Exact pins replayed cleanly: GL4ES `81547d986798e876de8b434193920b606a72363f`, Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, MainUI `8c68de2f...`, executable `9505a1c...`, and SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`. The complete accepted patch stacks and both Phase K patches apply to clean pinned trees.
- The new positive suite and mutation fixtures reject unconditional exposure, ES2/unknown provider, every missing provider proc, zero/insufficient limits, engine/Diffusion disagreement, absent callbacks, wrong target, lost GLSL allow, stripped multi-layers, bypassed loader, missing diffuse/normal array paths, sampler-unit mismatch, atlas/CPU/2-D fallback, wrong marker owner, and ordinary-startup changes.
- Retained texture-array, normal-bootstrap, 57-item renderer-contract, direct-drawable, uint-element, index-trace, WO49 topology/transform/per-unit-target, WO52 material, lifecycle, shader, package and proprietary-data gates passed. Python compilation, JSON parsing and `git diff --check` passed.
- Pre-qualification workflow `32508365615` failed at shader translation before build/artifact because of the macro-value mismatch; `32509025360` failed before artifact at Diffusion compile because the pinned header lacked the limit token; `32509723819` completed all builds but failed before artifact at the wrong-owner verifier assertion. These bounded failures produced no retained candidate/artifact.
- Sole retained qualifying workflow: [32510363562](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32510363562), push event, **success**, job [`96859751554`](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32510363562/job/96859751554), exact head `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`. It passed the complete source/rejection gates, built engine plus Half-Life and Diffusion client/server/menu for iPhoneOS arm64, passed the IPA contract, and uploaded the artifact. An automatic successful PR duplicate (`32510367825`) completed before cancellation; its artifact and run were deleted after exact identity verification, leaving exactly one qualifying workflow/artifact retained. Automatic Build & Deploy runs skipped.

### Artifact and IPA publication

- Retained GitHub artifact: [`Xash3DiOS-arm64-unsigned`](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32510363562/artifacts/9456949434), ID `9456949434`, archive size `8,618,551` bytes, archive digest `sha256:5ed24f8a6ad27dfaea62ed315329d8bdf79e95c5a0053a4ba36187236f42b744`, expiry `2026-09-04T17:57:43Z`.
- Exact unsigned IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 124, `8,717,677` bytes, SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`.
- Independent extraction verified the required app executable, `libref_gl4es.dylib`, Diffusion client/server/menu dylibs, all three production markers in their packaged owners, 13 Mach-O objects all thin arm64 (`CPU 0x0100000C`), and zero proprietary game assets.
- Exactly one tempfile.org object: [information page](https://tempfile.org/qyUGaEfR9Jp/); [direct IPA download](https://tempfile.org/qyUGaEfR9Jp/download); expiry `2026-08-23T18:53:49.725Z`. Metadata/security readback reports the exact filename, byte count and SHA-256, risk `safe`, no warning and no suspicious patterns. A fresh direct-download round trip reproduced the exact byte count and SHA-256.

### Expected markers, retained behavior, risks, and stop state

Expected production markers are `iOS production texture array provider:`, `iOS production texture array engine:`, and `iOS production texture array admission:`. The provider marker must report the live ES/proc/limit/ESSL/implementation terms; the engine and Diffusion markers must agree on enabled state and at least 16 layers. Bundle 116's locked normal-bootstrap arguments, 57-item contract, `a915906d` checksum, `terminal: PASS failures=0 diffusion_started=0`, direct-drawable ownership, uint-index, per-unit target, material/inactive-sampler, array uniform/VBO, lifecycle, menu, Half-Life, and quarantined `ch1map1` contracts remain unchanged.

Why the correction addresses the boundary: capability now flows only from a live qualified native provider through GL4ES's conditional token, an independently checked engine gate and exported array callbacks, Diffusion's independent agreement, complete landscape object creation/cleanup, and the real terrain shader/material consumer. The old iOS suppression no longer strips terrain-only multi-layer semantics, while ordinary mobile shader filtering still applies outside terrain. There is no false advertisement or fallback path.

Remaining risks: Phase K proves source structure, rejection behavior, exact-pin replay, full arm64 build/package, and packaged identity only. It does not prove that ordinary Diffusion terrain loads, renders, or transitions correctly on a device. Bundle 124 is therefore not terrain/device-accepted; no gameplay/device test is requested here. GitHub and tempfile retention are finite. The independent `ch1map1` track remains quarantined and untouched.

Durable ledger path: `Documentation/XASH3DIOS_PORTING_STATE.md`. The repository ledger commit is a documentation-only `[skip ci]` commit whose immutable hash is copied into the authoritative Google Docs report and final handoff. Both ledgers are read back after publication.

Stop state: **Work Order 56 Phase K Outcome A is complete at the orchestrator-review gate.** Do not contact Arjun, request evidence or device/gameplay testing, launch or retest Bundle 124, start another workflow/candidate/upload, change terrain/gameplay/`ch1map1`, or begin a later phase without a new explicit orchestrator-authored work order.

## 2026-08-22 — Work Order 56 Phase K acceptance and Phase L admission-device order

Orchestrator decision: **Work Order 56 Phase K Outcome A is accepted as build-qualified evidence.** Candidate `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`, workflow `32510363562`, artifact `9456949434`, and Bundle 124 establish one coherent conditional GL4ES/engine/Diffusion production texture-array admission route. The Phase K source, mutation, exact-pin replay, full arm64 build, packaged-owner, architecture, and proprietary-data gates are accepted. Bundle 124 is not yet device-accepted and the result does not establish landscape loading, terrain shader execution, rendering, transitions, gameplay, or `ch1map1`.

Selected next boundary: **WORK ORDER 56 PHASE L — BUNDLE 124 NORMAL-BOOTSTRAP PRODUCTION TEXTURE-ARRAY ADMISSION DEVICE ACCEPTANCE.** This remains a continuation of WO-056. It reuses the exact build-qualified IPA for one ordinary, menu-only launch on the established iPhone 16 Pro Max / iOS 26.6. It does not authorize a build, patch, CI run, new artifact, gameplay, terrain, map, transition, or `ch1map1` test.

### Exact candidate and locked procedure

- Candidate: `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`; workflow `32510363562`; retained artifact `Xash3DiOS-arm64-unsigned`, ID `9456949434`.
- IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 124, `8,717,677` bytes, SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`.
- Locked arguments: `-dev 2 -log -game diffusion -ref gl4es`; the self-test flag and any force-enable flag must be absent.
- Verify the exact IPA identity, preserve external Diffusion data, install over the existing app without deleting data, launch exactly once, reach a stable Diffusion menu, wait about 10 seconds, capture one screenshot, export the complete engine log, and stop.
- Do not click Start, New Game, difficulty, or any route that admits a map or gameplay. Do not exercise terrain or `ch1map1`. Do not rerun without orchestrator review.

### Required evidence and outcome gates

The log must show three agreeing enabled markers: `iOS production texture array provider:` with native ES3+, required procedures, at least 16 layers, ESSL 300, `advertised=1`, and `reason=complete`; `iOS production texture array engine:` with four procedures, at least 16 layers, `minimum=16`, and `enabled=1`; and `iOS production texture array admission:` with extension/callback agreement, at least 16 layers, `minimum=16`, `terrain_shaders=full`, and `enabled=1`. It must not contain `GL_EXT_texture_array - failed`, `Landscapes will be unavailable`, a relevant GL/shader failure, or unexpected termination. The menu must remain stable for the bounded observation.

- **Outcome A:** exact identity, complete one-run evidence, all three markers enabled and agreeing, stable menu, no prohibited warnings/failures/crash. Qualifies production admission during ordinary bootstrap only; terrain and gameplay remain unqualified.
- **Outcome B:** exact candidate reaches renderer initialization but a marker is false/mismatched/missing, a prohibited warning appears, a relevant GL/shader failure occurs, or the app crashes. Preserve the first divergence; do not patch, rebuild, or rerun.
- **Outcome C:** wrong/unverifiable IPA, arguments, data, installation, screenshot, or log; truncated evidence; or evidence not attributable to exactly one launch. Stop inconclusive; do not rerun.

Required package: verified IPA filename/bytes/hash; device/OS; one stable-menu screenshot; complete single-run log with filename/bytes/SHA-256 and the three markers; first divergence for Outcome B; matching `.ips` only for unexpected termination; explicit outcome and stop state.

ControlPlane authority and complete stopping conditions are in `WorkOrders/WO-056.md`, `Decisions/DEC-007.md`, and `Evidence/WO-056/manifest.md`. The preserved worker may request exactly this evidence package, validate it, update and read-back verify both ledgers and ControlPlane, push documentation-only reporting, message the delegating orchestrator with the result, and stop at orchestrator review.

Stop state: **Work Order 56 Phase L is active.** The first incomplete action is the preserved worker's exact evidence request and validation of the sole authorized normal-bootstrap device run. No engineering implementation work is authorized.

The authoritative Google Docs ledger was appended under revision guard and its Phase L stop-state paragraph was verified by readback at revision `AIroW36cJUxGI7JGaMrb1e_-ZnY-2hz35dp3f9oR5_8XOk5WxxvOGFH_ylpE2YQB81wyRM8whgNLXFbiu6v0RmievJgG1VBId2Arbg8P0Cg`.

## 2026-08-22 — Work Order 56 Phase L Outcome C worker report

Selected outcome: **WORK ORDER 56 PHASE L — Outcome C before device launch.** The exact Bundle 124 IPA identity is valid, but the candidate cannot execute the order's required ordinary Diffusion arguments. This is an argument/candidate mismatch, not a renderer rejection. No physical-device launch, gameplay action, build, CI run, artifact, upload, or runtime change occurred.

### Pre-launch evidence and exact boundary

- Verified IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 124, `8,717,677` bytes, SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`, matching candidate `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`, workflow `32510363562`, artifact `9456949434`.
- Required Phase L arguments: `-dev 2 -log -game diffusion -ref gl4es`, with `-gl4es_texture_array_selftest` absent.
- Actual candidate contract: `engine/platform/ios/launchdialog.m` assigns `-dev 2 -log -game diffusion -ref gl4es -gl4es_texture_array_selftest` to `textureArraySelftestArgs`, writes that value into the only launch field, calls `setEnabled:NO`, and constructs `argv` from the disabled field's text.
- Independent packaged readback: the exact extracted Bundle 124 `xash` executable contains the full self-test argument string and the self-test token; its `Info.plist` reports version `124`.
- The mismatch is therefore deterministic before installation. Launching the candidate would execute the bounded self-test route already qualified by Bundle 116, not the ordinary production-admission route Phase L is meant to discriminate.

### Outcome, evidence status, and stop gate

Outcome C applies because the arguments cannot be made correct for the exact immutable candidate. The worker stopped at Phase L procedure step 3. No app installation or launch was performed; no external Diffusion data changed; no stable-menu screenshot, engine log, or `.ips` exists; and the sole authorized device launch remains unconsumed. The absence of runtime markers is not treated as a renderer failure.

Bundle 116 remains physically qualified for the bounded native texture-array conformance harness. Bundle 124 remains build-qualified for the conditional production route. The first unqualified boundary remains live provider/engine/Diffusion production-admission agreement during an ordinary, self-test-free bootstrap. Terrain discovery/loading, array object creation in production, terrain shader execution, drawing, presentation, map transitions, gameplay, and `ch1map1` remain unqualified and untouched.

Exact files changed for Phase L reporting: `Documentation/CURRENT_STATE.md`, `WorkOrders/WO-056.md`, `Evidence/WO-056/manifest.md`, and `Documentation/XASH3DIOS_PORTING_STATE.md`. No source, patch, validator, workflow, IPA, artifact, game data, menu, input, terrain, map, transition, or gameplay file changed. No CI workflow was launched.

First incomplete step: orchestrator review of the contradictory immutable candidate/argument tuple and a decision whether a separately authorized ordinary-argument candidate is justified. The worker does not propose or begin that change automatically.

Stop state: **Work Order 56 Phase L is complete at Outcome C and the orchestrator-review gate.** Do not launch or retest Bundle 124, alter arguments or data, patch, build, run CI, create/upload an artifact, enter terrain/gameplay, modify `ch1map1`, or begin another phase without a new explicit orchestrator-authored order.

## Work Order 56 Phase L acceptance and Phase M ordinary-bootstrap candidate order

Orchestrator decision: **Work Order 56 Phase L Outcome C is accepted as a correct pre-launch stop.** Bundle 124's exact identity passed, but its disabled launch field deterministically includes `-gl4es_texture_array_selftest`; therefore launching it would repeat the diagnostic route instead of testing ordinary production admission. No device launch occurred and the one-run authorization remains unconsumed. Phase K's build-qualified production texture-array implementation is not rejected or reinterpreted.

Selected next boundary: **WORK ORDER 56 PHASE M — LOCKED ORDINARY-BOOTSTRAP CANDIDATE BUILD QUALIFICATION.** This remains a continuation of WO-056. It authorizes one bounded audit and the minimum coherent source/validation/package change needed to build a candidate whose exact locked arguments are `-dev 2 -log -game diffusion -ref gl4es`. It does not authorize device evidence, terrain, gameplay, or `ch1map1`.

### Baseline, objective, and first incomplete action

- Control baseline: `c7be0a237ad223e60b7808a903d2411a9154c153`; production baseline: candidate `976c38f3d99d7ef6eaf348188fabf4fe4e722be9`, workflow `32510363562`, artifact `9456949434`, Bundle 124 IPA SHA-256 `FB62C2903E21152DCB74C709656F8FEF841ACE2A22C281F27B90AC02F0E1D04F`.
- The iOS call graph is direct: `main` calls `IOS_LaunchDialog`, then `IOS_GetArgs`, then passes the resulting `argc/argv` to `Host_Main`. The disabled text field is therefore the authoritative candidate tuple.
- Objective: replace only the locked diagnostic tuple with the exact ordinary tuple, keep the field disabled, retain the self-test as explicit-flag-only dormant regression machinery, adapt the affected source/validation/package contracts, build at most one qualifying candidate, and stop before runtime qualification.
- First incomplete action: inventory every source, validator, mutation fixture, and IPA string check that encodes the default self-test tuple or dormancy invariant and record `scripts/ios/wo56m-ordinary-bootstrap-contract.json` or the reported semantic equivalent before or with implementation.

### Required implementation and package contract

The candidate must contain one exact standalone ordinary launch string and must not contain the old combined ordinary-plus-self-test default string. Package verification must use exact-line or equivalent discrimination rather than prefix substring matching. The self-test flag parser, conditional dispatch, bounded terminal route, harness, and markers must remain compiled but must not be automatically armed. Phase K's provider/engine/Diffusion predicates and markers remain unchanged.

Authorized runtime scope is limited to the locked value in `engine/platform/ios/launchdialog.m`; an accurate constant rename is allowed. Directly affected validators, mutation fixtures, the new machine contract, and `verify_ipa.sh` may change to enforce exact ordinary default arguments, reject accidental self-test activation, and retain all prior regression gates. The field remains disabled; editable settings, `settings.bin` behavior, alternate selectors/actions, cvars, environment overrides, force-enables, fallbacks, and workflow changes are prohibited.

Do not change GL4ES, renderer/engine/Diffusion capability gates, landscape loading, shaders, materials, texture units, samplers, cleanup, data, input, menus beyond the locked text value, maps, terrain, transitions, gameplay, or `ch1map1`. Do not delete or weaken the diagnostic harness. Do not request/run a device test or transfer the unconsumed Phase L authorization to the new candidate.

### Validation, outcomes, and stop gate

Positive and mutation coverage must prove exact ordinary tuple equality, locked-field authority, launch-to-`Host_Main` ownership, absence of the combined default string, dormant explicit-flag self-test machinery, rejection of unconditional dispatch/removal/Valve substitution/editable-field restoration/override/fallback, unchanged production predicates, and correct exact packaged-string logic. Retain every accepted Python/JSON, exact-pin, renderer-contract, texture-array, normal-bootstrap, drawable, uint-index, per-unit-target, material, lifecycle, shader, arm64, IPA, and proprietary-data gate; perform full iPhoneOS arm64 engine/Half-Life/Diffusion qualification.

- **Outcome A:** one coherent ordinary-argument candidate passes source, rejection, exact-pin, full-build, and IPA gates. Retain one qualifying workflow/artifact, publish and independently verify the unsigned IPA once, update/read back ControlPlane and both ledgers, and stop. The result is build-qualified only.
- **Outcome B:** the audit proves broader launch/settings/harness/renderer/data/workflow coupling is required. Make no partial runtime change or CI build; record the exact boundary and stop.
- **Outcome C:** source/package evidence cannot distinguish the exact standalone tuple or prove retained self-test dormancy. Make no runtime change/build; record the missing discriminator and stop.

Complete authority, rejection fixtures, evidence fields, and stopping conditions are materialized in `WorkOrders/WO-056.md`; `Documentation/CURRENT_STATE.md`, `Decisions/DEC-008.md`, and `Evidence/WO-056/manifest.md` form the current ControlPlane checkpoint.

Stop state: **Work Order 56 Phase M is active.** The preserved worker may execute the published build-only order, update/read-back verify all durable records, push, send the mandatory completion callback, and stop at orchestrator review. No device or later phase is authorized.

The authoritative Google Docs ledger was appended under revision guard and its Phase M stop-state paragraph was verified by readback at revision `AIroW37tae1LAWrBYYTMvYeeh_9sHD6ReMvvblPZDotrbAQSlIRULeEX4Xtbxvp6FKtHH08vVjI5DdWIvkmENwrDk9vVvA2jZdRMSmIwXfY`.

## 2026-08-22 — Work Order 56 Phase M Outcome A worker report

Selected outcome: **WORK ORDER 56 PHASE M — Outcome A, ordinary-argument candidate build-qualified.** Control baseline `38114ad981ecc145c16e2672abbc2dc688bcdaad`; implementation/candidate commit `5a529ff41d23b557e6e4e7878fb31284c7dfc661`. No device launch, screenshot, engine log, terrain, map, transition, gameplay, or `ch1map1` action was authorized or performed.

### Verified boundary, argument ownership, and structural cause

The verified failure boundary inherited from Phase L was deterministic argument ownership before device installation: Bundle 124's sole disabled field armed the self-test instead of ordinary startup. Phase M proved the complete route: `IOS_LaunchDialog` owns the exact locked field value and tokenizes it into `szArgc/szArgv`; `IOS_GetArgs` returns those values; iOS `main` passes them unchanged to `Host_Main`. No settings, environment, cvar, fallback, or alternate action overrides that route.

The structural correction changes only the locked source value to exact `-dev 2 -log -game diffusion -ref gl4es`, retaining `setEnabled:NO`. The self-test flag parser, conditional host/renderer dispatch, 57-item contract, harness, markers, bounded terminal path, and clean shutdown remain compiled but dormant unless the flag is explicitly supplied through a separately authorized future route. Phase K's provider/engine/Diffusion predicates and terrain consumer are byte-locked by the machine contract and unchanged. Machine-readable contract: `scripts/ios/wo56m-ordinary-bootstrap-contract.json`.

Argument ownership table:

- Locked source value — `IOS_LaunchDialog`, `engine/platform/ios/launchdialog.m`: one exact ordinary tuple assigned to the sole disabled field.
- Tokenization — `IOS_LaunchDialog`: field text split on spaces into `szArgc/szArgv`, without settings/fallback override.
- Export — `IOS_GetArgs`: returns those exact values.
- Host admission — `engine/common/launcher.c::main`: `IOS_LaunchDialog` → `IOS_GetArgs` → `Host_Main`.

### Exact files and commits

Implementation commit: `5a529ff41d23b557e6e4e7878fb31284c7dfc661` (`ios: qualify locked ordinary Diffusion bootstrap`). Exact implementation files changed:

- `engine/platform/ios/launchdialog.m`
- `scripts/gha/build_ios.sh`
- `scripts/ios/validate-ios-ordinary-bootstrap.py`
- `scripts/ios/validate-ios-production-array-admission.py`
- `scripts/ios/validate-ios-renderer-contract.py`
- `scripts/ios/validate-ios-selftest-boot.py`
- `scripts/ios/validate-ios-texture-array.py`
- `scripts/ios/verify_ipa.sh`
- `scripts/ios/wo56m-ordinary-bootstrap-contract.json`

Final reporting changes are limited to `Documentation/CURRENT_STATE.md`, `Documentation/XASH3DIOS_PORTING_STATE.md`, `WorkOrders/WO-056.md`, `Decisions/DEC-008.md`, and `Evidence/WO-056/manifest.md`; they are committed separately with `[skip ci]` after this report.

### Validation and rejection proof

- Python compilation and JSON parsing passed for the affected validators and new contract; `git diff --check` passed.
- Focused Phase M positive and mutation fixtures passed, rejecting tuple inequality, combined automatic self-test, Valve substitution, editable field, field-authority removal, call-flow bypass/reordering, removed flag parser/harness/terminal/marker, unconditional dispatch, settings/fallback override, substring-only package checks, and every locked Phase K production-owner mutation.
- Retained self-test bootstrap, 57-item renderer contract, native texture-array sampling/readback, production array admission, direct drawable, uint element, index trace, WO49 topology/transform/per-unit target, WO51 material state, WO52 material trace/inactive sampler, and Diffusion shader-policy suites passed.
- Exact patch replay passed against GL4ES `81547d986798e876de8b434193920b606a72363f`, Diffusion `14d156bf3a6993c172697fac83a937836c3b5561`, MainUI `8c68de2f2325a0130953719efc3ae413eb24e01a`, executable `9505a1c01f597e23c3acb7cbb8852b9dcfb0a038`, and SDL `5d249570393f7a37e037abf22cd6012a4cc56a71`.
- CI performed the affected Objective-C translation-unit and full iPhoneOS arm64 engine, Half-Life, and Diffusion client/server/menu qualification, then passed the IPA contract.

### Workflow, artifact, IPA, and publication

- Sole retained qualifying workflow: [32551387441](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32551387441), push event, success, exact head `5a529ff41d23b557e6e4e7878fb31284c7dfc661`; job [96978610370](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32551387441/job/96978610370).
- Automatic PR duplicate `32551389885` was cancelled during dependency installation; its build, IPA verification, and upload steps were skipped, so it produced no qualifying candidate or artifact.
- Retained GitHub artifact: [Xash3DiOS-arm64-unsigned](https://github.com/arjunyerevan95-dot/Xash3DiOS/actions/runs/32551387441/artifacts/9470194619), ID `9470194619`, archive size `8,617,082` bytes, digest `sha256:400cde7cf33dc29b6ca72e0376f6d05bc979202622e1e3b98d5cb3d7126e3eef`, expiry `2026-09-05T04:23:34Z`.
- Exact unsigned IPA: `xash3d-fwgs-ios-arm64.ipa`, Bundle 126, `8,717,507` bytes, SHA-256 `F5FE061690C0532C3086B2CCD650E541FCEB14F35128F7A35C66B670AE105ACF`.
- Exactly one tempfile object: [information page](https://tempfile.org/MrnVs2sedq5/); [direct IPA](https://tempfile.org/MrnVs2sedq5/download); ID `MrnVs2sedq5`; expiry epoch-ms `1787545730208`. Metadata/security reports the exact filename, byte count and SHA-256, risk `safe`, no warning and no suspicious patterns. A fresh direct-download round trip reproduced the exact size and SHA-256.

Independent package extraction verified Bundle 126, one exact standalone ordinary tuple in `xash`, zero combined ordinary-plus-self-test tuple, one separate self-test flag token, the provider and engine production markers in `libref_gl4es.dylib`, the admission marker in Diffusion `client_arm64.dylib`, retained diagnostic markers, 13 Mach-O objects all thin arm64 (`CPU 0x0100000C`), and zero proprietary game assets.

### Expected markers, qualification boundary, risks, and stop state

Expected ordinary runtime markers remain `iOS production texture array provider:`, `iOS production texture array engine:`, and `iOS production texture array admission:`. Diagnostic markers remain packaged but must not appear from automatic self-test dispatch under the ordinary tuple.

Why the correction addresses the cause: it changes the authoritative locked argument owner, and exact-line source/package discrimination proves the ordinary string cannot pass merely as a prefix of the removed combined string. The byte-locked renderer contracts prove the change does not broaden capability, enable terrain, or weaken the accepted self-test machinery.

Remaining risks: Bundle 126 is build-qualified only. No physical-device evidence proves live provider/engine/Diffusion agreement under ordinary startup. Terrain discovery/loading, production array creation, terrain shader use, drawing, presentation, maps, transitions, gameplay, and `ch1map1` remain unqualified and untouched. GitHub and tempfile retention are finite.

First incomplete step: orchestrator review and an explicit decision whether to authorize a separate evidence-only physical-device ordinary-bootstrap admission test. The unconsumed Phase L authorization did not transfer automatically and was not used.

Stop state: **Work Order 56 Phase M Outcome A is complete at the orchestrator-review gate.** Do not contact Arjun, request evidence or device testing, launch Bundle 126, run another workflow/candidate/upload, enter terrain/gameplay, change `ch1map1`, or begin a later phase without a new explicit orchestrator-authored work order.
