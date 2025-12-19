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

###############################################################################
#### Linux-Environment for docs-as-code toolchain #############################
###############################################################################

# Here you might change the base image to your needs
FROM ubuntu:24.04

USER root

### Set default shell to bash and environment variables #######################

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="$PATH:/root/.local/bin"

# Here you may set your private PyPI repository for package installation
# ENV PIP_INDEX_URL=

# Here you may set custom certificate paths if needed
# ENV REQUESTS_CA_BUNDLE=
# ENV SSL_CERT_FILE=

### Download and install corporate certificate ################################

# RUN curl -k -u user:password -O https://packages.my-company.com/certs/some-cert.pem \
#     && cp some-cert.pem /usr/local/share/ca-certificates/ \
#     && update-ca-certificates

### Install all packages in one layer to reduce image size ####################

RUN apt-get update --fix-missing && \
    apt-get install -y \
        curl \
        unzip \
        git \
        python3 \
        python3-venv \
        pipx \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

### Install Hermesbaby and let it install it's aux tools as well ##############

RUN pipx install hermesbaby && \
    pipx ensurepath && \
    hb --version && \
    hb ci install-tools


### Copy and setup run script #################################################

COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh


### EOF #######################################################################
