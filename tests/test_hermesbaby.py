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
import pytest
import subprocess
import time
from pathlib import Path
import sys


@pytest.mark.parametrize(
    "command_line",
    [
        "",
    ],
)
def test_help(cli_runner, command_line):

    from src.hermesbaby.__main__ import app

    result = cli_runner.invoke(app, command_line.split())
    assert result.exit_code == 0
    assert "Usage" in result.output


@pytest.mark.parametrize(
    "command_line",
    [
        f"{sys.executable} -m hermesbaby",
        f"poetry run hermesbaby",
        f"poetry run hb",
    ],
)
def test_entry_points(command_line):

    result = subprocess.run(
        command_line.split(),
        start_new_session=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0
    assert "Usage" in result.stdout


@pytest.mark.parametrize(
    "some_rel_path_as_str, option",
    [
        ("", ""),
        (".", ""),
        ("some/relative/path", ""),
        ("", "--template hello"),
        (".", "--template hello"),
        ("some/relative/path", "--template hello"),
    ],
)
def test_task_new(cli_runner, project_dir, some_rel_path_as_str, option):

    from src.hermesbaby.__main__ import app

    args = f"new {some_rel_path_as_str} {option}"

    result = cli_runner.invoke(app, args.split())

    some_rel_path = Path(some_rel_path_as_str)
    if some_rel_path_as_str == "":
        some_rel_path = "hello"

    path_to_index_md = project_dir / some_rel_path / "docs" / "index.md"

    assert (
        path_to_index_md.exists()
    ), f"Project path does not exist: {path_to_index_md}"


def test_task_html(cli_runner, project_dir):

    from src.hermesbaby.__main__ import app

    # Run the "new" command to set up the project
    result = cli_runner.invoke(app, ["new", "."])
    assert result.exit_code == 0, "Setup failed"

    result = cli_runner.invoke(app, ["html"])
    assert result.exit_code == 0, "Call failed"

    index_html = project_dir / "out" / "docs" / "html" / "index.html"
    assert index_html.exists(), f"Build output does not exist: {index_html}"


def test_task_config_file(cli_runner, project_dir):

    from src.hermesbaby.__main__ import app

    # Create a file ".hermesbaby" and write some content
    build_dir = "my-own-build-dir"

    config_file = project_dir / ".hermesbaby"
    with config_file.open("w") as f:
        f.write(f'CONFIG_BUILD__DIRS__BUILD="{build_dir}"' + os.linesep)

    # Run the "new" command to set up the project
    result = cli_runner.invoke(app, ["new", "."])
    assert result.exit_code == 0, "Setup failed"

    result = cli_runner.invoke(app, ["html"])
    assert result.exit_code == 0, "Call failed"

    index_html = project_dir / build_dir / "html" / "index.html"
    assert index_html.exists(), f"Build output does not exist: {index_html}"


def test_task_install(cli_runner):

    from src.hermesbaby.__main__ import app_tools

    # Run the "install" command to set up the project
    result = cli_runner.invoke(app_tools, ["install"])
    assert result.exit_code == 0, "Setup failed"

    result = cli_runner.invoke(app_tools, ["check", "--tag", "headless"])
    assert result.exit_code == 0, "Not all tools were installed"
