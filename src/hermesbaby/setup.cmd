:: #############################################################################
:: #                                                                           #
:: #   This file is part of hermesbaby - the software engineers' typewriter    #
:: #                                                                           #
:: #   Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)                #
:: #                                                                           #
:: #   https://hermesbaby.github.io                                            #
:: #                                                                           #
:: # - The MIT License (MIT)                                                   #
:: #   when this becomes part of your software                                 #
:: #                                                                           #
:: # - The Creative Commons Attribution-Share-Alike 4.0 International License  #
:: #   (CC BY-SA 4.0) when this is part of documentation, blogs, presentations #
:: #                  or other content                                         #
:: #                                                                           #
:: #############################################################################

:: Wrapper around setup.ps1

:: #############################################################################

:: setup.cmd

@echo off
REM Get the directory of the current script
set script_dir=%~dp0

REM Check if PowerShell script exists in the same directory
if not exist "%script_dir%setup.ps1" (
    echo "Error: setup.ps1 not found in the same directory as the wrapper script!"
    exit /b 1
)

REM Run the PowerShell script from the determined directory
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%script_dir%setup.ps1"

REM Check the exit code of PowerShell script
if %errorlevel% neq 0 (
    echo "Error: PowerShell script failed with exit code %errorlevel%"
    exit /b %errorlevel%
)

echo "Setup process completed successfully."
exit /b 0

:: ### EOF #####################################################################
