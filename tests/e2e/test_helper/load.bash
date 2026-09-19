# shellcheck shell=bash

# Make vendored helper libs discoverable in a portable way.
export BATS_LIB_PATH="${BATS_TEST_DIRNAME}/bats/lib${BATS_LIB_PATH:+:${BATS_LIB_PATH}}"

bats_load_library bats-support
bats_load_library bats-assert
bats_load_library bats-file

# `assert_files_equal'/`assert_files_not_equal' from bats-file compare files
# byte-for-byte, so they fail on files that only differ in line endings
# (e.g. LF vs. CRLF). The variants below normalize line endings before
# comparing.
#
# Globals:
#   BATSLIB_FILE_PATH_REM
#   BATSLIB_FILE_PATH_ADD
# Arguments:
#   $1 - 1st path
#   $2 - 2nd path
# Returns:
#   0 - named files are the same, ignoring line endings
#   1 - otherwise
# Outputs:
#   STDERR - details, on failure
assert_files_equal_ignore_eol() {
  local -r file1="$1"
  local -r file2="$2"
  if ! diff -q <(tr -d '\r' <"$file1") <(tr -d '\r' <"$file2") >/dev/null ; then
    local -r rem="${BATSLIB_FILE_PATH_REM-}"
    local -r add="${BATSLIB_FILE_PATH_ADD-}"
    batslib_print_kv_single 4 'path' "${file1/$rem/$add}" 'path' "${file2/$rem/$add}" \
      | batslib_decorate 'files are not the same (ignoring line endings)' \
      | fail
  fi
}

# This function is the logical complement of `assert_files_equal_ignore_eol'.
#
# Globals:
#   BATSLIB_FILE_PATH_REM
#   BATSLIB_FILE_PATH_ADD
# Arguments:
#   $1 - 1st path
#   $2 - 2nd path
# Returns:
#   0 - named files differ, ignoring line endings
#   1 - otherwise
# Outputs:
#   STDERR - details, on failure
assert_files_not_equal_ignore_eol() {
  local -r file1="$1"
  local -r file2="$2"
  if diff -q <(tr -d '\r' <"$file1") <(tr -d '\r' <"$file2") >/dev/null ; then
    local -r rem="${BATSLIB_FILE_PATH_REM-}"
    local -r add="${BATSLIB_FILE_PATH_ADD-}"
    batslib_print_kv_single 4 'path' "${file1/$rem/$add}" 'path' "${file2/$rem/$add}" \
      | batslib_decorate 'files are the same (ignoring line endings)' \
      | fail
  fi
}
