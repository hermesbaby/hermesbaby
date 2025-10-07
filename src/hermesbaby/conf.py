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
import platform
import re
import runpy
import subprocess
import sys

import kconfiglib
import requests
import urllib3
import yaml
from docutils import nodes
from docutils.parsers.rst import roles
from sphinx.util import logging

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
        f"There is no '{hermesbaby_config_file}', therefore using default configuration values. You may call 'hb configure' to create a custom configuration."
    )


### PATHS #####################################################################

_src_realpath = os.path.realpath(
    os.path.join(_cwd_realpath, kconfig.syms["BUILD__DIRS__SOURCE"].str_value)
)

_config_realpath = os.path.realpath(
    os.path.join(_cwd_realpath, kconfig.syms["BUILD__DIRS__CONFIG"].str_value)
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
import getpass

import git
from tzlocal import get_localzone

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

_metadata = f"commit: {_commit} | branch: {_git_branch} | built at {_print_out_timestamp} by {_username} | {_confidential_level}"

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
    "**/_attachments/*.rst",
    "**/_attachments/**/*.rst",
    "**/_attachments/*.md",
    "**/_attachments/**/*.md",
]

## Let's expand `some string` to `some string` instead of *some string*
default_role = "code"

master_doc = "index"

numfig = True


### Options for HTML output ###################################################
# @see https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Just initialize as a list here. To be filled from extensions below
html_static_path = ["html_static"]
html_css_files = [
    "custom.css",
]

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

    if "" != kconfig.syms["SCM__REPO__URL_GIT_CLIENT"].str_value:
        html_theme_options["repo_url"] = kconfig.syms[
            "SCM__REPO__URL_GIT_CLIENT"
        ].str_value

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
web_root_dir = os.path.join(_src_realpath, "web_root")
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
drawio_default_transparency = False  # Default: False
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

# prefer using SVG for its scalability, therefore use this instead of just "svg":
plantuml_output_format = "svg_img"

plantuml_latex_output_format = "pdf"


### Author diagrams of arbitrary types with "Mermaid" #########################
# @see https://sphinxcontrib-mermaid-demo.readthedocs.io
# @see https://mermaid.js.org/syntax/gitgraph.html

if False:

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

if False:

    extensions.append("sphinx.ext.graphviz")

    # In case a pdf is generated, we use pdf as output format:
    if "latex" == builder:
        graphviz_output_format = "pdf"
    else:
        graphviz_output_format = "svg"


### Add copy-to-clipboard button to codeblocks ################################
# @see https://sphinx-copybutton.readthedocs.io

extensions.append("sphinx_copybutton")


### Manage todos with "todo" ##################################################
# @see https://www.sphinx-doc.org/en/master/usage/extensions/todo.html

extensions.append("sphinx.ext.todo")

todo_include_todos = True


### Enable Lists of Figures and Tables ########################################
# @see loflot/README.md

extensions.append("hermesbaby.loflot")


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


### Render tables from excel files (xlsx)  ####################################
# @see https://github.com/kkAyataka/sphinxcontrib-xlsxtable

extensions.append("sphinxcontrib.xlsxtable")


### Register additional lexers for code-block directives  #####################

# Register lexer for *.robot files
from robotframeworklexer import RobotFrameworkLexer
from sphinx.highlighting import lexers

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
    os.path.join(_src_realpath, "bibliography.bib"),
]


def append_existing_files(file_list, filenames_to_check):
    for filename in filenames_to_check:
        if os.path.exists(filename):
            file_list.append(filename)
        else:
            logger.info(
                f"There is no '{filename}'. You may create one to start a bibliography. See https://www.bibtex.com/g/bibtex-format/ for more information."
            )


append_existing_files(bibtex_bibfiles, bibtex_bibfiles_candidates)

