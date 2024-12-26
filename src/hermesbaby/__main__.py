import argparse
import sys
import os
import multiprocessing
from sphinx.application import Sphinx
from sphinx_autobuild  import __main__ as sphinx_autobuild # Import sphinx-autobuild

def run_sphinx_build(
    src_dir, out_dir, builder='html', filenames=None, conf_dir=None, doctree_dir=None,
    force_all=False, fresh_env=False, parallel=None, confoverrides=None, verbosity=0, 
    warning_file=None, warning_as_error=False, keep_going=False, tags=None
):
    try:
        # Set parallel to the CPU count if set to 'auto'
        if parallel == 'auto':
            parallel = multiprocessing.cpu_count()

        # Build the app with provided options
        app = Sphinx(
            srcdir=src_dir,
            confdir=conf_dir or src_dir,     # Defaults to src_dir if not provided
            outdir=out_dir,
            doctreedir=doctree_dir or os.path.join(out_dir, '.doctrees'),
            buildername=builder,
            confoverrides=confoverrides or {},
            status=sys.stdout if verbosity > 0 else None,  # Handles verbose output
            warning=sys.stderr,              # Handles warning output
            freshenv=fresh_env,
            parallel=parallel or 1
        )

        # Set any additional tags if specified
        if tags:
            for tag in tags:
                app.tags.add(tag)

        # Set warning behavior
        if warning_as_error:
            app.warningiserror = True
        if keep_going:
            app.keep_going = True

        # Build the documentation
        app.build(force_all=force_all, filenames=filenames)

        print(f"Sphinx build finished. Build results are in {out_dir}")
        
        # Handle writing warnings to a file
        if warning_file:
            with open(warning_file, 'w') as f:
                f.write(app._warning.getvalue())

    except Exception as e:
        print(f"Error during Sphinx build: {e}")
        sys.exit(1)

def run_sphinx_autobuild(args, autobuild_options):
    """
    Run sphinx-autobuild with the specified arguments.
    """
    autobuild_args = [
        args.sourcedir,
        args.outputdir,
        *args.filenames,
        '-b', args.builder,
    ]

    if args.a:
        autobuild_args.append('-a')
    if args.E:
        autobuild_args.append('-E')
    if args.doctreedir:
        autobuild_args.extend(['-d', args.doctreedir])
    if args.jobs:
        autobuild_args.extend(['-j', str(args.jobs)])  # Convert jobs to string
    if args.confdir:
        autobuild_args.extend(['-c', args.confdir])
    if args.C:
        autobuild_args.append('-C')
    if args.D:
        for setting in args.D:
            autobuild_args.extend(['-D', setting])
    if args.A:
        for val in args.A:
            autobuild_args.extend(['-A', val])
    if args.tag:
        for tag in args.tag:
            autobuild_args.extend(['-t', tag])
    if args.n:
        autobuild_args.append('-n')

    # Additional autobuild options, converted to strings where needed
    if autobuild_options.port:
        autobuild_args.extend(['--port', str(autobuild_options.port)])
    if autobuild_options.host:
        autobuild_args.extend(['--host', autobuild_options.host])
    if autobuild_options.re_ignore:
        autobuild_args.extend(['--re-ignore', autobuild_options.re_ignore])
    if autobuild_options.ignore:
        autobuild_args.extend(['--ignore', autobuild_options.ignore])
    if autobuild_options.no_initial:
        autobuild_args.append('--no-initial')
    if autobuild_options.open_browser:
        autobuild_args.append('--open-browser')
    if autobuild_options.delay:
        autobuild_args.extend(['--delay', str(autobuild_options.delay)])  # Convert delay to string
    if autobuild_options.watch:
        autobuild_args.extend(['--watch', autobuild_options.watch])
    if autobuild_options.pre_build:
        autobuild_args.extend(['--pre-build', autobuild_options.pre_build])

    # Run sphinx-autobuild
    sphinx_autobuild.main(autobuild_args)


