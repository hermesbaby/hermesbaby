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
import json
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
_current_dir = Path(os.getcwd())


_config_file = CFG_CONFIG_DIR / "Kconfig"
_kconfig = kconfiglib.Kconfig(str(_config_file))


def _load_config():
    global _kconfig
    hermesbaby__config_file = _current_dir / CFG_CONFIG_CUSTOM_FILE
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
            print("Scoop installation successful.")
            return True
        else:
            print("Scoop installation did not succeed.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Scoop installation failed: {e}")
        return False


def _tools_install_tool(cmd: str, info: dict) -> bool:
    """
    Attempts to install a tool using the installation command specified in info.
    Returns True if the installation was successful, False otherwise.
    """
    if "install" not in info:
        print("      No installation command provided.")
        return False

    print(f"      Installing using command: {info['install']}")
    try:
        subprocess.run(info["install"], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"      Installation failed: {e}")
        return False

    # Verify that the tool is now available.
    if shutil.which(cmd):
        print("      Installation successful.")
        return True
    else:
        print("      Installation did not succeed.")
        return False


class SortedGroup(typer.core.TyperGroup):
    def list_commands(self, ctx):
        commands = super().list_commands(ctx)
        return sorted(commands)


app = typer.Typer(
    help="The Software and Systems Engineers' Typewriter",
    no_args_is_help=True,
    # cls=SortedGroup,
)


@app.command()
def new(
    ctx: typer.Context,
    directory: str = typer.Argument(
        None, help="Directory where to create the project. Default: current directory."
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

    templates_root_path = Path(__file__).parent.parent.parent / "templates"

    if directory is None:
        directory = "."
    if template is None:
        template = "nano-md"

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
    print(f"Creating project in {directory} using template {template}")

    cookiecutter(
        template=str(template_path),
        output_dir=directory,
        overwrite_if_exists=True,
        no_input=True,
    )


@app.command()
def html(ctx: typer.Context):
    """Build to format HTML"""

    _set_env()
    _load_config()

    _check_plantuml()
    check_tools()

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

    _check_plantuml()
    check_tools()

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

    yaml_template_file = CFG_CONFIG_DIR / "htaccess.yaml"
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
        shutil.copy(yaml_template_file, yaml_file)

    if not os.path.exists(expand_file):
        expand_file = None

    os.makedirs(os.path.dirname(outfile_file), exist_ok=True)

    create_htaccess_entries.main("", yaml_file, outfile_file, expand_file)


@app.command()
def publish():
    """
    Publish the build output to the configured server using SSH.
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


def _check_plantuml():
    """
    Checks for PlantUML.
    If not installed, downloads it.
    """

    print("Checking PlantUML installation...")

    tools_dir = CFG_CONFIG_DIR / "tools"
    version = "1.2024.7"
    plantuml_url = f"https://github.com/plantuml/plantuml/releases/download/v{version}/plantuml-{version}.jar"
    plantuml_path = tools_dir / "plantuml.jar"

    # Create tools directory if it doesn't exist
    os.makedirs(tools_dir, exist_ok=True)

    if plantuml_path.exists():
        print("PlantUML is already installed.")
        return

    print(f"Downloading PlantUML version {version} to {plantuml_path}...")
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
def check_scoop(
    auto: bool = typer.Option(
        False, "--auto", help="Automatically install scoop if missing"
    )
):
    """
    Checks if scoop is installed
    and installs missing extensions if --auto is specified.
    (Experimental feature)
    """
    if shutil.which("scoop"):
        print("Scoop is already installed.")
        return

    print("Scoop is missing.")
    if auto:
        print("Attempting to install scoop headlessly...")
        if _install_scoop():
            print("Scoop was installed successfully.")
        else:
            print("Failed to install scoop automatically.")
            raise typer.Exit(code=1)
    else:
        print("Please install scoop manually from https://scoop.sh/")
        raise typer.Exit(code=1)


@app.command()
def check_tools(
    auto: bool = typer.Option(
        False, "--auto", help="Automatically install missing tools"
    )
):
    """
    Checks for the presence of necessary external tools
    and installs missing extensions if --auto is specified.
    """
    tools = _tools_load_external_tools()  # Load commands from the JSON file

    if not tools:
        return

    num_tools_missing = 0
    print("Checking system for required tools...\n")
    for cmd, info in tools.items():
        print(f"   {cmd} ({info['official_name']}): ", end="")
        if shutil.which(cmd):
            print("found")
            # If found, we skip the rest of this iteration.
            continue

        # If the tool is missing:
        print("missing")
        print(f"      Website: {info['website']}")
        if "install" in info:
            print(f"      Install it via: {info['install']}")
            if auto:
                if not _tools_install_tool(cmd, info):
                    num_tools_missing += 1
            else:
                num_tools_missing += 1
        else:
            num_tools_missing += 1

        print()

    if not num_tools_missing:
        print("\nAll tools are present. You are ready to go!")
    else:
        print(f"\n{num_tools_missing} tools are missing. Please install them.")
        raise typer.Exit(code=1)


@app.command()
def check_vscode_extensions(
    auto: bool = typer.Option(
        False, "--auto", help="Automatically install missing VSCode extensions."
    )
):
    """
    Checks for the presence of recommended VSCode extensions (as defined in extensions.json)
    and installs missing extensions if --auto is specified.
    """
    if not shutil.which("code"):
        print("Visual Studio Code is not installed or 'code' command is not in PATH.")
        raise typer.Exit(code=1)

    # Load recommended VSCode extensions
    try:
        with open(CFG_CONFIG_DIR / "extensions.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("extensions.json not found.")
        raise typer.Exit(code=1)
    except json.JSONDecodeError:
        print("Error: extensions.json is not a valid JSON file.")
        raise typer.Exit(code=1)

    # Validate that data is in the expected format.
    if not isinstance(data, dict):
        print("Error: extensions.json must be a JSON object.")
        raise typer.Exit(code=1)
    if "recommendations" not in data or not isinstance(data["recommendations"], list):
        print("Error: extensions.json must contain a 'recommendations' list.")
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
        print("Error listing VSCode extensions:", e)
        raise typer.Exit(code=1)

    missing_extensions = [
        ext for ext in recommendations if ext not in installed_extensions
    ]

    if not missing_extensions:
        print("All recommended VSCode extensions are installed.")
    else:
        print("Missing VSCode extensions:")
        for ext in missing_extensions:
            print(f"  {ext}")
        if auto:
            print("\nAttempting to install missing extensions...")
            for ext in missing_extensions:
                try:
                    subprocess.run(
                        ["code", "--install-extension", ext], check=True, shell=True
                    )
                    print(f"Installed {ext} successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to install {ext}: {e}")
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
                print("\nThe following extensions are still missing:")
                for ext in missing_extensions:
                    print(f"  {ext}")
                raise typer.Exit(code=1)
            else:
                print("\nAll missing VSCode extensions installed successfully.")
        else:
            print(
                "\nPlease install the missing extensions manually using commands like:"
            )
            print("  code --install-extension " + " ".join(missing_extensions))
            raise typer.Exit(code=1)


@app.callback(invoke_without_command=False)
def pre_command(ctx: typer.Context):
    pass


if __name__ == "__main__":
    app()
