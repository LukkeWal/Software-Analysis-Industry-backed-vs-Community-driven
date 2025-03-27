"""
All writing of the data is done here. It retrieves data from GitHub and
saves it as csv files. This version uses asynchronous requests with aiohttp
to maximize the usage of the 5000 requests/hour limit.
"""
import os
import time
import math
from datetime import datetime
import asyncio
import aiohttp
import pytz
import pandas as pd
from dotenv import load_dotenv

from CoveredRepos import repositories, Repository

load_dotenv()  # Load environment variables from .env

# Configurations
SKIP_NO_REVIEWS = True
SKIP_BOT_PRS = True
API_WAIT_SECONDS = 0.75  # Not used explicitly now, but can be reintroduced if needed

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub API headers
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

TIMEZONE = pytz.timezone('Europe/Amsterdam')

# Global variables for rate limit info
test = 0
ratelimit_remaining = 5000
ratelimit_reset = 0

# Use a semaphore to limit concurrent requests
api_semaphore = asyncio.Semaphore(10)

async def send_API_request(url, session):
    global ratelimit_remaining, ratelimit_reset
    # If we've exhausted our rate limit, wait until reset time (+ a buffer)
    # if ratelimit_remaining <= 10:
    #     wait_time = ratelimit_reset - time.time()
    #     if wait_time > 0:
    #         print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Rate limit exceeded. Sleeping for {math.ceil(wait_time)+5} seconds.")
    #         await asyncio.sleep(wait_time + 5)
    try:
        async with api_semaphore:
            async with session.get(url, headers=HEADERS) as response:
                if response.status != 200:
                    print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Failed to fetch data: {response.status}. Retrying in 600 seconds...")
                    await asyncio.sleep(600)
                    return await send_API_request(url, session)
                # Update rate limit information from response headers
                ratelimit_remaining = int(response.headers.get('X-RateLimit-Remaining'))
                ratelimit_reset = int(response.headers.get('X-RateLimit-Reset'))
                reset_in = math.ceil(ratelimit_reset - time.time())
                # print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Rate Limit Info: limit={response.headers.get('X-RateLimit-Limit')}, "
                #       f"remaining={ratelimit_remaining}, reset={reset_in}s          ")
                return await response.json()
    except Exception as e:
        print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Error sending API request: {e}. Retrying in 600 seconds...")
        await asyncio.sleep(600)
        return await send_API_request(url, session)

async def get_pull_requests_by_date(repo, start_date, end_date, session):
    """
    Fetches all closed pull requests for a repository created between start_date (inclusive)
    and end_date (exclusive) by paging through the results.
    """
    pr_list = []
    page = 1
    start_dt = pd.to_datetime(start_date, utc=True)
    end_dt = pd.to_datetime(end_date, utc=True)
    last_date = datetime.now()

    while True:
        print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Fetching PRs page {page}, total PRs: {len(pr_list)}, "
              f"{last_date.strftime('%d-%m-%Y')} / {start_dt.strftime('%d-%m-%Y')}", end="\r")
        url = (
            f"https://api.github.com/repos/{repo}/pulls"
            f"?state=closed&sort=created&direction=desc&per_page=100&page={page}"
        )
        pr_page = await send_API_request(url, session)
        if not pr_page:
            break

        if SKIP_BOT_PRS:
            pr_page = [pr for pr in pr_page if pr.get("user", {}).get("type") != "Bot"]

        for pr in pr_page:
            pr_created = pd.to_datetime(pr["created_at"], utc=True)
            last_date = pr_created
            if pr_created >= end_dt:
                # PR is too recent (after or equal to end_date), skip it.
                continue
            if pr_created < start_dt:
                # Since results are sorted descending by creation date,
                # once a PR is older than start_date, all following ones will be too old.
                return pr_list
            pr_list.append(pr)
        page += 1

    print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Fetching PRs page {page}, total PRs: {len(pr_list)}, DONE")
    return pr_list

