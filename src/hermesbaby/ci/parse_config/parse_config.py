#! /usr/bin/env python3

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


"""
Functionality:

Read a JSON file and print shell export commands for each key-value pair.
Nested keys are flattened using double underscores (__) and converted to uppercase.
Gracefully: If it doesn't exist or is not valid JSON, then just print to stderr.


"""

import sys
import os
import json

ENV_PREFIX = "CONFIG_"

def flatten_json(data, prefix=''):
    """Flatten a nested dict into a single level dict with __ separator."""
    items = []
    for key, value in data.items():
        # Convert key to uppercase and replace hyphens with underscores
        clean_key = key.upper().replace('-', '_')
        new_key = f"{prefix}{clean_key}" if prefix else clean_key

        if isinstance(value, dict):
            # Add __ separator for nested keys
            items.extend(flatten_json(value, prefix=f"{new_key}__").items())
        elif isinstance(value, (list, tuple)):
            # For lists, we just store them as JSON strings
            items.append((new_key, json.dumps(value)))
        else:
            items.append((new_key, str(value)))
    return dict(items)

def get_env_vars_from_json(file_path, prefix=ENV_PREFIX):
    """
    Read a JSON file and return a dictionary of flattened environment variables.

    Args:
        file_path (str): Path to the JSON file.
        prefix (str): Prefix for the environment variables.

    Returns:
        dict: Flattened environment variables.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid JSON object.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")

    if not os.path.isfile(file_path):
        raise ValueError(f"'{file_path}' is not a file.")

    with open(file_path, 'r') as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"'{file_path}' must contain a JSON object (dict) at the top level.")

    return flatten_json(data, prefix=prefix)

def format_as_export_commands(env_vars):
    """
    Convert a dictionary of environment variables into shell export commands.

    Args:
        env_vars (dict): Dictionary of environment variables.

    Returns:
        list: List of shell export command strings.
    """
    commands = []
    for key, value in env_vars.items():
        # Escape characters that are special inside double quotes in shell:
        # \ (backslash), " (double quote), $ (dollar sign), ` (backtick)
        safe_value = value.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        commands.append(f'export {key}="{safe_value}"')
    return commands

def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: parse_config.py <file-path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        env_vars = get_env_vars_from_json(file_path)
        commands = format_as_export_commands(env_vars)
        for cmd in commands:
            print(cmd)
    except json.JSONDecodeError as e:
        print(f"Error: '{file_path}' is not a valid JSON file. {e}", file=sys.stderr)
        sys.exit(1)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
