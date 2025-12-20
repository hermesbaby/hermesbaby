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
import re

def sanitize_name(name: str) -> str:
    """Sanitize a name to be used as a filename."""
    # Replace spaces and special characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized.lower()

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
            output_mode = config.get('output', 'live')  # 'live' | 'silent' | 'on_error' | 'summary'

            if not external_program:
                logger.warning(f"No external program configured for builder '{builder}' in phase '{phase}'")
                continue

            # Prepare environment variables
            env = os.environ.copy()
            for var in env_vars:
                env[var['name']] = var['value']

            # Call the external program
            import time
            start_time = time.time()

            # Show summary for non-live modes
            if output_mode in ['silent', 'on_error', 'summary']:
                print(f"[{name}] Starting: {external_program}", file=sys.stderr)
            else:
                print(f"{[external_program] + args}", file=sys.stderr)

            # Prepare log file paths
            sanitized_name = sanitize_name(name)
            log_dir = cwd if cwd else output_dir
            stdout_log_path = os.path.join(log_dir, f"{sanitized_name}_stdout.log")
            stderr_log_path = os.path.join(log_dir, f"{sanitized_name}_stderr.log")
            console_log_path = os.path.join(log_dir, f"{sanitized_name}_console.log")

            try:
                process = subprocess.Popen(
                    [external_program] + args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    env=env,
                    cwd=cwd
                )

                # Open log files
                with open(stdout_log_path, 'w', encoding='utf-8') as stdout_log, \
                     open(stderr_log_path, 'w', encoding='utf-8') as stderr_log, \
                     open(console_log_path, 'w', encoding='utf-8') as console_log:

                    import threading
                    import queue

                    # Create queues for each stream
                    stdout_queue = queue.Queue()
                    stderr_queue = queue.Queue()

                    def read_stream(stream, stream_queue, stream_name):
                        """Read from stream and put into queue."""
                        for line in iter(stream.readline, ""):
                            stream_queue.put((stream_name, line))
                        stream_queue.put((stream_name, None))  # Signal end of stream

                    # Start threads to read stdout and stderr
                    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, stdout_queue, 'stdout'))
                    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, stderr_queue, 'stderr'))
                    stdout_thread.daemon = True
                    stderr_thread.daemon = True
                    stdout_thread.start()
                    stderr_thread.start()

                    # Process output from both streams
                    streams_active = {'stdout': True, 'stderr': True}
                    show_console = (output_mode == 'live')

                    while streams_active['stdout'] or streams_active['stderr']:
                        # Check stdout queue
                        try:
                            stream_name, line = stdout_queue.get(timeout=0.01)
                            if line is None:
                                streams_active['stdout'] = False
                            else:
                                # Write to stdout log and console log
                                stdout_log.write(line)
                                stdout_log.flush()
                                console_log.write(line)
                                console_log.flush()
                                # Print to console only if in live mode
                                if show_console:
                                    print(line, end='')
                        except queue.Empty:
                            pass

                        # Check stderr queue
                        try:
                            stream_name, line = stderr_queue.get(timeout=0.01)
                            if line is None:
                                streams_active['stderr'] = False
                            else:
                                # Write to stderr log and console log
                                stderr_log.write(line)
                                stderr_log.flush()
                                console_log.write(line)
                                console_log.flush()
                                # Print to console stderr only if in live mode
                                if show_console:
                                    print(line, end='', file=sys.stderr)
                        except queue.Empty:
                            pass

                    # Wait for threads to finish
                    stdout_thread.join()
                    stderr_thread.join()

                process.stdout.close()
                process.stderr.close()
                process.wait()

                elapsed_time = time.time() - start_time

                # Show summary for non-live modes
                if output_mode in ['silent', 'on_error', 'summary']:
                    if process.returncode == 0:
                        print(f"[{name}] Completed successfully in {elapsed_time:.2f}s", file=sys.stderr)
                    else:
                        print(f"[{name}] Failed with exit code {process.returncode} after {elapsed_time:.2f}s", file=sys.stderr)

                # Dump console log on error if in on_error mode
                if process.returncode != 0 and output_mode == 'on_error':
                    print(f"\n{'='*80}", file=sys.stderr)
                    print(f"ERROR OUTPUT FROM: {name}", file=sys.stderr)
                    print(f"{'='*80}", file=sys.stderr)
                    try:
                        with open(console_log_path, 'r', encoding='utf-8') as log_file:
                            log_lines = log_file.readlines()
                            # Show last 100 lines or full log if shorter
                            lines_to_show = log_lines[-100:] if len(log_lines) > 100 else log_lines
                            if len(log_lines) > 100:
                                print(f"[... showing last 100 of {len(log_lines)} lines ...]\n", file=sys.stderr)
                            for line in lines_to_show:
                                print(line, end='', file=sys.stderr)
                        print(f"\n{'='*80}", file=sys.stderr)
                        print(f"Full log: {console_log_path}", file=sys.stderr)
                        print(f"{'='*80}\n", file=sys.stderr)
                    except Exception as e:
                        print(f"Could not read console log: {e}", file=sys.stderr)

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
    logger = logging.getLogger(__name__)

    # Get the post-build programs configuration
    programs = app.config.pre_post_build_programs.get('post', [])

    for config in programs:
        condition = config.get('condition', 'always')  # Default to 'always'

        # Determine if the program should run based on the condition
        if condition == 'on_success' and exception is not None:
            logger.info(f"Skipping post-build program '{config.get('name')}' due to build failure.")
            continue
        elif condition == 'on_failure' and exception is None:
            logger.info(f"Skipping post-build program '{config.get('name')}' because the build succeeded.")
            continue

        # Call the program if the condition is met
        call_programs(app, 'post')

class SphinxError(Exception):
    """Custom exception to indicate Sphinx build failure due to pre or post build errors."""
    pass
