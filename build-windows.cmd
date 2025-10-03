@echo off

REM ################################################################
REM #                                                              #
REM #  This file is part of HermesBaby                             #
REM #                       the software engineer's typewriter     #
REM #                                                              #
REM #      https://github.com/hermesbaby                           #
REM #                                                              #
REM #  Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)    #
REM #                                                              #
REM #  License(s)                                                  #
REM #                                                              #
REM #  - MIT for contents used as software                         #
REM #  - CC BY-SA-4.0 for contents used as method or otherwise     #
REM #                                                              #
REM ################################################################

REM Build script for Windows binary distribution using PyInstaller

echo Building HermesBaby binary for Windows...

REM Check if we're in the correct directory
if not exist "hermesbaby.spec" (
    echo Error: hermesbaby.spec not found. Please run this script from the project root.
    exit /b 1
)

REM Install dependencies if not already installed
echo Installing dependencies...
poetry install --with dev

REM Clean previous builds
echo Cleaning previous builds...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist

REM Build the binary
echo Building binary with PyInstaller...
poetry run pyinstaller hermesbaby.spec

REM Check if binary was created
if exist "dist\hermesbaby.exe" (
    echo Binary created successfully at: dist\hermesbaby.exe

    REM Test the binary
    echo Testing binary...
    dist\hermesbaby.exe --version
    if %errorlevel% equ 0 (
        echo Binary test successful!
    ) else (
        echo Warning: Binary test failed
        exit /b 1
    )

    REM Create archive
    echo Creating archive...
    cd dist
    powershell -Command "Compress-Archive -Path hermesbaby.exe -DestinationPath hermesbaby-windows-x64.zip -Force"
    echo Archive created: dist\hermesbaby-windows-x64.zip
    cd ..

) else (
    echo Error: Binary creation failed
    exit /b 1
)

echo Windows binary build completed successfully!
