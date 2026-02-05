# shellcheck shell=bash

# Make vendored helper libs discoverable in a portable way.
export BATS_LIB_PATH="${BATS_TEST_DIRNAME}/bats/lib${BATS_LIB_PATH:+:${BATS_LIB_PATH}}"

bats_load_library bats-support
bats_load_library bats-assert
bats_load_library bats-file
