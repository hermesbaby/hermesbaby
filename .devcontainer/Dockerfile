FROM ubuntu:latest

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
    && apt-get -y install python3 python3-pip python3-venv \
    && ln -s /usr/bin/python3 /usr/bin/python \
    # Install PlantUML dependencies
    && apt-get -y install default-jre graphviz \
    # Install other dependencies that might be needed
    && apt-get -y install make gcc g++ \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Install poetry-dynamic-versioning
# RUN pip3 install poetry-dynamic-versioning

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

# Set the default shell to bash with pipefail option
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