#
# This section defines a custom style from references
#
# For techreports, online, and misc references the 
# KeyLabelStyle allows to define a custom label using the 
# 'key' field or the 'number' field
#
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.labels.alpha import LabelStyle as AlphaLabelStyle

class KeyLabelStyle(AlphaLabelStyle):
    def format_label(self, entry):
        label = super(KeyLabelStyle, self).format_label(entry)
        if (entry.type in ['techreport', 'online', 'misc']):
            label = entry.fields.get('key', entry.fields.get('number', label))
        return label

class CustomKeyStyle(UnsrtStyle):
    default_sorting_style = 'author_year_title'

    def __init__(self, *args, **kwargs):
        super(CustomKeyStyle, self).__init__(*args, **kwargs)
        self.label_style = KeyLabelStyle()
        self.format_labels = self.label_style.format_labels

from pybtex.plugin import register_plugin
register_plugin('pybtex.style.formatting', 'customkey', CustomKeyStyle)

bibtex_default_style = "customkey"  # unsorted or pick "ieee"/"plain"/"alpha", etc.

### Make use of Inkscape for PDF output work  #################################
# @see https://pypi.org/project/sphinxcontrib-svg2pdfconverter/

if False:
    extensions.append("sphinxcontrib.inkscapeconverter")


### Create hyperlinks to issues  ##############################################
# @see https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html

extensions.append("sphinx.ext.extlinks")

extlinks = {
    "jira": (kconfig.syms["LINK_PATTERNS__JIRA"].str_value, "%s"),
    "issue": (kconfig.syms["LINK_PATTERNS__ISSUE"].str_value, "%s"),
    "repo": (kconfig.syms["LINK_PATTERNS__REPO"].str_value, "%s"),
    "job": (kconfig.syms["LINK_PATTERNS__JOB"].str_value, "%s"),
    "user": (kconfig.syms["LINK_PATTERNS__USER"].str_value, "%s"),
}

extlinks_detect_hardcoded_links = False


### Create references to anchors in other documents with intersphinx ##########
# @see https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

_intersphinx_delayed_log_messages = []


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


