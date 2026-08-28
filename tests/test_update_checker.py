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
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.hermesbaby.update_checker import (
    get_cache_dir,
    get_check_file,
    should_check_for_updates,
    mark_checked,
    get_latest_version_from_pypi,
    compare_versions,
    check_for_updates,
)


@pytest.fixture
def temp_cache_dir(tmp_path, monkeypatch):
    """Create a temporary cache directory for testing."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    
    def mock_get_cache_dir():
        return cache_dir
    
    monkeypatch.setattr("src.hermesbaby.update_checker.get_cache_dir", mock_get_cache_dir)
    return cache_dir


def test_get_cache_dir():
    """Test that cache directory is created correctly."""
    cache_dir = get_cache_dir()
    assert cache_dir.exists()
    assert cache_dir.is_dir()
    assert "hermesbaby" in str(cache_dir)


def test_should_check_for_updates_no_file(temp_cache_dir):
    """Test that should_check_for_updates returns True when no check file exists."""
    assert should_check_for_updates() is True


def test_should_check_for_updates_old_check(temp_cache_dir):
    """Test that should_check_for_updates returns True when last check is old."""
    check_file = get_check_file()
    old_date = datetime.now() - timedelta(days=2)
    
    with open(check_file, "w") as f:
        json.dump({"last_check": old_date.isoformat()}, f)
    
    assert should_check_for_updates() is True


def test_should_check_for_updates_recent_check(temp_cache_dir):
    """Test that should_check_for_updates returns False when last check is recent."""
    check_file = get_check_file()
    recent_date = datetime.now() - timedelta(hours=12)
    
    with open(check_file, "w") as f:
        json.dump({"last_check": recent_date.isoformat()}, f)
    
    assert should_check_for_updates() is False


def test_should_check_for_updates_corrupted_file(temp_cache_dir):
    """Test that should_check_for_updates returns True when check file is corrupted."""
    check_file = get_check_file()
    
    with open(check_file, "w") as f:
        f.write("invalid json")
    
    assert should_check_for_updates() is True


def test_mark_checked(temp_cache_dir):
    """Test that mark_checked creates a valid check file."""
    mark_checked()
    
    check_file = get_check_file()
    assert check_file.exists()
    
    with open(check_file, "r") as f:
        data = json.load(f)
        assert "last_check" in data
        # Verify that the timestamp is recent (within last minute)
        last_check = datetime.fromisoformat(data["last_check"])
        assert datetime.now() - last_check < timedelta(minutes=1)


def test_compare_versions_equal():
    """Test comparing equal versions."""
    assert compare_versions("1.2.3", "1.2.3") == 0


def test_compare_versions_less():
    """Test comparing older version."""
    assert compare_versions("1.2.3", "1.2.4") == -1
    assert compare_versions("1.2.3", "1.3.0") == -1
    assert compare_versions("1.2.3", "2.0.0") == -1


def test_compare_versions_greater():
    """Test comparing newer version."""
    assert compare_versions("1.2.4", "1.2.3") == 1
    assert compare_versions("1.3.0", "1.2.3") == 1
    assert compare_versions("2.0.0", "1.2.3") == 1


def test_compare_versions_different_lengths():
    """Test comparing versions with different number of parts."""
    assert compare_versions("1.2", "1.2.0") == 0
    assert compare_versions("1.2", "1.2.1") == -1
    assert compare_versions("1.2.1", "1.2") == 1


def test_compare_versions_invalid():
    """Test comparing invalid versions returns 0."""
    assert compare_versions("invalid", "1.2.3") == 0
    assert compare_versions("1.2.3", "invalid") == 0


@patch("requests.get")
def test_get_latest_version_from_pypi_success(mock_get):
    """Test successful fetch from PyPI."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"info": {"version": "1.2.3"}}
    mock_get.return_value = mock_response
    
    version = get_latest_version_from_pypi("hermesbaby")
    assert version == "1.2.3"
    mock_get.assert_called_once_with("https://pypi.org/pypi/hermesbaby/json", timeout=5)


@patch("requests.get")
def test_get_latest_version_from_pypi_failure(mock_get):
    """Test that get_latest_version_from_pypi returns None on network error."""
    mock_get.side_effect = Exception("Network error")
    
    version = get_latest_version_from_pypi("hermesbaby")
    assert version is None


def test_check_for_updates_no_update(temp_cache_dir):
    """Test check_for_updates when no update is available."""
    with patch("src.hermesbaby.update_checker.get_latest_version_from_pypi") as mock_get_latest:
        mock_get_latest.return_value = "1.0.0"
        
        result = check_for_updates("1.0.0")
        assert result is None


def test_check_for_updates_update_available(temp_cache_dir):
    """Test check_for_updates when an update is available."""
    with patch("src.hermesbaby.update_checker.get_latest_version_from_pypi") as mock_get_latest:
        mock_get_latest.return_value = "2.0.0"
        
        result = check_for_updates("1.0.0")
        assert result == "2.0.0"


def test_check_for_updates_current_newer(temp_cache_dir):
    """Test check_for_updates when current version is newer than PyPI."""
    with patch("src.hermesbaby.update_checker.get_latest_version_from_pypi") as mock_get_latest:
        mock_get_latest.return_value = "1.0.0"
        
        result = check_for_updates("2.0.0")
        assert result is None


def test_check_for_updates_pypi_failure(temp_cache_dir):
    """Test check_for_updates when PyPI fetch fails."""
    with patch("src.hermesbaby.update_checker.get_latest_version_from_pypi") as mock_get_latest:
        mock_get_latest.return_value = None
        
        result = check_for_updates("1.0.0")
        assert result is None


def test_check_for_updates_respects_timing(temp_cache_dir):
    """Test that check_for_updates respects the daily check limit."""
    with patch("src.hermesbaby.update_checker.get_latest_version_from_pypi") as mock_get_latest:
        mock_get_latest.return_value = "2.0.0"
        
        # First check should work
        result1 = check_for_updates("1.0.0")
        assert result1 == "2.0.0"
        
        # Second check within same day should not check PyPI
        mock_get_latest.reset_mock()
        result2 = check_for_updates("1.0.0")
        assert result2 is None
        mock_get_latest.assert_not_called()
