# -*- coding: utf-8 -*-

# pylint: skip-file

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
import pathlib
import platform
import re
import sys
import requests
import urllib3
import yaml
from sphinx.util import logging
import kconfiglib

logger = logging.getLogger(__name__)

_cwd_realpath = os.path.realpath((os.environ.get("HERMESBABY_CWD")))
_conf_realpath = os.path.realpath(os.path.dirname(__file__))
_tools_realpath = os.path.realpath(os.path.join(_conf_realpath, "tools"))


### Import project configuration ##############################################
# @see https://www.kernel.org/doc/html/next/kbuild/kconfig-language.html

kconfig = kconfiglib.Kconfig()

hermesbaby_config_file = os.path.join(_cwd_realpath, ".hermesbaby")

if os.path.exists(hermesbaby_config_file):
    kconfig.load_config(hermesbaby_config_file)
    logger.info(f"Using configuration {hermesbaby_config_file}")
else:
    logger.info(
        f"File {hermesbaby_config_file} does not exist. You may call 'hermesbaby configure' to start custom configuration."
    )


### PATHS #####################################################################

_src_realpath = os.path.realpath(
    os.path.join(_cwd_realpath, kconfig.syms["BUILD__DIRS__SOURCE"].str_value)
)


def winning_config_realpath(filename: str) -> str:
    """Precedence: User overrides built-in."""

    config_realpath_user = os.path.join(_src_realpath, filename)
    config_realpath_builtin = os.path.join(_conf_realpath, filename)

    if os.path.exists(config_realpath_user):
        return config_realpath_user
    else:
        return config_realpath_builtin


###############################################################################

### SPHINX CONFIGURATION (GENERAL) ############################################
# @see https://www.sphinx-doc.org/en/master/usage/configuration.html

# The configuration values shall be placed in the same order as they are placed kconfig\.syms\["DOC__PROJECT"\]in the documenting manual.
# The documenting chapter of the manual shall be reflected by a section in this config file.
# The hyperlink to that chapter shall be placed in the very first line of that section.

# Helper variables which are used inside this configuration file which support a calculation of a
# configuration value shall be named so they start with an underscore ("_") so it"s obvious
# that they are local helper variables only used here.
# This is not a function by the interpreter but a common syntax hint to the programmer.

###############################################################################
### Investigte environment ####################################################
###############################################################################

# Investigate the environment variables
if False:
    f = open("env.txt", "w")
    for key, value in os.environ.items():
        f.write(f"{key}: {value}\n")
    f.close()

#
## Find the current builder ###################################################
#
# This configuration knows the following builders
#
# - "dirhtml"
# - "html"
# - "latex"
# - "revealjs"

builder = "dirhtml"
if "-b" in sys.argv:
    builder = sys.argv[sys.argv.index("-b") + 1]

### Project information #######################################################
# @see https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# pyright: reportShadowedImports=false
import datetime
from tzlocal import get_localzone
import git
import getpass

_timezone = get_localzone()
_current_time = datetime.datetime.now(_timezone)
_formatted_time = _current_time.strftime("%Y-%m-%d %H:%M:%S")
_print_out_timestamp = f"{_formatted_time} {_current_time.tzname()}"
_year = _current_time.strftime("%Y")


_git_upstream_repo_url = None
_git_repo_version = ""
_git_commit_sha_short = "n.a."
_git_branch = "n.a."
try:
    _repo = git.Repo(_src_realpath, search_parent_directories=True)
    try:
        _git_upstream_repo_url = _repo.remotes.origin.url
    except:
        pass
    try:
        _git_repo_version = _repo.git.describe(dirty="+")
    except:
        pass
    try:
        _git_commit_sha_short = _repo.git.rev_parse(_repo.head.object.hexsha, short=8)
    except:
        pass
    try:
        _git_branch = _repo.active_branch.name
    except TypeError:
        _git_branch = "detached HEAD"
except:
    pass

_username = getpass.getuser()


_commit = _git_repo_version
if "" == _commit:
    _commit = _git_commit_sha_short

