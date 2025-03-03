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
SKIP_BOT_PRS = True
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
            
            if SKIP_BOT_PRS:
                pr_page = [
                    pr 
                    for pr in pr_page
                    if pr.get("user", {}).get("type") != "Bot"
                ]
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
    - Calculates per-reviewer response times (first from PR creation, then from previous review)
    - Skips PRs based on criteria
    """
    # Fetch reviews (existing logic)
    reviews_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    review_response = requests.get(reviews_url, headers=HEADERS)
    time.sleep(API_WAIT_SECONDS)  # Wait to avoid hitting rate limits

    if review_response.status_code != 200:
        print(f"Failed to fetch reviews for {repo} PR#{pr_number}: {review_response.status_code}")
        return None

    reviews = review_response.json()
    # Filter out any reviews without a user or submitted_at (just to be safe)
    pr_author = user  # The PR creator's login
    reviews = [
        rv for rv in reviews
        if rv.get("user")
        and rv.get("submitted_at")
        and rv["user"]["login"] != pr_author
    ]

    # Sort reviews by the time they were submitted
    reviews_sorted = sorted(
        reviews,
        key=lambda r: pd.to_datetime(r["submitted_at"])
    )

    # Build parallel lists of reviewers and their response times
    reviewers_list = []
    reviewer_response_times_list = []

    # Initialize "last activity" time to PR creation
    last_activity_time = pd.to_datetime(created_at)

    for rv in reviews_sorted:
        reviewer_login = rv["user"]["login"]
        review_submitted_at = pd.to_datetime(rv["submitted_at"])

        # Calculate how long it took THIS reviewer to respond since last activity
        time_diff_hours = (review_submitted_at - last_activity_time).total_seconds() / 3600.0

        reviewers_list.append(reviewer_login)
        reviewer_response_times_list.append(time_diff_hours)

        # Update last_activity_time to this review's time
        last_activity_time = review_submitted_at

    total_reviews = len(reviewers_list)

    # If SKIP_NO_REVIEWS is True and we have no reviews, skip this PR
    if SKIP_NO_REVIEWS and total_reviews == 0:
        return None

    # Calculate "time to first review" purely from PR creation to first reviewer
    if len(reviewer_response_times_list) > 0:
        response_time = reviewer_response_times_list[0]
    else:
        response_time = None

    # Calculate "review time" (PR creation → merge or close)
    review_time = None
    if merged_at:
        review_time = pd.to_datetime(merged_at) - pd.to_datetime(created_at)
    elif closed_at:
        review_time = pd.to_datetime(closed_at) - pd.to_datetime(created_at)
    if review_time is not None:
        review_time = review_time.total_seconds() / 3600.0  # hours

    # Fetch PR size (additions, deletions, changed_files) - existing logic
    pr_details = get_pull_request_details(repo, pr_number)
    loc = None
    if (pr_details["additions"] is not None) and (pr_details["deletions"] is not None):
        loc = pr_details["additions"] + pr_details["deletions"]

    # Convert lists to comma-separated strings for CSV output 
    reviewers_str = ", ".join(reviewers_list)
    reviewer_times_str = ", ".join(f"{t:.2f}" for t in reviewer_response_times_list)

    return {
        "repo": repo,
        "pr_number": pr_number,
        "user": user,
        "created_at": created_at,
        "merged_at": merged_at,
        "closed_at": closed_at,
        "num_reviews": total_reviews,
        "reviewers": reviewers_str,
        "reviewer_response_times": reviewer_times_str,
        "response_time_hours": response_time,       # time to first review
        "review_time_hours": review_time,           # time to merge/close
        "lines_of_code": loc,
        "changed_files": pr_details["changed_files"],
        "url": url
    }


def main():
    for repo in repositories:
        print(f"Processing {repo.name}...")
        data = extract_review_metrics(repo.url, N=1000)
        df = pd.DataFrame(data)
        df.to_csv(f"metrics_{repo.url.replace('/', '_')}.csv", index=False)
        time.sleep(API_WAIT_SECONDS)  # Prevent hitting GitHub rate limits

    print("Data collection complete")


if __name__ == "__main__":
    main()
