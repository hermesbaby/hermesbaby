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
import kconfiglib
import pathlib
import platform
import re
import sys
import unicodedata
import requests
import time
import urllib3
import yaml
from sphinx.util import logging

_conf_location = os.path.realpath(os.path.dirname(__file__))

### Import project configuration ##############################################

kconfig = kconfiglib.Kconfig()

hermesbaby_config_file = pathlib.Path(os.environ.get("HERMESBABY_CWD")) / ".hermesbaby"

if hermesbaby_config_file.exists():
    kconfig.load_config(str(hermesbaby_config_file))

###############################################################################

project = kconfig.syms["DOC__PROJECT"].str_value

_author = kconfig.syms["DOC__AUTHOR"].str_value
_year = kconfig.syms["DOC__YEAR"].str_value
copyright = f"{_year}, {_author}"
