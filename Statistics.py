from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt
import numpy as np

FILTER_OUTLIERS = False

from DataHandler import (
    get_number_of_reviews_per_reviewer, 
    get_LOC_per_reviewer,
    get_average_response_time_hours_per_reviewer,
    get_review_time_hours_per_reviewer,
    repositories
)

def mannwhitneyu_test_num_reviews():
    industry = {}
    community = {}
    for repo in repositories:
        reviews = get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS)
        if repo.is_industry_backed:
            industry.update(reviews)
        else:
            community.update(reviews)

    # Extract the review counts as lists
    industry_values = list(industry.values())
    community_values = list(community.values())

    # # OPTIONALLY: remove reviewers with low (<50) review count, if you are more interested in overworked reviewers
    # industry_values = [val for val in industry_values if val >= 50]
    # community_values = [val for val in community_values if val >= 50]

    # Perform the Mann-Whitney U test
    # alternative='two-sided' tests for differences in the distributions
    result = mannwhitneyu(industry_values, community_values, alternative='two-sided')
    print(f"Mann-Whitney U statistic num reviews: {result.statistic} / {len(industry_values) * len(community_values)}")
    print(f"P-value: {result.pvalue}")

def mannwhitneyu_test_loc():
    industry = {}
    community = {}
    for repo in repositories:
        reviews = get_LOC_per_reviewer(repo)
        if repo.is_industry_backed:
            industry.update(reviews)
        else:
            community.update(reviews)

    # Extract the review counts as lists
    industry_values = list(industry.values())
    community_values = list(community.values())

    # # OPTIONALLY: remove reviewers with low (<50) review count, if you are more interested in overworked reviewers
    # industry_values = [val for val in industry_values if val >= 50]
    # community_values = [val for val in community_values if val >= 50]

    # Perform the Mann-Whitney U test
    # alternative='two-sided' tests for differences in the distributions
    result = mannwhitneyu(industry_values, community_values, alternative='two-sided')
    print(f"Mann-Whitney U statistic loc: {result.statistic} / {len(industry_values) * len(community_values)}")
    print(f"P-value: {result.pvalue}")

def mannwhitneyu_test_review_time():
    industry = {}
    community = {}
    for repo in repositories:
        reviews = get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS)
        if repo.is_industry_backed:
            industry.update(reviews)
        else:
            community.update(reviews)

    # Extract the review counts as lists
    industry_values = list(industry.values())
    community_values = list(community.values())

    # # OPTIONALLY: remove reviewers with low (<50) review count, if you are more interested in overworked reviewers
    # industry_values = [val for val in industry_values if val >= 50]
    # community_values = [val for val in community_values if val >= 50]

    # Perform the Mann-Whitney U test
    # alternative='two-sided' tests for differences in the distributions
    result = mannwhitneyu(industry_values, community_values, alternative='two-sided')
    print(f"Mann-Whitney U statistic review time: {result.statistic} / {len(industry_values) * len(community_values)}")
    print(f"P-value: {result.pvalue}")

def mannwhitneyu_test_response_time():
    industry = {}
    community = {}
    for repo in repositories:
        reviews = get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS)
        if repo.is_industry_backed:
            industry.update(reviews)
        else:
            community.update(reviews)

    # Extract the review counts as lists
    industry_values = list(industry.values())
    community_values = list(community.values())

    # # OPTIONALLY: remove reviewers with low (<50) review count, if you are more interested in overworked reviewers
    # industry_values = [val for val in industry_values if val >= 50]
    # community_values = [val for val in community_values if val >= 50]

    # Perform the Mann-Whitney U test
    # alternative='two-sided' tests for differences in the distributions
    result = mannwhitneyu(industry_values, community_values, alternative='two-sided')
    print(f"Mann-Whitney U statistic response time: {result.statistic} / {len(industry_values) * len(community_values)}")
    print(f"P-value: {result.pvalue}")

if __name__ == "__main__":
    mannwhitneyu_test_num_reviews()
    mannwhitneyu_test_loc()
    mannwhitneyu_test_review_time()
    mannwhitneyu_test_response_time()