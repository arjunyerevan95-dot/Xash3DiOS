#!/bin/bash

. scripts/lib.sh

cd "$GITHUB_WORKSPACE" || die

IOS_BUNDLE_VERSION=${GITHUB_RUN_NUMBER:-2}
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion $IOS_BUNDLE_VERSION" \
	engine/platform/ios/bundle/Info.plist || die

git -C 3rdparty/nanogl apply --check --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/nanogl-large-primitive.patch" || die
git -C 3rdparty/nanogl apply --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/nanogl-large-primitive.patch" || die
GL4ES_REF=${GL4ES_REF:-81547d986798e876de8b434193920b606a72363f}
GL4ES_ACTUAL_REF=$(git -C 3rdparty/gl4es/gl4es rev-parse HEAD) || die
if [ "$GL4ES_ACTUAL_REF" != "$GL4ES_REF" ]; then
	echo "Expected GL4ES $GL4ES_REF, got $GL4ES_ACTUAL_REF" >&2
	exit 1
fi
git -C 3rdparty/gl4es/gl4es apply --check --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/gl4es-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/gl4es-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/gl4es-drawable-bridge-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/gl4es-drawable-bridge-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check --unidiff-zero --ignore-space-change --ignore-whitespace "$GITHUB_WORKSPACE/scripts/ios/gl4es-uint-elements-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --unidiff-zero --ignore-space-change --ignore-whitespace "$GITHUB_WORKSPACE/scripts/ios/gl4es-uint-elements-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-index-trace-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-index-trace-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo49-topology-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo49-topology-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo49-transform-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo49-transform-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo49-texture-unit-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo49-texture-unit-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo52-material-trace-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo52-material-trace-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo52-trace-cap-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo52-trace-cap-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo56-texture-array-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo56-texture-array-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo56-production-array-admission-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo56-production-array-admission-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply --check "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo56-provider-lifecycle-ios.patch" || die
git -C 3rdparty/gl4es/gl4es apply "$GITHUB_WORKSPACE/scripts/ios/gl4es-wo56-provider-lifecycle-ios.patch" || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-drawable-bridge.py" \
	"$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/SDL" \
	"$GITHUB_WORKSPACE/3rdparty/gl4es/gl4es" --self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-uint-elements.py" \
	"$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/3rdparty/gl4es/gl4es" --self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-index-trace.py" \
	"$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/3rdparty/gl4es/gl4es" --self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-wo49-topology.py" \
	"$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/3rdparty/gl4es/gl4es" \
	--gl4es-only --self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-wo49-transform.py" \
	"$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/3rdparty/gl4es/gl4es" \
	--gl4es-only --self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-wo49-texture-unit.py" \
	"$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/3rdparty/gl4es/gl4es" \
	--self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-wo52-material-trace.py" \
	"$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/3rdparty/gl4es/gl4es" \
	--gl4es-only --self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-texture-array.py" \
	"$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/3rdparty/gl4es/gl4es" \
	--self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-provider-lifecycle.py" \
	"$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/3rdparty/gl4es/gl4es" \
	--self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-selftest-boot.py" \
	"$GITHUB_WORKSPACE" --self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-ordinary-bootstrap.py" \
	"$GITHUB_WORKSPACE" --self-test || die
python3 "$GITHUB_WORKSPACE/scripts/ios/validate-ios-renderer-contract.py" \
	"$GITHUB_WORKSPACE" --self-test || die
mkdir -p build || die
cc -std=gnu11 -DNANOGL_MANGLE_PREPEND=1 -DREF_DLL=1 \
	-I3rdparty/nanogl -I3rdparty/nanogl/GL \
	3rdparty/nanogl/tests/test_batch.c \
	3rdparty/nanogl/nanogl.c \
	3rdparty/nanogl/nanoWrap.c \
	-o build/nanogl-batch-test || die
./build/nanogl-batch-test || die

./waf configure --enable-lto --ios build install --destdir=build/ios || die_configure

cp -vr /Library/Frameworks/SDL2.framework ./build

pushd hlsdk || die
mkdir -p ../build/ios/libs || die
cmake -DCMAKE_SYSTEM_NAME=iOS -DCMAKE_OSX_DEPLOYMENT_TARGET=12.0 -DCMAKE_INSTALL_PREFIX=$(realpath ../build/ios/libs) -DCMAKE_BUILD_TYPE=Debug -B build -S .
cmake --build build --target install || die
popd || die

./scripts/ios/builddiffusion.sh || die

./scripts/ios/createipa.sh

mkdir -p artifacts/
mv "build/xash3d.ipa" "artifacts/xash3d-fwgs-ios-arm64.ipa"
