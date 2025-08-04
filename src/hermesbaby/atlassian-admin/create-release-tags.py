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

import argparse
import getpass
import os
import sys

import yaml

# @see https://atlassian-python-api.readthedocs.io/bitbucket.html
# @see https://github.com/atlassian-api/atlassian-python-api/tree/master/atlassian/bitbucket
# @see https://developer.atlassian.com/cloud/bitbucket/rest/intro/#authentication
# @see https://developer.atlassian.com/server/bitbucket/rest/v906/intro/#about
from atlassian import Bitbucket


def parse_args():
    parser = argparse.ArgumentParser(description="Create release tags")

    parser.add_argument(
        "--config", "-c", required=True, help="Path to the YAML configuration file"
    )
    parser.add_argument("--tag", "-t", required=True, help="Name of annotated tag")
    parser.add_argument(
        "--message", "-m", required=True, help="Description (message) of the tag"
    )

    group_tag = parser.add_mutually_exclusive_group(required=False)
    group_tag.add_argument(
        "--move",
        "-e",
        action="store_true",
        required=False,
        help="Move label if it exists",
    )
    group_tag.add_argument(
        "--delete",
        "-d",
        action="store_true",
        required=False,
        help="Delete label if it exists",
    )

    group_run = parser.add_mutually_exclusive_group(required=True)
    group_run.add_argument(
        "--dry-run", "-n", action="store_true", help="Enable dry-run mode"
    )
    group_run.add_argument("--force", "-f", action="store_true", help="Force changes")
    return parser.parse_args()


def get_access_token():
    access_token = os.getenv("ATLASSIAN_BITBUCKET_ACCESS_TOKEN")
    if not access_token:
        print("The environment variable 'ATLASSIAN_BITBUCKET_ACCESS_TOKEN' is not set.")
        print(
            "Please create a personal access token in Bitbucket and set it as 'ATLASSIAN_BITBUCKET_ACCESS_TOKEN'."
        )
        sys.exit(1)
    return access_token


def load_config(config_path):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def initialize_bitbucket(bitbucket_url, username, access_token):
    return Bitbucket(url=bitbucket_url, username=username, password=access_token)


def process_repositories(bitbucket, repositories, dry_run, tag, message, move, delete):
    processed_repos = set()

    def _set_tag(default_branch_name):
        if dry_run:
            print(f"[DRY-RUN] Would set {_info}")
        else:
            bitbucket.set_tag(
                project_key, repo_name, tag, default_branch_name, description=message
            )
            print(f"Set {_info}")

    def _delete_tag():
        if dry_run:
            print(f"[DRY-RUN] Would delete {_info}")
        else:
            bitbucket.delete_tag(project_key, repo_name, tag)
            print(f"Deleted {_info}")

    def _move_tag(default_branch_name):
        if dry_run:
            print(f"[DRY-RUN] Would move {_info}")
        else:
            bitbucket.delete_tag(project_key, repo_name, tag)
            bitbucket.set_tag(
                project_key, repo_name, tag, default_branch_name, description=message
            )
            print(f"Moved {_info}")

    for project_key, repo_names in repositories.items():
        server_repos = bitbucket.repo_list(project_key)
        server_repo_names = set(repo["name"] for repo in server_repos)

        for repo_name in repo_names:
            if not repo_name:
                print(
                    f"Invalid entry in the configuration file: {project_key} -> {repo_name}"
                )
                continue

            processed_repos.add(repo_name)

            default_branch = bitbucket.get_default_branch(project_key, repo_name)
            default_branch_name = default_branch.get("displayId")

            tags = list(
                bitbucket.get_tags(project_key, repo_name, filter=tag, limit=99999)
            )

            _info = f"tag {tag} with message '{message}' to branch {default_branch_name} in repo {project_key}/{repo_name}"

            if not delete and not move:  ### set #####################
                if tags:
                    print(
                        f"ERROR: Repo {repo_name}: Tag {tag} cannot be set because it already exists. Use option --move"
                    )
                else:
                    _set_tag(default_branch_name)
            elif delete:  ################## delete ##################
                if tags:
                    _delete_tag()
                else:
                    print(
                        f"WARNING: Repo {repo_name}: Tag {tag} couldn't be deleted because it doesn't exist."
                    )
            else:  ######################### move ####################
                if tags:
                    _move_tag(default_branch_name)
                else:
                    _set_tag(default_branch_name)

        unprocessed_repos = server_repo_names - processed_repos
        unprocessed_repos = sorted(unprocessed_repos)
        # Make the content unique:
        unprocessed_repos = list(dict.fromkeys(unprocessed_repos))
        if unprocessed_repos:
            print(f"Unprocessed repositories in project {project_key}:")
            for repo_name in unprocessed_repos:
                default_branch = bitbucket.get_default_branch(project_key, repo_name)
                default_branch_name = default_branch.get("displayId")
                print(f"  - {repo_name}, default branch: {default_branch_name}")


def main():
    args = parse_args()

    username = getpass.getuser()
    access_token = get_access_token()

    config = load_config(args.config)
    bitbucket_url = config.get("bitbucket_url")

    if not bitbucket_url:
        print("Bitbucket URL is not specified in the configuration file.")
        sys.exit(1)

    bitbucket = initialize_bitbucket(bitbucket_url, username, access_token)
    repositories = config.get("repositories", {})

    if not repositories:
        print("No repositories found in the configuration file.")
        sys.exit(1)

    process_repositories(
        bitbucket,
        repositories,
        args.dry_run,
        args.tag,
        args.message,
        args.move,
        args.delete,
    )


if __name__ == "__main__":
    main()
