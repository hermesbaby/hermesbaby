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


import pytest
import os
from pathlib import Path

from typer.testing import CliRunner


@pytest.fixture(scope="function")
def cli_runner():
    yield CliRunner()


@pytest.fixture(scope="function")
def project_dir(tmp_path):
    current_dir_as_str = Path.cwd()
    os.chdir(tmp_path)

    yield tmp_path

    os.chdir(current_dir_as_str)
