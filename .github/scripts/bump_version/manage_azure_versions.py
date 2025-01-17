#!/usr/bin/env python3
"""
manage_azure_versions.py

Usage:
    python manage_azure_versions.py <version>

Recursively updates 'version' keys in specified YAML files inside src/train and src/inference.
"""

import os
import sys
from typing import Union

import yaml

# Directories to search for YAML files
DIRECTORIES = ["src/train", "src/inference"]

# Filenames to update
FILENAMES = ["config.yaml", "env.yaml", "pipeline.yaml"]


def set_version_in_data(data: Union[dict, list], version: str) -> bool:
    """
    Recursively update the 'version' key in a nested dictionary or list.
    Returns True if any 'version' key was updated, else False.
    """
    updated = False

    if isinstance(data, dict):
        if "version" in data:
            data["version"] = version
            updated = True

        # Recursively handle nested dicts/lists
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
    Reads YAML, updates 'version', and writes back if changes were made.
    """
    if not os.path.exists(file_path):
        print(f"[WARNING] {file_path} does not exist. Skipping.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as exc:
        print(f"[ERROR] Unable to read YAML from {file_path}: {exc}")
        return

    if not data:
        print(f"[INFO] {file_path} is empty or invalid YAML. No changes made.")
        return

    if set_version_in_data(data, version):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False)
            print(f"[INFO] Updated version in {file_path} to {version}")
        except Exception as ex:
            print(f"[ERROR] Failed to write updated YAML to {file_path}: {ex}")
    else:
        print(f"[INFO] No 'version' key found in {file_path}. Nothing to update.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_azure_versions.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    print("========================================")
    print(f"[INFO] Updating Azure versions to {version}")
    print("========================================")

    for directory in DIRECTORIES:
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename in FILENAMES:
                    file_path = os.path.join(root, filename)
                    update_file_version(file_path, version)


if __name__ == "__main__":
    main()
