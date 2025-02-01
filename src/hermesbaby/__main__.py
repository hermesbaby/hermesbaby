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

from pathlib import Path
import logging
import os
import requests
import shutil
import subprocess
import sys
import kconfiglib
from cookiecutter.main import cookiecutter
import typer
import git

logger = logging.getLogger(__name__)

CFG_CONFIG_CUSTOM_FILE = ".hermesbaby"
CFG_CONFIG_DIR = Path(__file__).parent


_tool_path = Path(sys.executable).parent


_config_file = CFG_CONFIG_DIR / "Kconfig"
_kconfig = kconfiglib.Kconfig(str(_config_file))


def _load_config():
    global _kconfig
    current_dir = Path(os.getcwd())
    hermesbaby__config_file = current_dir / CFG_CONFIG_CUSTOM_FILE
    if hermesbaby__config_file.exists():
        _kconfig.load_config(str(hermesbaby__config_file))
        logger.info(f"Using configuration {hermesbaby__config_file}")
    else:
        logger.info(
            "File {hermesbaby__config_file} does not exist. Using default config only."
        )


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
def setup(ctx: typer.Context):
    """Setup up the tools"""

    _set_env()
    _load_config()

    tools_dir = CFG_CONFIG_DIR / "tools"

    ## Plantuml
    version = "1.2024.7"
    plantuml_url = f"https://github.com/plantuml/plantuml/releases/download/v{version}/plantuml-{version}.jar"
    plantuml_path = os.path.join(tools_dir, "plantuml.jar")

    # Ensure the directory exists
    os.makedirs(tools_dir, exist_ok=True)

    print(f"Downloading PlantUML version {version} to {plantuml_path}...")

    # Download the file
    try:
        response = requests.get(plantuml_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(plantuml_path, "wb") as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                out_file.write(chunk)
        print("PlantUML setup complete!")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PlantUML: {e}")


@app.command()
def new(
    ctx: typer.Context,
    directory: str = typer.Argument(
        None, help="Directory where to create the project. Default: current directory."
    ),
    template: str = typer.Option(
        None, "--template", "-t", help="Template to use. Default: nano-md."
    ),
):
    """Create a new project"""

    _set_env()
    _load_config()

    if directory is None:
        directory = "."
    if template is None:
        template = "nano-md"

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
    command = f"{_tool_path}/guiconfig {_config_file}"
    print(command)
    result = subprocess.run(command.split())

    # Don't retain any *.old file
    Path(CFG_CONFIG_CUSTOM_FILE + ".old").unlink(missing_ok=True)

    sys.exit(result.returncode)


@app.command()
def html(ctx: typer.Context):
    """Build to format HTML"""

    _set_env()
    _load_config()

    build_dir = Path(_kconfig.syms["BUILD__DIRS__BUILD"].str_value) / ctx.info_name
    build_dir.mkdir(parents=True, exist_ok=True)
    executable = os.path.join(_tool_path, "sphinx-build")
    command = f"""
        {executable}
        -b html
        -W
        -c {str(CFG_CONFIG_DIR)}
        {_kconfig.syms["BUILD__DIRS__SOURCE"].str_value}
        {build_dir}
    """
    print(command)
    result = subprocess.run(command.split())
    sys.exit(result.returncode)


@app.command()
def html_live(ctx: typer.Context):
    """Build to format HTML with live reload"""

    _set_env()
    _load_config()

    build_dir = Path(_kconfig.syms["BUILD__DIRS__BUILD"].str_value) / ctx.info_name
    build_dir.mkdir(parents=True, exist_ok=True)
    executable = os.path.join(_tool_path, "sphinx-autobuild")
    command = f"""
        {executable}
        -b html
        -j 10
        -W
        -c {str(CFG_CONFIG_DIR)}
        {_kconfig.syms["BUILD__DIRS__SOURCE"].str_value}
        {build_dir}
        --watch {str(CFG_CONFIG_DIR)}
        --re-ignore '_tags/.*'
        --port {int(_kconfig.syms["BUILD__PORTS__HTML__LIVE"].str_value)}
        --open-browser
    """
    print(command)
    result = subprocess.run(command.split())
    sys.exit(result.returncode)


@app.command()
def clean():
    """Clean the build directory"""

    _set_env()
    _load_config()

    folder_to_remove = _kconfig.syms["BUILD__DIRS__BUILD"].str_value
    print(f"Remove {folder_to_remove}")
    if Path(folder_to_remove).exists():
        shutil.rmtree(folder_to_remove)


@app.command()
def htaccess_update():
    """Update/create web_root/.htaccess from htaccess.yaml"""

    _set_env()
    _load_config()

    from .web_access_ctrl import create_htaccess_entries

    yaml_template_file = os.path.join(CFG_CONFIG_DIR, "htaccess.yaml")
    yaml_file = os.path.join(
        _kconfig.syms["BUILD__DIRS__SOURCE"].str_value, "htaccess.yaml"
    )
    outfile_file = os.path.join(
        _kconfig.syms["BUILD__DIRS__SOURCE"].str_value, "web_root", ".htaccess"
    )
    expand_file = os.path.join(
        _kconfig.syms["BUILD__DIRS__SOURCE"].str_value,
        "99-Appendix/99-Access-to-Published-Document/_tables/htaccess__all_users.yaml",
    )

    if not os.path.exists(yaml_file):
        print(f"Created template file {yaml_file}")
        shutil(yaml_template_file, yaml_file)

    if not os.path.exists(expand_file):
        expand_file = None

    create_htaccess_entries.main("", yaml_file, outfile_file, expand_file)


@app.command()
def publish():
    """
    Publish the build output to the specified server using SSH.
    """

    _set_env()
    _load_config()

    publish_host = _kconfig.syms["PUBLISH__HOST"].str_value
    scm_owner_kind = _kconfig.syms["SCM__OWNER_KIND"].str_value
    scm_owner = _kconfig.syms["SCM__OWNER"].str_value
    scm_repo = _kconfig.syms["SCM__REPO"].str_value
    dir_build = _kconfig.syms["BUILD__DIRS__BUILD"].str_value

    ssh_key_path = ".ci/.ssh/id_rsa"

    try:
        _repo = git.Repo(search_parent_directories=True)
        git_branch = _repo.active_branch.name
    except:
        typer.echo(f"Could not get git branch. Aborting publish step", err=True)
        raise typer.Exit(code=1)

    publish_url = (
        f"https://{publish_host}/{scm_owner_kind}/{scm_owner}/{scm_repo}/{git_branch}"
    )

    try:
        typer.echo(f"Publishing to {publish_url}")

        # Ensure the SSH key has correct permissions
        subprocess.run(["chmod", "600", str(ssh_key_path)], check=True, text=True)

        # Create and clean up remote directories
        ssh_cleanup_command = (
            f"ssh "
            f"-o StrictHostKeyChecking=no "
            f"-o UserKnownHostsFile=/dev/null "
            f"-i {ssh_key_path} "
            f"{scm_owner}@{publish_host} "
            f'"(mkdir -p /var/www/html/{scm_owner_kind}/{scm_owner}/{scm_repo} '
            f"&&  cd /var/www/html/{scm_owner_kind}/{scm_owner}/{scm_repo} "
            f'&& rm -rf {git_branch})"'
        )
        subprocess.run(ssh_cleanup_command, shell=True, check=True, text=True)

        # Compress and transfer files
        tar_command = (
            f"tar -czf - "
            f"-C {dir_build}/html . "
            f"| ssh "
            f"-o StrictHostKeyChecking=no "
            f"-o UserKnownHostsFile=/dev/null "
            f"-i {ssh_key_path} {scm_owner}@{publish_host} "
            f'"(cd /var/www/html/{scm_owner_kind}/{scm_owner}/{scm_repo} '
            f"&& mkdir -p {git_branch} "
            f'&& tar -xzf - -C {git_branch})"'
        )
        subprocess.run(tar_command, shell=True, check=True, text=True)

        typer.echo(f"Published to {publish_url}")

    except subprocess.CalledProcessError as e:
        typer.echo(f"Error during publishing: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def alex():

    command = """
    ls | \
    grep py \
    && echo 'Found Python files' \
    || echo 'No Python files found'
    """

    try:
        # Execute the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Print the standard output and error
        print("Output:")
        print(result.stdout)
        print("Error:")
        print(result.stderr)

        # Get the exit code
        print("Exit Code:", result.returncode)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    app()
