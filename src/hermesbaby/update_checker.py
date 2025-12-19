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

import json
import os
from datetime import datetime, timedelta
from pathlib import Path


def get_cache_dir():
    """Get the cache directory for storing update check information."""
    # Use platform-appropriate cache directory
    if os.name == "nt":  # Windows
        cache_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "hermesbaby"
    else:  # Unix-like (Linux, macOS)
        cache_dir = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "hermesbaby"
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_check_file():
    """Get the path to the update check file."""
    return get_cache_dir() / "update_check.json"


def should_check_for_updates():
    """
    Determine if we should check for updates.
    Returns True if more than 24 hours have passed since the last check.
    """
    check_file = get_check_file()
    
    if not check_file.exists():
        return True
    
    try:
        with open(check_file, "r") as f:
            data = json.load(f)
            last_check = datetime.fromisoformat(data.get("last_check", "2000-01-01T00:00:00"))
            return datetime.now() - last_check > timedelta(days=1)
    except (json.JSONDecodeError, ValueError, KeyError):
        # If file is corrupted, check again
        return True


def mark_checked():
    """Mark that we've checked for updates."""
    check_file = get_check_file()
    data = {"last_check": datetime.now().isoformat()}
    
    try:
        with open(check_file, "w") as f:
            json.dump(data, f)
    except Exception:
        # Silently fail if we can't write the file
        pass


def get_latest_version_from_pypi(package_name, timeout=5):
    """
    Fetch the latest version of a package from PyPI.
    
    Args:
        package_name: Name of the package on PyPI
        timeout: Request timeout in seconds
        
    Returns:
        Latest version string, or None if the request fails
    """
    try:
        # Lazy import to avoid startup cost
        import requests
        
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data["info"]["version"]
    except Exception:
        # Silently fail on any error (network issues, PyPI down, etc.)
        return None


def compare_versions(version1, version2):
    """
    Compare two version strings.
    
    Args:
        version1: First version string (e.g., "1.2.3")
        version2: Second version string (e.g., "1.2.4")
        
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    try:
        # Split versions and convert to integers for comparison
        parts1 = [int(x) for x in version1.split(".")]
        parts2 = [int(x) for x in version2.split(".")]
        
        # Pad shorter version with zeros
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))
        
        if parts1 < parts2:
            return -1
        elif parts1 > parts2:
            return 1
        else:
            return 0
    except (ValueError, AttributeError):
        # If comparison fails, assume versions are equal
        return 0


def check_for_updates(current_version, package_name="hermesbaby"):
    """
    Check if there's a newer version available on PyPI.
    
    Args:
        current_version: Currently installed version
        package_name: Name of the package on PyPI
        
    Returns:
        Latest version string if an update is available, None otherwise
    """
    if not should_check_for_updates():
        return None
    
    latest_version = get_latest_version_from_pypi(package_name)
    mark_checked()
    
    if latest_version is None:
        return None
    
    if compare_versions(current_version, latest_version) < 0:
        return latest_version
    
    return None