project = kconfig.syms["DOC__PROJECT"].str_value
author = kconfig.syms["DOC__AUTHOR"].str_value
copyright = (
    f"{kconfig.syms['DOC__YEAR'].str_value}, {kconfig.syms['DOC__AUTHOR'].str_value}"
)


_confidential_level = f"{kconfig.syms['DOC__CONFIDENTIALITY_LEVEL_LABEL'].str_value}: {kconfig.syms['DOC__CONFIDENTIALITY_LEVEL'].str_value}"

### Construct meta-data header:

_metadata = f"commit: {_commit} | branch: {_git_branch} | printed at {_print_out_timestamp} by {_username} | {_confidential_level}"

## Add CI information
# Indicator is the environment variable "BUILD_NUMBER" which is set by the CI/CD system.

_build_number = os.environ.get("BUILD_NUMBER")
if _build_number is not None:
    _metadata += f" | Jenkins build-no: {_build_number}"


### Make (project) information available in restructured text #################

## By using the placeholder functionality of Sphinx ###########################
# The exposed variables shall begin with "conf_" to make it clear that they are configuration variables.
rst_prolog = f"""
.. |conf_git_branch| replace:: {_git_branch}
.. |conf_metadata| replace:: {_metadata}
.. |conf_confidential_level| replace:: **{_confidential_level}**
"""


### General configuration #####################################################
# @see https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# @see https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-language
language = kconfig.syms["DOC__LANGUAGE"].str_value

templates_path = []

source_suffix = [".rst", ".md", ".ipynb"]

exclude_patterns = [
    "README.md",
    "**/_attachments/**/*.md",
]

## Let's expand `some string` to `some string` instead of *some string*
default_role = "code"

master_doc = "index"

numfig = True


### Options for HTML output ###################################################
# @see https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Just initialize as a list here. To be filled from extensions below
html_static_path = []

# Just initialize as a list here. To be filled from extensions below
html_extra_path = []

html_show_sourcelink = True

html_theme = "sphinx_material"

# Override the html_theme for previewing in VSCode.
# Esbonio language server we use in VSCode for previewing crashes when using the "sphinx_material" theme.
# We use environment variable "VSCODE_CLI" to detect if we are in the VSCode environment.

if os.environ.get("VSCODE_CLI") is not None:
    pass  # html_theme = "classic"


# The theme settings are theme specific. So wrap their settings into if-clauses for easy
# switching of themes.
if "sphinx_material" == html_theme:  ###########################################
    # @eee https://bashtage.github.io/sphinx-material/customization.html

    html_sidebars = {
        "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
    }

    html_theme_options = {
        "repo_name": "Code",
        "globaltoc_depth": 3,
        "globaltoc_collapse": "true",
        "globaltoc_includehidden": "true",
        # "localtoc_label_text": "Seiteninhalt",
        "localtoc_label_text": "Auf dieser Seite",
    }

    ## repo_url ###########################################
    html_theme_options["repo_url"] = (
        f"https://{kconfig.syms['SCM__HOST'].str_value}/{kconfig.syms['SCM__OWNER_KIND'].str_value}/{kconfig.syms['SCM__OWNER'].str_value}/repos/{kconfig.syms['SCM__REPO'].str_value}/browse"
    )

    ## nav_title ##########################################
    html_theme_options["nav_title"] = kconfig.syms["DOC__TITLE"].str_value

    if "" != kconfig.syms["STYLING__COLOR_PRIMARY"].str_value:
        html_theme_options["color_primary"] = kconfig.syms[
            "STYLING__COLOR_PRIMARY"
        ].str_value

    if "" != kconfig.syms["STYLING__COLOR_ACCENT"].str_value:
        html_theme_options["color_accent"] = kconfig.syms[
            "STYLING__COLOR_ACCENT"
        ].str_value

    html_title = f"{_metadata}"

elif "classic" == html_theme:  #################################################
    html_sidebars = {"**": []}

elif "pydata_sphinx_theme" == html_theme:  #####################################
    html_theme_options = {"show_toc_level": 2}

    pass

else:
    pass


