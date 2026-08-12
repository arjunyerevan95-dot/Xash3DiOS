#!/bin/bash

set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
IOS_DEPLOYMENT_TARGET=${IOS_DEPLOYMENT_TARGET:-12.0}

# Pin all three repositories so device-test artifacts remain reproducible even
# when Diffusion development moves ahead of this port.
DIFFUSION_REF=${DIFFUSION_REF:-14d156bf3a6993c172697fac83a937836c3b5561}
DIFFUSION_MAINUI_REF=${DIFFUSION_MAINUI_REF:-8c68de2f2325a0130953719efc3ae413eb24e01a}
DIFFUSION_EXECUTABLE_REF=${DIFFUSION_EXECUTABLE_REF:-9505a1c01f597e23c3acb7cbb8852b9dcfb0a038}

mkdir -p "$ROOT_DIR/build"
WORK_DIR=$(mktemp -d "$ROOT_DIR/build/diffusion-ios.XXXXXX")
SOURCE_DIR="$WORK_DIR/Diffusion"
STAGE_DIR="$WORK_DIR/stage"
APP_LIBS_DIR="$ROOT_DIR/build/ios/libs"

cleanup()
{
	rm -rf -- "$WORK_DIR"
}
trap cleanup EXIT

checkout_revision()
{
	local repository_url=$1
	local revision=$2
	local destination=$3

	git init -q "$destination"
	git -C "$destination" remote add origin "$repository_url"
	git -C "$destination" fetch -q --depth 1 origin "$revision"
	git -C "$destination" checkout -q --detach FETCH_HEAD

	local actual_revision
	actual_revision=$(git -C "$destination" rev-parse HEAD)
	if [ "$actual_revision" != "$revision" ]; then
		echo "Expected $revision from $repository_url, got $actual_revision" >&2
		exit 1
	fi
}

checkout_revision https://github.com/Aynekko/Diffusion.git "$DIFFUSION_REF" "$SOURCE_DIR"
checkout_revision https://github.com/Aynekko/Diffusion-MainUI.git "$DIFFUSION_MAINUI_REF" "$SOURCE_DIR/3rd-party/mainui_cpp"
checkout_revision https://github.com/Aynekko/Diffusion-executable.git "$DIFFUSION_EXECUTABLE_REF" "$SOURCE_DIR/3rd-party/game_launch"

# Diffusion inherits a Linux-only malloc header from its Source SDK utility
# layer. The iPhoneOS SDK exposes the same allocation APIs through stdlib.h.
git -C "$SOURCE_DIR" apply --unidiff-zero "$ROOT_DIR/scripts/ios/diffusion-ios.patch"
git -C "$SOURCE_DIR" apply --unidiff-zero "$ROOT_DIR/scripts/ios/diffusion-shaders-ios.patch"
git -C "$SOURCE_DIR" apply --unidiff-zero "$ROOT_DIR/scripts/ios/diffusion-liveness-ios.patch"
git -C "$SOURCE_DIR" apply --unidiff-zero "$ROOT_DIR/scripts/ios/diffusion-wo43-diagnostics-ios.patch"
python3 "$ROOT_DIR/scripts/ios/validate-diffusion-ios-policy.py" "$SOURCE_DIR"

# Refuse to produce an IPA if any shader reachable through the iOS mobile
# profile fails after the exact pinned GL4ES translation used on-device.
bash "$ROOT_DIR/scripts/ios/validate-diffusion-mobile-shaders.sh" "$SOURCE_DIR"

IOS_SDK_PATH=$(xcrun --sdk iphoneos --show-sdk-path)
IOS_CLANG=$(xcrun --sdk iphoneos --find clang)
IOS_CLANGXX=$(xcrun --sdk iphoneos --find clang++)
IOS_AR=$(xcrun --sdk iphoneos --find ar)
IOS_STRIP=$(xcrun --sdk iphoneos --find strip)
IOS_RANLIB=$(xcrun --sdk iphoneos --find ranlib)
IOS_TARGET_FLAGS="--target=aarch64-apple-ios -isysroot$IOS_SDK_PATH -mios-version-min=$IOS_DEPLOYMENT_TARGET -DXASH_IOS=1"

