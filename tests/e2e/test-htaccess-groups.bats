#!/usr/bin/env bats

load "test_helper/load.bash"

setup() {
    mkdir -p "$BATS_TEST_TMPDIR/mock"
    cat > "$BATS_TEST_TMPDIR/mock/pyad.py" <<'EOF'
from types import SimpleNamespace

memberships = {
    "alice": ["team-z", "team-a-child", "team-a", "team-m"],
    "bob": ["team-z", "team-b", "team-a-child", "team-a"],
    "nobody": [],
}

class ADUser:
    @staticmethod
    def from_cn(name):
        return SimpleNamespace(get_attribute=lambda attribute: memberships[name])

class ADGroup:
    @staticmethod
    def from_dn(dn):
        return SimpleNamespace(cn=dn)

aduser = SimpleNamespace(ADUser=ADUser)
adgroup = SimpleNamespace(ADGroup=ADGroup)
EOF
    export PYTHONPATH="$BATS_TEST_TMPDIR/mock${PYTHONPATH:+:$PYTHONPATH}"
}

@test "hb htaccess groups sorts a member's groups" {
    run python -m hermesbaby htaccess groups alice
    assert_success
    assert_output "$(cat <<'EOF'
Groups for member alice:
  team-a
  team-a-child
  team-m
  team-z
EOF
)"
}

@test "hb htaccess groups sorts each member's groups and their shared groups" {
    run python -m hermesbaby htaccess groups alice bob
    assert_success
    assert_output "$(cat <<'EOF'
Groups for member alice:
  team-a
  team-a-child
  team-m
  team-z

Groups for member bob:
  team-a
  team-a-child
  team-b
  team-z

Shared groups between all members:
  team-a
  team-a-child
  team-z
EOF
)"
}

@test "hb htaccess groups handles members with no groups" {
    run python -m hermesbaby htaccess groups alice nobody
    assert_success
    assert_output "$(cat <<'EOF'
Groups for member alice:
  team-a
  team-a-child
  team-m
  team-z

Groups for member nobody:

Shared groups between all members:
EOF
)"
}
