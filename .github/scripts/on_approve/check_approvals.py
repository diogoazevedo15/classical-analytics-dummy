#!/usr/bin/env python
"""
check_approvals.py

This script checks if a Pull Request has at least one approval.
Exit code 1 if there are not enough approvals.
"""

import argparse
import sys

import requests


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check the number of approvals on a PR."
    )
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

    # Extract owner and repo name
    try:
        owner, repo_name = args.repo.split("/")
    except ValueError:
        print("[ERROR] --repo should be in the format 'owner/repo'.")
        sys.exit(1)

    pr_number = args.pr_number

    print("========================================")
    print(f"[INFO] Checking approvals for PR #{pr_number} in {owner}/{repo_name}.")
    print("========================================")

    # Construct the API request URL for PR reviews
    reviews_url = (
        f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pr_number}/reviews"
    )

    # Make the request to GitHub API
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {args.token}",
    }

    response = requests.get(reviews_url, headers=headers)
    if response.status_code != 200:
        print(
            f"[ERROR] Failed to fetch reviews. HTTP Status Code: {response.status_code}"
        )
        print(f"[ERROR] Response: {response.text}")
        sys.exit(1)

    reviews_data = response.json()

    # Count how many reviews are "APPROVED"
    approvals = sum(1 for review in reviews_data if review.get("state") == "APPROVED")

    print(f"[INFO] Found {approvals} approval(s).")

    # We require at least 1 approval
    if approvals < 1:
        print("[ERROR] Not enough approvals. Exiting with failure.")
        sys.exit(1)
    else:
        print("[SUCCESS] Enough approvals found. Proceeding.")


if __name__ == "__main__":
    main()
