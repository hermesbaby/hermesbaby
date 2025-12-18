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

eval $(hb ci config-to-env build_parameters.json)


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

# Build always HTML
hb html

# Build optionally PDF and embed into HTML
# The switch CONFIG_PUBLISH__CREATE_AND_EMBED_PDF may come from
# - the .hermesbaby file
# - the build_parameters.json file
if [ "${CONFIG_PUBLISH__CREATE_AND_EMBED_PDF:-}" == "y" ]; then
    hb pdf
    pdf_file=$(basename $(ls "$CONFIG_BUILD__DIRS__BUILD"/pdf/*.tex) .tex).pdf
    cp "$CONFIG_BUILD__DIRS__BUILD"/pdf/$pdf_file "$CONFIG_BUILD__DIRS__BUILD"/html
fi


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
