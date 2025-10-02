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


from enum import Enum, auto
import sys
import subprocess
import shutil
import importlib.metadata

class InstallKind(Enum):
    PIPX = auto()
    VIRTUALENV = auto()
    GLOBAL = auto()
    EDITABLE = auto()
    SYSTEM = auto()
    UNKNOWN = auto()

def _is_editable() -> bool:
    try:
        dist = importlib.metadata.distribution("hermesbaby")
        for file in dist.files or []:
            if str(file).endswith(".egg-link"):
                return True
        return False
    except importlib.metadata.PackageNotFoundError:
        return False

def _is_pipx() -> bool:
    if not shutil.which("pipx"):
        return False
    try:
        result = subprocess.run(["pipx", "list"], capture_output=True, text=True, check=True)
        return "hermesbaby" in result.stdout
    except subprocess.CalledProcessError:
        return False

def _is_virtualenv() -> bool:
    return sys.prefix != sys.base_prefix

def _is_system_install() -> bool:
    try:
        import hermesbaby
        return hermesbaby.__file__.startswith(("/usr/", "/lib/", "/opt/"))
    except ImportError:
        return False

def detect_install_kind() -> InstallKind:
    if _is_editable():
        return InstallKind.EDITABLE
    if _is_pipx():
        return InstallKind.PIPX
    if _is_virtualenv():
        return InstallKind.VIRTUALENV
    if _is_system_install():
        return InstallKind.SYSTEM
    if sys.prefix == sys.base_prefix:
        return InstallKind.GLOBAL
    return InstallKind.UNKNOWN
