"""
all reading of the data is done through this file, it retrieves the data in a number
of different formats for varying use cases
"""
import pandas as pd
from os.path import isfile

from GenerateData import Repository, repositories

DATA_FOLDER = "100PR/"

def get_generated_repositories():
    result = []
    for repo in repositories:
        if isfile(f"{DATA_FOLDER}metric_{repo.url.replace("/", "_")}.csv"):
            result.append(repo)
    return result

def load_repository_metrics(repo: Repository) -> pd.DataFrame:
    """
    returns the full dataframe of repository metrics
    """
    data = pd.read_csv(f"{DATA_FOLDER}metric_{repo.url.replace("/", "_")}.csv")
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

def get_number_of_reviews_per_reviewer(repo):
    result = {}
    reviewers = get_all_reviewers(repo)
    for reviewer in reviewers:
        result[reviewer] = get_number_of_reviews(repo, reviewer)
    return result