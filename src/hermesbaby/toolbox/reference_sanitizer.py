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

import os
import re
import argparse

cfg_search_identifier = r'[ a-zA-Z0-9äÄüÜöÖ_.-]+'
cfg_allowed_chars = 'a-zA-Z0-9_'

# Mapping of umlauts to their non-umlaut representatives
umlaut_map = {
    'Ä': 'Ae', 'ä': 'ae',
    'Ö': 'Oe', 'ö': 'oe',
    'Ü': 'Ue', 'ü': 'ue',
    'ß': 'ss'
}

def replace_umlauts(text):
    for umlaut, replacement in umlaut_map.items():
        text = text.replace(umlaut, replacement)
    return text

def replace_non_alphanumeric_with_underscore(file_path, pattern, dry_run):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        print(f"Skipping file due to encoding error: {file_path}")
        return

    new_lines = []
    for line_number, line in enumerate(lines):
        matches = re.finditer(pattern, line)
        modified_line = line
        for match in matches:
            if match.groups():
                original_group = match.group(1)
                # Replace umlauts in the group
                modified_group = replace_umlauts(original_group)
                new_group = re.sub(rf'[^{cfg_allowed_chars}]', '_', modified_group)
                if original_group != new_group:
                    start_col = match.start(1)
                    end_col = match.end(1)
                    print(f"{file_path}:{line_number + 1}:{start_col + 1}-{end_col}: {match.group(0)}")
                    print(f"Original Group: {original_group}")
                    print(f"Modified Group: {new_group}")
                    modified_line = modified_line[:start_col] + new_group + modified_line[end_col:]
        new_lines.append(modified_line)

    if not dry_run:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
        except UnicodeEncodeError:
            print(f"Skipping file due to encoding error while writing: {file_path}")

def process_files(dir_path, patterns, dry_run):
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.rst'):
                file_path = os.path.join(root, file)
                for pattern in patterns:
                    replace_non_alphanumeric_with_underscore(file_path, pattern, dry_run)

def main():
    parser = argparse.ArgumentParser(description="Sanitize internal references rst files.")
    parser.add_argument("directory", help="Directory to start the search from.")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-f", "--force", action="store_true", help="Perform the changes.")
    mode_group.add_argument("-n", "--dry-run", action="store_true", help="Perform a dry run without making any changes.")

    args = parser.parse_args()
    directory = args.directory
    dry_run = args.dry_run

    patterns = [
        rf'^.. _({cfg_search_identifier}):$',        # Anchor Style: .. _anchor:
        rf':ref:`({cfg_search_identifier})`',        # Reference Style: :ref:`anchor`
        rf':ref:`.+<({cfg_search_identifier})>`',    # Reference Style: :ref:`Some Text <anchor>`
    ]



    process_files(directory, patterns, dry_run)

if __name__ == "__main__":
    main()