def print_help():
    help_text = """
usage: hermesbaby [OPTIONS] SOURCEDIR OUTPUTDIR [FILENAMES...]

Generate documentation from source files. hermesbaby generates documentation from the files in SOURCEDIR and places it in OUTPUTDIR. It looks for 'conf.py' in SOURCEDIR for the configuration settings.
The 'hermesbaby-quickstart' tool may be used to generate template files, including 'conf.py'. hermesbaby can create documentation in different formats. A format is selected by specifying the builder name 
on the command line; it defaults to HTML. Builders can also perform other tasks related to documentation processing. By default, everything that is outdated is built. Output only for selected files can
be built by specifying individual filenames.

positional arguments:
  sourcedir         path to documentation source files
  outputdir         path to output directory
  filenames         a list of specific files to rebuild. Ignored if -a is specified

options:
  -h, --help        show this help message and exit
  --version         show program's version number and exit

general options:
  -b BUILDER        builder to use (default: html)
  -a                write all files (default: only write new and changed files)
  -E                don't use a saved environment, always read all files
  -d PATH           path for the cached environment and doctree files (default: OUTPUTDIR/.doctrees)
  -j N, --jobs N    build in parallel with N processes where possible (special value "auto" will set N to cpu-count)

build configuration options:
  -c PATH           path where configuration file (conf.py) is located (default: same as SOURCEDIR)
  -C                use no config file at all, only -D options
  -D setting=value  override a setting in configuration file
  -A name=value     pass a value into HTML templates
  -t TAG            define tag: include "only" blocks with TAG
  -n                nit-picky mode, warn about all missing references

console output options:
  -v                increase verbosity (can be repeated)
  -q                no output on stdout, just warnings on stderr
  -Q                no output at all, not even warnings
  --color           do emit colored output (default: auto-detect)
  -N, --no-color    do not emit coloured output (default: auto-detect)
  -w FILE           write warnings (and errors) to given file
  -W                turn warnings into errors
  --keep-going      with -W, keep going when getting warnings
  -T                show full traceback on exception
  -P                run Pdb on exception

autobuild options:
  --autobuild       automatically rebuild the documentation and serve it with live reload
  --port PORT       port to serve documentation on (0 for a free port)
  --host HOST       hostname to serve documentation on
  --re-ignore RE_IGNORE
                    regex for files to ignore when watching for changes
  --ignore IGNORE   glob for files to ignore when watching for changes
  --no-initial      skip the initial build
  --open-browser    open the browser after building documentation
  --delay DELAY     how long to wait before opening the browser
  --watch DIR       additional directories to watch
  --pre-build COMMAND
                    additional command(s) to run prior to building documentation
""".strip()  # Strip trailing newlines to ensure no extra newline at the end
    print(help_text)

