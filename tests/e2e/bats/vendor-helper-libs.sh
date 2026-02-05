#!/usr/bin/env bash
set -euo pipefail

# Where your vendored bats lives today
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIB_DIR="$ROOT_DIR/bats/lib"

# Pinned versions (stable + reproducible)
BATS_SUPPORT_VERSION="0.3.0"
BATS_ASSERT_VERSION="2.2.4"
BATS_FILE_VERSION="0.4.0"

mkdir -p "$LIB_DIR"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fetch_and_extract_tar_gz() {
  local url="$1"
  local outdir="$2"
  local strip="$3"

  echo "Downloading: $url"
  curl -fsSL "$url" -o "$tmp/pkg.tgz"
  rm -rf "$outdir"
  mkdir -p "$outdir"
  tar -xzf "$tmp/pkg.tgz" -C "$outdir" --strip-components="$strip"
}

# bats-support
fetch_and_extract_tar_gz \
  "https://github.com/bats-core/bats-support/archive/refs/tags/v${BATS_SUPPORT_VERSION}.tar.gz" \
  "$LIB_DIR/bats-support" \
  1

# bats-assert
fetch_and_extract_tar_gz \
  "https://github.com/bats-core/bats-assert/archive/refs/tags/v${BATS_ASSERT_VERSION}.tar.gz" \
  "$LIB_DIR/bats-assert" \
  1

# bats-file
fetch_and_extract_tar_gz \
  "https://github.com/bats-core/bats-file/archive/refs/tags/v${BATS_FILE_VERSION}.tar.gz" \
  "$LIB_DIR/bats-file" \
  1

echo
echo "Vendored helper libs into: $LIB_DIR"
ls -1 "$LIB_DIR" | sed 's/^/  - /'
