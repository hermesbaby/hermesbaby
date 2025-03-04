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
from importlib.resources import files
import importlib.metadata
import logging
import json
import os
import requests
import platform
import shutil
from typing import List
import subprocess
import sys
import kconfiglib
from cookiecutter.main import cookiecutter
import typer
import git

__version__ = importlib.metadata.version("hermesbaby")

logger = logging.getLogger(__name__)

CFG_CONFIG_CUSTOM_FILE = ".hermesbaby"
CFG_CONFIG_DIR = Path(__file__).parent


_tool_path = Path(sys.executable).parent


def _get_template_dir():
    return files("hermesbaby").joinpath("templates")


_config_file = CFG_CONFIG_DIR / "Kconfig"
_kconfig = kconfiglib.Kconfig(str(_config_file))


def _load_config():
    global _kconfig
    hermesbaby__config_file = Path(os.getcwd()) / CFG_CONFIG_CUSTOM_FILE
    if hermesbaby__config_file.exists():
        _kconfig.load_config(str(hermesbaby__config_file))
        logger.info(f"Using configuration {hermesbaby__config_file}")
    else:
        logger.info(
            "File {hermesbaby__config_file} does not exist. Using default config only."
        )


def _set_env():
    os.environ["HERMESBABY_CWD"] = os.getcwd()


def _tools_load_external_tools() -> dict:
    file_path = CFG_CONFIG_DIR / "external_tools.json"
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        typer.echo(f"Error: {file_path} not found.")
        return {}


def _install_scoop() -> bool:
    """
    Attempts to install scoop in a headless manner by running the scoop installation
    command in PowerShell and providing the required input ('A') automatically.
    Returns True if the installation appears successful.
    """
    # This is the command suggested on https://scoop.sh/#/:
    install_command = (
        "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force; "
        "iwr -useb get.scoop.sh | iex"
    )
    try:
        # Run the command in PowerShell.
        # The input "A\n" is piped to the process to simulate the user pressing 'A'.
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", install_command],
            input="A\n",
            # capture_output=True,
            text=True,
            check=True,
        )
        # After running the command, check if scoop is now installed.
        if shutil.which("scoop"):
            typer.echo("Scoop installation successful.")
            return True
        else:
            typer.echo("Scoop installation did not succeed.")
            return False
    except subprocess.CalledProcessError as e:
        typer.echo(f"Scoop installation failed: {e}")
        return False


def _tools_install_tool(tool: str, info: dict) -> bool:
    """
    Attempts to install a tool using the installation command specified in info.
    Returns True if the installation was successful, False otherwise.
    """
    if "install" not in info:
        typer.echo("      No installation command provided.")
        return False

    typer.echo(f"      Installing using command: {info['install']['windows']}")
    try:
        subprocess.run(info["install"]['windows'], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"      Installation failed: {e}")
        return False

    # Verify that the tool is now available.
    if shutil.which(info['run'][platform.system().lower()]):
        typer.echo("      Installation successful.")
        return True
    else:
        typer.echo("      Installation did not succeed.")
        return False


