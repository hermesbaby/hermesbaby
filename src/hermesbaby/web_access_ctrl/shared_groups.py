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
from pyad import aduser, adgroup

def get_member_groups(membername):
    try:
        member = aduser.ADUser.from_cn(membername)
        groups = member.get_attribute("memberOf")
        return [adgroup.ADGroup.from_dn(group).cn for group in groups]
    except Exception as e:
        print(f"An error occurred for member {membername}: {e}")
        return []

def main(membernames):
    all_member_groups = {}

    for membername in membernames:
        groups = get_member_groups(membername)
        all_member_groups[membername] = groups
        print(f"Groups for member {membername}:")
        for group in groups:
            print(f"  {group}")
        print()

    if len(membernames) > 1:
        shared_groups = set(all_member_groups[membernames[0]])
        for groups in all_member_groups.values():
            shared_groups &= set(groups)

        print("Shared groups between all members:")
        for group in shared_groups:
            print(f"  {group}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get group memberships for specified Active Directory members.")
    parser.add_argument('membernames', metavar='U', type=str, nargs='+', help='List of membernames to check')
    args = parser.parse_args()

    main(args.membernames)
