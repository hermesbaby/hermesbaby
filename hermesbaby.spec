# -*- mode: python ; coding: utf-8 -*-

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

import sys
import os
from pathlib import Path

# Get the source directory
src_dir = Path(os.getcwd()) / "src"
hermesbaby_dir = src_dir / "hermesbaby"

# Get cookiecutter package data
import cookiecutter
cookiecutter_path = Path(cookiecutter.__file__).parent

# Platform-specific binary handling for Linux shared library issues
binaries = []
if not sys.platform.startswith('win'):
    # On Linux, explicitly include Python shared library if found
    import sysconfig
    python_lib_path = sysconfig.get_config_var('LIBDIR')
    if python_lib_path:
        python_lib_name = sysconfig.get_config_var('LDLIBRARY')
        if python_lib_name and os.path.exists(os.path.join(python_lib_path, python_lib_name)):
            binaries.append((os.path.join(python_lib_path, python_lib_name), '.'))
        # Also try the instsoname variant
        python_lib_instsoname = sysconfig.get_config_var('INSTSONAME') 
        if python_lib_instsoname and os.path.exists(os.path.join(python_lib_path, python_lib_instsoname)):
            binaries.append((os.path.join(python_lib_path, python_lib_instsoname), '.'))

# Data files to include
datas = [
    # Templates directory
    (str(hermesbaby_dir / "templates"), "hermesbaby/templates"),
    # Configuration files
    (str(hermesbaby_dir / "external_tools.json"), "hermesbaby"),
    (str(hermesbaby_dir / "vscode-extensions"), "hermesbaby/vscode-extensions"),
    (str(hermesbaby_dir / "htaccess.yaml"), "hermesbaby"),
    (str(hermesbaby_dir / "Kconfig"), "hermesbaby"),
    (str(hermesbaby_dir / "Makefile"), "hermesbaby"),
    (str(hermesbaby_dir / "tools"), "hermesbaby/tools"),
    (str(hermesbaby_dir / "plantuml.config"), "hermesbaby"),
    (str(hermesbaby_dir / "puppeteer.config.json"), "hermesbaby"),
    (str(hermesbaby_dir / "scoopfile-build.json"), "hermesbaby"),
    # Static files
    (str(hermesbaby_dir / "html_static"), "hermesbaby/html_static"),
    # Setup scripts
    (str(hermesbaby_dir / "setup.sh"), "hermesbaby"),
    (str(hermesbaby_dir / "setup.cmd"), "hermesbaby"),
    (str(hermesbaby_dir / "setup.ps1"), "hermesbaby"),
    # Cookiecutter data files
    (str(cookiecutter_path / "VERSION.txt"), "cookiecutter"),
]

# Conditionally add package subdirectories that exist and have content
package_dirs = [
    "atlassian-admin",
    "loflot",
    "pre-post-build",
    "rst-frontmatter",
    "tag-anything",
    "toctree-only",
    "toolbox",
    "update",
    "web_access_ctrl"
]

for pkg_dir in package_dirs:
    pkg_path = hermesbaby_dir / pkg_dir
    if pkg_path.exists():
        # Check if directory has Python files or other meaningful content
        try:
            has_content = any(
                f.suffix in ['.py', '.yaml', '.yml', '.json', '.txt', '.md']
                for f in pkg_path.rglob('*')
                if f.is_file() and not f.name.startswith('.') and '__pycache__' not in str(f)
            )
            if has_content:
                datas.append((str(pkg_path), f"hermesbaby/{pkg_dir}"))
        except Exception:
            # If we can't read the directory, skip it
            pass
# Note: Package directories are conditionally included based on content
# Tools directory is excluded as it contains downloaded tools that will be fetched at runtime

# Build dynamic hidden imports list based on available package directories
base_hiddenimports = [
    # Core hermesbaby package
    'hermesbaby',

    # CLI framework
    'typer',

    # Configuration management
    'kconfiglib',

    # Template engine
    'cookiecutter',

    # HTTP requests
    'requests',
    'urllib3',

    # Documentation framework
    'sphinx',
    'sphinx.util',
    'sphinx.util.logging',
    'sphinx.ext.intersphinx',
    'sphinx.highlighting',

    # Git operations
    'git',

    # Date/time handling
    'datetime',
    'tzlocal',

    # Document processing
    'docutils',
    'docutils.nodes',
    'docutils.parsers.rst',
    'docutils.parsers.rst.roles',

    # Web scraping/parsing
    'bs4',

    # YAML processing
    'yaml',

    # Bibliography
    'pybtex',
    'pybtex.style.formatting.unsrt',
    'pybtex.style.labels.alpha',
    'pybtex.plugin',

    # Robot Framework lexer
    'robotframeworklexer',

    # Traceability
    'mlx.traceability',

    # Package resources
    'pkg_resources',

    # Standard library modules that might need explicit inclusion
    'importlib.metadata',
    'importlib.resources',
    'json',
    'platform',
    'subprocess',
    'pathlib',
    'ssl',
    'html',
    're',
    'runpy',
    'getpass',
]

# Add package-specific hidden imports only if they were included in datas
dynamic_hiddenimports = []
for pkg_dir in package_dirs:
    pkg_path = hermesbaby_dir / pkg_dir
    if pkg_path.exists():
        try:
            has_content = any(
                f.suffix in ['.py', '.yaml', '.yml', '.json', '.txt', '.md']
                for f in pkg_path.rglob('*')
                if f.is_file() and not f.name.startswith('.') and '__pycache__' not in str(f)
            )
            if has_content:
                dynamic_hiddenimports.append(f'hermesbaby.{pkg_dir}')
        except Exception:
            pass

hiddenimports = base_hiddenimports + dynamic_hiddenimports

# Analysis configuration
a = Analysis(
    [str(hermesbaby_dir / "__main__.py")],
    pathex=[str(src_dir)],
    binaries=binaries,  # Include platform-specific binaries
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Only exclude clearly unused GUI packages
        'turtle', 'pydoc_data',
        # Exclude unused networking/crypto (if not needed)
        'ftplib', 'poplib', 'imaplib',
    ],
    noarchive=False,
    optimize=2,  # Enable Python optimization level 2
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    # Add explicit handling for shared library issues on Linux
)

# Package configuration
pyz = PYZ(a.pure)

# Create COLLECT for one-directory mode (faster startup)
exe = EXE(
    pyz,
    a.scripts,
    [],  # Empty - binaries and datas will be in COLLECT
    name='hb',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Disable stripping on all platforms to avoid shared library issues
    upx=True if sys.platform.startswith('win') else False,  # UPX only on Windows
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Add additional flags for Linux shared library handling
    **({'exclude_binaries': True} if not sys.platform.startswith('win') else {}),
)

# One-directory distribution for faster startup
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,  # Disable stripping on all platforms to avoid shared library issues
    upx=True if sys.platform.startswith('win') else False,  # UPX only on Windows
    upx_exclude=[],
    name='hb-dist'
)
