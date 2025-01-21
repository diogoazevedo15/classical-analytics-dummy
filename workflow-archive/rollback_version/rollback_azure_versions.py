#!/usr/bin/env python3
"""
rollback_azure_versions.py

Usage:
    python rollback_azure_versions.py <old_version>

This script updates all 'version' fields in relevant YAML files
under src/train and src/inference back to <old_version>.
"""

import os
import sys
from typing import Union

import yaml

# Directories & Filenames that must revert to old version
DIRECTORIES = ["src/train", "src/inference"]
FILENAMES = ["config.yaml", "env.yaml", "pipeline.yaml"]


def set_version_in_data(data: Union[dict, list], version: str) -> bool:
    """
    Recursively update the 'version' key in a nested dictionary or list.
    Returns True if any 'version' key was updated, else False.
    """
    updated = False

    if isinstance(data, dict):
        # Update top-level 'version' if present
        if "version" in data:
            data["version"] = version
            updated = True

        # Recurse deeper
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


def update_file_version(file_path: str, version: str) -> bool:
    """
    Reads the YAML file, updates 'version' keys, and writes back if changed.
    Returns True if a change was made, otherwise False.
    """
    if not os.path.exists(file_path):
        print(f"[WARNING] {file_path} does not exist. Skipping.")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as ex:
        print(f"[ERROR] Could not read {file_path}: {ex}")
        return False

    if not data:
        print(f"[INFO] {file_path} is empty or invalid. Skipping.")
        return False

    if set_version_in_data(data, version):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False)
            print(f"[INFO] Rolled back {file_path} to version {version}")
            return True
        except Exception as ex:
            print(f"[ERROR] Failed to write updated YAML to {file_path}: {ex}")
            return False
    else:
        print(f"[INFO] No 'version' key found in {file_path}; nothing to revert.")
        return False


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Usage: rollback_azure_versions.py <old_version>")
        sys.exit(1)

    old_version = sys.argv[1]
    print("======================================")
    print(f"[INFO] Rolling back Azure versions to {old_version}")
    print("======================================")

    total_updates = 0

    for directory in DIRECTORIES:
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename in FILENAMES:
                    file_path = os.path.join(root, filename)
                    if update_file_version(file_path, old_version):
                        total_updates += 1

    print(f"[INFO] Completed rollback. Files updated: {total_updates}")


if __name__ == "__main__":
    main()
