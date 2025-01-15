"""
Script for recursively updating 'version' keys in YAML files
across specified directories and filenames.
"""

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

    # If data is a dictionary, check if it has a 'version' key and update it.
    if isinstance(data, dict):
        if "version" in data:
            data["version"] = version
            updated = True

        # Recursively process all dictionary values.
        for value in data.values():
            if isinstance(value, (dict, list)):
                if set_version_in_data(value, version):
                    updated = True

    # If data is a list, recursively process each item that might be a dict or list.
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
    # Load the file contents
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as exc:
        print(f"Error reading {file_path}: {exc}")
        return

    # If the file is empty or invalid, skip
    if not data:
        print(f"Skipping {file_path}: file is empty or invalid.")
