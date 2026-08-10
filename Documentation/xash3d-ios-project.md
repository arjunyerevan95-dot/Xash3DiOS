# Xash3DiOS project

Xash3DiOS is an arm64 iOS/iPadOS porting project based on the actively
maintained Xash3D FWGS engine. Its first target is a reproducible unsigned IPA
that runs legally acquired Half-Life data on current Apple devices. Its second
target is the Diffusion total conversion.

The repository deliberately starts from current FWGS rather than the historic
armv7-only `mittorn/xash3d-ios` fork. The old fork remains a reference for
platform archaeology, not a source baseline.

## Asset and distribution policy

No Valve, Half-Life, or Diffusion game data belongs in source control or CI
artifacts. The application must accept user-supplied, legally acquired data via
its Files-visible Documents directory. Engine, menu, client, and server code
that must execute on iOS is compiled for arm64 and bundled in the IPA.

CI produces an unsigned/ad-hoc-signed IPA for personal sideloading. A user or
device-testing service must re-sign it with an appropriate Apple identity.

## Proof-of-life gates

1. **Package:** CI creates an arm64 IPA containing the engine, SDL2, and the
   portable HLSDK client/server libraries. The verifier checks every Mach-O and
   reports its minimum deployment target.
2. **Platform:** On a physical device, launch in both landscape orientations,
   confirm a non-zero drawable, exercise background/foreground recovery, and
   repeat a cold relaunch.
3. **Half-Life:** Import the `valve` directory, reach the menu, load a map, move,
   look, save, load, and transition between maps.
4. **Input:** Reproduce the established SeriousiOS/eDukeiOS contract: an
   invisible left movement region, relative right-side look, additive gyro,
   editable normalized action buttons, interruption cleanup, and additive
   controller/keyboard input.
5. **Diffusion fallback:** Compile Diffusion client, server, and MainUI for
   arm64; first attempt gameplay with `gl_renderer 0` through the engine's GLES
   renderer.
6. **Diffusion renderer:** Only after Gate 5, expose the GLES3 compatibility
   entry points to the client renderer, port GLSL 1.30 shaders to GLSL ES 3.00,
   and restore effects incrementally.

Each gate should produce a device log and a short pass/fail checklist. Renderer
work must not begin based solely on a successful compile or menu launch.

## Touch-control contract

The initial implementation should use Xash's maintained touch and gyro systems
instead of introducing a second UIKit input stack. The target behavior is:

- invisible left 46% movement region with a 12-point dead zone;
- relative look that preserves fractional display scale and composes with gyro;
- Use, Jump, Crouch, Next Weapon, Pause, and optional Fire buttons;
- tap-to-fire and 125 ms hold-to-sustain semantics;
- a two-second Pause hold to enter layout editing;
- versioned, normalized layout persistence and complete per-finger cleanup on
  interruption, backgrounding, or mode changes;
- native menu pointer behavior and additive controller/keyboard support.

Exact input changes are deferred until the stock touch path is validated on a
physical device, so renderer, data-import, and input failures remain separable.

## Upstream synchronization

- Engine upstream: <https://github.com/FWGS/xash3d-fwgs>
- Diffusion game code: <https://github.com/Aynekko/Diffusion>
- Diffusion MainUI: <https://github.com/Aynekko/Diffusion-MainUI>

Keep `upstream` pointed at FWGS. Merge or rebase upstream changes deliberately;
do not replace this repository with ZIP snapshots, because FWGS relies on Git
submodules.
