# bump_versions.py

import json
import os
import sys

import yaml


def main():
    # Load PR labels from environment variable
    pr_labels_json = os.getenv("PR_LABELS", "[]")
    pr_labels = json.loads(pr_labels_json)
    labels = [label["name"] for label in pr_labels]

    print(f"Labels: {labels}")

    # Define label combinations
    label_combinations = [
        ["dev", "train"],
        ["dev", "inference"],
        ["prd", "train"],
        ["prd", "inference"],
        ["model", "dev"],
        ["model", "prd"],
    ]

    # Check if PR has any of the required label combinations
    def has_labels(required_labels, labels):
        return all(label in labels for label in required_labels)

    matches_combination = any(has_labels(combo, labels) for combo in label_combinations)

    if not matches_combination:
        print("No matching label combinations found. Version not bumped.")
        sys.exit(0)

    # Read current version from version.yaml
    version_file = "version.yaml"
    with open(version_file, "r") as f:
        data = yaml.safe_load(f)

    version_str = data.get("version", "0.0")
    major, minor = map(int, version_str.split("."))

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

    # Update version
    new_version = f"{major}.{minor}"
    data["version"] = new_version

    # Write updated version back to version.yaml
    with open(version_file, "w") as f:
        yaml.dump(data, f)

    print(f"Version updated to {new_version}")

    # Output the new version for GitHub Actions
    # Using environment file for output
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        print(f"new_version={new_version}", file=f)


if __name__ == "__main__":
    main()
