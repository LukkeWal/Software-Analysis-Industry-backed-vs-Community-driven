import os
from dotenv import load_dotenv
import requests
import pandas as pd
import time

load_dotenv()  # Load environment variables from .env

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub API headers
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# List of repositories (owner/repo format)
repositories = [
    "microsoft/vscode",
    "tensorflow/tensorflow",
    #"flutter/flutter", # caused http error 500
    "facebook/react",
    "kubernetes/kubernetes",
    #"home-assistant/core", # caused http error 500
    "godotengine/godot",
    "GNOME/gimp",
    "obsproject/obs-studio",
    "mattermost/mattermost-server"
]

def get_pull_requests(repo):
    """
    Fetches the last 100 pull requests from a repository.
    """
    url = f"https://api.github.com/repos/{repo}/pulls?state=closed&per_page=100"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch PRs for {repo}: {response.status_code}")
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

def extract_review_metrics(repo):
    """
    Extracts code review metrics from pull requests.
    """
    pull_requests = get_pull_requests(repo)
    metrics = []

    for pr in pull_requests:
        pr_number = pr['number']
        created_at = pr['created_at']
        merged_at = pr.get('merged_at')
        closed_at = pr.get('closed_at')
        user = pr['user']['login']
        url = pr['url']

        # Fetch review details
        review_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
        review_response = requests.get(review_url, headers=HEADERS)

        if review_response.status_code == 200:
            reviews = review_response.json()
            num_reviews = len(reviews)
            
            review_times = []
            for review in reviews:
                review_submitted = review.get('submitted_at')
                if review_submitted:
                    review_times.append(review_submitted)

            if review_times:
                review_times.sort()
                first_review_time = review_times[0]
            else:
                first_review_time = None

        else:
            num_reviews = 0
            first_review_time = None

        # Calculate response time (PR creation → first review)
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

        metrics.append({
            "repo": repo,
            "pr_number": pr_number,
            "user": user,
            "created_at": created_at,
            "merged_at": merged_at,
            "closed_at": closed_at,
            "num_reviews": num_reviews,
            "response_time_hours": response_time,
            "review_time_hours": review_time,
            "lines_of_code": pr_details["additions"] + pr_details["deletions"],
            "changed_files": pr_details["changed_files"],
            "url": url
        })

        # Delay to prevent hitting GitHub API rate limits
        time.sleep(1)

    return metrics

def main():
    # Collect data for all repositories
    all_data = []
    for repo in repositories:
        print(f"Processing {repo}...")
        data = extract_review_metrics(repo)
        df = pd.DataFrame(data)
        df.to_csv(f"metric_{repo.replace("/", "_")}.csv", index=False)
        time.sleep(2)  # Prevent rate limiting
    
    print("Data collection complete. Saved to 'code_review_metrics.csv'.")

if __name__ == "__main__":
    main()
