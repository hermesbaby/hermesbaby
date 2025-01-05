#############################################################################
#                                                                           #
#   This file is part of hermesbaby - the software engineers' typewriter    #
#                                                                           #
#   Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)                #
#                                                                           #
#   https://hermesbaby.github.io                                            #
#                                                                           #
# - The MIT License (MIT)                                                   #
#   when this becomes part of your software                                 #
#                                                                           #
# - The Creative Commons Attribution-Share-Alike 4.0 International License  #
#   (CC BY-SA 4.0) when this is part of documentation, blogs, presentations #
#                  or other content                                         #
#                                                                           #
#############################################################################

# Things to be done right after the container is created.

# Let's check this file from time to time for stuff which can move to the container creation.

### STUFF ###################################################################

# TODO: Add installation steps from :ref:`sec_docs_as_code_prerequisites`

# Get the directory where the script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Get all files matching the pattern scoopfile*.json in the script's directory
$scoopFiles = Get-ChildItem -Path $scriptDir -Filter "scoopfile*.json"

# Iterate over each file and call the scoop import command
foreach ($file in $scoopFiles) {
    scoop import $file.FullName
}


### EOF #####################################################################
