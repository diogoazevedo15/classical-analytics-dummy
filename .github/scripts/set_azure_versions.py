#!/usr/bin/env python3
"""
Script for recursively updating 'version' keys in YAML files across specified directories and filenames.

Usage:
    python update_version.py <version>
"""

import os
import sys
from typing import Union

import yaml

# Directories to search for YAML files
DIRECTORIES = ["src/train", "src/inference"]

# Filenames in which we'll update the version
FILENAMES = ["config.yaml", "env.yaml", "pipeline.yaml"]


def set_version_in_data(data: Union[dict, list], version: str) -> bool:
    """
    Recursively update the 'version' key in a nested dictionary or list of dictionaries.

    :param data: A dictionary or list potentially containing 'version' keys.
    :param version: The new version string to set.
    :return: True if any 'version' key was updated; otherwise, False.
    """
    updated = False

    if isinstance(data, dict):
        if "version" in data:
            data["version"] = version
            updated = True

        for value in data.values():
            if isinstance(value, (dict, list)):
                if set_version_in_data(value, version):
                    updated = True

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                if set_version_in_data(item, version):
                    updated = True

    return updated


def update_file_version(file_path: str, version: str) -> None:
    """
    Reads YAML from a file, updates its 'version' keys recursively,
    and writes it back if changes were made.

    :param file_path: Path to the YAML file.
    :param version: The version string to set.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as exc:
        print(f"Error reading {file_path}: {exc}")
        return

    if not data:
        print(f"Skipping {file_path}: file is empty or invalid.")
        return

    if set_version_in_data(data, version):
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)
        print(f"Updated version in {file_path} to {version}")
    else:
        print(f"No 'version' key found in {file_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python update_version.py <version>")
        sys.exit(1)

    version = sys.argv[1]

    # Iterate over specified directories and filenames to update the version.
    for directory in DIRECTORIES:
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename in FILENAMES:
                    file_path = os.path.join(root, filename)
                    update_file_version(file_path, version)


if __name__ == "__main__":
    main()
