"""The missing docstring"""

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

import argparse
import os
import sys
import yaml
from pyad import aduser, adgroup


def get_ldap_path(name):
    try:
        user = aduser.ADUser.from_cn(name)
        if user and user.dn:
            if "OU=Groups" in user.dn:
                return "group", f"Require ldap-group {user.dn}"
            else:
                return "user", f"Require ldap-user {user.dn}"
    except Exception:
        pass

    try:
        group = adgroup.ADGroup.from_cn(name)
        if group and group.dn:
            if "OU=Groups" in group.dn:
                return "group", f"Require ldap-group {group.dn}"
            else:
                return "user", f"Require ldap-user {group.dn}"
    except Exception as e:
        print(f"Warning: Could not find entity {name}", file=sys.stderr)
        return None, None

    print(f"Could not determine the type for {name}", file=sys.stderr)
    return None, None


def expand_users(ldap_groups):
    print(
        f"Group expansion is enabled. Begin searching for users of the given groups. This may take 1..3 minutes; grab a coffee ...",
        file=sys.stderr,
    )
    all_users = set()
    for group_name in ldap_groups:
        try:
            group = adgroup.ADGroup.from_cn(group_name)
            if group:
                members = group.get_members()
                for member in members:
                    all_users.add(member.cn)
        except Exception as e:
            print(
                f"An error occurred while expanding group {group_name}: {e}",
                file=sys.stderr,
            )
    return sorted(all_users)


def main(names, yaml_file, out_file, expand_file):
    all_names = set(names)
    ldap_groups = []

    if yaml_file:
        with open(yaml_file, "r") as file:
            config = yaml.safe_load(file)
            ldap_groups = config.get("ldap-group", [])
            ldap_users = config.get("ldap-user", [])
            all_names.update(ldap_groups + ldap_users)

    users = []
    groups = []

    for name in all_names:
        type_, ldap_path = get_ldap_path(name)
        if ldap_path:
            if type_ == "user":
                users.append(ldap_path)
            elif type_ == "group":
                groups.append(ldap_path)

    users.sort()
    groups.sort()

    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    with open(out_file, "w") as file:
        for user in users:
            print(user, file=file)
        for group in groups:
            print(group, file=file)
        print("Satisfy Any", file=file)

    print(f"LDAP objects written to {out_file}", file=sys.stderr)

    if expand_file:
        expanded_users = expand_users(ldap_groups)
        with open(expand_file, "w") as file:
            yaml.dump({"expanded-users": expanded_users}, file)
        print(f"Expanded users written to {expand_file}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get LDAP paths for specified Active Directory users or groups."
    )

    parser.add_argument(
        "names",
        type=str,
        nargs="*",
        metavar="N",
        help="List of usernames or group names to check",
    )
    parser.add_argument(
        "--yaml", type=str, help="YAML file specifying ldap-group and ldap-user entries"
    )
    parser.add_argument("--out", help="Output .htaccess file path")
    parser.add_argument(
        "--expand",
        type=str,
        help="Output YAML file to expand all users from ldap groups",
    )

    args = parser.parse_args()
    main(args.names, args.yaml, args.out, args.expand)
