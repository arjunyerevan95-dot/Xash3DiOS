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

for required_path in \
	"$INFO_PLIST" \
	"$ENGINE_PATH" \
	"$SDL_PATH" \
	"$DIFFUSION_CLIENT_PATH" \
	"$DIFFUSION_SERVER_PATH"; do
	if [ ! -e "$required_path" ]; then
		echo "Required bundle item is missing: $required_path" >&2
		exit 1
	fi
done

plutil -lint "$INFO_PLIST"

MINIMUM_OS=$(/usr/libexec/PlistBuddy -c 'Print :MinimumOSVersion' "$INFO_PLIST")
FILE_SHARING=$(/usr/libexec/PlistBuddy -c 'Print :UIFileSharingEnabled' "$INFO_PLIST")

if [ "$FILE_SHARING" != "true" ]; then
	echo "UIFileSharingEnabled must remain enabled for user-supplied game data" >&2
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

if [ "$DYLIB_COUNT" -lt 9 ]; then
	echo "Expected engine, Half-Life, and Diffusion dylibs; found $DYLIB_COUNT" >&2
	exit 1
fi

codesign -dv "$APP_PATH" >/dev/null 2>&1

echo "Verified: $IPA_PATH"
echo "Application: $(basename "$APP_PATH")"
echo "Minimum iOS: $MINIMUM_OS"
echo "Mach-O files: $MACHO_COUNT"
echo "Game dylibs: $DYLIB_COUNT"