def _create_intersphinx_mapping_from_yaml(some_yaml_heredoc, user, password):
    """
    Create intersphinx_mapping from a YAML heredoc.
    Adds validation, optional basic-auth injection, and reachability probing
    (HEAD request for objects.inv) while deferring log output via
    _intersphinx_delayed_log_messages.
    YAML format:
      specifications:
        - identifier: <name>
          url: https://host/path
          options: {}            # optional
    """
    REF_INDEX_FILE = "objects.inv"

    # Normalize possibly tuple-wrapped credentials (current config captures as single-item tuples)
    if isinstance(user, (tuple, list)):
        user = user[0] if user else None
    if isinstance(password, (tuple, list)):
        password = password[0] if password else None

    if not some_yaml_heredoc or not some_yaml_heredoc.strip():
        _intersphinx_delayed_log_messages.append(
            dict(
                level="warning",
                text="Empty YAML provided for intersphinx configuration. 'intersphinx' stays disabled.",
            )
        )
        return None

    try:
        config_data = yaml.safe_load(some_yaml_heredoc)
    except yaml.YAMLError as e:
        _intersphinx_delayed_log_messages.append(
            dict(level="error", text=f"Error parsing intersphinx YAML: {e}")
        )
        return None

    if not isinstance(config_data, dict):
        _intersphinx_delayed_log_messages.append(
            dict(
                level="error",
                text="Parsed intersphinx YAML root is not a mapping. Aborting.",
            )
        )
        return None

    specs = config_data.get("specifications", [])
    if not isinstance(specs, list):
        _intersphinx_delayed_log_messages.append(
            dict(
                level="error",
                text="Key 'specifications' must contain a list. Aborting.",
            )
        )
        return None

    intersphinx_mapping = {}
    added = 0
    skipped = 0

    for idx, spec in enumerate(specs):
        if not isinstance(spec, dict):
            _intersphinx_delayed_log_messages.append(
                dict(
                    level="warning",
                    text=f"Specification #{idx} is not a mapping. Skipped.",
                )
            )
            skipped += 1
            continue

        identifier = spec.get("identifier")
        url = spec.get("url")
        options = spec.get("options", {})

        if not identifier:
            _intersphinx_delayed_log_messages.append(
                dict(
                    level="warning",
                    text=f"Specification #{idx} missing 'identifier'. Skipped.",
                )
            )
            skipped += 1
            continue
        if not url:
            _intersphinx_delayed_log_messages.append(
                dict(
                    level="warning",
                    text=f"Specification '{identifier}' missing 'url'. Skipped.",
                )
            )
            skipped += 1
            continue

        # Inject credentials
        if user and password:
            url = url.replace("://", f"://{user}:{password}@")

        intersphinx_mapping[identifier] = (url, options)
        added += 1

    if added == 0:
        _intersphinx_delayed_log_messages.append(
            dict(
                level="warning",
                text="No valid intersphinx specifications found. 'intersphinx' stays disabled.",
            )
        )
        return None

    _intersphinx_delayed_log_messages.append(
        dict(
            level="info",
            text=f"Prepared {added} intersphinx mapping(s), skipped {skipped} invalid specification(s).",
        )
    )

    # Probe availability of objects.inv
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for identifier, (url_with_auth, _opts) in intersphinx_mapping.items():
        # Remove injected credentials for display
        display_url = re.sub(r"://[^@]+@", "://", url_with_auth)
        test_url = f"{url_with_auth.rstrip('/')}/{REF_INDEX_FILE}"
        try:
            response = requests.head(test_url, verify=False, timeout=5)
            if response.status_code == 200:
                _intersphinx_delayed_log_messages.append(
                    dict(
                        level="info",
                        text=f"[intersphinx:{identifier}] Found cross-reference index at {display_url}",
                    )
                )
            else:
                _intersphinx_delayed_log_messages.append(
                    dict(
                        level="warning",
                        text=f"[intersphinx:{identifier}] No '{REF_INDEX_FILE}' at {display_url} (HTTP {response.status_code}).",
                    )
                )
        except requests.exceptions.RequestException as e:
            _intersphinx_delayed_log_messages.append(
                dict(
                    level="error",
                    text=f"[intersphinx:{identifier}] Error probing {display_url}: {e}",
                )
            )
            # continue probing others; keep existing entries

    return intersphinx_mapping


def _intersphinx__workaround_corporate_ssl_certificates():
    import ssl

    from sphinx.ext.intersphinx import fetch_inventory

    def patched_fetch_inventory(app, uri, inv):
        try:
            return fetch_inventory(app, uri, inv, ssl._create_unverified_context())
        except Exception as e:
            app.warn(f"Failed to fetch inventory from {uri}: {e}")
            return {}


intersphinx_mapping = None

_intersphinx_config_path = os.path.join(_src_realpath, "cross-doc-ref.config.yaml")
_intersphinx_user = (kconfig.syms["PUBLISH__CROSS_REFERENCES__USER"].str_value,) or None
_intersphinx_password = (
    kconfig.syms["PUBLISH__CROSS_REFERENCES__PASSWORD"].str_value,
) or None

_intersphinx_config_as_yaml = None
if os.path.exists(_intersphinx_config_path):
    with open(_intersphinx_config_path, "r") as f:
        _intersphinx_config_as_yaml = f.read()

if _intersphinx_config_as_yaml:

    extensions.append("sphinx.ext.intersphinx")

    _intersphinx__workaround_corporate_ssl_certificates()

    intersphinx_mapping = _create_intersphinx_mapping_from_yaml(
        _intersphinx_config_as_yaml, _intersphinx_user, _intersphinx_password
    )

    app_setups.append(setup_app__intersphinx)


