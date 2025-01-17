#!/usr/bin/env python
"""
rollback_global_version.py

Usage:
  python rollback_global_version.py <old_version>

This script will overwrite the "version" field in version.yaml with <old_version>.
It expects <old_version> to be in the format "major.minor".
"""

import sys

import yaml

VERSION_FILE = "version.yaml"


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Usage: rollback_global_version.py <old_version>")
        sys.exit(1)

    old_version = sys.argv[1]
    print(f"[INFO] Rolling back global version to: {old_version}")

    # Create version.yaml if it doesn't exist, or overwrite if it does
    data = {"version": old_version}
    try:
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)
    except Exception as ex:
        print(f"[ERROR] Failed to write {VERSION_FILE}: {ex}")
        sys.exit(1)

    print("[INFO] Successfully rolled back version.yaml")
    print(f"[INFO] version.yaml content -> version: {old_version}")


if __name__ == "__main__":
    main()
