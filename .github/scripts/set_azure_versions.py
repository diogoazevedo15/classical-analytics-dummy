# .github/scripts/set_azure_versions.py

import os
import sys

import yaml


def set_version_in_data(data, version):
    if isinstance(data, dict):
        updated = False
        if "version" in data:
            data["version"] = version
            updated = True
        # Recursively check nested dictionaries
        for value in data.values():
            if isinstance(value, dict):
                if set_version_in_data(value, version):
                    updated = True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        if set_version_in_data(item, version):
                            updated = True
        return updated
    return False


def update_versions(version):
    # Directories to search
    directories = ["src/train", "src/inference"]

    # Filenames to update
    filenames = ["config.yaml", "env.yaml", "pipeline.yaml"]

    for directory in directories:
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename in filenames:
                    file_path = os.path.join(root, filename)
                    with open(file_path, "r") as f:
                        try:
                            data = yaml.safe_load(f)
                        except yaml.YAMLError as exc:
                            print(f"Error parsing {file_path}: {exc}")
                            continue

                    if data is None:
                        print(f"Skipping {file_path}: file is empty.")
                        continue

                    updated = set_version_in_data(data, version)
                    if updated:
                        with open(file_path, "w") as f:
                            yaml.dump(data, f, sort_keys=False)
                        print(f"Updated version in {file_path}")
                    else:
                        print(f"No 'version' key found in {file_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python set_azure_versions.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    update_versions(version)
