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
