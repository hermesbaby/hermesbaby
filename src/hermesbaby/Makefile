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
# Entry points for docs-as-code framework                                     #
###############################################################################

# Deactivate all default rules
.SUFFIXES:

# Deactivate all built-in implicit targets
.DEFAULT:

# Run w/o explicit target(s)
.PHONY: default
default: help


### CONFIGURATION #############################################################
# You can set these variables from the command line, and also
# from the environment for the first two.

# Determine the directory where the current Makefile is located
MAKEFILE_PATH := $(abspath $(firstword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(dir $(MAKEFILE_PATH))

include $(MAKEFILE_DIR)/.config

# Build (can be overridden by environment)
CFG_DIR_SOURCE             ?= $(CONFIG_BUILD__DIRS__SOURCE)
CFG_DIR_CONFIG             ?= $(CONFIG_BUILD__DIRS__CONFIG)
CFG_DIR_BUILD              ?= $(CONFIG_BUILD__DIRS__BUILD)
CFG_PORT_HTML_LIVE         ?= $(CONFIG_BUILD__PORTS__HTML__LIVE)
CFG_PORT_PRESENTATION_LIVE ?= $(CONFIG_BUILD__PORTS__PRESENTATION__LIVE)

# Publish (no override possible)
CFG_PUBLISH_OWNER_KIND     := $(CONFIG_SCM__OWNER_KIND)
CFG_PUBLISH_OWNER          := $(CONFIG_SCM__OWNER)
CFG_PUBLISH_REPO           := $(CONFIG_SCM__REPO)
CFG_PUBLISH_GIT_BRANCH     := $(or $(branch),$(shell git branch --show-current),branch-is-unknown)
CFG_PUBLISH_HOST           := $(CONFIG_PUBLISH__HOST)
CFG_PUBLISH_URL            := $(CFG_PUBLISH_HOST)/$(CFG_PUBLISH_OWNER_KIND)/$(CFG_PUBLISH_OWNER)/$(CFG_PUBLISH_REPO)/$(CFG_PUBLISH_GIT_BRANCH)


### FIDDLE AREA ###############################################################

.PHONY: fiddle
fiddle:
	echo fiddle


### IMPLEMENTATION ############################################################

define HELP_SCREEN
Usage: make -f doc/Makefile <target>
Make target for working with the documentation

Known targets are are:

        install           : (Re)-install necessary development environment.
                            The environment is being installed in a virtual environment in subfolder .venv/ of the
                            local repository folder.
                            All tools except Latex, necessary for command build-pdf are installed.

        configure         : Start configuration tool for documentation.

        html              : Make documentation in HTML format

        html-live         : Continuous (re-)build of HTML output.
                            Rebuild is being triggered by file changes inside folder CONFIG_BUILD__DIRS__BUILD. Start local webserver.

        redirect-check    : Check redirects in the documentation

        redirect-update   : Update redirects in the documentation

        pdf               : Make documentation in PDF format
                            Requires Miktex (Latex) distribution

        pdf-live          : Make documentation in PDF format
                            Rebuild is being triggered by file changes inside folder CFG_DIR_BUILD.
                            Requires Miktex (Latex) distribution
                            Requires SumatraPDF Viewer

        presentation      : Make presentation in reveal.js

        presentation-live : Make presentation in reveal.js
                            Rebuild is being triggered by file changes inside folder CFG_DIR_BUILD.

        clean             : Clean build output folder (default: out/docs)

        clean-install     : Remove complete installation (located in .venv/)
                            Next other command will re-install tools.

        help              : Show this screen


 Following settings can be changed by setting environment variables:

        (Directories are either relative to working directory or absolute.)

        CFG_DIR_SOURCE        : Directory of source files
                                Default: $(CONFIG_BUILD__DIRS__SOURCE)

        CFG_DIR_CONFIG        : Directory of documentation's source files
                                Default: $(CONFIG_BUILD__DIRS__CONFIG)

        CFG_DIR_BUILD         : Directory of documentation's source files
                                Default: $(CONFIG_BUILD__DIRS__BUILD)

        CFG_PORT_HTML_LIVE    : The TCP/IP port of the local webserver when building html live.
                                Default: $(CONFIG_BUILD__LIVE__PORTS__HTML)

        CFG_PORT_PRESENTATION_LIVE    : The TCP/IP port of the local webserver when building presentation live.
                                        Default: $(CONFIG_BUILD__LIVE__PORTS__PRESENTATION)

endef


# Always invoke one shell for all lines in a recipe
# @see https://www.gnu.org/software/make/manual/html_node/One-Shell.html
.ONESHELL:


ifeq ($(OS),Windows_NT)
SHELL = git-bash
else
SHELL = /bin/bash
endif

PYTHON = python3


# Disable all implicit targets
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:


# Enable parallel execution (where possible)
MAKEFLAGS += ---jobs=5


.PHONY: help
help:
	$(info $(HELP_SCREEN))


.PHONY: install
install: clean-install .tools/.are-up-to-date


.tools/.are-up-to-date:
	$(PYTHON) -m pipx install poetry
	export PATH="$$PATH:$$HOME/.local/bin" # Works for root. Not tested for other users.
	mkdir .tools/
	version=1.2024.7 ; curl -L -o .tools/plantuml.jar https://github.com/plantuml/plantuml/releases/download/v$$version/plantuml-$$version.jar
	touch .tools/.are-up-to-date


.PHONY: deps-are-up-to-date
deps-are-up-to-date: poetry.toml pyproject.toml
	poetry update --with docs --without docs-dev


.PHONY: deps-are-up-to-date-dev
deps-are-up-to-date-dev: poetry.toml pyproject.toml
	poetry update --with docs --with docs-dev


.PHONY: clean
clean:
	rm -rf "$(CONFIG_BUILD__DIRS__BUILD)"


clean-install:
	rm -rf .venv/
	rm -rf .tools/
	rm -f  poetry.lock


.PHONY: _doc_build_boilerplate_files
_doc_build_boilerplate_files: \
        $(CFG_DIR_SOURCE)/conf.py \
        $(CFG_DIR_SOURCE)/Kconfig \
        $(CFG_DIR_SOURCE)/.config \
        $(CFG_DIR_SOURCE)/redirects.txt \
        $(CFG_DIR_SOURCE)/references.bib \
        $(CFG_DIR_SOURCE)/index.rst \
        $(CFG_DIR_SOURCE)/webroot/.htaccess


$(MAKEFILE_DIR)/.config:
	cd $(@D) ; \
        poetry run alldefconfig


#$(CFG_DIR_CONFIG)/index.rst:
index.rst:
	cat > $@ <<'EOF'
	.. _sec_doc_root:

	Your specification
	##################

	Hello.
	EOF


$(CFG_DIR_CONFIG)/webroot/.htaccess:
	mkdir -p $(@D) ;\
	touch $@


.PHONY: configure
configure: .tools/.are-up-to-date deps-are-up-to-date-dev
	(cd "$(CONFIG_BUILD__DIRS__CONFIG)" ; poetry run guiconfig )


.PHONY: htaccess-update
htaccess-update: .tools/.are-up-to-date deps-are-up-to-date-dev
	poetry run python \
	sphinx-contrib/web-access-ctrl/src/web_access_ctrl/create-htaccess-entries.py \
	--yaml docs/htaccess.yaml \
	--out docs/web_root/.htaccess \
	--expand docs/99-Appendix/99-Access-to-Published-Document/_tables/htaccess__all_users.yaml


.PHONY: html-live
html-live: .tools/.are-up-to-date deps-are-up-to-date-dev
	mkdir -p "$(CFG_DIR_BUILD)/$@"
	# Start continuous build, open browser automatically which reloads on change.
	@echo "Building sources at $(CFG_DIR_SOURCE)"
	poetry run sphinx-autobuild \
        -j 10 \
        -W \
        -c "$(CFG_DIR_CONFIG)" \
        --watch $(CFG_DIR_CONFIG) \
        "$(CFG_DIR_SOURCE)" \
        "$(CFG_DIR_BUILD)/$@" \
        --re-ignore '_tags/.*' \
        --port "$(CFG_PORT_HTML_LIVE)" \
        --open-browser


.PHONY: html
html: .tools/.are-up-to-date deps-are-up-to-date
	mkdir -p "$(CFG_DIR_BUILD)/$@"
	@echo "Building sources at $(CFG_DIR_SOURCE)"
	poetry run sphinx-build \
        -W \
        -c "$(CFG_DIR_CONFIG)" \
        "$(CFG_DIR_SOURCE)" \
        "$(CFG_DIR_BUILD)/$@"


.PHONY: sanitize-refs
sanitize-refs: .tools/.are-up-to-date deps-are-up-to-date-dev
	poetry run $(PYTHON) sphinx-contrib/toolbox/src/toolbox/reference_sanitizer.py docs/ --force


.PHONY: pdf-live
pdf-live: .tools/.are-up-to-date deps-are-up-to-date-dev
	mkdir -p "$(CFG_DIR_BUILD)/$@"
	@echo "Building sources at $(CFG_DIR_SOURCE)"
	poetry run sphinx-autobuild \
        -j 10 \
        -W \
        -b latex \
        -c "$(CFG_DIR_CONFIG)" \
        --watch $(CFG_DIR_CONFIG) \
        "$(CFG_DIR_SOURCE)" \
        "$(CFG_DIR_BUILD)/$@" \
        --re-ignore '_tags/.*'


.PHONY: pdf
pdf: .tools/.are-up-to-date deps-are-up-to-date
	mkdir -p "$(CFG_DIR_BUILD)/$@"
	@echo "Building sources at $(CFG_DIR_SOURCE)"
	poetry run sphinx-build \
        -W \
        -b latex \
        -c "$(CFG_DIR_CONFIG)" \
        "$(CFG_DIR_SOURCE)" \
        "$(CFG_DIR_BUILD)/$@"


.PHONY: redirect-check
redirect-check: html
	@echo "Building sources at $(CFG_DIR_SOURCE)"
	poetry run sphinx-build \
        -W \
        -b rediraffecheckdiff \
        -c "$(CFG_DIR_CONFIG)" \
        "$(CFG_DIR_SOURCE)" \
        "$(CFG_DIR_BUILD)/$<"


.PHONY: redirect-update
redirect-update: html
	@echo "Building sources at $(CFG_DIR_SOURCE)"
	poetry run sphinx-build \
        -b rediraffewritediff  \
        -c "$(CFG_DIR_CONFIG)" \
        "$(CFG_DIR_SOURCE)" \
        "$(CFG_DIR_BUILD)/$<"


.PHONY: is-working-tree-clean
is-working-tree-clean:
	@printf "Checking if working tree clean: " ; \
	if [ -z "$$(git status --porcelain)" ]; then \
        echo PASSED ; \
	else \
        echo "FAILED: Publishing is only possible with clean working tree. Check-in your changes or resolve differently. "; \
        git status ; \
        exit 1 ; \
	fi  \


.PHONY: check-and-push
check-and-push: .tools/.are-up-to-date deps-are-up-to-date  is-working-tree-clean  html
	git push


.PHONY: check-and-push-force-with-lease
check-and-push-force-with-lease: .tools/.are-up-to-date deps-are-up-to-date  is-working-tree-clean  html
	git push --force-with-lease


.PHONY: is-no-pending-push
is-no-pending-push:
	@printf "Checking if there is no pending push: " ; \
	if [ -z "$$(git fetch && git status --porcelain --branch | grep -E 'ahead|behind')" ]; then \
        echo PASSED ; \
	else \
        echo "FAILED: Publishing is only possible with pending pushes. Push your branch or resolve differently. "; \
        git status ; \
        exit 1 ; \
	fi  \


.PHONY: publish
publish: is-working-tree-clean  is-no-pending-push redirect-check publish-procedure


.PHONY: publish-on-ci
publish-on-ci: redirect-check publish-procedure


.PHONY: publish-procedure
publish-procedure: .tools/.are-up-to-date deps-are-up-to-date  html
	@echo "Publishing to $(CFG_PUBLISH_URL)"
	chmod 600 .ci/.ssh/id_rsa
	ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i .ci/.ssh/id_rsa $(CFG_PUBLISH_OWNER)@$(CFG_PUBLISH_HOST) "(mkdir -p /var/www/html/$(CFG_PUBLISH_OWNER_KIND)/$(CFG_PUBLISH_OWNER)/$(CFG_PUBLISH_REPO); cd /var/www/html/$(CFG_PUBLISH_OWNER_KIND)/$(CFG_PUBLISH_OWNER)/$(CFG_PUBLISH_REPO); rm -rf $(CFG_PUBLISH_GIT_BRANCH) )"
	tar -czf - -C "$(CFG_DIR_BUILD)/html" . | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i .ci/.ssh/id_rsa $(CFG_PUBLISH_OWNER)@$(CFG_PUBLISH_HOST) "( cd /var/www/html/$(CFG_PUBLISH_OWNER_KIND)/$(CFG_PUBLISH_OWNER)/$(CFG_PUBLISH_REPO) ; mkdir -p $(CFG_PUBLISH_GIT_BRANCH) ; tar -xzf - -C $(CFG_PUBLISH_GIT_BRANCH) )"
	@echo Published to $(CFG_PUBLISH_URL)


.PHONY: clean-publish-orphans
clean-publish-orphans: .tools/.are-up-to-date deps-are-up-to-date-dev
	@echo "Cleaning orphaned branches"
	existing_branches=$$(poetry run python sphinx-contrib/atlassian-admin/get_branches.py --owner $(CFG_PUBLISH_OWNER) --repo $(CFG_PUBLISH_REPO) )
	chmod 600 .ci/.ssh/id_rsa
	# Log on webserver to get the list all directories under the repository folder
	existing_publish_directories=$$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i .ci/.ssh/id_rsa $(CFG_PUBLISH_OWNER)@$(CFG_PUBLISH_HOST) "( cd /var/www/html/$(CFG_PUBLISH_OWNER_KIND)/$(CFG_PUBLISH_OWNER)/$(CFG_PUBLISH_REPO) ; ls -d */ )" )
	# Create the list of directories which do not have a corresponding branch anymore:
	orphans=$$(comm -23 <(echo "$$existing_publish_directories" | tr -d '/' | sort) <(echo "$$existing_branches" | sort) )
	# Log on webserver and remove all directories that are not in the list of existing branches
	ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i .ci/.ssh/id_rsa $(CFG_PUBLISH_OWNER)@$(CFG_PUBLISH_HOST) "( cd /var/www/html/$(CFG_PUBLISH_OWNER_KIND)/$(CFG_PUBLISH_OWNER)/$(CFG_PUBLISH_REPO) ; rm -rf $$orphans )"
	@echo "Cleaned orphaned branches"