### Access control for publish on Apache 2 ####################################

web_root_dir = os.path.join(_src_realpath, "references.bib")
if os.path.exists(web_root_dir):
    html_extra_path.append(web_root_dir)


### Options for latex / PDF output ############################################
# @see https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output
# @see more settings at https://www.sphinx-doc.org/en/master/latex.html#the-latex-elements-configuration-setting

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "12pt",
    "preamble": r"""
\setlength{\headheight}{15pt}
\addtolength{\topmargin}{-3pt}
\usepackage[utf8]{inputenc}

%% --------------------------------------------------
%% |:sec:| add list of figures, list of tables, list of code blocks to TOC
%% --------------------------------------------------
\makeatletter
\renewcommand{\sphinxtableofcontents}{%
    %
    % before resetting page counter, let's do the right thing.
    \if@openright\cleardoublepage\else\clearpage\fi
    \pagenumbering{roman}%
    \begingroup
        \parskip \z@skip
        \tableofcontents
    \endgroup
    %
    %% addtional lists
    \if@openright\cleardoublepage\else\clearpage\fi
    \addcontentsline{toc}{chapter}{Abbildungsverzeichnis}%
    \listoffigures
    %
    \if@openright\cleardoublepage\else\clearpage\fi
    \addcontentsline{toc}{chapter}{Tabellenverzeichnis}%
    \listoftables
    %
    \if@openright\cleardoublepage\else\clearpage\fi
    \if@openright\cleardoublepage\else\clearpage\fi
    \addcontentsline{toc}{chapter}{Verzeichnis der Quellcodes}%
    \listof{literalblock}{Verzeichnis der Quellcodes}%
    %
    \if@openright\cleardoublepage\else\clearpage\fi
    \pagenumbering{arabic}%
}
\makeatother


""",
}


# @see https://chatgpt.com/share/1ed3fcdf-0405-45a3-9fd6-fcb97d7e793c
def sanitize_filename(internal_string):
    # Normalize the string to decompose special characters (like umlauts)
    normalized_string = internal_string
    # normalized_string = unicodedata.normalize('NFKD', internal_string)

    # Encode the normalized string to ASCII bytes, ignoring non-ASCII characters
    ascii_bytes = normalized_string.encode("ascii", "ignore")

    # Decode the bytes back to a string
    ascii_string = ascii_bytes.decode("ascii")

    # Replace spaces and other undesirable characters with underscores
    safe_string = re.sub(r"[^\w\s-]", "", ascii_string).strip().lower()
    safe_string = re.sub(r"[-\s]+", "_", safe_string)

    return safe_string


_pdf_basename = sanitize_filename(kconfig.syms["DOC__TITLE"].str_value)

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        "index",
        f"{_pdf_basename}.tex",
        kconfig.syms["DOC__TITLE"].str_value,
        author,
        "manual",
    ),
    (
        "00-Project-Manual/index",
        f"Projekthandbuch-{project}.tex",
        project,
        author,
        "manual",
    ),
]


###############################################################################
### EXTENSIONS AND THEIR SETTINGS #############################################
###############################################################################

# Ordered list. Order: Most general first, then for more and more special usescases
# Just initialize as a list here. To be filled from extensions below
extensions = []

# List of functions to be called by Sphinx's setup(app) function
app_setups = []


### Create redirects for moved pages ##########################################
# @see https://sphinxext-rediraffe.readthedocs.io

redirects_file = os.path.join(_src_realpath, "redirects.txt")

if os.path.exists(redirects_file):

    extensions.append("sphinxext.rediraffe")

    rediraffe_redirects = str(redirects_file)
    rediraffe_branch = _git_branch


### Enable support for RSS-Feed readers #######################################
# @see https://github.com/lsaffre/sphinxfeed
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! Sphinxfeed will include only .rst files !!!
# !!! that have a :date: field with a date    !!!
# !!! that does not lie in the future.        !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#

extensions.append("sphinxfeed")

# mandatory options
feed_base_url = f"https://{kconfig.syms['PUBLISH__HOST'].str_value}"
feed_description = f"{kconfig.syms['DOC__TITLE'].str_value}"
feed_author = kconfig.syms["DOC__AUTHOR"].str_value

