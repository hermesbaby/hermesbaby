import argparse
import os
import sys
from paver import tasks as paver


def main():
    options = sys.argv[1:] or ["hello"]
    pavement_path = os.path.join(os.path.dirname(__file__), "pavement.py")
    paver.main(["--file", pavement_path, "--quiet"] + options)


if __name__ == "__main__":
    main()
