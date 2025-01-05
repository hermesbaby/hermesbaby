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

import subprocess
from sphinx.application import Sphinx
import logging
import os
import sys

def setup(app: Sphinx):
    app.add_config_value('pre_post_build_programs', {'pre': [], 'post': []}, 'env')
    app.connect('builder-inited', call_pre_build_programs)
    app.connect('build-finished', call_post_build_programs)
    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

def replace_placeholders(value, output_dir, source_dir, config_dir):
    if isinstance(value, str):
        return value.replace('$outputdir', str(output_dir)).replace('$sourcedir', str(source_dir)).replace('$configdir', str(config_dir))
    if isinstance(value, list):
        return [replace_placeholders(v, output_dir, source_dir, config_dir) if isinstance(v, str) else v for v in value]
    if isinstance(value, dict):
        return {k: replace_placeholders(v, output_dir, source_dir, config_dir) if isinstance(v, str) else v for k, v in value.items()}
    return value

def call_programs(app: Sphinx, phase: str):
    logger = logging.getLogger(__name__)

    # Get the current builder
    builder = app.builder.name

    # Get the pre or post build programs configuration
    programs = app.config.pre_post_build_programs.get(phase, [])

    # Sort the configurations if not already sorted (this can be optimized)
    programs.sort(key=lambda x: x.get('order', 0))

    for config in programs:
        if config.get('builder') == builder or config.get('builder') == 'all':
            name = config.get('name')
            if not name:
                logger.warning(f"Program configuration missing 'name' for builder '{builder}' in phase '{phase}'")
                continue

            output_dir = app.builder.outdir
            source_dir = app.srcdir
            config_dir = app.confdir

            external_program = replace_placeholders(config.get('program'), output_dir, source_dir, config_dir)
            args = replace_placeholders(config.get('args', []), output_dir, source_dir, config_dir)
            severity = config.get('severity', 'warning')
            env_vars = replace_placeholders(config.get('environment', []), output_dir, source_dir, config_dir)
            cwd = replace_placeholders(config.get('cwd', None), output_dir, source_dir, config_dir)

            if not external_program:
                logger.warning(f"No external program configured for builder '{builder}' in phase '{phase}'")
                continue

            # Prepare environment variables
            env = os.environ.copy()
            for var in env_vars:
                env[var['name']] = var['value']

            # Call the external program
            print(f"{[external_program] + args}", file=sys.stderr)
            try:
                process = subprocess.Popen(
                    [external_program] + args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    cwd=cwd
                )

                # Read and print stdout and stderr in real-time
                for stdout_line in iter(process.stdout.readline, ""):
                    print(stdout_line, end='')
                for stderr_line in iter(process.stderr.readline, ""):
                    print(stderr_line, end='', file=sys.stderr)

                process.stdout.close()
                process.stderr.close()
                process.wait()

                if process.returncode != 0:
                    message = f"Error calling external program '{name}' during phase '{phase}'"
                    if severity == 'error' or (severity == 'warning' and app.warningiserror):
                        logger.error(message)
                        raise SphinxError(f"External program '{name}' failed with exit code {process.returncode}")
                    elif severity == 'warning':
                        logger.warning(message)

            except subprocess.CalledProcessError as e:
                message = f"Error calling external program '{name}' during phase '{phase}': {e}\n{e.stderr}"
                if severity == 'error' or (severity == 'warning' and app.warningiserror):
                    logger.error(message)
                    raise SphinxError(f"External program '{name}' failed with exit code {e.returncode}")
                elif severity == 'warning':
                    logger.warning(message)
                else:
                    logger.info(message)

def call_pre_build_programs(app: Sphinx):
    call_programs(app, 'pre')

def call_post_build_programs(app: Sphinx, exception):
    call_programs(app, 'post')

class SphinxError(Exception):
    """Custom exception to indicate Sphinx build failure due to pre or post build errors."""
    pass
