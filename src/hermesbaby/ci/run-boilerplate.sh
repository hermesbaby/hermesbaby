#!/usr/bin/env bash

###############################################################################
### RUN #######################################################################
###############################################################################

# Fail and exist immediately on unset environment variables and/or broken pipes
set -euo pipefail


### Get out of detached HEAD state. ###########################################

# The documentation generator shall retrieve the git information and insert it
# into the documentation. Therefore this step is necessary.

# Jenkins has set environment variable "branch" to the branch name.
if [ -n "$branch" ]; then
    git checkout "$branch"
fi


### PROCESS build/your-build-config.json ######################################

export HERMESBABY_CI_OPTIONS_JSON_PATH="build/your-build-config.json"
echo "Populating environment from CI options JSON file at: $HERMESBABY_CI_OPTIONS_JSON_PATH"
eval $(hb ci config-to-env "$HERMESBABY_CI_OPTIONS_JSON_PATH")


### Optionally install hermesbaby from specific branch ########################

# Used for canary/testing builds of hermesbaby itself.
#
# So it can be injected by an entry in the your-build-config.json:
# { "HERMESBABY_USE_BRANCH": "feature/xyz" }

if [ -n "${CONFIG_HERMESBABY_USE_BRANCH:-}" ]; then
    echo "Updating hermesbaby installation to branch: $CONFIG_HERMESBABY_USE_BRANCH"

    commit_hash=$(curl -s "https://api.github.com/repos/hermesbaby/hermesbaby/branches/$CONFIG_HERMESBABY_USE_BRANCH" | jq -r .commit.sha)
    echo "Resolved branch '$CONFIG_HERMESBABY_USE_BRANCH' to commit hash: $commit_hash"

    pipx install --force git+https://github.com/hermesbaby/hermesbaby.git@"$CONFIG_HERMESBABY_USE_BRANCH"
else
    echo "Updating hermesbaby installation to latest version from pip index"
    pipx upgrade hermesbaby
fi

pipx ensurepath
hb --version
hb ci install-tools


### RUN WORKFLOW EMBEDDED IN HERMESBABY #######################################

# Let hermesbaby handle the CI workflow.
# It is implemented in https://github.com/hermesbaby/hermesbaby/blob/main/src/hermesbaby/ci/run.sh

# This section relies on the injection of the following environment variables:
#
# -- From Jenkins vault --
# export YOUR_ENV_VARIABLE_CARRYING_THE_HERMES_API_TOKEN
#
# -- From job configuration --
# export YOUR_ENV_VARIABLE_CARRYING_THE_BRANCH_NAME
# export YOUR_ENV_VARIABLE_CARRYING_THE_REPO_NAME
# export YOUR_ENV_VARIABLE_CARRYING_THE_PROJECT_OR_ORGANIZATION_NAME

# Interface YOUR-CI_ENVIRONMENT <-> hermesbaby / hermes:
export HERMES_API_TOKEN="$YOUR_ENV_VARIABLE_CARRYING_THE_HERMES_API_TOKEN"
export HERMES_PUBLISH_BASE_URL="https://docs.your-company.domain/root-docs"
export HERMES_PUBLISH_PROJECT="$YOUR_ENV_VARIABLE_CARRYING_THE_PROJECT_OR_ORGANIZATION_NAME"
export HERMES_PUBLISH_REPO="$YOUR_ENV_VARIABLE_CARRYING_THE_REPO_NAME"
export HERMES_PUBLISH_BRANCH="$YOUR_ENV_VARIABLE_CARRYING_THE_BRANCH_NAME"

hb ci run


### END OF WORKFLOW ###########################################################

exit 0


### EOF #######################################################################
