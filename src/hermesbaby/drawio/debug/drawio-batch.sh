#!/usr/bin/env bash
set -euo pipefail

# Batch-convert all .drawio files under docs/ to SVGs in out/drawio/, preserving
# relative paths. Designed to mirror the Sphinx conversion flags while running
# outside Sphinx for isolation/debugging.

ROOT_DIR=${ROOT_DIR:-$(pwd)}
DOCS_DIR=${DOCS_DIR:-"${ROOT_DIR}/docs"}
OUT_DIR=${OUT_DIR:-"${ROOT_DIR}/out/drawio"}
DRAWIO_BIN=${DRAWIO_BIN:-$(command -v drawio || true)}
TIMEOUT_SECS=${TIMEOUT_SECS:-10}
SCALE=${SCALE:-1.0}
PAGE_INDEX=${PAGE_INDEX:-0}
FORMAT=${FORMAT:-svg}

if [[ -z "${DRAWIO_BIN}" ]]; then
  echo "drawio binary not found (set DRAWIO_BIN)" >&2
  exit 1
fi

# Start Xvfb if DISPLAY is not set (headless mode)
XVFB_PID=""
if [[ -z "${DISPLAY:-}" ]]; then
  if command -v Xvfb >/dev/null 2>&1; then
    echo "[drawio] Starting Xvfb for headless rendering..."
    Xvfb :99 -screen 0 1920x1080x24 >/dev/null 2>&1 &
    XVFB_PID=$!
    export DISPLAY=:99
    sleep 1  # Give Xvfb time to start
    echo "[drawio] Xvfb running on DISPLAY=${DISPLAY}"
  else
    echo "[drawio] Warning: No DISPLAY set and Xvfb not found. Draw.io may fail." >&2
  fi
fi

# Cleanup function
cleanup() {
  if [[ -n "${XVFB_PID}" ]]; then
    echo "[drawio] Stopping Xvfb (PID ${XVFB_PID})..."
    kill "${XVFB_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

mkdir -p "${OUT_DIR}"

# Clean output directory if desired
if [[ "${CLEAN_OUT:-0}" == "1" ]]; then
  rm -rf "${OUT_DIR:?}"/*
fi

# Create temp files for tracking results
RESULTS_DIR=$(mktemp -d -t drawio-results-XXXXXX)
SUCCESS_LOG="${RESULTS_DIR}/success.log"
FAILURE_LOG="${RESULTS_DIR}/failure.log"
touch "${SUCCESS_LOG}" "${FAILURE_LOG}"

convert_file() {
  local infile="$1"
  local rel
  rel=$(realpath --relative-to="${DOCS_DIR}" "${infile}")
  local stem
  stem="${rel%.drawio}"
  local outfile="${OUT_DIR}/${stem}.${FORMAT}"
  local outdir
  outdir=$(dirname "${outfile}")
  mkdir -p "${outdir}"

  local tmp_profile
  tmp_profile=$(mktemp -d -t drawio-XXXXXX)

  echo "[drawio] Converting ${rel}"
  local start_time
  start_time=$(date +%s)

  if env \
    DRAWIO_DISABLE_UPDATE=1 \
    DRAWIO_DISABLE_AUTOUPDATE=1 \
    DBUS_SESSION_BUS_ADDRESS=disabled \
    NO_AT_BRIDGE=1 \
    timeout "${TIMEOUT_SECS}" "${DRAWIO_BIN}" \
      --export \
      --crop \
      --page-index "${PAGE_INDEX}" \
      --scale "${SCALE}" \
      --format "${FORMAT}" \
      --output "${outfile}" \
      "${infile}" \
      --disable-dev-shm-usage \
      --disable-gpu \
      --js-flags=--max-old-space-size=4096 \
      --disable-renderer-backgrounding \
      --disable-background-timer-throttling \
      --user-data-dir="${tmp_profile}" \
      --disk-cache-dir=/dev/null \
      --disable-application-cache \
      --disable-http-cache \
      --disable-extensions \
      --no-sandbox 2>/dev/null; then
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "[drawio] ✓ ${rel} (${duration}s)"
    echo "${rel}" >> "${SUCCESS_LOG}"
  else
    local exit_code=$?
    echo "[drawio] ✗ ${rel} (exit code: ${exit_code})"
    echo "${rel}" >> "${FAILURE_LOG}"
  fi

  rm -rf "${tmp_profile}"
}

export -f convert_file
export DOCS_DIR OUT_DIR DRAWIO_BIN TIMEOUT_SECS SCALE PAGE_INDEX FORMAT SUCCESS_LOG FAILURE_LOG

# Count total files
total_files=$(find "${DOCS_DIR}" -type f -name '*.drawio' | wc -l)
echo "[drawio] Found ${total_files} .drawio files to convert"
echo ""

find "${DOCS_DIR}" -type f -name '*.drawio' -print0 | sort -z | xargs -0 -n1 -P "${JOBS:-4}" bash -c 'convert_file "$0"'

# Print summary
echo ""
echo "============================================"
echo "Conversion Summary"
echo "============================================"
success_count=$(wc -l < "${SUCCESS_LOG}")
failure_count=$(wc -l < "${FAILURE_LOG}")
echo "Total files:    ${total_files}"
echo "Successful:     ${success_count}"
echo "Failed:         ${failure_count}"
echo ""

if [[ ${failure_count} -gt 0 ]]; then
  echo "Failed files:"
  cat "${FAILURE_LOG}"
  echo ""
fi

echo "Outputs in: ${OUT_DIR}"
rm -rf "${RESULTS_DIR}"

exit ${failure_count}
