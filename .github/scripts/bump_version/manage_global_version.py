#!/usr/bin/env python
"""
manage_global_version.py

Usage:
  python manage_global_version.py get_version
    -> Prints the current version (X.Y) to stdout and writes
       pr_version=X.Y to GITHUB_OUTPUT

  python manage_global_version.py bump
    -> Reads PR labels from the environment to decide whether to bump major or minor.
       If 'prd' in labels, bump major and reset minor to 0.
       If 'dev' in labels, bump minor.
       If no relevant labels, do nothing.
       Writes the updated version to version.yaml
"""

import json
import os
import sys

import yaml

# List of label combinations that trigger any bump
REQUIRED_LABEL_COMBINATIONS = [
    ["dev", "train"],
    ["dev", "inference"],
    ["prd", "train"],
    ["prd", "inference"],
    ["model", "dev"],
    ["model", "prd"],
]


def get_labels_from_env(env_var="PR_LABELS"):
    """
    Retrieve a JSON array of labels from an environment variable
    (e.g., PR_LABELS='[{"name": "dev"}, {"name": "train"}]').
    Returns a list of label names.
    """
    pr_labels_json = os.getenv(env_var, "[]")
    try:
        labels_info = json.loads(pr_labels_json)
        labels = [
            item["name"]
            for item in labels_info
            if isinstance(item, dict) and "name" in item
        ]
    except json.JSONDecodeError:
        labels = []
    return labels


def has_required_label_combination(labels, combinations):
    """
    Returns True if any of the provided label combinations is found in the labels list.
    """
    return any(all(lbl in labels for lbl in combo) for combo in combinations)


def read_version(version_file="version.yaml"):
    """
    Reads version in the form "major.minor" from version.yaml.
    Returns (major, minor) as integers. If not found, defaults to (0, 0).
    """
    if not os.path.exists(version_file):
        return 0, 0

    try:
        with open(version_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as ex:
        print(f"[ERROR] Could not read {version_file}: {ex}")
        return 0, 0

    version_str = data.get("version", "0.0")
    try:
        major_str, minor_str = version_str.split(".")
        major, minor = int(major_str), int(minor_str)
        return major, minor
    except ValueError:
        print("[WARNING] version.yaml contains an invalid format. Resetting to 0.0")
        return 0, 0


def write_version(major, minor, version_file="version.yaml"):
    """
    Writes the version (formatted "major.minor") into version.yaml.
    """
    version_str = f"{major}.{minor}"
    data = {"version": version_str}
    with open(version_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    print(f"[INFO] Version updated to {version_str}")


def get_current_version_string():
    """
    Returns the current version string (e.g., "1.2").
    """
    major, minor = read_version()
    return f"{major}.{minor}"


def bump_version():
    """
    Bumps version based on labels from the environment.
      - If "prd" in labels -> Bump major, reset minor to 0
      - Else if "dev" in labels -> Bump minor
      - If no relevant labels, do nothing
    """
    labels = get_labels_from_env()
    print(f"[INFO] PR Labels: {labels}")

    if not has_required_label_combination(labels, REQUIRED_LABEL_COMBINATIONS):
        print("[INFO] No relevant label combinations found. No version bump needed.")
        return

    major, minor = read_version()

    if "prd" in labels:
        print("[INFO] 'prd' label detected. Bumping major version.")
        major += 1
        minor = 0
    elif "dev" in labels:
        print("[INFO] 'dev' label detected. Bumping minor version.")
        minor += 1
    else:
        print("[INFO] No recognized label for version bump. Exiting.")
        return

    write_version(major, minor)


def main():
    if len(sys.argv) < 2:
        print("Usage: manage_global_version.py [get_version|bump]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "get_version":
        version = get_current_version_string()
        # Print to stdout (so logs can show it)
        print(version)

        # Also write to GITHUB_OUTPUT in the style you requested
        github_output = os.environ.get("GITHUB_OUTPUT", "")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as out:
                out.write(f"pr_version={version}\n")

    elif command == "bump":
        bump_version()
    else:
        print(f"[ERROR] Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
