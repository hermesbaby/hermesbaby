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

import os
import pytest
import sys
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Mock pyad module before any imports that use it
sys.modules['pyad'] = MagicMock()
sys.modules['pyad.aduser'] = MagicMock()
sys.modules['pyad.adgroup'] = MagicMock()


class MockADUser:
    """Mock Active Directory User"""
    def __init__(self, cn, dn):
        self.cn = cn
        self.dn = dn


class MockADGroup:
    """Mock Active Directory Group"""
    def __init__(self, cn, dn, members=None):
        self.cn = cn
        self.dn = dn
        self._members = members or []
    
    def get_members(self):
        return self._members


@pytest.fixture
def mock_aduser():
    """Fixture to mock pyad.aduser.ADUser"""
    with patch('hermesbaby.web_access_ctrl.create_htaccess_entries.aduser') as mock:
        yield mock


@pytest.fixture
def mock_adgroup():
    """Fixture to mock pyad.adgroup.ADGroup"""
    with patch('hermesbaby.web_access_ctrl.create_htaccess_entries.adgroup') as mock:
        yield mock


@pytest.fixture
def sample_yaml_basic(tmp_path):
    """Create a basic htaccess.yaml file"""
    yaml_file = tmp_path / "htaccess.yaml"
    content = {
        "ldap-user": ["user1", "user2"],
        "ldap-group": ["group1"]
    }
    with open(yaml_file, "w") as f:
        yaml.dump(content, f)
    return yaml_file


@pytest.fixture
def sample_yaml_with_maintainers(tmp_path):
    """Create an htaccess.yaml file with maintainers section"""
    yaml_file = tmp_path / "htaccess.yaml"
    content = {
        "ldap-user": ["user1", "user2"],
        "ldap-group": ["group1"],
        "maintainers": {
            "ldap-user": ["maintainer1", "maintainer2"],
            "ldap-group": ["maintainerGroup"]
        }
    }
    with open(yaml_file, "w") as f:
        yaml.dump(content, f)
    return yaml_file


def test_basic_htaccess_generation(tmp_path, sample_yaml_basic, mock_aduser, mock_adgroup):
    """Test basic .htaccess generation without maintainers"""
    from hermesbaby.web_access_ctrl.create_htaccess_entries import main
    
    # Mock LDAP responses
    # For users, return user objects
    def mock_user_lookup(name):
        if name.startswith('user'):
            return MockADUser(name, f"CN={name},OU=Users,DC=example,DC=com")
        # For groups, throw exception so it falls through to adgroup lookup
        raise Exception(f"Not a user: {name}")
    
    # For groups, return group objects
    def mock_group_lookup(name):
        if name.startswith('group'):
            return MockADGroup(name, f"CN={name},OU=Groups,DC=example,DC=com")
        raise Exception(f"Not a group: {name}")
    
    mock_aduser.ADUser.from_cn.side_effect = mock_user_lookup
    mock_adgroup.ADGroup.from_cn.side_effect = mock_group_lookup
    
    out_file = tmp_path / ".htaccess"
    
    # Run the main function
    main([], sample_yaml_basic, out_file, None)
    
    # Verify output file exists
    assert out_file.exists()
    
    # Verify content
    content = out_file.read_text()
    assert "<RequireAny>" in content
    assert "Require user user1" in content
    assert "Require user user2" in content
    assert "Require ldap-group CN=group1,OU=Groups,DC=example,DC=com" in content
    assert "</RequireAny>" in content