export CC="$IOS_CLANG $IOS_TARGET_FLAGS"
export CXX="$IOS_CLANGXX $IOS_TARGET_FLAGS"
export AR="$IOS_AR"
export STRIP="$IOS_STRIP"
export RANLIB="$IOS_RANLIB"
export CFLAGS="$IOS_TARGET_FLAGS"
export CXXFLAGS="$IOS_TARGET_FLAGS"
export LINKFLAGS="$IOS_TARGET_FLAGS"
export LDFLAGS="$IOS_TARGET_FLAGS"

cd "$SOURCE_DIR"

# Configure every declared subproject so Diffusion's Waf graph is complete.
# The game-specific MainUI is required as well: without it Xash falls back to
# the generic menu and combines that layout with Diffusion's high-resolution
# button artwork.
python3 ./waf configure -T debug --disable-werror
python3 ./waf build --targets=client,server,menu
python3 ./waf install --targets=client,server,menu --destdir="$STAGE_DIR"

CLIENT_DYLIB="$STAGE_DIR/diffusion/bin/client_arm64.dylib"
SERVER_DYLIB="$STAGE_DIR/diffusion/bin/server_arm64.dylib"
MENU_DYLIB="$STAGE_DIR/diffusion/bin/menu_arm64.dylib"

for required_dylib in "$CLIENT_DYLIB" "$SERVER_DYLIB" "$MENU_DYLIB"; do
	if [ ! -f "$required_dylib" ]; then
		echo "Diffusion iOS build did not produce $required_dylib" >&2
		exit 1
	fi

	architectures=$(lipo -archs "$required_dylib")
	case " $architectures " in
		*" arm64 "*) ;;
		*)
			echo "Diffusion dylib is not arm64: $required_dylib ($architectures)" >&2
			exit 1
			;;
	esac
done

mkdir -p "$APP_LIBS_DIR/bin"
cp "$CLIENT_DYLIB" "$APP_LIBS_DIR/bin/client_arm64.dylib"
cp "$SERVER_DYLIB" "$APP_LIBS_DIR/bin/server_arm64.dylib"
cp "$MENU_DYLIB" "$APP_LIBS_DIR/bin/menu_arm64.dylib"

# Keep Diffusion's menu data game-scoped so regular Half-Life continues to use
# its own localization and keyboard descriptions.
mkdir -p "$APP_LIBS_DIR/diffusion/resource"
cp "$SOURCE_DIR/3rd-party/mainui_cpp/translations/gameui_english.txt" \
	"$APP_LIBS_DIR/diffusion/resource/gameui_english.txt"
cp "$SOURCE_DIR/3rd-party/mainui_cpp/gamedir_data/kb_act.lst" \
	"$APP_LIBS_DIR/diffusion/kb_act.lst"
cp "$SOURCE_DIR/3rd-party/mainui_cpp/gamedir_data/kb_def.lst" \
	"$APP_LIBS_DIR/diffusion/kb_def.lst"

# User archives take precedence over the app's normal game directory. Stage
# corrected shaders in the dedicated iOS override tree mounted last by Xash.
mkdir -p "$APP_LIBS_DIR/ios_overrides/diffusion/glsl"
cp -R "$SOURCE_DIR/glsl/." "$APP_LIBS_DIR/ios_overrides/diffusion/glsl/"

echo "Diffusion iOS modules staged from:"
echo "  Diffusion:            $DIFFUSION_REF"
echo "  Diffusion-MainUI:     $DIFFUSION_MAINUI_REF"
echo "  Diffusion-executable: $DIFFUSION_EXECUTABLE_REF"
file "$APP_LIBS_DIR/bin/client_arm64.dylib" "$APP_LIBS_DIR/bin/server_arm64.dylib" "$APP_LIBS_DIR/bin/menu_arm64.dylib"
xcrun vtool -show-build "$APP_LIBS_DIR/bin/client_arm64.dylib"
xcrun vtool -show-build "$APP_LIBS_DIR/bin/server_arm64.dylib"
xcrun vtool -show-build "$APP_LIBS_DIR/bin/menu_arm64.dylib"
