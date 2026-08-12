#!/bin/bash

set -euo pipefail

IPA_PATH=${1:-artifacts/xash3d-fwgs-ios-arm64.ipa}

if [ ! -f "$IPA_PATH" ]; then
	echo "IPA not found: $IPA_PATH" >&2
	exit 1
fi

VERIFY_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/xash3d-ios-verify.XXXXXX")
cleanup()
{
	rm -rf "$VERIFY_ROOT"
}
trap cleanup EXIT

unzip -q "$IPA_PATH" -d "$VERIFY_ROOT"
APP_PATH=$(find "$VERIFY_ROOT/Payload" -maxdepth 1 -type d -name '*.app' -print -quit)

if [ -z "$APP_PATH" ]; then
	echo "No application bundle found in $IPA_PATH" >&2
	exit 1
fi

INFO_PLIST="$APP_PATH/Info.plist"
ENGINE_PATH="$APP_PATH/xash"
SDL_PATH="$APP_PATH/SDL2.framework/SDL2"
DIFFUSION_CLIENT_PATH="$APP_PATH/bin/client_arm64.dylib"
DIFFUSION_SERVER_PATH="$APP_PATH/bin/server_arm64.dylib"
DIFFUSION_MENU_PATH="$APP_PATH/bin/menu_arm64.dylib"
DIFFUSION_LOCALIZATION_PATH="$APP_PATH/diffusion/resource/gameui_english.txt"
DIFFUSION_MATHLIB_PATH="$APP_PATH/ios_overrides/diffusion/glsl/mathlib.h"
DIFFUSION_ALPHA_COVERAGE_PATH="$APP_PATH/ios_overrides/diffusion/glsl/alpha2coverage.h"
DIFFUSION_SHAFTS_SHADER_PATH="$APP_PATH/ios_overrides/diffusion/glsl/genshafts_fp.glsl"
GL4ES_RENDERER_PATH="$APP_PATH/libref_gl4es.dylib"

for required_path in \
	"$INFO_PLIST" \
	"$ENGINE_PATH" \
	"$SDL_PATH" \
	"$DIFFUSION_CLIENT_PATH" \
	"$DIFFUSION_SERVER_PATH" \
	"$DIFFUSION_MENU_PATH" \
	"$DIFFUSION_LOCALIZATION_PATH" \
	"$DIFFUSION_MATHLIB_PATH" \
	"$DIFFUSION_ALPHA_COVERAGE_PATH" \
	"$DIFFUSION_SHAFTS_SHADER_PATH" \
	"$GL4ES_RENDERER_PATH"; do
	if [ ! -e "$required_path" ]; then
		echo "Required bundle item is missing: $required_path" >&2
		exit 1
	fi
done

if ! grep -q 'XASH_MOBILE_GLES' "$DIFFUSION_ALPHA_COVERAGE_PATH"; then
	echo "Diffusion mobile shader profile is missing from the IPA" >&2
	exit 1
fi

DIFFUSION_CLIENT_STRINGS="$VERIFY_ROOT/diffusion-client.strings"
strings "$DIFFUSION_CLIENT_PATH" > "$DIFFUSION_CLIENT_STRINGS"
if ! grep -q 'iOS mobile renderer profile: canonical materials, shared animated-model shader layout, on-demand shaders' "$DIFFUSION_CLIENT_STRINGS"; then
	echo "Diffusion client was built without the iOS renderer profile" >&2
	exit 1
fi

if ! grep -q 'iOS foliage liveness policy: bounded_lines=' "$DIFFUSION_CLIENT_STRINGS"; then
	echo "Diffusion client was built without bounded foliage liveness diagnostics" >&2
	exit 1
fi

if ! grep -q 'iOS world traversal:' "$DIFFUSION_CLIENT_STRINGS"; then
	echo "Diffusion client was built without bounded world-traversal diagnostics" >&2
	exit 1
fi

for wo43_client_marker in \
	'WO43 GL interval begin:' \
	'WO43 GL phase transition:' \
	'WO43 GL exact first failure:' \
	'WO43 GL attribution gap:' \
	'WO43 init phase: state=begin' \
	'WO43 init phase: state=end' \
	'WO43 init gap:'; do
	if ! grep -q "$wo43_client_marker" "$DIFFUSION_CLIENT_STRINGS"; then
		echo "Diffusion client is missing WO43 marker: $wo43_client_marker" >&2
		exit 1
	fi
done

DIFFUSION_MENU_STRINGS="$VERIFY_ROOT/diffusion-menu.strings"
strings "$DIFFUSION_MENU_PATH" > "$DIFFUSION_MENU_STRINGS"
if ! grep -q 'iOS mobile menu policy: decorative background map disabled; UI callbacks remain active' "$DIFFUSION_MENU_STRINGS"; then
	echo "Diffusion menu was built without the mobile background-map policy" >&2
	exit 1
fi

if ! grep -q 'Diffusion menu action: starting chapter' "$DIFFUSION_MENU_STRINGS"; then
	echo "Diffusion menu was built without actionable mobile menu diagnostics" >&2
	exit 1
fi

GL4ES_RENDERER_STRINGS="$VERIFY_ROOT/gl4es-renderer.strings"
strings "$GL4ES_RENDERER_PATH" > "$GL4ES_RENDERER_STRINGS"

if ! grep -q 'iOS liveness renderer policy: bounded_frames=12' "$GL4ES_RENDERER_STRINGS"; then
	echo "Renderer was built without bounded flush/present liveness diagnostics" >&2
	exit 1
