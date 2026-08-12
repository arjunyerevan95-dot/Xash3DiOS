#!/bin/bash

cd "$GITHUB_WORKSPACE" || exit 1

SDL_REF=${SDL_REF:-5d249570393f7a37e037abf22cd6012a4cc56a71}
git clone https://github.com/libsdl-org/SDL -b "release-$SDL_VERSION"
git -C SDL checkout --detach "$SDL_REF" || exit 1

SDL_ACTUAL_REF=$(git -C SDL rev-parse HEAD) || exit 1
if [ "$SDL_ACTUAL_REF" != "$SDL_REF" ]; then
	echo "Expected SDL $SDL_REF, got $SDL_ACTUAL_REF" >&2
	exit 1
fi

git -C SDL apply --check --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/sdl2-display-audit-ios.patch" || exit 1
git -C SDL apply --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/sdl2-display-audit-ios.patch" || exit 1
git -C SDL apply --check --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/sdl2-wo43-diagnostics-ios.patch" || exit 1
git -C SDL apply --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/sdl2-wo43-diagnostics-ios.patch" || exit 1
git -C SDL apply --check -p3 --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/sdl2-wo43-phase-b-correction-ios.patch" || exit 1
git -C SDL apply -p3 --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/sdl2-wo43-phase-b-correction-ios.patch" || exit 1
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-display-audit.py" "$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/SDL" || exit 1

cd SDL/Xcode/SDL || exit 1
xcodebuild -scheme xcFramework-iOS -target xcFramework-iOS build -configuration Release
sudo cp -vr Products/SDL2.xcframework/ios-arm64/SDL2.framework /Library/Frameworks

cd "$GITHUB_WORKSPACE" || exit 1

git clone https://github.com/FWGS/hlsdk-portable hlsdk -b mobile_hacks --depth=1