def parse_arguments():
    parser = argparse.ArgumentParser(prog="hermesbaby", add_help=False)

    # Positional arguments
    parser.add_argument('sourcedir', nargs='?', help="Path to documentation source files.")
    parser.add_argument('outputdir', nargs='?', help="Path to output directory.")

    # General options
    parser.add_argument('-b', '--builder', default='html', help="Builder to use (default: html).")
    parser.add_argument('-a', action='store_true', help="Write all files (default: only write new and changed files).")
    parser.add_argument('-E', action='store_true', help="Don't use a saved environment, always read all files.")
    parser.add_argument('-d', '--doctreedir', help="Path for the cached environment and doctree files (default: OUTPUTDIR/.doctrees).")
    parser.add_argument('-j', '--jobs', help="Build in parallel with N processes where possible (default: 1). Use 'auto' for automatic detection.", default=1)
    
    # Build configuration options
    parser.add_argument('-c', '--confdir', help="Path where configuration file (conf.py) is located (default: same as SOURCEDIR).")
    parser.add_argument('-C', action='store_true', help="Use no config file at all, only -D options.")
    parser.add_argument('-D', action='append', help="Override a setting in configuration file (use multiple -D for multiple overrides).")
    parser.add_argument('-A', action='append', help="Pass a value into HTML templates (use multiple -A for multiple values).")
    parser.add_argument('-t', '--tag', action='append', help="Define tag: include 'only' blocks with TAG.")
    parser.add_argument('-n', action='store_true', help="Nit-picky mode, warn about all missing references.")

    # Console output options
    parser.add_argument('-v', action='count', default=0, help="Increase verbosity (can be repeated).")
    parser.add_argument('-q', action='store_true', help="No output on stdout, just warnings on stderr.")
    parser.add_argument('-Q', action='store_true', help="No output at all, not even warnings.")
    parser.add_argument('--color', action='store_true', help="Emit colored output.")
    parser.add_argument('-N', '--no-color', action='store_true', help="Do not emit colored output.")
    parser.add_argument('-w', '--warnings-file', help="Write warnings (and errors) to given file.")
    parser.add_argument('-W', action='store_true', help="Turn warnings into errors.")
    parser.add_argument('--keep-going', action='store_true', help="With -W, keep going when getting warnings.")
    parser.add_argument('-T', action='store_true', help="Show full traceback on exception.")
    parser.add_argument('-P', action='store_true', help="Run Pdb on exception.")

    # Autobuild options
    parser.add_argument('--autobuild', action='store_true', help="Automatically rebuild and serve documentation with live reload.")
    parser.add_argument('--port', help="Port to serve documentation on (0 for free port).")
    parser.add_argument('--host', help="Hostname to serve documentation on.")
    parser.add_argument('--re-ignore', help="Regex for files to ignore when watching for changes.")
    parser.add_argument('--ignore', help="Glob for files to ignore when watching for changes.")
    parser.add_argument('--no-initial', action='store_true', help="Skip the initial build.")
    parser.add_argument('--open-browser', action='store_true', help="Open the browser after building documentation.")
    parser.add_argument('--delay', help="How long to wait before opening the browser.")
    parser.add_argument('--watch', help="Additional directories to watch.")
    parser.add_argument('--pre-build', help="Additional command(s) to run prior to building the documentation.")

    # Positional argument for specific filenames
    parser.add_argument('filenames', nargs='*', help="List of specific files to rebuild. Ignored if -a is specified.")

    parser.add_argument('--version', action='store_true', help="Show program's version number and exit.")

    return parser

def main():
    parser = parse_arguments()

    # If --help is requested, show the custom help output
    if '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        sys.exit(0)

    # If --version is requested
    if '--version' in sys.argv:
        print("hermesbaby version 1.0.0")
        sys.exit(0)

    # Check if no arguments are provided
    if len(sys.argv) == 1:
        sys.stderr.write("usage: hermesbaby [OPTIONS] SOURCEDIR OUTPUTDIR [FILENAMES...]\n")
        sys.exit(2)

    args = parser.parse_args()

    # If --autobuild is specified, run sphinx-autobuild
    if args.autobuild:
        run_sphinx_autobuild(args, autobuild_options=args)
        return

    # Normal build process
    # Convert job argument to int or 'auto'
    jobs = args.jobs
    if isinstance(jobs, str) and jobs.isdigit():
        jobs = int(jobs)

    # Prepare config overrides from the -D option
    confoverrides = {}
    if args.D:
        for item in args.D:
            key, value = item.split('=', 1)
            confoverrides[key] = value

    # Ensure sourcedir and outputdir are provided
    if not args.sourcedir or not args.outputdir:
        sys.stderr.write("usage: hermesbaby [OPTIONS] SOURCEDIR OUTPUTDIR [FILENAMES...]\n")
        sys.exit(2)

    # Run the Sphinx build with parsed arguments
    run_sphinx_build(
        src_dir=args.sourcedir,
        out_dir=args.outputdir,
        builder=args.builder,
        filenames=args.filenames,
        conf_dir=args.confdir,
        doctree_dir=args.doctreedir,
        force_all=args.a,
        fresh_env=args.E,
        parallel=jobs,
        confoverrides=confoverrides,
        verbosity=args.v,
        warning_file=args.warnings_file,
        warning_as_error=args.W,
        keep_going=args.keep_going,
        tags=args.tag
    )

if __name__ == "__main__":
    main()
