"""
Script for bumping version numbers based on specific label combinations
from pull request events. The script reads the current version from a
YAML file, checks for required label combinations, and updates the version
accordingly. It is designed to be used in a CI/CD pipeline to automate
version management.
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
    Retrieve JSON-formatted labels from an environment variable and parse them.
    Returns a list of label names.
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
    Checks if the given labels list has *any* of the specified required label combinations.
    """
    return any(
        all(req_label in labels for req_label in combo) for combo in combinations
    )


def read_version(file_path: str) -> tuple[int, int]:
    """
    Reads the version in 'major.minor' format from a YAML file.
    Returns (major, minor) as integers.
    If the file or version key is missing, defaults to '0.0'.
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
    Writes the version in 'major.minor' format back to the YAML file.
    """
    data = {"version": f"{major}.{minor}"}
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    print(f"Version updated to {major}.{minor}")


def main():
    # Retrieve labels from environment
    labels = get_labels_from_env()
    print(f"Labels: {labels}")

    # Check if any of the required label combinations is present
    if not has_label_combination(labels, REQUIRED_LABEL_COMBINATIONS):
        print("No matching label combinations found. Version not bumped.")
        sys.exit(0)

    # Read current version from version.yaml
    version_file = "version.yaml"
    major, minor = read_version(version_file)

    # Determine version bump type
    if "prd" in labels:
        # Bump major version and reset minor
        major += 1
        minor = 0
    elif "dev" in labels:
        # Bump minor version
        minor += 1
    else:
        # No action needed
        print("No matching labels for version bump.")
        sys.exit(0)

    # Write the updated version back
    write_version(version_file, major, minor)


if __name__ == "__main__":
    main()