def _check_plantuml():
    """
    Checks for PlantUML.
    If not installed, downloads it.
    """

    typer.echo("Checking PlantUML installation...")

    tools_dir = CFG_CONFIG_DIR / "tools"
    version = "1.2024.7"
    plantuml_url = f"https://github.com/plantuml/plantuml/releases/download/v{version}/plantuml-{version}.jar"
    plantuml_path = tools_dir / "plantuml.jar"

    # Create tools directory if it doesn't exist
    os.makedirs(tools_dir, exist_ok=True)

    if plantuml_path.exists():
        typer.echo("PlantUML is already installed.")
        return

    typer.echo(f"Downloading PlantUML version {version} to {plantuml_path}...")
    try:
        response = requests.get(plantuml_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(plantuml_path, "wb") as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                out_file.write(chunk)
        typer.echo("PlantUML setup complete!")
    except requests.exceptions.RequestException as e:
        typer.echo(f"Error downloading PlantUML: {e}")


class SortedGroup(typer.core.TyperGroup):
    def list_commands(self, ctx):
        commands = super().list_commands(ctx)
        return sorted(commands)


app = typer.Typer(
    help="The Software and Systems Engineers' Typewriter",
    no_args_is_help=True,
    # cls=SortedGroup,
)

app_htaccess = typer.Typer(
    help="Manage access of published document",
    no_args_is_help=True,
)
app.add_typer(app_htaccess, name="htaccess")

app_tools = typer.Typer(
    help="All about tools called while building the documentation",
    no_args_is_help=True,
)
app.add_typer(app_tools, name="tools")


@app.callback(invoke_without_command=False)
def version(
    version: bool = typer.Option(
        None,
        "--version",
        callback=lambda value: print(__version__) or exit() if value else None,
        is_eager=True,
        help="Show the version and exit.",
    )
):
    """CLI Tool hb"""


@app.command()
def new(
    ctx: typer.Context,
    directory: str = typer.Argument(
        None,
        help="Directory where to create the project. Default: subdirectory with name of template.",
    ),
    template: str = typer.Option(
        None, "--template", "-t", help="Template to use. Default: nano-md."
    ),
    list_templates: bool = typer.Option(
        False, "--list", "-l", help="List available templates"
    ),
):
    """Create a new project"""

    _set_env()
    _load_config()

    templates_root_path = _get_template_dir()

    if template is None:
        template = "nano-md"
    if directory is None:
        directory = template

    # If --list is provided, list available template directories and exit.
    if list_templates:
        try:
            templates = [d.name for d in templates_root_path.iterdir() if d.is_dir()]
        except Exception as e:
            typer.echo(f"Error listing templates: {e}", err=True)
            raise typer.Abort()
        if not templates:
            typer.echo(f"No templates found in {templates_root_path}")
        else:
            typer.echo("Available templates:")
            for t in sorted(templates):
                typer.echo(f"  - {t}")
        raise typer.Exit()

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

    cookiecutter(
        template=str(template_path),
        output_dir=directory,
        overwrite_if_exists=True,
        no_input=True,
    )

    typer.echo(
        f"Created new project in directory {directory} using template {template}"
    )


@app.command()
def html(
    ctx: typer.Context,
    directory: str = typer.Argument(
        ".",
        help="Directory where to execute the command. ",
    ),
):
    """Build to format HTML"""

    _set_env()
    _load_config()

    _check_plantuml()

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
    typer.echo(command)
    result = subprocess.run(command.split(), cwd=directory)
    sys.exit(result.returncode)


@app.command()
def html_live(
    ctx: typer.Context,
    directory: str = typer.Argument(
        ".",
        help="Directory where to execute the command. ",
    ),
):
    """Build to format HTML with live reload"""

    _set_env()
    _load_config()

    _check_plantuml()

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
    typer.echo(command)
    result = subprocess.run(command.split(), cwd=directory)
    sys.exit(result.returncode)


@app.command()
def configure(
    ctx: typer.Context,
    directory: str = typer.Argument(
        ".",
        help="Directory where to execute the command. ",
    ),
):
    """Configure the project"""

    _set_env()
    _load_config()

    # Set environment variable KCONFIG_CONFIG to the value of CFG_CONFIG_CUSTOM_FILE
    os.environ["KCONFIG_CONFIG"] = CFG_CONFIG_CUSTOM_FILE

    # Start "guiconfig" as a subprocess:
    # - Pass the Kconfig instance to it
    # - Write the configuration to CFG_CONFIG_CUSTOM_FILE
    command = f"{_tool_path}/guiconfig {_config_file}"
    typer.echo(command)
    result = subprocess.run(command.split(), cwd=directory)

    # Don't retain any *.old file
    Path(CFG_CONFIG_CUSTOM_FILE + ".old").unlink(missing_ok=True)

    sys.exit(result.returncode)


@app.command()
def clean(
    ctx: typer.Context,
    directory: str = typer.Argument(
        ".",
        help="Directory where to execute the command. ",
    ),
):
    """Clean the build directory"""

    _set_env()
    _load_config()

    folder_to_remove = Path(directory) / _kconfig.syms["BUILD__DIRS__BUILD"].str_value
    typer.echo(f"Remove {folder_to_remove}")
    if Path(folder_to_remove).exists():
        shutil.rmtree(folder_to_remove)


@app_htaccess.command()
def groups(
    ctx: typer.Context,
    members: List[str] = typer.Argument(
        None,
        help="Member or members to check. ",
    ),
):
    """Lists the groups one or more members are in. If more than one given, also the groups they share."""

    if not members:
        typer.echo("No members given.")
        typer.echo(ctx.get_help())
        raise typer.Exit()

    from .web_access_ctrl import shared_groups

    shared_groups.main(members)


@app_htaccess.command()
def members(
    ctx: typer.Context,
    groups: List[str] = typer.Argument(
        None,
        help="Group or groups to check. ",
    ),
):
    """List the members of one or more groups"""

    if not groups:
        typer.echo("No groups given.")
        typer.echo(ctx.get_help())
        raise typer.Exit()

    typer.echo (f"Grap a coffee, this may take a while...")

    from .web_access_ctrl import group_members

    group_members.main(groups)


# Obsolete. Use hb htaccess --update instead
@app_htaccess.command()
def update(
    ctx: typer.Context,
    directory: str = typer.Argument(
        ".",
        help="Directory where to execute the command. ",
    ),
):
    """Update/create web_root/.htaccess from htaccess.yaml"""

    if not directory:
        typer.echo(ctx.get_help())
        raise typer.Exit()

    _set_env()
    _load_config()

    from .web_access_ctrl import create_htaccess_entries

    yaml_template_file = CFG_CONFIG_DIR / "htaccess.yaml"
    yaml_file = Path(directory) / os.path.join(
        _kconfig.syms["BUILD__DIRS__SOURCE"].str_value, "htaccess.yaml"
    )
    outfile_file = Path(directory) / os.path.join(
        _kconfig.syms["BUILD__DIRS__SOURCE"].str_value, "web_root", ".htaccess"
    )
    expand_file = Path(directory) / os.path.join(
        _kconfig.syms["BUILD__DIRS__SOURCE"].str_value,
        "99-Appendix/99-Access-to-Published-Document/_tables/htaccess__all_users.yaml",
    )

    if not os.path.exists(yaml_file):
        typer.echo(f"Created template file {yaml_file}")
        shutil.copy(yaml_template_file, yaml_file)

    if not os.path.exists(expand_file):
        expand_file = None



    create_htaccess_entries.main("", yaml_file, outfile_file, expand_file)


@app.command()
def publish(
    ctx: typer.Context,
    directory: str = typer.Argument(
        ".",
        help="Directory where to execute the command. ",
    ),
):
    """
    Publish the build output to the configured server using SSH.
    """

    _set_env()
    _load_config()

    publish_host = _kconfig.syms["PUBLISH__HOST"].str_value
    scm_owner_kind = _kconfig.syms["SCM__OWNER_KIND"].str_value
    scm_owner = _kconfig.syms["SCM__OWNER"].str_value
    scm_repo = _kconfig.syms["SCM__REPO"].str_value
    dir_build = Path(directory) / _kconfig.syms["BUILD__DIRS__BUILD"].str_value

    ssh_key_path = (
        Path(directory) / _kconfig.syms["PUBLISH__SSH_PATH"].str_value / "id_rsa"
    )

    try:
        _repo = git.Repo(search_parent_directories=True, path=directory)
        git_branch = _repo.active_branch.name
    except:
        typer.echo(f"Could not get git branch. Aborting publish step", err=True)
        raise typer.Exit(code=1)

    publish_url = (
        f"https://{publish_host}/{scm_owner_kind}/{scm_owner}/{scm_repo}/{git_branch}"
    )

    try:
        typer.echo(f"Publishing to {publish_url}")

        publish_source_folder = f"{dir_build}/html"

        # In case the publish_source_folder doesn't exist raise an exception:
        if not os.path.exists(publish_source_folder):
            raise Exception(
                f"Publish source folder {publish_source_folder} does not exist."
            )

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
            f"-C {publish_source_folder} . "
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

    except Exception as e:
        typer.echo(f"Error during publishing: {e}", err=True)
        raise typer.Exit(code=1)


@app_tools.command()
def check_scoop(
    install: bool = typer.Option(
        False, "--install", help="Automatically install scoop if missing"
    )
):
    """
    Checks if scoop is installed
    and installs missing extensions if --install is specified.
    (Experimental feature)
    """
    if shutil.which("scoop"):
        typer.echo("Scoop is already installed.")
        return

    typer.echo("Scoop is missing.")
    if install:
        typer.echo("Attempting to install scoop headlessly...")
        if _install_scoop():
            typer.echo("Scoop was installed successfully.")
        else:
            typer.echo("Failed to install scoop automatically.")
            raise typer.Exit(code=1)
    else:
        typer.echo("Please install scoop manually from https://scoop.sh/")
        raise typer.Exit(code=1)


@app_tools.command()
def check(
    install: bool = typer.Option(
        False, "--install", help="Automatically install missing tools"
    ),
    tag: str = typer.Option(
        None, "--tag", help="Filter tag"
    )
):
    """
    Checks for the presence of necessary external tools
    and installs missing extensions if --install is specified.
    """
    tools = _tools_load_external_tools()  # Load commands from the JSON file

    if not tools:
        return

    if tag:
        tools = {k: v for k, v in tools.items() if tag in v.get("tags", [])}

    num_tools_missing = 0
    typer.echo("Checking system for required tools...\n")
    for tool, info in tools.items():
        typer.echo(f"   {tool}: ", nl=False)
        if shutil.which(info['run'][platform.system().lower()]):
            typer.echo("found")
            # If found, we skip the rest of this iteration.
            continue

        # If the tool is missing:
        typer.echo("missing")
        typer.echo(f"      Website: {info['website']}")
        try:
            install_cmd = info['install'][platform.system().lower()]
        except KeyError:
            install_cmd = None
        if install_cmd:
            typer.echo(f"      Install it via: {install_cmd}")
            if install:
                if not _tools_install_tool(tool, info):
                    num_tools_missing += 1
            else:
                num_tools_missing += 1
        else:
            num_tools_missing += 1

        typer.echo()

    if not num_tools_missing:
        typer.echo("\nAll tools are present. You are ready to go!")
    else:
        typer.echo(f"\n{num_tools_missing} tools are missing. Please install them.")
        raise typer.Exit(code=1)


@app_tools.command()
def check_vscode_extensions(
    install: bool = typer.Option(
        False, "--install", help="Automatically install missing VSCode extensions."
    )
):
    """
    Checks for the presence of recommended VSCode extensions (as defined in extensions.json)
    and installs missing extensions if --install is specified.
    """
    if not shutil.which("code"):
        typer.echo(
            "Visual Studio Code is not installed or 'code' command is not in PATH."
        )
        raise typer.Exit(code=1)

    # Load recommended VSCode extensions
    try:
        with open(CFG_CONFIG_DIR / "extensions.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        typer.echo("extensions.json not found.")
        raise typer.Exit(code=1)
    except json.JSONDecodeError:
        typer.echo("Error: extensions.json is not a valid JSON file.")
        raise typer.Exit(code=1)

    # Validate that data is in the expected format.
    if not isinstance(data, dict):
        typer.echo("Error: extensions.json must be a JSON object.")
        raise typer.Exit(code=1)
    if "recommendations" not in data or not isinstance(data["recommendations"], list):
        typer.echo("Error: extensions.json must contain a 'recommendations' list.")
        raise typer.Exit(code=1)

    recommendations = data["recommendations"]

    # List currently installed extensions
    try:
        result = subprocess.run(
            ["code", "--list-extensions"],
            capture_output=True,
            text=True,
            check=True,
            shell=True,
        )
        installed_extensions = set(result.stdout.splitlines())
    except subprocess.CalledProcessError as e:
        typer.echo("Error listing VSCode extensions:", e)
        raise typer.Exit(code=1)

    missing_extensions = [
        ext for ext in recommendations if ext not in installed_extensions
    ]

    if not missing_extensions:
        typer.echo("All recommended VSCode extensions are installed.")
    else:
        typer.echo("Missing VSCode extensions:")
        for ext in missing_extensions:
            typer.echo(f"  {ext}")
        if install:
            typer.echo("\nAttempting to install missing extensions...")
            for ext in missing_extensions:
                try:
                    subprocess.run(
                        ["code", "--install-extension", ext], check=True, shell=True
                    )
                    typer.echo(f"Installed {ext} successfully.")
                except subprocess.CalledProcessError as e:
                    typer.echo(f"Failed to install {ext}: {e}")
            # Re-check installed extensions after installation attempts
            result = subprocess.run(
                ["code", "--list-extensions"],
                capture_output=True,
                text=True,
                check=True,
                shell=True,
            )
            installed_extensions = set(result.stdout.splitlines())
            missing_extensions = [
                ext for ext in recommendations if ext not in installed_extensions
            ]
            if missing_extensions:
                typer.echo("\nThe following extensions are still missing:")
                for ext in missing_extensions:
                    typer.echo(f"  {ext}")
                raise typer.Exit(code=1)
            else:
                typer.echo("\nAll missing VSCode extensions installed successfully.")
        else:
            typer.echo(
                "\nPlease install the missing extensions manually using commands like:"
            )
            typer.echo("  code --install-extension " + " ".join(missing_extensions))
            raise typer.Exit(code=1)


@app_tools.command()
def install():
    """Install the external tools necessary for documentation build"""

    typer.echo("Installing tools for CI/CD pipeline")

    # Check if running on Ubuntu Linux
    # Check if running on Linux
    system = platform.system()
    if system != "Linux":
        typer.echo(f"Error: This command is only supported on Debian-based Linux distributions. Detected system: {system}")
        raise typer.Exit(code=1)

    # Check if it's a Debian-based distribution
    is_debian_based = False
    try:
        with open("/etc/os-release", "r") as f:
            os_info = f.read().lower()
            if "debian" in os_info or "ubuntu" in os_info:
                is_debian_based = True
    except FileNotFoundError:
        pass

    if not is_debian_based:
        typer.echo("Error: This command is only supported on Debian-based Linux distributions.")
        raise typer.Exit(code=1)


    path = Path(__file__).parent

    command = f"{path}/setup.sh"
    typer.echo(command)
    result = subprocess.run(command.split(), cwd=path)

    sys.exit(result.returncode)



if __name__ == "__main__":
    app()
