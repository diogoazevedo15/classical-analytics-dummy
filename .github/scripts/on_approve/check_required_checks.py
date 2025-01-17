#!/usr/bin/env python
"""
check_required_checks.py

This script checks if certain checks (e.g., Lint Check and Repository Tests)
have passed successfully on the HEAD commit of the Pull Request.
"""

import argparse
import sys

import requests


def parse_args():
    parser = argparse.ArgumentParser(description="Check required checks for a PR.")
    parser.add_argument(
        "--repo", required=True, help="Repository in the format 'owner/repo'."
    )
    parser.add_argument(
        "--token", required=True, help="GitHub token for authentication."
    )
    parser.add_argument(
        "--pr-number", required=True, type=int, help="Pull Request number."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Extract owner/repo
    try:
        owner, repo_name = args.repo.split("/")
    except ValueError:
        print("[ERROR] --repo should be in the format 'owner/repo'.")
        sys.exit(1)

    pr_number = args.pr_number

    print("========================================")
    print(
        f"[INFO] Checking required checks for PR #{pr_number} in {owner}/{repo_name}."
    )
    print("========================================")

    # 1) First, get the PR to retrieve the HEAD SHA
    pr_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pr_number}"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {args.token}",
    }

    pr_response = requests.get(pr_url, headers=headers)
    if pr_response.status_code != 200:
        print(
            f"[ERROR] Failed to fetch PR #{pr_number}. HTTP Status Code: {pr_response.status_code}"
        )
        print(f"[ERROR] Response: {pr_response.text}")
        sys.exit(1)

    pr_data = pr_response.json()
    head_sha = pr_data.get("head", {}).get("sha")

    if not head_sha:
        print("[ERROR] Could not determine PR head SHA.")
        sys.exit(1)

    print(f"[INFO] Found head SHA: {head_sha}")

    # 2) List check runs for the HEAD commit
    check_runs_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits/{head_sha}/check-runs"
    checks_response = requests.get(check_runs_url, headers=headers)
    if checks_response.status_code != 200:
        print(
            f"[ERROR] Failed to fetch check runs for commit {head_sha}. HTTP Status Code: {checks_response.status_code}"
        )
        print(f"[ERROR] Response: {checks_response.text}")
        sys.exit(1)

    checks_data = checks_response.json()
    check_runs = checks_data.get("check_runs", [])

    # 3) Evaluate required checks
    lint_check_passed = False
    repository_tests_passed = False

    # Checking for "Lint Check" and "Repository Tests" by name
    for check in check_runs:
        check_name = check.get("name")
        conclusion = check.get("conclusion")

        # For debugging/logging:
        print(f"[INFO] Found check: {check_name}, conclusion: {conclusion}")

        if check_name == "Lint Check" and conclusion == "success":
            lint_check_passed = True
        elif check_name == "Repository Tests" and conclusion == "success":
            repository_tests_passed = True

    # 4) Validate
    if not lint_check_passed:
        print("[ERROR] Lint Check did not pass.")
        sys.exit(1)

    if not repository_tests_passed:
        print("[ERROR] Repository Tests did not pass.")
        sys.exit(1)

    print("[SUCCESS] All required checks have passed.")


if __name__ == "__main__":
    main()
