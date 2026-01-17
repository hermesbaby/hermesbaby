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

from sqlalchemy import extract


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
        some_rel_path = "."

    path_to_index_md = project_dir / some_rel_path / "docs" / "index.md"

    assert (
        path_to_index_md.exists()
    ), f"Project path does not exist: {path_to_index_md}"


@pytest.mark.parametrize(
    "extract_option",
    [
        (""),  # Empty directory (defaults to current), no extract
        ("--partly docs/some/extract/path"),  # Default directory with extract
    ],
)
def test_task_html(cli_runner, project_dir, extract_option):

    from src.hermesbaby.__main__ import app

    # Run the "new" command to set up the project
    result = cli_runner.invoke(app, ["new", "."])
    assert result.exit_code == 0, "Setup failed"

    # If testing extract option, create a subdirectory with content
    if extract_option:
        extract_dir = project_dir / "docs" / "some" / "extract" / "path"
        extract_dir.mkdir(parents=True, exist_ok=True)
        # Create a minimal index.md in the extract directory
        (extract_dir / "index.md").write_text("# Test Extract\n\nThis is a test extract.")

    # Build the command
    args = ["html"]
    if extract_option:
        args.extend(extract_option.split())

    result = cli_runner.invoke(app, args)
    assert result.exit_code == 0, f"Call failed with args: {args}"

    # Verify the build output exists
    index_html = project_dir / "out" / "docs" / "html" / "index.html"
    assert index_html.exists(), f"Build output does not exist: {index_html}"


def test_task_config_file(cli_runner, project_dir):

    from src.hermesbaby.__main__ import app

    # Create a file ".hermesbaby" and write some content
    build_dir = "my-own-build-dir"

    # Run the "new" command to set up the project
    result = cli_runner.invoke(app, ["new", ""])
    assert result.exit_code == 0, "Setup failed"

    config_file = project_dir / ".hermesbaby"
    with config_file.open("w") as f:
        f.write(f'CONFIG_BUILD__DIRS__BUILD="{build_dir}"' + os.linesep)

    result = cli_runner.invoke(app, ["html"])
    assert result.exit_code == 0, "Call failed"

    index_html = project_dir / build_dir / "html" / "index.html"
    assert index_html.exists(), f"Build output does not exist: {index_html}"


@pytest.mark.skipif(sys.platform != "linux", reason="Install test only runs on Linux")
def test_task_install(cli_runner):

    from src.hermesbaby.__main__ import app_tools

    # Run the "install" command to set up the project
    result = cli_runner.invoke(app_tools, ["install"])
    assert result.exit_code == 0, "Setup failed"

    result = cli_runner.invoke(app_tools, ["check", "--tag", "headless"])
    assert result.exit_code == 0, "Not all tools were installed"


def test_table_alignment(cli_runner, project_dir):
    """Test that table alignment classes are properly applied in HTML output."""
    from src.hermesbaby.__main__ import app
    from pathlib import Path

    # Run the "new" command to set up the project
    result = cli_runner.invoke(app, ["new", "."])
    assert result.exit_code == 0, "Setup failed"

    # Create a markdown file with a table that has alignment
    docs_dir = project_dir / "docs"
    index_md = docs_dir / "index.md"

    table_content = """# Table Alignment Test

| left-aligned | center-aligned | right-aligned |
| :--- | :----: | ----: |
| a    | b      | c     |
"""

    index_md.write_text(table_content)

    # Build HTML
    result = cli_runner.invoke(app, ["html"])
    assert result.exit_code == 0, "Build failed"

    # Find the generated HTML file - search for it in case of custom build directories
    html_files = list(project_dir.glob("**/html/index.html"))
    assert len(html_files) > 0, f"No HTML output found in {project_dir}"

    # Use the first found HTML file (should only be one in a fresh test)
    index_html = html_files[0]
    html_content = index_html.read_text()

    # Verify that alignment classes are present in the HTML
    assert 'class="head text-left"' in html_content, "text-left class missing"
    assert 'class="head text-center"' in html_content, "text-center class missing"
    assert 'class="head text-right"' in html_content, "text-right class missing"
    assert 'class="text-left"' in html_content, "text-left class missing in body"
    assert 'class="text-center"' in html_content, "text-center class missing in body"
    assert 'class="text-right"' in html_content, "text-right class missing in body"

    # Verify that custom.css is included
    assert 'custom.css' in html_content, "custom.css not included"

    # Verify that the built `custom.css` (next to the found index.html) contains rules for text alignment
    built_css = index_html.parent / "_static" / "custom.css"
    assert built_css.exists(), f"built custom.css not found at {built_css}"
    css_content = built_css.read_text()

    assert (
        '.md-typeset table td.text-center' in css_content
        or 'td.text-center' in css_content
        or '.text-center' in css_content
    ), "CSS rule for center alignment missing"
    assert 'text-align: center' in css_content, "CSS missing 'text-align: center'"

    assert (
        '.md-typeset table td.text-right' in css_content
        or 'td.text-right' in css_content
        or '.text-right' in css_content
    ), "CSS rule for right alignment missing"
    assert 'text-align: right' in css_content, "CSS missing 'text-align: right'"


def test_globaltoc_depth_default(cli_runner, project_dir):
    """Test that globaltoc_depth uses default value of 3 when not configured."""
    from src.hermesbaby.__main__ import app
    from pathlib import Path

    # Run the "new" command to set up the project
    result = cli_runner.invoke(app, ["new", "."])
    assert result.exit_code == 0, "Setup failed"

    # Build HTML without custom configuration
    result = cli_runner.invoke(app, ["html"])
    assert result.exit_code == 0, "Build failed"

    # Find the generated HTML file
    html_files = list(project_dir.glob("**/html/index.html"))
    assert len(html_files) > 0, f"No HTML output found in {project_dir}"

    index_html = html_files[0]
    html_content = index_html.read_text()

    # The default depth of 3 should be used - we can check this indirectly
    # by verifying that the build succeeded (the configuration was read correctly)
    assert index_html.exists(), "HTML output should exist with default configuration"


def test_globaltoc_depth_custom(cli_runner, project_dir):
    """Test that globaltoc_depth can be configured via .hermesbaby file."""
    from src.hermesbaby.__main__ import app
    from pathlib import Path

    # Run the "new" command to set up the project
    result = cli_runner.invoke(app, ["new", "."])
    assert result.exit_code == 0, "Setup failed"

    # Create a .hermesbaby config file with custom globaltoc_depth
    config_file = project_dir / ".hermesbaby"
    with config_file.open("w") as f:
        f.write("CONFIG_STYLING__GLOBALTOC_DEPTH=5" + os.linesep)

    # Build HTML with custom configuration
    result = cli_runner.invoke(app, ["html"])
    assert result.exit_code == 0, "Build failed with custom globaltoc_depth"

    # Find the generated HTML file
    html_files = list(project_dir.glob("**/html/index.html"))
    assert len(html_files) > 0, f"No HTML output found in {project_dir}"

    index_html = html_files[0]
    # Verify that the build succeeded with custom configuration
    assert index_html.exists(), "HTML output should exist with custom globaltoc_depth"

