import argparse
import os
import sys
from paver.easy import task, consume_args, sh, path
from cookiecutter.main import cookiecutter


# Load dynamic paths and configuration from environment variables
SOURCE_DIR = path(os.getenv("HERMESBABY_SOURCE_DIR", "docs"))
BUILD_DIR = path(os.getenv("HERMESBABY_BUILD_DIR", "out/docs"))
LIVE_PORT = int(os.getenv("HERMESBABY_LIVE_PORT", 1976))

# Define builder and common arguments for Sphinx commands
BUILDER = "html"
SPHINX_BUILD_ARGS = f"-b {BUILDER} -W {SOURCE_DIR} {BUILD_DIR}"

# Command templates for Sphinx build and Sphinx autobuild
SPHINX_BUILD_COMMAND = f"sphinx-build {SPHINX_BUILD_ARGS}"
SPHINX_AUTOBUILD_COMMAND = f"sphinx-autobuild --port {LIVE_PORT} {SPHINX_BUILD_ARGS}"


@task
def hello():
    print("Hello")


@task
@consume_args
def new(args):

    # Argument/option handling
    parser = argparse.ArgumentParser(description="Parse arguments from a variable.")
    parser.add_argument(
        "directory",
        nargs="?",
        type=str,
        default=".",
        help="The directory where to create the project",
    )
    parser.add_argument(
        "--template", type=str, default="vscode_scratch", help="From scratch"
    )
    arguments = parser.parse_args(args)

    # Error handling
    templates_root_path = os.path.join(os.path.dirname(__file__), "../..", "templates")
    template_path = os.path.join(templates_root_path, arguments.template)
    if not os.path.exists(template_path):
        print(
            f"Template does not exist. Choose from: {os.listdir(templates_root_path)}",
            file=sys.stderr,
        )
        exit(1)

    # Execution
    cookiecutter(
        template=template_path,
        output_dir=arguments.directory,
        overwrite_if_exists=True,
        no_input=True,
    )


@task
def html():
    BUILD_DIR.makedirs()
    sh(SPHINX_BUILD_COMMAND)


@task
def html_live():
    BUILD_DIR.makedirs()
    sh(SPHINX_AUTOBUILD_COMMAND)


@task
def clean():
    if BUILD_DIR.exists():
        BUILD_DIR.rmtree()
        print(f"Cleaned: {BUILD_DIR}")
    else:
        print(f"Nothing to clean: {BUILD_DIR}")
