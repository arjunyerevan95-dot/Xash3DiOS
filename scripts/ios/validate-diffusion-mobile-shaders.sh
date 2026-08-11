#!/bin/bash

set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
SOURCE_DIR=${1:?usage: validate-diffusion-mobile-shaders.sh DIFFUSION_SOURCE_DIR}
GL4ES_DIR="$ROOT_DIR/3rdparty/gl4es/gl4es"
VALIDATOR=$(command -v glslangValidator || true)

if [ -z "$VALIDATOR" ]; then
	echo "glslangValidator is required for the Diffusion mobile shader gate" >&2
	exit 1
fi

WORK_DIR=$(mktemp -d "${TMPDIR:-/tmp}/diffusion-shader-gate.XXXXXX")
cleanup()
{
	rm -rf -- "$WORK_DIR"
}
trap cleanup EXIT

cc -std=gnu11 -DEGL_NO_X11 \
	-I"$GL4ES_DIR/include" \
	-I"$GL4ES_DIR/src/gl" \
	-I"$GL4ES_DIR/src" \
	-I"$GL4ES_DIR/src/glx" \
	"$ROOT_DIR/scripts/ios/gl4es-shaderconv-dump.c" \
	"$GL4ES_DIR/src/gl/shaderconv.c" \
	"$GL4ES_DIR/src/gl/preproc.c" \
	"$GL4ES_DIR/src/gl/shader_hacks.c" \
	"$GL4ES_DIR/src/gl/string_utils.c" \
	-lm -o "$WORK_DIR/gl4es-shaderconv-dump"

python3 "$ROOT_DIR/scripts/ios/validate-diffusion-mobile-shaders.py" \
	"$SOURCE_DIR" "$WORK_DIR/gl4es-shaderconv-dump" "$VALIDATOR"