fi

if ! grep -q 'iOS display audit GL4ES:' "$GL4ES_RENDERER_STRINGS"; then
	echo "Renderer was built without paired GL4ES framebuffer diagnostics" >&2
	exit 1
fi

if ! grep -q 'Native GLES3 core NPOT support enabled' "$GL4ES_RENDERER_STRINGS"; then
	echo "GL4ES was built without the GLES3 full-NPOT capability fix" >&2
	exit 1
fi

if ! grep -q 'compressed texture buffer overrun' "$GL4ES_RENDERER_STRINGS"; then
	echo "Renderer was built without compressed-texture bounds checks" >&2
	exit 1
fi

ENGINE_STRINGS="$VERIFY_ROOT/engine.strings"
strings "$ENGINE_PATH" > "$ENGINE_STRINGS"
if ! grep -q 'iOS liveness instrumentation: host, screen, renderer, foliage, flush, swap/present' "$ENGINE_STRINGS"; then
	echo "Engine was built without bounded host/screen liveness diagnostics" >&2
	exit 1
fi

if ! grep -q 'iOS display audit policy: gl_attribution_frames=12 init_timeout_seconds=120 native_sample_seconds=2 baseline=pre-world checksum=5x4x4 sentinel=disabled' "$ENGINE_STRINGS"; then
	echo "Engine was built without independent GL-attribution and initialization windows" >&2
	exit 1
fi

for wo43_engine_marker in \
	'WO43 Phase B diagnostics:' \
	'WO43 init timing:' \
	'WO43 init heartbeat:' \
	'WO43 init terminal:' \
	'WO43 native presentation:' \
	'WO43 normal-scene proof:'; do
	if ! grep -q "$wo43_engine_marker" "$ENGINE_STRINGS"; then
		echo "Engine is missing WO43 marker: $wo43_engine_marker" >&2
		exit 1
	fi
done

if ! grep -q 'iOS display audit ScreenFade:' "$ENGINE_STRINGS"; then
	echo "Engine was built without paired ScreenFade diagnostics" >&2
	exit 1
fi

SDL_STRINGS="$VERIFY_ROOT/sdl.strings"
strings "$SDL_PATH" > "$SDL_STRINGS"
if grep -q 'sentinel_bars=' "$SDL_STRINGS"; then
	echo "SDL still contains the disabled Run-51 sentinel path" >&2
	exit 1
fi

SDL_EXPORTS="$VERIFY_ROOT/sdl.exports"
nm -gU "$SDL_PATH" > "$SDL_EXPORTS"
if ! grep -q '_SDL_XASH_IOSDisplayAuditSnapshot$' "$SDL_EXPORTS"; then
	echo "SDL display-audit snapshot export is missing" >&2
	exit 1
fi

plutil -lint "$INFO_PLIST"

MINIMUM_OS=$(/usr/libexec/PlistBuddy -c 'Print :MinimumOSVersion' "$INFO_PLIST")
FILE_SHARING=$(/usr/libexec/PlistBuddy -c 'Print :UIFileSharingEnabled' "$INFO_PLIST")
BUNDLE_VERSION=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$INFO_PLIST")

if [ "$FILE_SHARING" != "true" ]; then
	echo "UIFileSharingEnabled must remain enabled for user-supplied game data" >&2
	exit 1
fi

case "$BUNDLE_VERSION" in
	''|*[!0-9]*)
		echo "CFBundleVersion must be a positive integer, got: $BUNDLE_VERSION" >&2
		exit 1
		;;
esac

if [ "$BUNDLE_VERSION" -le 1 ]; then
	echo "CFBundleVersion must increase beyond the legacy value 1" >&2
	exit 1
fi

verify_arm64_macho()
{
	local binary_path=$1
	local file_description
	local architectures

	file_description=$(file "$binary_path")
	case "$file_description" in
		*Mach-O*) ;;
		*) return 0 ;;
	esac

	architectures=$(lipo -archs "$binary_path")
	case " $architectures " in
		*" arm64 "*) ;;
		*)
			echo "Mach-O does not contain arm64: $binary_path ($architectures)" >&2
			exit 1
			;;
	esac

	echo "Mach-O: ${binary_path#"$APP_PATH"/} [$architectures]"
	xcrun vtool -show-build "$binary_path"
}

MACHO_COUNT=0
while IFS= read -r -d '' candidate; do
	if file "$candidate" | grep -q 'Mach-O'; then
		MACHO_COUNT=$((MACHO_COUNT + 1))
		verify_arm64_macho "$candidate"
	fi
done < <(find "$APP_PATH" -type f -print0)

DYLIB_COUNT=$(find "$APP_PATH" -type f -name '*.dylib' | wc -l | tr -d ' ')

if [ "$MACHO_COUNT" -lt 3 ]; then
	echo "Expected the engine, SDL2, and game libraries; found $MACHO_COUNT Mach-O files" >&2
	exit 1
fi

if [ "$DYLIB_COUNT" -lt 10 ]; then
	echo "Expected engine, Half-Life, and Diffusion dylibs; found $DYLIB_COUNT" >&2
	exit 1
fi

codesign -dv "$APP_PATH" >/dev/null 2>&1

echo "Verified: $IPA_PATH"
echo "Application: $(basename "$APP_PATH")"
echo "Bundle version: $BUNDLE_VERSION"
echo "Minimum iOS: $MINIMUM_OS"
echo "Mach-O files: $MACHO_COUNT"
echo "Game dylibs: $DYLIB_COUNT"
