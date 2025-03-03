"""
all reading of the data is done through this file, it retrieves the data in a number
of different formats for varying use cases
"""
import pandas as pd
import numpy as np
from os.path import isfile

from GenerateData import Repository, repositories

DATA_FOLDER = "1000PR/"

def get_generated_repositories():
    result = []
    for repo in repositories:
        if isfile(f"{DATA_FOLDER}metrics_{repo.url.replace("/", "_")}.csv"):
            result.append(repo)
    return result

def load_repository_metrics(repo: Repository) -> pd.DataFrame:
    """
    returns the full dataframe of repository metrics
    """
    data = pd.read_csv(f"{DATA_FOLDER}metrics_{repo.url.replace("/", "_")}.csv")
    # set the date columns to the relavant format
    data["created_at"] = pd.to_datetime(data["created_at"])
    data["merged_at"] = pd.to_datetime(data["merged_at"])
    data["closed_at"] = pd.to_datetime(data["closed_at"])
    return data

def get_all_reviewers(repo: Repository):
    """
    get a list with the names of all reviewers for a repository
    """
    metrics = load_repository_metrics(repo)
    reviewers_set = set()  # Use a set to store unique reviewers
    # Iterate through each row and add reviewers
    for reviewer_list in metrics["reviewers"].dropna():  # Ignore NaN values
        reviewers_set.update(reviewer_list.split(", "))  # Split and add to set
    return sorted(reviewers_set)  # Return sorted list of unique reviewers

def get_number_of_reviews(repo: Repository, reviewer: str):
    """
    get the count of the amount of reviews done by the given reviewer
    """
    metrics = load_repository_metrics(repo)
    return metrics["reviewers"].str.count(reviewer).sum()

def get_number_of_reviews_per_reviewer(repo, filter_outliers: bool = False):
    result = {}
    reviewers = get_all_reviewers(repo)
    for reviewer in reviewers:
        result[reviewer] = get_number_of_reviews(repo, reviewer)
    if filter_outliers:
        result = remove_outliers_from_dict(result)
    return result

def get_LOC_of_reviewer(repo: Repository, reviewer: str):
    """
    get the amount of LOC a reviewer reviewed in a repository.
    the LOC of any PR this reviewer has reviewed at least once will be summed
    """
    metrics = load_repository_metrics(repo)
    reviewer_metrics = metrics["reviewers"].str.contains(reviewer, na=False)
    filtered_metrics = metrics[reviewer_metrics]
    return filtered_metrics["lines_of_code"].dropna().sum()

def get_LOC_per_reviewer(repo, filter_outliers: bool = False):
    """
    get the LOC reviewed by all reviewers in a repository. Returns a dict
    with reviewers names as keys and their summed LOC as values
    """
    result = {}
    reviewers = get_all_reviewers(repo)
    for reviewer in reviewers:
        result[reviewer] = get_LOC_of_reviewer(repo, reviewer)
    if filter_outliers:
        result = remove_outliers_from_dict(result)
    return result

def get_review_time_hours_of_reviewer(repo: Repository, reviewer: str):
    """
    get the amount of LOC a reviewer reviewed in a repository.
    the LOC of any PR this reviewer has reviewed at least once will be summed
    """
    metrics = load_repository_metrics(repo)
    reviewer_metrics = metrics["reviewers"].str.contains(reviewer, na=False)
    filtered_metrics = metrics[reviewer_metrics]
    return filtered_metrics["review_time_hours"].dropna().sum()

def get_review_time_hours_per_reviewer(repo, filter_outliers: bool = False):
    """
    get the LOC reviewed by all reviewers in a repository. Returns a dict
    with reviewers names as keys and their summed LOC as values
    """
    result = {}
    reviewers = get_all_reviewers(repo)
    for reviewer in reviewers:
        result[reviewer] = get_review_time_hours_of_reviewer(repo, reviewer)
    if filter_outliers:
        result = remove_outliers_from_dict(result)
    return result

def get_average_response_time_hours_of_reviewer(repo: Repository, reviewer: str):
    """
    get the amount of LOC a reviewer reviewed in a repository.
    the LOC of any PR this reviewer has reviewed at least once will be summed
    """
    metrics = load_repository_metrics(repo)
    metrics = metrics.copy()
    metrics["first_reviewer"] = metrics["reviewers"].apply(
        lambda x: x.split(",")[0].strip() if pd.notna(x) and x.strip() != "" else None
    )
    filtered_metrics = metrics[metrics["first_reviewer"] == reviewer]
    if len(filtered_metrics) == 0:
        return None
    avg_response_time = filtered_metrics["response_time_hours"].dropna().mean()
    return avg_response_time

def get_average_response_time_hours_per_reviewer(repo, filter_outliers: bool = False):
    """
    get the LOC reviewed by all reviewers in a repository. Returns a dict
    with reviewers names as keys and their summed LOC as values
    """
    result = {}
    reviewers = get_all_reviewers(repo)
    for reviewer in reviewers:
        response_time = get_average_response_time_hours_of_reviewer(repo, reviewer)
        if response_time is None:
            continue
        result[reviewer] = get_average_response_time_hours_of_reviewer(repo, reviewer)
    if filter_outliers:
        result = remove_outliers_from_dict(result)
    return result

def remove_outliers_from_dict(data: dict):
    # Extract the values (results) from the dictionary
    results = list(data.values())
    # Compute Q1 (25th percentile) and Q3 (75th percentile)
    Q1 = np.percentile(results, 25)
    Q3 = np.percentile(results, 75)
    # Compute IQR
    IQR = Q3 - Q1
    # Define the lower and upper bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    # Filter out outliers based on the bounds
    filtered_dict = {key: value for key, value in data.items() if lower_bound <= value <= upper_bound}
    return filtered_dict
