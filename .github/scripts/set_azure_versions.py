# set_azure_versions.py

import os
import sys

import yaml


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

                    if not isinstance(data, dict):
                        print(f"Skipping {file_path}: not a valid YAML mapping.")
                        continue

                    if "version" in data:
                        data["version"] = version
                        updated = True
                    else:
                        updated = False

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
