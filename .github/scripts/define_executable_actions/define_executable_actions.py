"""
define_executable_actions.py
A simple script to determine which steps in the MLOps pipeline should run,
based on the labels assigned to the pull request.

Environment Variables:
- PR_LABELS_JSON: JSON array of label strings (from the main workflow).
- GITHUB_OUTPUT: Path to the GitHub output file for setting job outputs.

Outputs are appended as lines to the GITHUB_OUTPUT file:
- exec_get_pr_version=[true|false]
- exec_push_to_azure_dev=[true|false]
- exec_push_to_azure_shared_registry=[true|false]
- exec_tag_version=[true|false]

Usage:
  python define_executable_actions.py
"""

import json
import os


def has_any(label_set, labels):
    """Return True if there's at least one overlapping label."""
    return not label_set.isdisjoint(labels)


def main():
    # Read the JSON string of labels from environment
    labels_json = os.environ.get("PR_LABELS_JSON", "[]")
    try:
        # Parse the JSON array (e.g., ["dev", "train"])
        raw_labels = json.loads(labels_json)
        # Normalize to lower-case set
        labels = {lbl.strip().lower() for lbl in raw_labels if lbl.strip()}
    except json.JSONDecodeError:
        print("Error: Could not parse PR_LABELS_JSON; defaulting to empty set.")
        labels = set()

    # Define label sets
    set_env = {
        "dev",
        "qua",
        "prod",
    }  # For get_pr_version, push_to_azure_dev, tag_version
    set_scenario = {"train", "inference", "utils", "tests"}
    set_env_shared = {"qua", "prod"}  # For push_to_azure_shared_registry

    # Determine which actions to execute
    exec_get_pr_version = has_any(set_env, labels) and has_any(set_scenario, labels)
    exec_push_to_azure_dev = exec_get_pr_version
    exec_tag_version = exec_get_pr_version

    # push_to_azure_shared_registry requires at least one label in set_env_shared AND one in set_scenario
    exec_push_to_azure_shared_registry = has_any(set_env_shared, labels) and has_any(
        set_scenario, labels
    )

    # Print (for debugging in logs)
    print("Detected labels:", labels)
    print("exec_get_pr_version:", exec_get_pr_version)
    print("exec_push_to_azure_dev:", exec_push_to_azure_dev)
    print("exec_push_to_azure_shared_registry:", exec_push_to_azure_shared_registry)
    print("exec_tag_version:", exec_tag_version)

    # Write the outcomes to GITHUB_OUTPUT
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as out:
            out.write(f"exec_get_pr_version={str(exec_get_pr_version).lower()}\n")
            out.write(f"exec_push_to_azure_dev={str(exec_push_to_azure_dev).lower()}\n")
            out.write(
                f"exec_push_to_azure_shared_registry={str(exec_push_to_azure_shared_registry).lower()}\n"
            )
            out.write(f"exec_tag_version={str(exec_tag_version).lower()}\n")


if __name__ == "__main__":
    main()
