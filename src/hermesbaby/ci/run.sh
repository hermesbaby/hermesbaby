#!/usr/bin/env bash

################################################################
#                                                              #
#  This file is part of HermesBaby                             #
#                       the software engineer's typewriter     #
#                                                              #
#      https://github.com/hermesbaby                           #
#                                                              #
#  Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)    #
#                                                              #
#  License(s)                                                  #
#                                                              #
#  - MIT for contents used as software                         #
#  - CC BY-SA-4.0 for contents used as method or otherwise     #
#                                                              #
################################################################

###############################################################################
### RUN #######################################################################
###############################################################################

### Get out of detached HEAD state. ###########################################

# The documentation generator shall retrieve the git information and insert it
# into the documentation. Therefore this step is necessary.

# Jenkins has set environment variable "branch" to the branch name.
if [ -n "$branch" ]; then
    git checkout "$branch"
fi

### Do the work in the printshop ##############################################

# Fail and exist immediately on unset environment variables and/or broken pipes
set -euo pipefail

### Process userBuildConfig.json ##############################################

source <(python3 "$(dirname "$0")/userBuildConfig.py")


### DELETE publication when branch is deleted and exit  #######################

if [[ "${trigger:-}" == "REF DELETED" ]]; then
    echo "Detected REF DELETED trigger; skipping build/package/publish steps."
    curl -k \
        -X DELETE \
        -H "Authorization: Bearer $SECRET_HERMES_API_TOKEN" \
        https://docs.your-company.com/projects/$gitProject/$componentName/$branch
    exit 0
fi


### BUILD #####################################################################

hb html


### PACKAGE and PUBLISH #######################################################

# This section relies on the injection of the following environment variables:
#
# -- From Jenkins vault --
# export SECRET_HERMES_API_TOKEN
#
# -- From job configuration --
# export branch
# export componentName
# export gitProject


if [ -f .hermesbaby ]; then
    # In-place: strip trailing \r from each line
    sed -i 's/\r$//' .hermesbaby
fi

# Get CONFIG_BUILD__DIRS__BUILD
[ -f .hermesbaby ] && source .hermesbaby || CONFIG_BUILD__DIRS__BUILD=out/docs

# PACKAGE

tar -czf \
    $CONFIG_BUILD__DIRS__BUILD/html.tar.gz \
    -C $CONFIG_BUILD__DIRS__BUILD/html \
    .

# PUBLISH

curl -k \
    -X PUT \
    -H "Authorization: Bearer $SECRET_HERMES_API_TOKEN" \
    -F "file=@$CONFIG_BUILD__DIRS__BUILD/html.tar.gz" \
    https://docs.your-company.com/projects/$gitProject/$componentName/$branch


### END OF WORKFLOW ###########################################################

exit 0


### EOF #######################################################################