logger.info(f"intersphinx_mapping: {intersphinx_mapping}")


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
# @see https://sphinx-needs.readthedocs.io/
# @see https://sphinx-needs.readthedocs.io/en/latest/configuration.html

extensions.append("sphinx_needs")

needs_id_required = False

needs_id_regex = "^[a-zA-Z0-9_]{5,}"

needs_title_optional = True

# style: Select from "Declaring element" at https://plantuml.com/deployment-diagram
needs_types = [
    # Own items
    dict(
        directive="uc",
        title="UseCase",
        prefix="uc_",
        color="#FFFFFF",
        style="usecase",
    ),
    dict(
        directive="block",
        title="Block",
        prefix="block_",
        color="#FFFFFF",
        style="rectangle",
    ),
    dict(
        directive="con",
        title="Connection",
        prefix="con_",
        color="#FFFFFF",
        style="queue",
    ),
    dict(
        directive="comp",
        title="Component",
        prefix="comp_",
        color="#FFFFFF",
        style="component",
    ),
    dict(
        directive="if",
        title="Interface",
        prefix="if_",
        color="#FFFFFF",
        style="interface",
    ),
    dict(
        directive="constraint",
        title="Constraint",
        prefix="constraint_",
        color="#FFFFFF",
        style="boundary",
    ),
    dict(
        directive="decision",
        title="Decision",
        prefix="decision_",
        color="#FFFFFF",
        style="hexagon",
    ),
    dict(
        directive="concept",
        title="Concept",
        prefix="concept_",
        color="#FFFFFF",
        style="cloud",
    ),
    # Incoming items
    dict(
        directive="spec",
        title="Specification",
        prefix="spec_",
        color="#FFFFFF",
        style="artifact",
    ),
    dict(
        directive="req",
        title="Requirement",
        prefix="req_",
        color="#FFFFFF",
        style="artifact",
    ),
]

needs_role_need_template = "{title:*^20s}"


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


### Add Jupyter notebooks to the toctree ######################################
# @see https://myst-nb.readthedocs.io/en/latest/configuration.html
# @see https://docs.readthedocs.io/en/stable/guides/jupyter.html

extensions.append("myst_nb")

# Timeout for notebooks, default of 30 seconds
nb_execution_timeout = 60


### Add other markdown formats other than .rst  ##############################
# @see https://www.sphinx-doc.org/en/master/usage/markdown.html
# @see https://myst-parser.readthedocs.io/en/latest/sphinx/intro.html
# @see https://myst-parser.readthedocs.io/en/latest/index.html
# @see https://myst-parser.readthedocs.io/en/latest/configuration.html


# Avoid clash with myst_nb (below). myst_nb automatically activates myst_parser.
# So if extensions already contains "myst_nb", we do not add "myst_parser" again.
if "myst_nb" not in extensions:
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
    # "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]


smartquotes = False  #  Prevent (c) → ©, etc.

myst_substitutions = {}

myst_substitutions_from_config = {
    f"CONFIG_{key}": symbol.str_value
    for key, symbol in kconfig.syms.items()
    if symbol.visibility
}

# Here we merge myst_substitutions_from_config into myst_substitutions.
# In case of conflict, myst_substitutions_from_config has higher precedence.
for key, value in myst_substitutions_from_config.items():
    if key not in myst_substitutions:
        myst_substitutions[key] = value
    else:
        myst_substitutions[key] = myst_substitutions_from_config[key]


substitutions_realpath_user = os.path.join(_src_realpath, "substitutions.yaml")

# In case `substitutions_realpath_user` exists, then it is read in to the dict myst_substitutions_from_file
if os.path.exists(substitutions_realpath_user):
    logger.info(f"Loading substitutions from {substitutions_realpath_user}")
    try:
        with open(substitutions_realpath_user, "r", encoding="utf-8") as file:
            substitutions_from_file = yaml.safe_load(file)
            if substitutions_from_file:
                for key, value in substitutions_from_file.items():
                    if key not in myst_substitutions:
                        myst_substitutions[key] = value
                    else:
                        myst_substitutions[key] = substitutions_from_file[key]
    except Exception as e:
        logger.error(
            f"Error loading substitutions from {substitutions_realpath_user}: {e}"
        )