# optional options
feed_field_name = _print_out_timestamp
feed_filename = "rss.xml"
feed_entry_permalink = True
feed_use_atom = True
use_dirhtml = False


### Draw diagrams with "draw.io" ##############################################
# @see https://pypi.org/project/sphinxcontrib-drawio/

extensions.append("sphinxcontrib.drawio")

## Settings regarding run in headless mode

# Prevent from nasty console flickering
drawio_disable_verbose_electron = True

# Linux-only settings:
if "Linux" == platform.system():

    # Run virtual X-Server.
    drawio_headless = True

    # Make it work in docker containers
    drawio_no_sandbox = True


## Settings regarding the output

drawio_default_export_scale = 100  # Default: 100
drawio_default_transparency = True  # Default: False
drawio_builder_export_format = (
    {  # dict ( builder: format (one out of: ["png", "jpg", "svg", "pdf"]) )
        "html": "svg",
        "latex": "pdf",
    }
)


### Embedd diagrams as code in plantuml language with "plantuml" #############
# @see https://github.com/sphinx-contrib/plantuml
# @see https://crashedmind.github.io/PlantUMLHitchhikersGuide/

extensions.append("sphinxcontrib.plantuml")


## Settings regarding run in headless mode

_plantuml_config_file = "plantuml.config"


plantuml = f"java -jar {os.path.join(_tools_realpath, 'plantuml.jar')} -config {winning_config_realpath(_plantuml_config_file)}"


## Settings regarding the output

plantuml_batch_size = 500
plantuml_output_format = "svg"
plantuml_latex_output_format = "pdf"


### Author diagrams of arbitrary types with "Mermaid" #########################
# @see https://sphinxcontrib-mermaid-demo.readthedocs.io
# @see https://mermaid.js.org/syntax/gitgraph.html

extensions.append("sphinxcontrib.mermaid")

# Set the output format depending on builder:
# Use svg but overwrite it in case we want to build a pdf via latex-builder

mermaid_output_format = "svg"


def setup_app__mermaid(app):
    app.connect("builder-inited", _mermaid_on_builder_inited)


app_setups.append(setup_app__mermaid)


def _mermaid_on_builder_inited(app):

    if "latex" == app.builder.name:
        # Override setting(s)
        app.config.mermaid_output_format = "pdf"


# This allows commands other than binary executables to be executed on Windows.
# Does work on Windows, only.
if "Windows" == platform.system():
    mermaid_cmd_shell = "True"

# For individual parameters, a list of parameters can be added. Refer to https://github.com/mermaidjs/mermaid.cli#options.
mermaid_params = []

# Make it work under Linux as root (in CI in docker container)
# Works on Windows with any user as well.
mermaid_params += ["-p", winning_config_realpath("puppeteer.config.json")]

# Styling
mermaid_params += ["--backgroundColor", "transparent"]
mermaid_params += ["--theme", "forest"]
mermaid_params += ["--width", "400"]

mermaid_d3_zoom = True


### Author diagrams of arbitrary types with "Graphviz" ########################
# @see https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html
# @see https://graphviz.org/gallery/
# @see https://graphviz.org/docs/attrs/rankdir/

extensions.append("sphinx.ext.graphviz")


### Add copy-to-clipboard button to codeblocks ################################
# @see https://sphinx-copybutton.readthedocs.io

extensions.append("sphinx_copybutton")


### Manage todos with "todo" ##################################################
# @see https://www.sphinx-doc.org/en/master/usage/extensions/todo.html

extensions.append("sphinx.ext.todo")

todo_include_todos = True


### Add sophistic html elements - use with care ###############################
# @see https://sphinx-design.readthedocs.io

extensions.append("sphinx_design")

tags_create_tags = False


### Add tagging ###############################################################
# @see https://sphinx-tags.readthedocs.io

extensions.append("sphinx_tags")

# Enable/disable the functionality
tags_create_tags = False

