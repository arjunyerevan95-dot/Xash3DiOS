#!/bin/bash

. scripts/lib.sh

cd "$GITHUB_WORKSPACE" || die

git -C 3rdparty/nanogl apply --check --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/nanogl-large-primitive.patch" || die
git -C 3rdparty/nanogl apply --unidiff-zero "$GITHUB_WORKSPACE/scripts/ios/nanogl-large-primitive.patch" || die
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
