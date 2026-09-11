# Pinned (not "latest") so the shipped Python stays on the version pyproject.toml
# requires (python = "^3.12") instead of drifting to whatever Ubuntu ships next,
# which broke dependency builds (e.g. msgpack, pillow) when it jumped to 3.14.
FROM ubuntu:24.04

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages
RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils dialog 2>&1 \
    # Install git, process tools, lsb-release (common in install instructions for CLIs)
    && apt-get -y install git wget curl ca-certificates gnupg lsb-release \
    # Required for setup.sh
    && apt-get -y install sudo \
    # Install Python
    && apt-get -y install python3 python3-pip python3-venv python3-dev \
    && ln -s /usr/bin/python3 /usr/bin/python \
    # Install PlantUML dependencies
    && apt-get -y install default-jre graphviz \
    # Install other dependencies that might be needed
    && apt-get -y install make gcc g++ \
    # VS Code's integrated terminal sets LANG=en_US.UTF-8, but this base image
    # only ships C/C.utf8/POSIX, so Python's locale.setlocale(LC_ALL, '') (called
    # unconditionally by sphinx-build) fails with "unsupported locale setting"
    && apt-get -y install locales \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Install poetry-dynamic-versioning
# RUN pip3 install poetry-dynamic-versioning

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

# Set the default shell to bash with pipefail option
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