# Configuring the functionality
tags_create_badges = True
tags_page_header = "Tags"
tags_page_title = "Seiten getaggt mit"

tags_badge_colors = {
    "in_work": "warrning",
    "draft": "dark",
    "in_review": "primary",
    "approved": "success",
    "info": "info",
    "in_doubt": "danger",
}


### Include Markdown (*.md) sources, e.g. for tables  #########################
# @see https://sphinx-mdinclude.omnilib.dev

extensions.append("sphinx_mdinclude")


### Register additional lexers for code-block directives  #####################

from sphinx.highlighting import lexers


# Register lexer for *.robot files

from robotframeworklexer import RobotFrameworkLexer

lexers["robot"] = RobotFrameworkLexer()


# Register <next-lexer-to-come>

### Create sophisticated tables  ##############################################
# @see https://sharm294.github.io/sphinx-datatables/
# @see https://datatables.net/

extensions.append("sphinxcontrib.jquery")
extensions.append("sphinx_datatables")


### Enable bibliography in bibtex format ######################################
# @see https://sphinxcontrib-bibtex.readthedocs.io/
# @see https://www.bibtex.com/g/bibtex-format/

extensions.append("sphinxcontrib.bibtex")

bibtex_bibfiles = []

bibtex_bibfiles_candidates = [
    os.path.join(_src_realpath, "references.bib"),
]


def append_existing_files(file_list, filenames_to_check):
    for filename in filenames_to_check:
        if os.path.exists(filename):
            file_list.append(filename)
        else:
            logger.info(
                f"There is no '{filename}'. You may create one to start a bibliography."
            )


append_existing_files(bibtex_bibfiles, bibtex_bibfiles_candidates)


### Make use of Inkscape for PDF output work  #################################
# @see https://pypi.org/project/sphinxcontrib-svg2pdfconverter/

extensions.append("sphinxcontrib.inkscapeconverter")


### Create hyperlinks to issues  ##############################################
# @see https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html

extensions.append("sphinx.ext.extlinks")

extlinks = {
    "jira": (kconfig.syms["LINK_PATTERNS__JIRA"].str_value, "%s"),
    "repo": (kconfig.syms["LINK_PATTERNS__REPO"].str_value, "%s"),
    "user": (kconfig.syms["LINK_PATTERNS__USER"].str_value, "%s"),
}

extlinks_detect_hardcoded_links = False


### Create references to anchors in other documents with intersphinx ##########
# @see https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html


_intersphinx_delayed_log_messages = []


def _intersphinx_populate_mapping(
    config_path: str, user: str = None, password: str = None
):
    """Populate intersphinx_mapping with tuples (URL, None)"""

    REF_INDEX_FILE = "objects.inv"

    ret_val = {}

    # Read in the YAML file
    config_data = None
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config_data = yaml.safe_load(config_file)
            ret_val = {
                spec["identifier"]: (spec["url"], None)
                for spec in config_data.get("specifications", [])
            }
            _intersphinx_delayed_log_messages.append(
                dict(
                    level="info", text=f"Loaded intersphinx mappings from {config_path}"
                )
            )
    except FileNotFoundError:
        _intersphinx_delayed_log_messages.append(
            dict(
                level="info",
                text=f"{config_path} not found. 'intersphinx' stays disabled.",
            )
        )
    except yaml.YAMLError as e:
        _intersphinx_delayed_log_messages.append(
            dict(level="error", text=f"Error parsing YAML from {config_path}: {e}")
        )
    except KeyError as e:
        _intersphinx_delayed_log_messages.append(
            dict(level="error", text=f"Missing expected key in YAML data: {e}")
        )

    # Inject user and password into URLs
    if user and password:
        for key, value in ret_val.items():
            url = value[0]
            url_with_auth = url.replace("://", f"://{user}:{password}@")
            ret_val[key] = (url_with_auth, None)

    # Probe if the URLs are reachable
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for key, value in ret_val.items():
        url = value[0]
        url_wo_auth = url.replace(f"{user}:{password}@", "")

        # probe if there is the file `objects.inv` available (do not download, just check)
        try:
            response = requests.head(f"{url}/{REF_INDEX_FILE}", verify=False)
            if response.status_code == 200:
                _intersphinx_delayed_log_messages.append(
                    dict(
                        level="info",
                        text=f"Found cross-reference index file at {url_wo_auth} (HTTP {response.status_code})",
                    )
                )
            else:
                _intersphinx_delayed_log_messages.append(
                    dict(
                        level="warning",
                        text=f"Cross-reference index file not found at {url_wo_auth} (HTTP {response.status_code}). Check {{config_path}}",
                    )
                )
        except requests.exceptions.RequestException as e:
            _intersphinx_delayed_log_messages.append(
                dict(level="error", text=f"Error while probing {url_wo_auth}: {e}")
            )

    return ret_val


