#!/usr/bin/env bash

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

### Enable exit on error ######################################################
set -e


### Sudo wrapper ###############################################################

SUDO=
if which sudo; then
    SUDO=sudo
fi


### Configure apt for non-interactive, headless installation ##################
export DEBIAN_FRONTEND=noninteractive


### Update local apt index ####################################################
$SUDO apt-get update -y


### Make available drawio in headless mode ####################################

# Install drawio

if which drawio; then
    echo "drawio is already installed"
else
    version=26.0.16
    drawio_package=drawio-amd64-${version}.deb
    curl -L -o $drawio_package https://github.com/jgraph/drawio-desktop/releases/download/v${version}/$drawio_package
    $SUDO apt install -y ./$drawio_package
    rm $drawio_package
fi

# Install virtual X-Server
if which xvfb-run; then
    echo "xvfb is already installed"
else
    $SUDO apt-get install -y xvfb
fi


### Install Graphviz ###########################################################

if which dot; then
    echo "Graphviz is already installed"
else
    $SUDO apt-get install -y graphviz
fi


### Install plantuml ###########################################################

if which plantuml; then
    echo "PlantUML is already installed"
else
    $SUDO apt-get install -y plantuml
fi


### Install java ###############################################################

if which java; then
    echo "Java is already installed"
else
    $SUDO apt-get install -y openjdk-11-jre
fi
java --version


### Install mermaid command line tool #########################################

# Install nodejs (brings package manager npm with it)
if which node; then
    echo "nodejs is already installed"
else
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash
    $SUDO apt install -y nodejs
fi
node --version


# Mermaid CLI
if which mmdc; then
    echo "mermaid-cli is already installed"
else
    $SUDO npm install -g @mermaid-js/mermaid-cli
fi
mmdc --version



### Reload environment ########################################################
source ~/.bashrc


### EOF #######################################################################

