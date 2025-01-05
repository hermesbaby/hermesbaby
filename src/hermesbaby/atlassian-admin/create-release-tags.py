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
import sys
import getpass
import yaml
from atlassian import Bitbucket
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Create release tags')

    parser.add_argument('--config',  "-c", required=True, help='Path to the YAML configuration file')
    parser.add_argument('--branch',  "-b", required=True, help='Branch to tag')
    parser.add_argument('--tag',     "-t", required=True, help='Name of annotated tag')
    parser.add_argument('--message', "-m", required=True, help='Description (message) of the tag')

    group_tag = parser.add_mutually_exclusive_group(required=False)
    group_tag.add_argument('--move',   '-e', action='store_true', required=False, help='Move label if it exists')
    group_tag.add_argument('--delete', '-d', action='store_true', required=False, help='Delete label if it exists')

    group_run = parser.add_mutually_exclusive_group(required=True)
    group_run.add_argument('--dry-run', '-n', action='store_true', help='Enable dry-run mode')
    group_run.add_argument('--force',   '-f', action='store_true', help='Force changes')
    return parser.parse_args()

def get_access_token():
    access_token = os.getenv('ATLASSIAN_BITBUCKET_ACCESS_TOKEN')
    if not access_token:
        print("The environment variable 'ATLASSIAN_BITBUCKET_ACCESS_TOKEN' is not set.")
        print("Please create a personal access token in Bitbucket and set it as 'ATLASSIAN_BITBUCKET_ACCESS_TOKEN'.")
        sys.exit(1)
    return access_token

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def initialize_bitbucket(bitbucket_url, username, access_token):
    return Bitbucket(
        url=bitbucket_url,
        username=username,
        password=access_token
    )

def process_repositories(bitbucket, repositories, dry_run, tag, message, commit_revision, move, delete):

    def _set_tag():
        if dry_run:
            print(f"[DRY-RUN] Would set {_info}")
        else:
            bitbucket.set_tag(project_key, repo_name, tag, commit_revision, description=message)
            print(f"Set {_info}")

    def _delete_tag():
        if dry_run:
            print(f"[DRY-RUN] Would delete {_info}")
        else:
            bitbucket.delete_tag(project_key, repo_name, tag)
            print(f"Deleted {_info}")

    def _move_tag():
        if dry_run:
            print(f"[DRY-RUN] Would move {_info}")
        else:
            bitbucket.delete_tag(project_key, repo_name, tag)
            bitbucket.set_tag(project_key, repo_name, tag, commit_revision, description=message)
            print(f"Moved {_info}")

    for project_key, repo_names in repositories.items():
        for repo_name in repo_names:
            if not project_key or not repo_name:
                print(f"Invalid entry in the configuration file: {project_key} -> {repo_name}")
                continue

            tags = list(bitbucket.get_tags(project_key, repo_name, filter=tag, limit=99999))

            _info = f"tag {tag} with message '{message}' to branch {commit_revision} in repo {project_key}/{repo_name}"

            if not delete and not move: ### set #####################
                if tags:
                    print(f"ERROR: Repo {repo_name}: Tag {tag} cannot be set because it already exists. Use option --move")
                else:
                    _set_tag()
            elif delete: ################## delete ##################
                if tags:
                    _delete_tag()
                else:
                    print(f"WARNING: Repo {repo_name}: Tag {tag} couldn't be deleted because it doesn't exist.")
            else: ######################### move ####################
                if tags:
                    _move_tag()
                else:
                    _set_tag()

def main():
    args = parse_args()

    username = getpass.getuser()
    access_token = get_access_token()

    config = load_config(args.config)
    bitbucket_url = config.get('bitbucket_url')

    if not bitbucket_url:
        print("Bitbucket URL is not specified in the configuration file.")
        sys.exit(1)

    bitbucket = initialize_bitbucket(bitbucket_url, username, access_token)
    repositories = config.get('repositories', {})

    if not repositories:
        print("No repositories found in the configuration file.")
        sys.exit(1)

    process_repositories(bitbucket, repositories, args.dry_run, args.tag, args.message, args.branch, args.move, args.delete)

if __name__ == '__main__':
    main()
