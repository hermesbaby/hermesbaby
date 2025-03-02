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
from pyad import adgroup

def get_group_members(group_name):
    try:
        group = adgroup.ADGroup.from_cn(group_name)
        members = group.get_members()
        return [member.cn for member in members]
    except Exception as e:
        print(f"An error occurred for group {group_name}: {e}")
        return []

def main(group_names):
    for group_name in group_names:
        members = get_group_members(group_name)
        print(f"Members of group {group_name}:")
        print(", ".join(sorted(members)))
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get members of specified Active Directory groups.")
    parser.add_argument('group_names', metavar='G', type=str, nargs='+', help='List of group names to check')
    args = parser.parse_args()

    main(args.group_names)