def test_htaccess_with_maintainers_users_only(tmp_path, mock_aduser, mock_adgroup):
    """Test .htaccess generation with maintainers (users only)"""
    from hermesbaby.web_access_ctrl.create_htaccess_entries import main
    
    # Create YAML with maintainers
    yaml_file = tmp_path / "htaccess.yaml"
    content = {
        "ldap-user": ["user1"],
        "maintainers": {
            "ldap-user": ["maintainer1", "maintainer2"]
        }
    }
    with open(yaml_file, "w") as f:
        yaml.dump(content, f)
    
    # Mock LDAP responses
    def mock_user_lookup(name):
        return MockADUser(name, f"CN={name},OU=Users,DC=example,DC=com")
    
    mock_aduser.ADUser.from_cn.side_effect = mock_user_lookup
    mock_adgroup.ADGroup.from_cn.side_effect = Exception("Not found")
    
    out_file = tmp_path / ".htaccess"
    
    # Run the main function
    main([], yaml_file, out_file, None)
    
    # Verify output file exists
    assert out_file.exists()
    
    # Verify content includes ErrorDocument
    content = out_file.read_text()
    assert "ErrorDocument 401" in content
    assert "maintainer1" in content
    assert "maintainer2" in content
    assert "Access denied" in content
    assert "Please contact one of the maintainers" in content


def test_htaccess_with_maintainers_groups(tmp_path, mock_aduser, mock_adgroup):
    """Test .htaccess generation with maintainers including groups (expanded)"""
    from hermesbaby.web_access_ctrl.create_htaccess_entries import main
    
    # Create YAML with maintainers including a group
    yaml_file = tmp_path / "htaccess.yaml"
    content = {
        "ldap-user": ["user1"],
        "maintainers": {
            "ldap-user": ["maintainer1"],
            "ldap-group": ["maintainerGroup"]
        }
    }
    with open(yaml_file, "w") as f:
        yaml.dump(content, f)
    
    # Mock LDAP responses
    def mock_user_lookup(name):
        if name.startswith('user') or name.startswith('maintainer'):
            return MockADUser(name, f"CN={name},OU=Users,DC=example,DC=com")
        raise Exception(f"Not a user: {name}")
    
    # Mock group with members
    group_members = [
        MockADUser("groupMember1", "CN=groupMember1,OU=Users,DC=example,DC=com"),
        MockADUser("groupMember2", "CN=groupMember2,OU=Users,DC=example,DC=com")
    ]
    
    def mock_group_lookup(name):
        if name == "maintainerGroup":
            return MockADGroup(name, f"CN={name},OU=Groups,DC=example,DC=com", group_members)
        raise Exception(f"Not a group: {name}")
    
    mock_aduser.ADUser.from_cn.side_effect = mock_user_lookup
    mock_adgroup.ADGroup.from_cn.side_effect = mock_group_lookup
    
    out_file = tmp_path / ".htaccess"
    
    # Run the main function
    main([], yaml_file, out_file, None)
    
    # Verify output file exists
    assert out_file.exists()
    
    # Verify content includes ErrorDocument with expanded group members
    content = out_file.read_text()
    assert "ErrorDocument 401" in content
    assert "maintainer1" in content
    # Group members should be expanded and included
    assert "groupMember1" in content
    assert "groupMember2" in content


def test_htaccess_without_maintainers_no_error_document(tmp_path, sample_yaml_basic, mock_aduser, mock_adgroup):
    """Test that ErrorDocument is NOT generated when maintainers section is absent"""
    from hermesbaby.web_access_ctrl.create_htaccess_entries import main
    
    # Mock LDAP responses
    def mock_user_lookup(name):
        if name.startswith('user'):
            return MockADUser(name, f"CN={name},OU=Users,DC=example,DC=com")
        raise Exception(f"Not a user: {name}")
    
    def mock_group_lookup(name):
        if name.startswith('group'):
            return MockADGroup(name, f"CN={name},OU=Groups,DC=example,DC=com")
        raise Exception(f"Not a group: {name}")
    
    mock_aduser.ADUser.from_cn.side_effect = mock_user_lookup
    mock_adgroup.ADGroup.from_cn.side_effect = mock_group_lookup
    
    out_file = tmp_path / ".htaccess"
    
    # Run the main function
    main([], sample_yaml_basic, out_file, None)
    
    # Verify output file exists
    assert out_file.exists()
    
    # Verify ErrorDocument is NOT present
    content = out_file.read_text()
    assert "ErrorDocument 401" not in content


