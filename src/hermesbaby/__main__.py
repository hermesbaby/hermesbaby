import os
from pathlib import Path
import shutil
import subprocess
import sys
import typer
from cookiecutter.main import cookiecutter

CFG_DIR_SOURCE = "docs"
CFG_DIR_CONFIG = "docs"
CFG_DIR_BUILD = "out/docs"
CFG_PORT_HTML_LIVE = 1976

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
def html(ctx: typer.Context):
    """Build HTML documentation"""
    current_work_dir = Path.cwd()
    build_dir = Path(CFG_DIR_BUILD) / ctx.info_name
    build_dir.mkdir(parents=True, exist_ok=True)
    command = f"""
        sphinx-build \
        -j 10 \
        -W \
        -c {CFG_DIR_CONFIG} \
        {CFG_DIR_SOURCE} \
        {build_dir} \
    """
    result = subprocess.run(command.split())
    sys.exit(result.returncode)


@app.command()
def html_live(ctx: typer.Context):
    """Build HTML documentation with live reload"""
    build_dir = Path(CFG_DIR_BUILD) / ctx.info_name
    build_dir.mkdir(parents=True, exist_ok=True)
    command = f"""
        sphinx-autobuild \
        -j 10 \
        -W \
        -c {CFG_DIR_CONFIG} \
        {CFG_DIR_SOURCE} \
        {build_dir} \
        --re-ignore '_tags/.*' \
        --port {CFG_PORT_HTML_LIVE} \
        --open-browser
    """
    result = subprocess.run(command.split())
    sys.exit(result.returncode)


@app.command()
def clean():
    """Clean the build directory"""
    if Path(CFG_DIR_BUILD).exists():
        shutil.rmtree(CFG_DIR_BUILD)


if __name__ == "__main__":
    app()
