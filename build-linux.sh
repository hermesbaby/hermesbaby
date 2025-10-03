#!/bin/bash

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

# Build script for Linux binary distribution using PyInstaller

set -e

echo "Building HermesBaby binary for Linux..."

# Check if we're in the correct directory
if [ ! -f "hermesbaby.spec" ]; then
    echo "Error: hermesbaby.spec not found. Please run this script from the project root."
    exit 1
fi

# Install dependencies if not already installed
echo "Installing dependencies..."
poetry install --with dev

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/

# Build the binary
echo "Building binary with PyInstaller..."
poetry run pyinstaller hermesbaby.spec

# Check if binary was created
if [ -f "dist/hermesbaby" ]; then
    echo "Binary created successfully at: dist/hermesbaby"

    # Make it executable
    chmod +x dist/hermesbaby

    # Test the binary
    echo "Testing binary..."
    if ./dist/hermesbaby --version; then
        echo "Binary test successful!"
    else
        echo "Warning: Binary test failed"
        exit 1
    fi

    # Create archive
    echo "Creating archive..."
    cd dist
    tar -czf hermesbaby-linux-x64.tar.gz hermesbaby
    echo "Archive created: dist/hermesbaby-linux-x64.tar.gz"

else
    echo "Error: Binary creation failed"
    exit 1
fi

echo "Linux binary build completed successfully!"
