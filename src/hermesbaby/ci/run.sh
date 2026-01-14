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

### Do the work in the printshop ##############################################

# Fail and exist immediately on unset environment variables and/or broken pipes
set -euo pipefail

### NECESSARY ENVIRONMENT VARIABLES ###########################################

# This script relies on the injection of the following environment variables:
#
# -- From Jenkins vault --
# export HERMES_API_TOKEN
#
#
# From SCM trigger
# export HERMES_SCM_TRIGGER
#
# -- From job configuration --
# export HERMESBABY_CI_OPTIONS_JSON_PATH
# export HERMES_BASE_URL
# export HERMES_PUBLISH_PROJECT
# export HERMES_PUBLISH_REPO
# export HERMES_PUBLISH_BRANCH


### Inject hermesbaby project configuration into environment ##################

# Make sure that there is a .hermesbaby file even the project doesn't have one
# Also make sure that the .hermesbaby file contains most recent parameters
hb configure --update

# Strip possible trailing \r from each line
sed -i 's/\r$//' .hermesbaby

# Inject into environment
source .hermesbaby


### Inject CI options into environment ########################################
# The build may have injected a file with build parameteres.
# Those parameters may even override the project configuration parameters.
# Note here: the parameters in the json-file are prefixed with CONFIG_
# as they begin win the .hermesbaby file. So do not use 'CONFIG_' in the
# json file.
# This prefixing has security aspects as well. By this there is no chance to
# override the environment variables used in the publish step

echo "Populating environment from CI options JSON file at: $HERMESBABY_CI_OPTIONS_JSON_PATH"
eval $(hb ci config-to-env "$HERMESBABY_CI_OPTIONS_JSON_PATH")


### BUILD #####################################################################

# Build always HTML
hb html

# Build optionally PDF and embed into HTML
# The switch CONFIG_PUBLISH__CREATE_AND_EMBED_PDF may come from
# - the .hermesbaby file
# - the build_parameters.json file
if [ "${CONFIG_PUBLISH__CREATE_AND_EMBED_PDF:-n}" == "y" ]; then
    hb pdf
    pdf_file=$(basename $(ls "$CONFIG_BUILD__DIRS__BUILD"/pdf/*.tex) .tex).pdf
    cp "$CONFIG_BUILD__DIRS__BUILD"/pdf/$pdf_file "$CONFIG_BUILD__DIRS__BUILD"/html
fi


### PACKAGE and PUBLISH #######################################################

# PACKAGE

tar -czf \
    $CONFIG_BUILD__DIRS__BUILD/html.tar.gz \
    -C $CONFIG_BUILD__DIRS__BUILD/html \
    .


# PUBLISH

# Check if publishing should be skipped
if [ "${CONFIG_PUBLISH_SKIP_PUBLISH:-n}" == "y" ]; then
    echo "Publishing is skipped due to CONFIG_PUBLISH_SKIP_PUBLISH being set to 'y'."
    exit 0
fi

# Publish to hermes ( @see https://github.com/hermesbaby/hermes )
curl -k \
    -X PUT \
    -H "Authorization: Bearer $HERMES_API_TOKEN" \
    -F "file=@$CONFIG_BUILD__DIRS__BUILD/html.tar.gz" \
    $HERMES_PUBLISH_BASE_URL/$HERMES_PUBLISH_PROJECT/$HERMES_PUBLISH_REPO/$HERMES_PUBLISH_BRANCH


### END OF WORKFLOW ###########################################################

exit 0


### EOF #######################################################################
