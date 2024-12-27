import os
from paver import tasks as paver


def main():
    pavement_path = os.path.join(os.path.dirname(__file__), "pavement.py")
    paver.main(["--file", pavement_path, "--quiet", "hello"])


if __name__ == "__main__":
    main()
