"""
Script for bumping version numbers based on specific label combinations
from pull request events.

This script works in two modes:

1. get_version:
   Reads the current version from 'version.yaml' and prints it (with no extra output).

2. bump:
   Reads the current version from 'version.yaml', checks the PR labels (from the
   environment variable PR_LABELS), and if the required label combinations are found,
   bumps the version accordingly. For a "prd" label, the major version is bumped (with
   minor reset to 0); for a "dev" label (and not "prd"), the minor version is bumped.
   If no matching label combinations are found, the version is left unchanged.
"""

import json
import os
import sys

import yaml

# Predefine the allowed label combinations that trigger a version bump.
REQUIRED_LABEL_COMBINATIONS = [
    ["dev", "train"],
    ["dev", "inference"],
    ["prd", "train"],
    ["prd", "inference"],
    ["model", "dev"],
    ["model", "prd"],
]


def get_labels_from_env(env_var_name: str = "PR_LABELS") -> list[str]:
    """
    Retrieve JSON-formatted labels from an environment variable and return a list of label names.
    """
    pr_labels_json = os.getenv(env_var_name, "[]")
    try:
        pr_labels = json.loads(pr_labels_json)
    except json.JSONDecodeError:
        pr_labels = []
    return [
        label["name"]
        for label in pr_labels
        if isinstance(label, dict) and "name" in label
    ]


def has_label_combination(labels: list[str], combinations: list[list[str]]) -> bool:
    """
    Returns True if any of the provided label combinations is present in the labels list.
    """
    return any(
        all(req_label in labels for req_label in combo) for combo in combinations
    )


def read_version(file_path: str) -> tuple[int, int]:
    """
    Reads the version from a YAML file in the format "major.minor".
    If the file or the version key is missing, returns (0, 0).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            version_str = data.get("version", "0.0")
    except FileNotFoundError:
        version_str = "0.0"
    try:
        major, minor = map(int, version_str.split("."))
    except ValueError:
        major, minor = 0, 0
    return major, minor


def write_version(file_path: str, major: int, minor: int) -> None:
    """
    Writes the version (formatted as "major.minor") back to the given YAML file.
    """
    data = {"version": f"{major}.{minor}"}
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    print(f"Version updated to {major}.{minor}")


def get_current_version():
    """
    Reads and prints the current version from version.yaml.
    In 'get_version' mode, only the version string is printed.
    """
    version_file = "version.yaml"
    _, _ = read_version(version_file)  # Can be used if additional logic is needed.
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        version_str = data.get("version", "0.0")
    except FileNotFoundError:
        version_str = "0.0"
    # Print only the version number (trimmed) so that it can be captured cleanly.
    print(version_str.strip())


def bump_version():
    """
    Reads the current version from version.yaml, checks if the PR labels include any of
    the required combinations, and if so, bumps the version accordingly.
    """
    # Get the labels from the environment.
    labels = get_labels_from_env()
    print(f"Labels: {labels}")
    if not has_label_combination(labels, REQUIRED_LABEL_COMBINATIONS):
        print("No matching label combinations found. Version not bumped.")
        sys.exit(0)  # Exit without error so that CI/CD continues if no bump is needed.

    version_file = "version.yaml"
    major, minor = read_version(version_file)

    # Determine bump type.
    if "prd" in labels:
        # Bump major version and reset minor.
        major += 1
        minor = 0
    elif "dev" in labels:
        # Bump minor version.
        minor += 1
    else:
        print("No matching labels for version bump.")
        sys.exit(0)

    # Write out the new version.
    write_version(version_file, major, minor)


def main():
    if len(sys.argv) < 2:
        print("Usage: bump_versions.py [get_version|bump]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "get_version":
        get_current_version()
    elif mode == "bump":
        bump_version()
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