def test_htaccess_maintainers_empty_section(tmp_path, mock_aduser, mock_adgroup):
    """Test .htaccess generation when maintainers section exists but is empty"""
    from hermesbaby.web_access_ctrl.create_htaccess_entries import main
    
    # Create YAML with empty maintainers
    yaml_file = tmp_path / "htaccess.yaml"
    content = {
        "ldap-user": ["user1"],
        "maintainers": {}
    }
    with open(yaml_file, "w") as f:
        yaml.dump(content, f)
    
    # Mock LDAP responses
    def mock_user_lookup(name):
        return MockADUser(name, f"CN={name},OU=Users,DC=example,DC=com")
    
    mock_aduser.ADUser.from_cn.side_effect = mock_user_lookup
    mock_adgroup.ADGroup.from_cn.side_effect = Exception("Not found")
    
    out_file = tmp_path / ".htaccess"
    
    # Run the main function
    main([], yaml_file, out_file, None)
    
    # Verify output file exists
    assert out_file.exists()
    
    # Verify ErrorDocument is NOT present when maintainers is empty
    content = out_file.read_text()
    assert "ErrorDocument 401" not in content


def test_maintainers_list_formatting(tmp_path, mock_aduser, mock_adgroup):
    """Test that maintainers are properly formatted in the error message"""
    from hermesbaby.web_access_ctrl.create_htaccess_entries import main
    
    # Create YAML with multiple maintainers
    yaml_file = tmp_path / "htaccess.yaml"
    content = {
        "ldap-user": ["user1"],
        "maintainers": {
            "ldap-user": ["alice", "bob", "charlie"]
        }
    }
    with open(yaml_file, "w") as f:
        yaml.dump(content, f)
    
    # Mock LDAP responses
    def mock_user_lookup(name):
        return MockADUser(name, f"CN={name},OU=Users,DC=example,DC=com")
    
    mock_aduser.ADUser.from_cn.side_effect = mock_user_lookup
    mock_adgroup.ADGroup.from_cn.side_effect = Exception("Not found")
    
    out_file = tmp_path / ".htaccess"
    
    # Run the main function
    main([], yaml_file, out_file, None)
    
    # Verify maintainers are formatted correctly (comma-separated)
    content = out_file.read_text()
    # Should contain all maintainers with commas
    assert "alice" in content
    assert "bob" in content
    assert "charlie" in content
    # Check they're in a comma-separated list
    assert "alice, bob, charlie" in content or "alice,bob,charlie" in content.replace(" ", "")


def test_backward_compatibility(tmp_path, sample_yaml_basic, mock_aduser, mock_adgroup):
    """Test that existing functionality still works without maintainers section"""
    from hermesbaby.web_access_ctrl.create_htaccess_entries import main
    
    # Mock LDAP responses
    def mock_user_lookup(name):
        if name.startswith('user'):
            return MockADUser(name, f"CN={name},OU=Users,DC=example,DC=com")
        raise Exception(f"Not a user: {name}")
    
    def mock_group_lookup(name):
        if name.startswith('group'):
            return MockADGroup(name, f"CN={name},OU=Groups,DC=example,DC=com")
        raise Exception(f"Not a group: {name}")
    
    mock_aduser.ADUser.from_cn.side_effect = mock_user_lookup
    mock_adgroup.ADGroup.from_cn.side_effect = mock_group_lookup
    
    out_file = tmp_path / ".htaccess"
    
    # Should work fine without maintainers
    main([], sample_yaml_basic, out_file, None)
    
    assert out_file.exists()
    content = out_file.read_text()
    assert "<RequireAny>" in content
    assert "</RequireAny>" in content
