#!/bin/env bash

### EXECUTION CONTROL #########################################################

# Enable strict error handling and debugging
set -euxo pipefail

# In case CTLR-C the entire script is aborted
trap "exit" INT

# Log all output to a temporary log file
log_file=$(mktemp /tmp/$(basename "$0")-XXXXXX.log)
exec > >(tee -a "$log_file") 2>&1
echo "Logging to file: $log_file"


### PREAMBLE ##################################################################

purspose="Test that CI can create and embed PDF into HTML package"
echo "Starting test: $purspose"


### Execute ###################################################################

source /d/github/hermesbaby/hermesbaby/.venv/Scripts/activate

# Create test data
cd $(mktemp -d)
python -m hermesbaby new --template hello .
git init .
git add .
git commit -m "1"
echo '{ "PUBLISH__CREATE_AND_EMBED_PDF": "y" }' | tee build_parameters.json

# Item-under-test:
/d/github/hermesbaby/hermesbaby/src/hermesbaby/ci/run.sh


### Evaluate ##################################################################

ls ./out/docs/html.tar.gz && echo "PASS: HTML generated" || echo "FAIL: HTML missing"
tar -tzf ./out/docs/html.tar.gz | grep the_default_title.pdf && echo "PASS: PDF present in package" || echo "FAIL: PDF missing in package"


### Summary ###################################################################

echo "Test complete: $purspose"
exit 0

### EOF #######################################################################
