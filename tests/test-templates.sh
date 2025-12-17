#!/bin/bash

### Configuration #############################################################

commands="html pdf"
templates_priority="zero hello log-ledger"

# Enable dry run by uncommenting the following line
#ECHO="echo dry-run: "
ECHO=""


### Execution control #########################################################

set -uo pipefail

# In case CTLR-C the entire script is aborted
trap "exit" INT

# Print all not only to the console but also to the log file.
# So the output shall be seen on the console as well as saved to a file for later inspection.
# The temporary log is created for each test run anew.
log_file=$(mktemp /tmp/hermesbaby-test-templates-log-XXXXXX.txt)
exec > >(tee -a "$log_file") 2>&1
echo "Logging to file: $log_file"


### EXECUTION #################################################################

templates=$(poetry run python -m hermesbaby new --list-templates | grep -E ' - ' | sed 's/ *- //g')

# Ensure priority templates are tested first
templates="$templates_priority $templates"
templates=$(echo "$templates" | tr ' ' '\n' | awk '!seen[$0]++' | tr '\n' ' ')

echo -e "Templates to test in that order:\n$templates"
echo
echo -e "Commands to test in that order:\n$commands"

# Loop through each template and run the commands
# Exit immediately if a command exits with a non-zero status

# Activate the virtual environment of this dev project:
source "$(poetry env info --path)/Scripts/activate"

set -e

results=""
for template in $templates ; do
    project_dir=$(mktemp -d)

    echo "========================================================="
    echo "Testing template: $template"
    echo "Directory: $project_dir"

    $ECHO python -m hermesbaby new --template "$template" "$project_dir"

    if [ "$template" = "log-ledger" ] ; then
        cd "$project_dir"
        ./mk-my-day.sh --skip-open-vscode
    fi

    for command in $commands; do
        echo "---------------------------------------------------------"
        echo "  Building command: $command"
        cd "$project_dir"
        ($ECHO python -m hermesbaby "$command") && result=PASSED || result=FAILED

        ## Create a line with template, command and result:
        echo "Test result for template '$template' with command '$command': $result"
        ## Append that line to the overall results variable:
        results="$results\nTest result for template '$template' with command '$command': $result"
    done
done

echo
echo "========================================================="
echo -e "Test results summary:$results"
echo "Log file saved at: $log_file"
echo "========================================================="
echo


### EOF #######################################################################