def setup_app__intersphinx(app):
    logger = logging.getLogger(__name__)
    for message in _intersphinx_delayed_log_messages:
        level = message["level"]
        text = message["text"]

        if level == "info":
            logger.info(text)
        elif level == "warning":
            logger.warning(text)
        elif level == "error":
            logger.error(text)


intersphinx_mapping = _intersphinx_populate_mapping(
    config_path=os.path.join(_conf_realpath, "cross-doc-ref.config.yaml"),
    user=kconfig.syms["PUBLISH__CROSS_REFERENCES__USER"].str_value,
    password=kconfig.syms["PUBLISH__CROSS_REFERENCES__PASSWORD"].str_value,
)


def _intersphinx__workaround_corporate_ssl_certificates():
    from sphinx.ext.intersphinx import fetch_inventory
    import ssl

    def patched_fetch_inventory(app, uri, inv):
        try:
            return fetch_inventory(app, uri, inv, ssl._create_unverified_context())
        except Exception as e:
            app.warn(f"Failed to fetch inventory from {uri}: {e}")
            return {}

    fetch_inventory = patched_fetch_inventory


# TODO: Activate (if activated this will lead to necessity of working communication to the hosts specified in the cross-doc-ref.config.yaml) ). Do not activate before a tolerance is built in to enable a "limb-build" when no connection is available.
# TODO: Also introduce a dedicated kconfig.syms['PUBLISH__CROSS_REFERENCES__ENABLE'].str_value to enable/disable the intersphinx feature.
if False:
    app_setups.append(setup_app__intersphinx)


# Activate intersphinx in case configuration file exists and there is at least one entry below `specifications`
# TODO: Activate after issue with ssl certificates on CIBS is solved
if False:
    if intersphinx_mapping:
        extensions.append("sphinx.ext.intersphinx")
        _intersphinx__workaround_corporate_ssl_certificates()


### Link documentation items with "mlx.traceability" ##########################
# @see https://melexis.github.io/sphinx-traceability-extension

extensions.append("mlx.traceability")

import mlx.traceability

html_static_path.append(
    os.path.join(os.path.dirname(mlx.traceability.__file__), "assets")
)

traceability_relationships = {
    "jira": "",
}

traceability_relationship_to_string = {
    "jira": "JIRA item",
}

traceability_external_relationship_to_url = {
    "jira": "https://jira.yourcompany.com/browse/field1",
}

traceability_render_relationship_per_item = True


### sphinx-needs - Adds needs/requirements to sphinx  ########################
# @see https://sphinx-needs.readthedocs.io/en/latest/configuration.html

extensions.append("sphinx_needs")

needs_id_required = False

needs_id_regex = "^[a-zA-Z0-9_]{5,}"

needs_title_optional = True

needs_types = [
    # Own items
    dict(
        directive="usecase",
        title="UseCase",
        prefix="UC_",
        color="#FFFFFF",
        style="usecase",
    ),
    dict(
        directive="block",
        title="Block",
        prefix="BLOCK_",
        color="#FFFFFF",
        style="component",
    ),
    dict(
        directive="connection",
        title="Connection",
        prefix="CON_",
        color="#FFFFFF",
        style="interface",
    ),
    dict(
        directive="component",
        title="Component",
        prefix="COMP_",
        color="#FFFFFF",
        style="component",
    ),
    dict(
        directive="interface",
        title="Interface",
        prefix="IF_",
        color="#FFFFFF",
        style="interface",
    ),
    # Incoming items
    dict(
        directive="jira_spec",
        title="JIRA-Spec",
        prefix="JIRA_SPEC",
        color="#FFFFFF",
        style="file",
    ),
    dict(
        directive="jira_req",
        title="JIRA-Req",
        prefix="JIRA_REQ_",
        color="#FFFFFF",
        style="file",
    ),
]

