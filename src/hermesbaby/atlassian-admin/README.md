<---
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

# Atlassian Admin

- JIRA Change Management (CM)
- BitBucket Source Code Management (SCM)

admin command line tools.


## Bitbucket Default Branch Updater

Synopsis

```
python3 bitbucket-default-branch.py
```

This script changes the default branch of specified Bitbucket repositories to `develop`, with support for dry-run mode.

### Features

- Automatically determine the current logged-in username.
- Use a personal access token for authentication via an environment variable.
- Read the Bitbucket server URL and repository list from a YAML configuration file.
- Support dry-run mode to preview actions without making changes.
- Force mode to apply changes.

### Prerequisites

- Python 3.x
- `atlassian-python-api` library
- `pyyaml` library

### Installation

1. Install the required Python libraries:

    ```bash
    pip install atlassian-python-api pyyaml
    ```

2. Ensure you have a personal access token for Bitbucket and set it as an environment variable:

    ```bash
    export ATLASSIAN_ACCESS_TOKEN=your-access-token
    ```

### YAML Configuration File Format

Create a YAML configuration file (e.g., `repos.yml`) with the following structure:

```yaml
bitbucket_url: https://your-bitbucket-server-url
repositories:
  PROJECT1:
    - repo1
    - repo2
  PROJECT2:
    - repo3
    - repo4
  PROJECT3:
    - repo5

