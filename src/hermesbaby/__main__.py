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
from pathlib import Path
import shutil
import subprocess
import sys
import kconfiglib
import typer
from cookiecutter.main import cookiecutter


CFG_CONFIG_CUSTOM_FILE = ".hermesbaby"
CFG_CONFIG_DIR = Path(__file__).parent.parent.parent / "config"


config_file = CFG_CONFIG_DIR / "Kconfig"
kconfig = kconfiglib.Kconfig(str(config_file))


def _load_config():
    global kconfig
    current_dir = Path(os.getcwd())
    hermesbaby_config_file = current_dir / CFG_CONFIG_CUSTOM_FILE
    if hermesbaby_config_file.exists():
        kconfig.load_config(str(hermesbaby_config_file))


def _set_env():
    os.environ["HERMESBABY_CWD"] = os.getcwd()


app = typer.Typer(
    help="The Software and Systems Engineers' Typewriter", no_args_is_help=True
)


@app.command()
def hello(ctx: typer.Context):
    """Say hello"""
    print(ctx.info_name.capitalize())


@app.command()
def new(
    ctx: typer.Context,
    directory: str = typer.Argument(
        None, help="Directory where to create the project. Default: current directory."
    ),
    template: str = typer.Option(
        None, "--template", "-t", help="Template to use. Default: vscode_scratch."
    ),
):
    """Create a new project"""

    _set_env()
    _load_config()

    if directory is None:
        directory = "."
    if template is None:
        template = "vscode_scratch"

    templates_root_path = Path(__file__).parent.parent.parent / "templates"
    template_path = templates_root_path / template

    # The output directory is the current working directory plus

    # Error handling
    if not template_path.exists():
        typer.echo(
            f"Template does not exist. Choose from: {os.listdir(templates_root_path)}",
            err=True,
        )
        raise typer.Abort()

    # Execution
    print(f"Creating project in {directory} using template {template}")

    cookiecutter(
        template=str(template_path),
        output_dir=directory,
        overwrite_if_exists=True,
        no_input=True,
    )


@app.command()
def configure(ctx: typer.Context):
    """Configure the project"""

    _set_env()
    _load_config()

    # Set environment variable KCONFIG_CONFIG to the value of CFG_CONFIG_CUSTOM_FILE
    os.environ["KCONFIG_CONFIG"] = CFG_CONFIG_CUSTOM_FILE

    # Start "guiconfig" as a subprocess:
    # - Pass the Kconfig instance to it
    # - Write the configuration to CFG_CONFIG_CUSTOM_FILE
    command = f"guiconfig {config_file}"
    print(command)
    result = subprocess.run(command.split())
    sys.exit(result.returncode)


@app.command()
def html(ctx: typer.Context):
    """Build HTML documentation"""

    _set_env()
    _load_config()

    build_dir = Path(kconfig.syms["BUILD__DIRS__BUILD"].str_value) / ctx.info_name
    build_dir.mkdir(parents=True, exist_ok=True)
    command = f"""
        sphinx-build
        -j 10
        -W
        -c {str(CFG_CONFIG_DIR)}
        {kconfig.syms["BUILD__DIRS__SOURCE"].str_value}
        {build_dir}
    """
    print(command)
    result = subprocess.run(command.split())
    sys.exit(result.returncode)


@app.command()
def html_live(ctx: typer.Context):
    """Build HTML documentation with live reload"""

    _set_env()
    _load_config()

    build_dir = Path(kconfig.syms["BUILD__DIRS__BUILD"].str_value) / ctx.info_name
    build_dir.mkdir(parents=True, exist_ok=True)
    command = f"""
        sphinx-autobuild
        -j 10
        -W
        -c {str(CFG_CONFIG_DIR)}
        {kconfig.syms["BUILD__DIRS__SOURCE"].str_value}
        {build_dir}
        --watch {str(CFG_CONFIG_DIR)}
        --re-ignore '_tags/.*'
        --port {int(kconfig.syms["BUILD__PORTS__HTML__LIVE"].str_value)}
        --open-browser
    """
    print(command)
    result = subprocess.run(command.split())
    sys.exit(result.returncode)


@app.command()
def clean():
    """Clean the build directory"""

    _load_config()

    if Path(kconfig.syms["BUILD__DIRS__BUILD"].str_value).exists():
        shutil.rmtree(kconfig.syms["BUILD__DIRS__BUILD"].str_value)


if __name__ == "__main__":
    app()