## Wishes to be implemented in the future in sphinx_needs:
# - WISH_A: Option needs_id_from_title as element of own needs_type, default: False
# - WISH_A: Every custom need type shall get own role along with the directive:
#   dict(directive="uc", ...) makes available directive .. usecase:: and also role :uc:`UC_1234`.


### Render reST from data in any format using Jinja2 templating engine ######
# @see https://jinja.palletsprojects.com/templates
# @see https://sphinxcontribdatatemplates.readthedocs.io/en/latest/index.html

extensions.append("sphinxcontrib.datatemplates")

templates_path.append(os.path.join(_src_realpath, "datatemplates"))


import html
from bs4 import BeautifulSoup
import re


def html_to_rst(html_content):
    """
    Converts HTML content to reStructuredText (reST).

    Args:
    html_content (str): The HTML content to convert.

    Returns:
    str: The converted reST content.
    """
    # Unescape HTML entities
    unescaped_content = html.unescape(html_content)

    # Parse HTML content
    soup = BeautifulSoup(unescaped_content, "html.parser")

    # Convert HTML to reST
    rst_content = convert_tags_to_rst(soup)

    # Remove subsequent empty lines from the text
    rst_content = re.sub(r"\n\s*\n+", "\n\n", rst_content)

    # Apply intendation
    indent_spaces = 4
    indent = " " * indent_spaces
    indented_lines = [
        (indent + line if line.strip() else line) for line in rst_content.split("\n")
    ]
    rst_content = "\n".join(indented_lines)

    return rst_content


def convert_tags_to_rst(element):
    """
    Recursively converts HTML tags to reST.

    Args:
    element (BeautifulSoup element): Parsed HTML element.

    Returns:
    str: The converted reST content.
    """
    if element.name is None:
        return str(element)

    rst_content = ""
    if element.name == "b" or element.name == "strong":
        rst_content += f"**{element.get_text()}**"
    elif element.name == "i" or element.name == "em":
        rst_content += f"*{element.get_text()}*"
    elif element.name == "a":
        href = element.get("href", "")
        text = element.get_text()
        rst_content += f"`{text} <{href}>`_"
    elif element.name == "p":
        rst_content += f"\n\n{element.get_text()}\n\n"
    elif element.name == "br":
        rst_content += "\n"
    elif element.name == "h1":
        text = element.get_text()
        rst_content += f"\n\n{text}\n{'=' * len(text)}\n\n"
    elif element.name == "h2":
        text = element.get_text()
        rst_content += f"\n\n{text}\n{'-' * len(text)}\n\n"
    elif element.name == "ul":
        rst_content += "\n\n" + "".join(
            [
                f"* {convert_tags_to_rst(li)}\n"
                for li in element.find_all("li", recursive=False)
            ]
        )
    elif element.name == "ol":
        rst_content += "\n\n" + "".join(
            [
                f"#. {convert_tags_to_rst(li)}\n"
                for li in element.find_all("li", recursive=False)
            ]
        )
    else:
        # Handle other tags or nested content
        for child in element.children:
            rst_content += convert_tags_to_rst(child)

    return rst_content


def setup_app__datatemplates(app):
    app.connect("builder-inited", _datatemplates_on_builder_inited)


app_setups.append(setup_app__datatemplates)


def _datatemplates_on_builder_inited(app):

    if app.builder.name == "dirhtml" or app.builder.name == "html":
        # Access the Jinja2 environment
        env = app.builder.templates.environment

        # Register the custom filter
        env.filters["html_to_rst"] = html_to_rst


