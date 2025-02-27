from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt
import numpy as np

from DataHandler import get_number_of_reviews_per_reviewer, repositories

def perform_mannwhitneyu_test():
    industry = {}
    community = {}
    for repo in repositories:
        reviews = get_number_of_reviews_per_reviewer(repo)
        if repo.is_industry_backed:
            industry.update(reviews)
        else:
            community.update(reviews)

    # Extract the review counts as lists
    industry_values = list(industry.values())
    community_values = list(community.values())

    # OPTIONALLY: remove reviewers with low (<50) review count, if you are more interested in overworked reviewers
    industry_values = [val for val in industry_values if val >= 50]
    community_values = [val for val in community_values if val >= 50]

    # Visualize the distributions
    plt.figure(figsize=(12, 6))
    plt.hist(industry_values, bins=40, alpha=0.7, label='Industry', color='lightblue', edgecolor='black')
    plt.hist(community_values, bins=40, alpha=0.7, label='Community', color='#D8BFD8', edgecolor='black')
    plt.xlabel('Number of Reviews per Reviewer')
    plt.ylabel('Frequency')
    plt.title('Histogram of Reviews per Reviewer')
    plt.legend()
    plt.show()

    # Perform the Mann-Whitney U test
    # alternative='two-sided' tests for differences in the distributions
    result = mannwhitneyu(industry_values, community_values, alternative='two-sided')
    print(f"Mann-Whitney U statistic: {result.statistic}")
    print(f"P-value: {result.pvalue}")


if __name__ == "__main__":
    perform_mannwhitneyu_test()