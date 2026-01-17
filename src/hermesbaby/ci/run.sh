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


# Make sure that there is a .hermesbaby file even the project doesn't have one
# Also make sure that the .hermesbaby file contains most recent parameters
hb configure --update


### DISCOVER DOCUMENTS ########################################################

HERMESBABY_FILES=()

discover_documents() {
    echo ">>> Discovering HermesBaby project files in workspace"

    # Search for .hermesbaby files in a simple and robust manner. Do not use any environment variables
    mapfile -t HERMESBABY_FILES < <( \
        find . \
            \( -path ./.git \
                -o -path '*/_attachments' \
                -o -path '*/_figures' \
                -o -path '*/_listings' \
            \) \
            -prune \
            -o -name .hermesbaby -print \
            | awk '{ depth = gsub("/", "/", $0); print depth, $0 }' \
            | sort -nr -k1,1 -k2,2 \
            | awk '{ $1=""; sub(/^ /,""); print }'
    )

    # Print discovered files
    echo "Discovered ${#HERMESBABY_FILES[@]} HermesBaby project(s):"
    for rel in "${HERMESBABY_FILES[@]}"; do
        echo " - ${rel#./}"
    done
}


### BUILD #####################################################################

build() {
    # Also make sure that the .hermesbaby file contains most recent parameters
    hb configure --update

    # Inject hermesbaby project configuration into environment

    # Strip possible trailing \r from each line
    sed -i 's/\r$//' .hermesbaby

    # Apply the .hermesbaby file to the environment only for this function
    (
        # Inject into environment and make it available across
        source .hermesbaby

        mkdir -p "$CONFIG_BUILD__DIRS__BUILD"/html
        touch "$CONFIG_BUILD__DIRS__BUILD"/html/index.html
        ls "$CONFIG_BUILD__DIRS__BUILD"/html/

        # Build HTML
        hb html

        # Build optionally PDF and embed into HTML
        # The switch CONFIG_PUBLISH__CREATE_AND_EMBED_PDF may come from
        # - the .hermesbaby file
        # - the build_parameters.json file
        if [ "${CONFIG_PUBLISH__CREATE_AND_EMBED_PDF:-n}" == "y" ]; then
            echo "### Building HermesBaby project to PDF in $PWD"
            hb pdf
            pdf_file=$(basename $(ls "$CONFIG_BUILD__DIRS__BUILD"/pdf/*.tex) .tex).pdf
            cp "$CONFIG_BUILD__DIRS__BUILD"/pdf/$pdf_file "$CONFIG_BUILD__DIRS__BUILD"/html
        fi
    )
}


### PACKAGE ###################################################################

package() {

    # Apply the .hermesbaby file to the environment only for this function
    (
        source .hermesbaby

        # Optional create a tarball which is embedded into the published site
        if [ "${CONFIG_PUBLISH__TARBALL:-n}" == "y" ]; then
            echo "Creating tarball site.tar.gz and injecting it into $CONFIG_BUILD__DIRS__BUILD/html.tar.gz"
            tar -czf \
                $CONFIG_BUILD__DIRS__BUILD/site.tar.gz \
                -C $CONFIG_BUILD__DIRS__BUILD/html \
                .
            mv $CONFIG_BUILD__DIRS__BUILD/site.tar.gz $CONFIG_BUILD__DIRS__BUILD/html/
        fi

        tar -czf \
            $CONFIG_BUILD__DIRS__BUILD/html.tar.gz \
            -C $CONFIG_BUILD__DIRS__BUILD/html \
            .
    )
}


### PUBLISH ###################################################################

publish () {
    local hermesbaby_file=$1

    # Apply the .hermesbaby file to the environment only for this function
    (
        source .hermesbaby

        # Check if publishing should be skipped
        if [ "${CONFIG_PUBLISH_SKIP_PUBLISH:-n}" == "y" ]; then
            echo "Publishing is skipped due to CONFIG_PUBLISH_SKIP_PUBLISH being set to 'y'."
            exit 0
        fi

        # Append the project name coming from the .hermesbaby file in case we are not in the root folder
        local document="$HERMES_PUBLISH_REPO"
        if [ "$hermesbaby_file" != "./.hermesbaby" ]; then
            document+="-${CONFIG_PUBLISH__REPO}"
        fi

        # Publish to hermes ( @see https://github.com/hermesbaby/hermes )
        curl --fail-with-body -k \
            -X PUT \
            -H "Authorization: Bearer $HERMES_API_TOKEN" \
            -F "file=@$CONFIG_BUILD__DIRS__BUILD/html.tar.gz" \
            $HERMES_PUBLISH_BASE_URL/$HERMES_PUBLISH_PROJECT/$document/$HERMES_PUBLISH_BRANCH
    )
}


### EXECUTION FLOW ############################################################

loop_over() {
    local step=$1
    for rel in "${HERMESBABY_FILES[@]}"; do
        pushd "$(dirname "$rel")" > /dev/null
        echo ">>> Running step '$step' for project: ${rel#./}"
        $step $rel
        popd > /dev/null
    done
}

discover_documents
loop_over build
loop_over package
loop_over publish

### END OF WORKFLOW ###########################################################

exit 0


### EOF #######################################################################
