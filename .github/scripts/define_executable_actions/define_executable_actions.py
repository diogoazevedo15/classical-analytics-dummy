#!/usr/bin/env python3
"""
define_executable_actions.py
A simple script to determine which steps in the MLOps pipeline should run,
based on the labels assigned to the pull request.

Environment Variables:
- ALL_LABELS: Space-separated list of PR labels.
- GITHUB_OUTPUT: Path to the GitHub output file for setting job outputs.

Outputs are appended as lines to the GITHUB_OUTPUT file:
- exec_get_pr_version=[true|false]
- exec_push_to_azure_dev=[true|false]
- exec_push_to_azure_shared_registry=[true|false]
- exec_tag_version=[true|false]

Usage:
  python define_executable_actions.py
"""

import os


def has_any(label_set, labels):
    """Return True if there's at least one common label."""
    return not label_set.isdisjoint(labels)


def main():
    # Read all labels from environment
    labels_str = os.environ.get("ALL_LABELS", "")
    labels = {label.strip().lower() for label in labels_str.split() if label.strip()}

    # Define relevant label sets
    set_env = {
        "dev",
        "qua",
        "prod",
    }  # For get_pr_version, push_to_azure_dev, tag_version
    set_scenario = {"train", "inference", "utils", "tests"}
    set_env_shared = {"qua", "prod"}  # For push_to_azure_shared_registry

    # Decide which actions to execute
    # All these three require at least one label in set_env AND one in set_scenario:
    exec_get_pr_version = has_any(set_env, labels) and has_any(set_scenario, labels)
    exec_push_to_azure_dev = exec_get_pr_version
    exec_tag_version = exec_get_pr_version

    # push_to_azure_shared_registry requires at least one label in set_env_shared AND one in set_scenario:
    exec_push_to_azure_shared_registry = has_any(set_env_shared, labels) and has_any(
        set_scenario, labels
    )

    # Print (for debugging in logs)
    print("Detected labels:", labels)
    print("exec_get_pr_version:", exec_get_pr_version)
    print("exec_push_to_azure_dev:", exec_push_to_azure_dev)
    print("exec_push_to_azure_shared_registry:", exec_push_to_azure_shared_registry)
    print("exec_tag_version:", exec_tag_version)

    # Write outputs to GITHUB_OUTPUT so the calling workflow can access them
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
