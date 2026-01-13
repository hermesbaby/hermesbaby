<!---
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
-->

# Sphinx Contrib PreAndPostbuild

Motivation:

- `sphinx-autobuild` lacks of ability of a post-build-action, has an option `--pre-build COMMAND`, though
- `sphinx-build` lacks of pre- and also post-build.

With PreAndPostbuild you have a common way.

## Output Logging

The extension automatically captures and logs all output from the executed programs to three separate log files:

- `<sanitized-name>_stdout.log` - Contains only stdout output
- `<sanitized-name>_stderr.log` - Contains only stderr output
- `<sanitized-name>_console.log` - Contains combined stdout and stderr output as they appeared on the console

The log files are created in the working directory specified by `cwd`, or in the output directory if `cwd` is not specified. The name is sanitized by replacing special characters with underscores and converting to lowercase.

Example how to configure n `conf.py`:

```
extensions.append('pre_post_build')

# Configuration for pre and post build programs
pre_post_build_programs = {
    'pre': [
        {
            'name': 'Pre HTML Program',
            'builder': 'html',
            'program': '/path/to/your/pre_html/program',
            'args': ['--output-dir', '$outputdir', '--source-dir', '$sourcedir', '--config-dir', '$configdir'],
            'order': 1,  # Optional order key to ensure the order of execution
            'severity': 'info',  # Optional severity key
            'environment': [{'name': 'OUTPUT_DIR', 'value': '$outputdir'}, {'name': 'SOURCE_DIR', 'value': '$sourcedir'}, {'name': 'CONFIG_DIR', 'value': '$configdir'}],  # Optional environment variables
            'cwd': '$outputdir'  # Use the output directory as working directory
        },
        {
            'name': 'Pre LaTeX Program',
            'builder': 'latex',
            'program': '/path/to/your/pre_latex/program',
            'args': ['--arg2', 'value2'],
            'order': 2,  # Optional order key to ensure the order of execution
            'severity': 'warning',  # Optional severity key
            'environment': [],  # Optional environment variables
            'cwd': None  # Optional working directory
        },
        # Add other pre-build configurations as needed
    ],
    'post': [
        {
            'name': 'Post HTML Program',
            'builder': 'html',
            'program': '/path/to/your/post_html/program',
            'args': ['--output-dir', '$outputdir', '--source-dir', '$sourcedir', '--config-dir', '$configdir'],
            'order': 1,  # Optional order key to ensure the order of execution
            'severity': 'error',  # Optional severity key
            'environment': [{'name': 'OUTPUT_DIR', 'value': '$outputdir'}, {'name': 'SOURCE_DIR', 'value': '$sourcedir'}, {'name': 'CONFIG_DIR', 'value': '$configdir'}],  # Optional environment variables
            'cwd': '$outputdir'  # Use the output directory as working directory
        },
        {
            'name': 'Post LaTeX Program',
            'builder': 'latex',
            'program': '/path/to/your/post_latex/program',
            'args': ['--arg2', 'value2'],
            'order': 2,  # Optional order key to ensure the order of execution
            'severity': 'warning',  # Optional severity key
            'environment': [],  # Optional environment variables
            'cwd': None  # Optional working directory
        },
        # Add other post-build configurations as needed
    ]
}

```