### Add other markdown formats other than .rst  ##############################
# @see https://www.sphinx-doc.org/en/master/usage/markdown.html
# @see https://myst-parser.readthedocs.io/en/latest/sphinx/intro.html
# @see https://myst-parser.readthedocs.io/en/latest/index.html


# Avoid clash with myst_nb (below). myst_nb automatically activates myst_parser.
if False:
    extensions.append("myst_parser")

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

###############################################################################
### BEGIN OF SPHINX-TOOLBOX EXTENSION #########################################
###############################################################################
# @see https://sphinx-toolbox.readthedocs.io

### Add configuration values ##################################################
# @see https://sphinx-toolbox.readthedocs.io/en/latest/extensions/confval.html

extensions.append("sphinx_toolbox.confval")


### Add next toolbox extension here ###########################################
# @see


###############################################################################
### END OF SPHINX-TOOLBOX EXTENSION ###########################################
###############################################################################


###############################################################################
### BEGIN OF COMPUTATIONAL NARRATIVE WITH JUPYTER #############################
###############################################################################

### Embed python code and its results #########################################
# @see https://jupyter-sphinx.readthedocs.io
# @see https://blog.jupyter.org/integrating-output-in-documentation-with-jupyter-sphinx-ecf569ddab85

extensions.append("jupyter_sphinx")


### Add Jupyter notebooks to the toctree ######################################
# @see https://myst-nb.readthedocs.io/en/latest/configuration.html
# @see https://docs.readthedocs.io/en/stable/guides/jupyter.html

extensions.append("myst_nb")

# Timeout for notebooks, default of 30 seconds
nb_execution_timeout = 60


###############################################################################
### END OF COMPUTATIONAL NARRATIVE WITH JUPYTER ###############################
###############################################################################

###############################################################################
### BEGIN OF EXTENSIONS UNDER EARLY DEVELOPMENT ###############################
###############################################################################

sys.path.append(os.path.join(_conf_realpath, ".."))

### Tag sections, paragraphs, figures, ... anything ###########################
# @see ../sphinx-contrib/pre-post-build/README.md


extensions.append("hermesbaby.pre-post-build")

pre_post_build_programs = {
    "post": [
        {
            "name": "Create PDF from Latex code",
            "builder": "latex",
            "program": "make",
            "cwd": "$outputdir",
            "severity": "info",
        },
        {
            "name": "View",
            "builder": "latex",
            "program": "sumatrapdf",
            "args": [f"$outputdir\\{_pdf_basename}.pdf"],
            "severity": "info",
        },
    ]
}


### Conditional toctree entries with toctree-only #############################
# @see ../sphinx-contrib/toctree-only/README.md

extensions.append("hermesbaby.toctree-only")


## By applying Jinja2 Templating Engine every rst file ########################

# @see https://ericholscher.com/blog/2016/jul/25/integrating-jinja-rst-sphinx/
# @see https://stackoverflow.com/questions/54520956/declare-additional-dependency-to-sphinx-build-in-an-extension
# @see https://www.sphinx-doc.org/en/master/extdev/appapi.html
# @see https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.add_config_value
# @see https://jinja.palletsprojects.com/en/3.0.x/api/


config_as_dict = {
    key: symbol.str_value for key, symbol in kconfig.syms.items() if symbol.visibility
}


def rstjinja(app, docname, source):
    """
    Render our pages as a jinja template for fancy templating goodness.
    """
    src = source[0]
    try:
        rendered = app.builder.templates.render_string(src, app.config.config_as_dict)
    except:
        print("ERROR in Jinja template while processing " + docname)

    source[0] = rendered


def setup_app__rstjinja(app):
    app.add_config_value(name="config_as_dict", default={}, rebuild=True)
    app.connect("source-read", rstjinja)


app_setups.append(setup_app__rstjinja)

###############################################################################
### END OF EXTENSIONS UNDER EARLY DEVELOPMENT #################################
###############################################################################

### Call all the above collected app setups functions #########################


def setup(app):
    for app_setup in app_setups:
        app_setup(app)


### EOF #######################################################################
