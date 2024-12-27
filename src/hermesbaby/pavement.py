import argparse
import os
import sys
from paver.easy import *
from cookiecutter.main import cookiecutter


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