else:
    logger.info(
        f"There is no '{substitutions_realpath_user}'. You may create one to define substitutions with Jinja statements."
    )

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


###############################################################################
### END OF COMPUTATIONAL NARRATIVE WITH JUPYTER ###############################
###############################################################################

###############################################################################
### BEGIN OF EXTENSIONS UNDER EARLY DEVELOPMENT ###############################
###############################################################################

_extensions_under_development_path = os.path.join(_conf_realpath, "..")
sys.path.append(_extensions_under_development_path)

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


if False:
    app_setups.append(setup_app__rstjinja)

###############################################################################
### END OF EXTENSIONS UNDER EARLY DEVELOPMENT #################################
###############################################################################


###############################################################################
### Extend by user-defined project's conf.py ##################################
###############################################################################


def _ensure_requirements(requirements_file):
    if not os.path.isfile(requirements_file):
        # No requirements file, nothing to do
        return
    import pkg_resources
    from pkg_resources import DistributionNotFound, VersionConflict

    with open(requirements_file) as f:
        required = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]
    if not required:
        # Empty requirements.txt
        return
    try:
        pkg_resources.require(required)
    except (DistributionNotFound, VersionConflict):
        logger.info(
            f"[hermesbaby] Installing requirements from {requirements_file} ..."
        )
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file]
        )
        logger.info("[hermesbaby] Relaunching build process...")
        os.execv(sys.executable, [sys.executable] + sys.argv)


_user_conf_path = os.path.join(_config_realpath, "conf.py")
if os.path.exists(_user_conf_path):
    logger.info(
        f"Using project config file {_user_conf_path}. If you like, tell me what great things you have done there within a new ticket at https://github.com/hermesbaby/hermesbaby/issues ."
    )
else:
    logger.info(
        f"There is no '{_user_conf_path}', You may place a custom conf.py there to extend your docs-as-code environment."
    )
    _user_conf_path = None

# Bootstrap dependencies
if _user_conf_path:
    _user_requirements_path = os.path.join(_config_realpath, "requirements.txt")
    if os.path.exists(_user_requirements_path):
        logger.info(f"Using project requirements file {_user_requirements_path}")
        _ensure_requirements(_user_requirements_path)
    else:
        logger.info(
            f"There is no '{_user_requirements_path}'. You may place a custom requirements.txt there to install additional dependencies."
        )


class MockApp:
    def __init__(self):
        self._calls = []

    def __getattr__(self, name):
        def recorder(*args, **kwargs):
            self._calls.append((name, args, kwargs))

        return recorder


_mock_app = MockApp()

_mock_extentions = []

_hermesbaby_extention_api = {
    "extensions": _mock_extentions,
    "roles": roles,
    "nodes": nodes,
    "app": _mock_app,
}

if _user_conf_path:

    # Integrate the user-provided conf.py file and inject the api
    user_ns = runpy.run_path(_user_conf_path, init_globals=_hermesbaby_extention_api)

    # Back-inject
    for key in _hermesbaby_extention_api:
        _hermesbaby_extention_api[key] = user_ns[key]

    # Insert the user-defined extensions into the list of extensions
    for ext in _mock_extentions:
        if ext not in extensions:
            extensions.append(ext)


###############################################################################
### Call all the above collected app setups functions #########################
###############################################################################


def setup(app):
    for app_setup in app_setups:
        app_setup(app)

    # Replay all calls (connect, add_config_value, etc.)
    for method, args, kwargs in _mock_app._calls:
        getattr(app, method)(*args, **kwargs)


### EOF #######################################################################
