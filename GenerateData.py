"""
all writing of the data is done here. It retrieves data from GitHub and
saves it as csv files
"""
import os
import time
import datetime
import requests
import pandas as pd
from dotenv import load_dotenv

from CoveredRepos import repositories, Repository

load_dotenv()  # Load environment variables from .env

# Configurations
SKIP_NO_REVIEWS = True
API_WAIT_SECONDS = 0.72  # Number of seconds to wait after each API call

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub API headers
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_N_pull_requests(repo, N):
    """
    Fetches the last N pull requests from a repository using the /pulls API.
    """
    pr_list = []
    page = 1

    while len(pr_list) < N:
        print(f"Fetching PRs: {len(pr_list)} / {N}", end="\r")
        url = f"https://api.github.com/repos/{repo}/pulls?state=closed&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        time.sleep(API_WAIT_SECONDS)  # Wait to avoid hitting rate limits

        if response.status_code == 200:
            pr_page = response.json()
            if not pr_page:  # No more PRs available
                break

            pr_list.extend(pr_page[:N - len(pr_list)])  # Add only up to N PRs
            page += 1  # Move to the next page
        else:
            print(f"Failed to fetch PRs for {repo}: {response.status_code}")
            break

    print(f"Fetching PRs: {len(pr_list)} / {N}")
    return pr_list


def get_reviewers(repo, pr_number):
    """
    Fetches the list of reviewers for a pull request.
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    response = requests.get(url, headers=HEADERS)
    time.sleep(API_WAIT_SECONDS)  # Wait to avoid hitting rate limits

    if response.status_code == 200:
        reviews = response.json()
        reviewers = [review["user"]["login"] for review in reviews if review.get("user")]
        return reviewers
    else:
        print(f"Failed to fetch reviewers for {repo} PR#{pr_number}: {response.status_code}")
        return []


def get_pull_request_details(repo, pr_number):
    """
    Fetches additional details for a pull request including:
    - additions
    - deletions
    - changed_files
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    response = requests.get(url, headers=HEADERS)
    time.sleep(API_WAIT_SECONDS)  # Wait to avoid hitting rate limits

    if response.status_code == 200:
        pr_data = response.json()
        return {
            "additions": pr_data.get("additions", 0),
            "deletions": pr_data.get("deletions", 0),
            "changed_files": pr_data.get("changed_files", 0)
        }
    else:
        print(f"Failed to fetch PR details for {repo} PR#{pr_number}: {response.status_code}")
        return {"additions": None, "deletions": None, "changed_files": None}


def extract_review_metrics(repo, N):
    """
    Extracts code review metrics from the last N pull requests.
    Processes them sequentially with API rate limiting.
    """
    pull_requests = get_N_pull_requests(repo, N)
    metrics = []

    for i, pr in enumerate(pull_requests, 1):
        print(f"Processing PR {i}/{len(pull_requests)}: #{pr['number']}", end="\r")

        pr_number = pr['number']
        created_at = pr['created_at']
        merged_at = pr.get('merged_at')
        closed_at = pr.get('closed_at')
        user = pr['user']['login']
        url = pr['url']

        # Process PR
        result = process_pull_request(repo, pr_number, user, created_at, merged_at, closed_at, url)
        if result:
            metrics.append(result)

    print(f"Processing complete for {repo}.")
    return metrics


def process_pull_request(repo, pr_number, user, created_at, merged_at, closed_at, url):
    """
    Processes a single pull request:
    - Fetches reviewers (each review is counted separately)
    - Fetches review details
    - Fetches PR size (lines changed)
    - Skips PRs based on criteria
    """
    # Fetch reviewers
    reviewers_list = get_reviewers(repo, pr_number)
    total_reviews = len(reviewers_list)

    # Skip if no reviewers and configured to skip
    if SKIP_NO_REVIEWS and not reviewers_list:
        return None

    # Fetch review details
    review_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    review_response = requests.get(review_url, headers=HEADERS)
    time.sleep(API_WAIT_SECONDS)  # Wait to avoid hitting rate limits

    if review_response.status_code == 200:
        reviews = review_response.json()
        review_times = [review.get('submitted_at') for review in reviews if review.get('submitted_at')]
        first_review_time = min(review_times) if review_times else None
    else:
        first_review_time = None

    # Calculate response time
    response_time = None
    if first_review_time:
        response_time = pd.to_datetime(first_review_time) - pd.to_datetime(created_at)
        response_time = response_time.total_seconds() / 3600  # Convert to hours

    # Calculate review time (PR creation → merge/close)
    review_time = None
    if merged_at:
        review_time = pd.to_datetime(merged_at) - pd.to_datetime(created_at)
    elif closed_at:
        review_time = pd.to_datetime(closed_at) - pd.to_datetime(created_at)

    review_time = review_time.total_seconds() / 3600 if review_time else None  # Convert to hours

    # Fetch PR details (additions, deletions, changed files)
    pr_details = get_pull_request_details(repo, pr_number)

    loc = None if pr_details["additions"] is None or pr_details["deletions"] is None else pr_details["additions"] + pr_details["deletions"]

    return {
        "repo": repo,
        "pr_number": pr_number,
        "user": user,
        "created_at": created_at,
        "merged_at": merged_at,
        "closed_at": closed_at,
        "num_reviews": total_reviews,
        "reviewers": ", ".join(reviewers_list),
        "response_time_hours": response_time,
        "review_time_hours": review_time,
        "lines_of_code": loc,
        "changed_files": pr_details["changed_files"],
        "url": url
    }

def main():
    for repo in repositories:
        print(f"Processing {repo.name}...")
        data = extract_review_metrics(repo.url, N=5)
        df = pd.DataFrame(data)
        df.to_csv(f"metrics_{repo.url.replace('/', '_')}.csv", index=False)
        time.sleep(API_WAIT_SECONDS)  # Prevent hitting GitHub rate limits

    print("Data collection complete")


if __name__ == "__main__":
    main()
