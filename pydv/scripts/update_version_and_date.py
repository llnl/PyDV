import argparse
import fileinput
import os
from datetime import date

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pydv")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get the version number from the version file
version_file = os.path.join(SCRIPTS_DIR, "version.txt")
with open(version_file, "r") as fp:
    version = fp.read().replace("\n", "")
    version_list = version.split(".")
    major, minor, patch = int(version_list[0]), int(version_list[1]), int(version_list[2])

# Determine the new version from the specified type of change
parser = argparse.ArgumentParser()
parser.add_argument("type", choices=["major", "minor", "patch", "date"])
args = parser.parse_args().type
if args == "major":
    major += 1
    minor = 0
    patch = 0
elif args == "minor":
    minor += 1
    patch = 0
elif args == "patch":
    patch += 1
new_version = f"{major}.{minor}.{patch}"

# Replace the version everwhere in the source code where it appears.
files = [
    os.path.join(ROOT_DIR, "pyproject.toml"),
    os.path.join(ROOT_DIR, ".github", "workflows", "release.yml"),
    os.path.join(SOURCE_DIR, "pdvplot.py"),
    os.path.join(SOURCE_DIR, "pdv.py"),
    os.path.join(ROOT_DIR, "docs", "conf.py"),
    os.path.join(SCRIPTS_DIR, "version.txt"),
]
for afile in files:
    with fileinput.FileInput(afile, inplace=True) as fp:
        for line in fp:
            print(line.replace(version, new_version), end="")

# Special case: the conf.py file also wants a representation of just major.minor
with fileinput.FileInput(os.path.join(ROOT_DIR, "docs", "conf.py"), inplace=True) as fp:
    for line in fp:
        print(line.replace(f"{version_list[0]}.{version_list[1]}", f"{major}.{minor}"), end="")

# Replace the date
with open(os.path.join(SCRIPTS_DIR, "date.txt")) as fp:
    old_date = fp.read().replace("\n", "")
new_date = date.today()
new_date = f"{new_date.month:02d}.{new_date.day:02d}.{new_date.year:04d}"
files = [
    os.path.join(SOURCE_DIR, "pdv.py"),
    os.path.join(SCRIPTS_DIR, "date.txt"),
]
for afile in files:
    with fileinput.FileInput(afile, inplace=True) as fp:
        for line in fp:
            print(line.replace(old_date, new_date), end="")