async def get_pull_request_details(repo, pr_number, session):
    """
    Fetches additional details for a pull request: additions, deletions, and changed_files.
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    pr_data = await send_API_request(url, session)
    return {
        "additions": pr_data.get("additions", 0),
        "deletions": pr_data.get("deletions", 0),
        "changed_files": pr_data.get("changed_files", 0)
    }

async def process_pull_request(repo, pr_number, user, created_at, merged_at, closed_at, url, session):
    """
    Processes a single pull request by fetching its reviews, calculating response times,
    and retrieving additional PR details.
    """
    reviews_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    reviews = await send_API_request(reviews_url, session)
    pr_author = user
    reviews = [
        rv for rv in reviews
        if rv.get("user") and rv.get("submitted_at") and rv["user"]["login"] != pr_author
    ]
    reviews_sorted = sorted(reviews, key=lambda r: pd.to_datetime(r["submitted_at"]))

    reviewers_list = []
    reviewer_response_times_list = []
    last_activity_time = pd.to_datetime(created_at)

    for rv in reviews_sorted:
        reviewer_login = rv["user"]["login"]
        review_submitted_at = pd.to_datetime(rv["submitted_at"])
        time_diff_hours = (review_submitted_at - last_activity_time).total_seconds() / 3600.0
        reviewers_list.append(reviewer_login)
        reviewer_response_times_list.append(time_diff_hours)
        last_activity_time = review_submitted_at

    total_reviews = len(reviewers_list)

    if SKIP_NO_REVIEWS and total_reviews == 0:
        return None

    response_time = reviewer_response_times_list[0] if reviewer_response_times_list else None
    review_time = None
    if merged_at:
        review_time = pd.to_datetime(merged_at) - pd.to_datetime(created_at)
    elif closed_at:
        review_time = pd.to_datetime(closed_at) - pd.to_datetime(created_at)
    if review_time is not None:
        review_time = review_time.total_seconds() / 3600.0

    pr_details = await get_pull_request_details(repo, pr_number, session)
    loc = None
    if (pr_details["additions"] is not None) and (pr_details["deletions"] is not None):
        loc = pr_details["additions"] + pr_details["deletions"]

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
        "review_time_hours": review_time,             # time to merge/close
        "lines_of_code": loc,
        "changed_files": pr_details["changed_files"],
        "url": url
    }

async def extract_review_metrics(repo, start_date, end_date, session):
    """
    Extracts code review metrics from pull requests within the specified date range.
    Fetches PR pages sequentially but processes each PR concurrently.
    """
    pull_requests = await get_pull_requests_by_date(repo, start_date, end_date, session)
    print(f"total pull requests: {len(pull_requests)} before starting the extract review metrics")
    x = 2300
    if len(pull_requests) > x:
        pull_requests = pull_requests[:x]
    metrics = []

    tasks = []
    for i, pr in enumerate(pull_requests, 1):
        print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Processing PR {i}/{len(pull_requests)}: #{pr['number']}", end="\r")
        pr_number = pr['number']
        created_at = pr['created_at']
        merged_at = pr.get('merged_at')
        closed_at = pr.get('closed_at')
        user = pr['user']['login']
        url = pr['url']
        tasks.append(
            asyncio.create_task(process_pull_request(repo, pr_number, user, created_at, merged_at, closed_at, url, session))
        )

    results = await asyncio.gather(*tasks)
    for result in results:
        if result:
            metrics.append(result)
    print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Processing complete for {repo}.")
    return metrics

async def main():
    start_date = "2024-01-01"
    end_date = "2024-02-16"
    async with aiohttp.ClientSession() as session:
        for repo in repositories:
            print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Processing {repo.name}...")
            data = await extract_review_metrics(repo.url, start_date, end_date, session)
            df = pd.DataFrame(data)
            # Replace '/' with '_' for a valid filename
            filename = f"metrics_{repo.url.replace('/', '_')}.csv"
            df.to_csv(filename, index=False)
            print(f"{datetime.now(TIMEZONE).strftime('%H:%M')} Saved data to {filename}")
    print("Data collection complete")

if __name__ == "__main__":
    asyncio.run(main())
