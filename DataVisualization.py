"""
Here information about the data is visualized through plots or commandline output
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from DataHandler import (
    load_repository_metrics, 
    get_number_of_reviews_per_reviewer, 
    get_generated_repositories, 
    Repository,
    get_LOC_per_reviewer,
    get_review_time_hours_per_reviewer,
    get_average_response_time_hours_per_reviewer,
    remove_outliers_from_dict
)
    
FILTER_OUTLIERS = True
SHOW_PLOTS = True
SAVE_PLOTS = False


def print_date_range(repo: Repository):
    """
    print the date of the first pull request in the repo and the last, as well as the amount of time between them
    """
    metrics = load_repository_metrics(repo)
    start = metrics["created_at"].min()
    end = metrics["closed_at"].max()
    num_unique_reviewers = metrics["reviewers"].explode().nunique()
    print(f"{repo.name}, {start.strftime("%d-%m-%Y")}, {end.strftime("%d-%m-%Y")}, {end-start}\t length:{len(metrics)}\tnum reviewers: {num_unique_reviewers}")

def barplot_number_of_reviews_per_reviewer(repo: Repository):
    """
    create a barplot that plots a bar for every reviewer in the repo, representing
    the amount of reviews they have done
    """
    num_reviews = get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS)
    # Create bar plot
    plt.figure(figsize=(12, 6))
    plt.barh(list(num_reviews.keys()), list(num_reviews.values()), color='steelblue')
    plt.xlabel("Number of Reviews")
    plt.ylabel("Reviewers")
    plt.title(f"Number of Reviews Per Reviewer: {repo.name}")
    plt.gca().invert_yaxis()  # Invert y-axis for better readability
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    
    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()

def boxplots_spread_number_of_reviews_per_reviewer_per_repo():
    """
    create boxplots to visualize the spread of the amount of reviews
    per reviewer between all repositories
    """
    repo_data = {}
    colors = []
    for repo in get_generated_repositories():
        repo_data[repo.name] = list(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS).values())
        if repo.is_industry_backed:
            colors.append('lightblue')
        else:
            colors.append("#D8BFD8")

    plt.figure(figsize=(12, 6))
    # Create boxplot
    box = plt.boxplot(repo_data.values(), tick_labels=repo_data.keys(), patch_artist=True, boxprops=dict(facecolor='lightblue'))
    for i, patch in enumerate(box['boxes']):
        patch.set_facecolor(colors[i])
    # Formatting
    plt.xlabel("Repositories")
    plt.ylabel("number of reviews per reviewer")
    plt.xticks(rotation=30, ha="right")  # Rotate x-axis labels for better readability
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()

def boxplots_spread_number_of_LOC_per_reviewer_per_repo():
    """
    create boxplots to visualize the spread of the amount of reviewed LOC
    per reviewer between all repositories
    """
    repo_data = {}
    colors = []
    for repo in get_generated_repositories():
        repo_data[repo.name] = list(get_LOC_per_reviewer(repo, FILTER_OUTLIERS).values())
        if repo.is_industry_backed:
            colors.append('lightblue')
        else:
            colors.append("#D8BFD8")

    plt.figure(figsize=(12, 6))
    # Create boxplot
    box = plt.boxplot(repo_data.values(), tick_labels=repo_data.keys(), patch_artist=True, boxprops=dict(facecolor='lightblue'))
    for i, patch in enumerate(box['boxes']):
        patch.set_facecolor(colors[i])
    # Formatting
    plt.xlabel("Repositories")
    plt.ylabel("number of reviewed lines of code per reviewer")
    plt.xticks(rotation=30, ha="right")  # Rotate x-axis labels for better readability
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()

def boxplots_spread_review_time_hours_per_reviewer_per_repo():
    """
    create boxplots to visualize the spread of the amount of
    total review time in hours per reviewer
    """
    repo_data = {}
    colors = []
    for repo in get_generated_repositories():
        repo_data[repo.name] = list(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values())
        if repo.is_industry_backed:
            colors.append('lightblue')
        else:
            colors.append("#D8BFD8")

    plt.figure(figsize=(12, 6))
    # Create boxplot
    box = plt.boxplot(repo_data.values(), tick_labels=repo_data.keys(), patch_artist=True, boxprops=dict(facecolor='lightblue'))
    for i, patch in enumerate(box['boxes']):
        patch.set_facecolor(colors[i])
    # Formatting
    plt.xlabel("Repositories")
    plt.ylabel("total review time in hours per reviewer")
    plt.xticks(rotation=30, ha="right")  # Rotate x-axis labels for better readability
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()

def boxplots_spread_average_response_time_hours_per_reviewer_per_repo():
    """
    create boxplots to visualize the spread of the amount of
    average response time in hours per reviewer, a PRs response time
    is accounted to a specific reviewer if they were the first
    to review a PR
    """
    repo_data = {}
    colors = []
    for repo in get_generated_repositories():
        repo_data[repo.name] = list(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values())
        if repo.is_industry_backed:
            colors.append('lightblue')
        else:
            colors.append("#D8BFD8")

    plt.figure(figsize=(12, 6))
    # Create boxplot
    box = plt.boxplot(repo_data.values(), tick_labels=repo_data.keys(), patch_artist=True, boxprops=dict(facecolor='lightblue'))
    for i, patch in enumerate(box['boxes']):
        patch.set_facecolor(colors[i])
    # Formatting
    plt.xlabel("Repositories")
    plt.ylabel("average response time in hours per reviewer")
    plt.xticks(rotation=30, ha="right")  # Rotate x-axis labels for better readability
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()

def boxplots_spread_number_of_reviews_per_reviewer_per_category():
    """
    create boxplots to visualize the spread of the amount of reviews
    per reviewer between the two categories
    """
    category_data = {"Industry-Backed": [], "Community-Driven": []}
    colors = ['lightblue', "#D8BFD8"]
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            category_data["Industry-Backed"].extend(list(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS).values()))
        else: 
            category_data["Community-Driven"].extend(list(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS).values()))

    plt.figure(figsize=(12, 6))
    # Create boxplot
    box = plt.boxplot(category_data.values(), tick_labels=category_data.keys(), patch_artist=True, boxprops=dict(facecolor='lightblue'))
    for i, patch in enumerate(box['boxes']):
        patch.set_facecolor(colors[i])
    # Formatting
    plt.xlabel("Categories")
    plt.ylabel("number of reviews per reviewer")
    plt.xticks(rotation=30, ha="right")  # Rotate x-axis labels for better readability
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()
    return

def boxplots_spread_number_of_LOC_per_reviewer_per_category():
    """
    create boxplots to visualize the spread of the amount of reviewed LOC
    per reviewer between all repositories
    """
    category_data = {"Industry-Backed": [], "Community-Driven": []}
    colors = ['lightblue', "#D8BFD8"]
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            category_data["Industry-Backed"].extend(list(get_LOC_per_reviewer(repo, FILTER_OUTLIERS).values()))
        else: 
            category_data["Community-Driven"].extend(list(get_LOC_per_reviewer(repo, FILTER_OUTLIERS).values()))

    plt.figure(figsize=(12, 6))
    # Create boxplot
    box = plt.boxplot(category_data.values(), tick_labels=category_data.keys(), patch_artist=True, boxprops=dict(facecolor='lightblue'))
    for i, patch in enumerate(box['boxes']):
        patch.set_facecolor(colors[i])
    # Formatting
    plt.xlabel("Categories")
    plt.ylabel("number of reviewed lines of code per reviewer")
    plt.xticks(rotation=30, ha="right")  # Rotate x-axis labels for better readability
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()
    return

def boxplots_spread_review_time_hours_per_reviewer_per_category():
    """
    create boxplots to visualize the spread of the amount of
    total review time in hours per reviewer
    """
    category_data = {"Industry-Backed": [], "Community-Driven": []}
    colors = ['lightblue', "#D8BFD8"]
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            category_data["Industry-Backed"].extend(list(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values()))
        else: 
            category_data["Community-Driven"].extend(list(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values()))

    plt.figure(figsize=(12, 6))
    # Create boxplot
    box = plt.boxplot(category_data.values(), tick_labels=category_data.keys(), patch_artist=True, boxprops=dict(facecolor='lightblue'))
    for i, patch in enumerate(box['boxes']):
        patch.set_facecolor(colors[i])
    # Formatting
    plt.xlabel("Categories")
    plt.ylabel("total review time in hours per reviewer")
    plt.xticks(rotation=30, ha="right")  # Rotate x-axis labels for better readability
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()
    return

def boxplots_spread_average_response_time_hours_per_reviewer_per_category():
    """
    create boxplots to visualize the spread of the amount of
    average response time in hours per reviewer, a PRs response time
    is accounted to a specific reviewer if they were the first
    to review a PR
    """
    category_data = {"Industry-Backed": [], "Community-Driven": []}
    colors = ['lightblue', "#D8BFD8"]
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            category_data["Industry-Backed"].extend(list(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values()))
        else: 
            category_data["Community-Driven"].extend(list(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values()))

    plt.figure(figsize=(12, 6))
    # Create boxplot
    box = plt.boxplot(category_data.values(), tick_labels=category_data.keys(), patch_artist=True, boxprops=dict(facecolor='lightblue'))
    for i, patch in enumerate(box['boxes']):
        patch.set_facecolor(colors[i])
    # Formatting
    plt.xlabel("Categories")
    plt.ylabel("average response time in hours per reviewer")
    plt.xticks(rotation=30, ha="right")  # Rotate x-axis labels for better readability
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()
    return

def histogram_one_distribution(dist: list, xlabel, color="blue"):
    plt.figure(figsize=(12, 6))
    plt.hist(dist, bins=40, alpha=0.7, color=color, edgecolor='black')
    plt.xlabel(xlabel)
    plt.ylabel('Frequency')
    plt.legend()
    plt.show()
    return

def histogram_two_distributions(distOne, distTwo, xlabel):
    # max_value = max(max(distOne), max(distTwo))
    # min_value = min(min(distOne), min(distTwo))
    # bins = np.linspace(min_value, max_value, 40)  # 40 evenly spaced bin edges
    plt.figure(figsize=(12, 6))
    # plt.hist(distOne, bins=bins, alpha=0.7, label='Industry', color='lightblue', edgecolor='black')
    # plt.hist(distTwo, bins=bins, alpha=0.7, label='Community', color='#D8BFD8', edgecolor='black')

    sns.kdeplot(distOne, label="Industry", color="blue", linewidth=2)
    sns.kdeplot(distTwo, label="Community", color="red", linewidth=2)

    # plt.hist(distOne, bins=40, density=True, histtype='step', linewidth=1, label='Industry', color='blue')
    # plt.hist(distTwo, bins=40, density=True, histtype='step', linewidth=1, label='Community', color='red')

    plt.xlabel(xlabel)
    plt.xlim(left=0)
    plt.ylabel('Frequency')
    plt.legend()
    plt.show()
    return

def histogram_number_of_reviews_per_reviewer(repo: Repository):
    if repo.is_industry_backed: 
        color = "lightblue"
    else:
        color = "#D8BFD8"
    dist = list(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS).values())
    histogram_one_distribution(dist, f"number of reviews per reviewer in {repo.name}", color=color)
    return

def histogram_number_of_LOC_per_reviewer(repo: Repository):
    if repo.is_industry_backed: 
        color = "lightblue"
    else:
        color = "#D8BFD8"
    dist = list(get_LOC_per_reviewer(repo, FILTER_OUTLIERS).values())
    histogram_one_distribution(dist, f"number of lines of code per reviewer in {repo.name}", color=color)
    return

def histogram_review_time_hours_per_reviewer(repo: Repository):
    if repo.is_industry_backed: 
        color = "lightblue"
    else:
        color = "#D8BFD8"
    dist = list(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values())
    histogram_one_distribution(dist, f"review time hours per reviewer in {repo.name}", color=color)
    return

def histogram_average_response_time_hours_per_reviewer(repo: Repository):
    if repo.is_industry_backed: 
        color = "lightblue"
    else:
        color = "#D8BFD8"
    dist = list(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values())
    histogram_one_distribution(dist, f"average response time per reviewer in {repo.name}", color = color)
    return

def histogram_number_of_reviews_per_reviewer_per_category():
    category_data = {"Industry-Backed": [], "Community-Driven": []}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            category_data["Industry-Backed"].extend(list(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS).values()))
        else: 
            category_data["Community-Driven"].extend(list(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS).values()))

    histogram_two_distributions(category_data["Industry-Backed"], 
                                category_data["Community-Driven"], 
                                "number of reviews per reviewer")
    return

def histogram_number_of_LOC_per_reviewer_per_category():
    category_data = {"Industry-Backed": [], "Community-Driven": []}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            category_data["Industry-Backed"].extend(list(get_LOC_per_reviewer(repo, FILTER_OUTLIERS).values()))
        else: 
            category_data["Community-Driven"].extend(list(get_LOC_per_reviewer(repo, FILTER_OUTLIERS).values()))
    histogram_two_distributions(category_data["Industry-Backed"], 
                                category_data["Community-Driven"], 
                                "number of lines of code per reviewer")
    return

def histogram_review_time_hours_per_reviewer_per_category():
    category_data = {"Industry-Backed": [], "Community-Driven": []}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            category_data["Industry-Backed"].extend(list(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values()))
        else: 
            category_data["Community-Driven"].extend(list(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values()))
    histogram_two_distributions(category_data["Industry-Backed"], 
                                category_data["Community-Driven"], 
                                "total review time per reviewer")
    return

def histogram_average_response_time_hours_per_reviewer_per_category():
    category_data = {"Industry-Backed": [], "Community-Driven": []}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            category_data["Industry-Backed"].extend(list(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values()))
        else: 
            category_data["Community-Driven"].extend(list(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS).values()))
    histogram_two_distributions(category_data["Industry-Backed"], 
                                category_data["Community-Driven"], 
                                "average reponse time per reviewer")
    return

def scatterplot_num_reviews_vs_response_time():
    industry_backed_num_reviews = {}
    community_driven_num_reviews = {}
    industry_backed_response_time = {}
    community_driven_response_time = {}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            industry_backed_num_reviews.update(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))
            industry_backed_response_time.update(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
        else: 
            community_driven_num_reviews.update(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))
            community_driven_response_time.update(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
    # Find common reviewers
    common_reviewers_industry = set(industry_backed_num_reviews.keys()) & set(industry_backed_response_time.keys())
    common_reviewers_community = set(community_driven_num_reviews.keys()) & set(community_driven_response_time.keys())
    # Extract values for scatter plot
    industry_backed_num_reviews = [industry_backed_num_reviews[reviewer] for reviewer in common_reviewers_industry]
    community_driven_num_reviews = [community_driven_num_reviews[reviewer] for reviewer in common_reviewers_community]
    industry_backed_response_time = [industry_backed_response_time[reviewer] for reviewer in common_reviewers_industry]
    community_driven_response_time = [community_driven_response_time[reviewer] for reviewer in common_reviewers_community]


    plt.scatter(industry_backed_num_reviews, industry_backed_response_time, alpha=0.5, color="blue", label='Industry')
    plt.scatter(community_driven_num_reviews, community_driven_response_time, alpha=0.5, color="red", label="Community")

    # Fit and plot trend line for Industry
    if len(industry_backed_num_reviews) > 1:
        m_ind, b_ind = np.polyfit(industry_backed_num_reviews, industry_backed_response_time, 1)
        plt.plot(industry_backed_num_reviews, m_ind * np.array(industry_backed_num_reviews) + b_ind, color="blue", linestyle="--")

    # Fit and plot trend line for Community
    if len(community_driven_num_reviews) > 1:
        m_com, b_com = np.polyfit(community_driven_num_reviews, community_driven_response_time, 1)
        plt.plot(community_driven_num_reviews, m_com * np.array(community_driven_num_reviews) + b_com, color="red", linestyle="--")

    plt.xlabel("number of reviews")
    plt.ylabel("average response time (hours)")
    plt.legend()
    plt.show()

def scatterplot_num_reviews_vs_review_time():
    industry_backed_num_reviews = {}
    community_driven_num_reviews = {}
    industry_backed_response_time = {}
    community_driven_response_time = {}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            industry_backed_num_reviews.update(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))
            industry_backed_response_time.update(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
        else: 
            community_driven_num_reviews.update(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))
            community_driven_response_time.update(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
    # Find common reviewers
    common_reviewers_industry = set(industry_backed_num_reviews.keys()) & set(industry_backed_response_time.keys())
    common_reviewers_community = set(community_driven_num_reviews.keys()) & set(community_driven_response_time.keys())
    # Extract values for scatter plot
    industry_backed_num_reviews = [industry_backed_num_reviews[reviewer] for reviewer in common_reviewers_industry]
    community_driven_num_reviews = [community_driven_num_reviews[reviewer] for reviewer in common_reviewers_community]
    industry_backed_response_time = [industry_backed_response_time[reviewer] for reviewer in common_reviewers_industry]
    community_driven_response_time = [community_driven_response_time[reviewer] for reviewer in common_reviewers_community]


    plt.scatter(industry_backed_num_reviews, industry_backed_response_time, alpha=0.5, color="blue", label='Industry')
    plt.scatter(community_driven_num_reviews, community_driven_response_time, alpha=0.5, color="red", label="Community")

    # Fit and plot trend line for Industry
    if len(industry_backed_num_reviews) > 1:
        m_ind, b_ind = np.polyfit(industry_backed_num_reviews, industry_backed_response_time, 1)
        plt.plot(industry_backed_num_reviews, m_ind * np.array(industry_backed_num_reviews) + b_ind, color="blue", linestyle="--")

    # Fit and plot trend line for Community
    if len(community_driven_num_reviews) > 1:
        m_com, b_com = np.polyfit(community_driven_num_reviews, community_driven_response_time, 1)
        plt.plot(community_driven_num_reviews, m_com * np.array(community_driven_num_reviews) + b_com, color="red", linestyle="--")

    plt.xlabel("number of reviews")
    plt.ylabel("total review time (hours)")
    plt.legend()
    plt.show()

def scatterplot_num_reviews_vs_loc():
    industry_backed_num_reviews = {}
    community_driven_num_reviews = {}
    industry_backed_response_time = {}
    community_driven_response_time = {}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            industry_backed_num_reviews.update(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))
            industry_backed_response_time.update(get_LOC_per_reviewer(repo, FILTER_OUTLIERS))
        else: 
            community_driven_num_reviews.update(get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))
            community_driven_response_time.update(get_LOC_per_reviewer(repo, FILTER_OUTLIERS))
    # Find common reviewers
    common_reviewers_industry = set(industry_backed_num_reviews.keys()) & set(industry_backed_response_time.keys())
    common_reviewers_community = set(community_driven_num_reviews.keys()) & set(community_driven_response_time.keys())
    # Extract values for scatter plot
    industry_backed_num_reviews = [industry_backed_num_reviews[reviewer] for reviewer in common_reviewers_industry]
    community_driven_num_reviews = [community_driven_num_reviews[reviewer] for reviewer in common_reviewers_community]
    industry_backed_response_time = [industry_backed_response_time[reviewer] for reviewer in common_reviewers_industry]
    community_driven_response_time = [community_driven_response_time[reviewer] for reviewer in common_reviewers_community]


    plt.scatter(industry_backed_num_reviews, industry_backed_response_time, alpha=0.5, color="blue", label='Industry')
    plt.scatter(community_driven_num_reviews, community_driven_response_time, alpha=0.5, color="red", label="Community")

    # Fit and plot trend line for Industry
    if len(industry_backed_num_reviews) > 1:
        m_ind, b_ind = np.polyfit(industry_backed_num_reviews, industry_backed_response_time, 1)
        plt.plot(industry_backed_num_reviews, m_ind * np.array(industry_backed_num_reviews) + b_ind, color="blue", linestyle="--")

    # Fit and plot trend line for Community
    if len(community_driven_num_reviews) > 1:
        m_com, b_com = np.polyfit(community_driven_num_reviews, community_driven_response_time, 1)
        plt.plot(community_driven_num_reviews, m_com * np.array(community_driven_num_reviews) + b_com, color="red", linestyle="--")

    plt.xlabel("number of reviews")
    plt.ylabel("lines of code")
    plt.legend()
    plt.show()

def scatterplot_respone_time_vs_loc():
    industry_backed_num_reviews = {}
    community_driven_num_reviews = {}
    industry_backed_response_time = {}
    community_driven_response_time = {}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            industry_backed_num_reviews.update(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
            industry_backed_response_time.update(get_LOC_per_reviewer(repo, FILTER_OUTLIERS))
        else: 
            community_driven_num_reviews.update(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
            community_driven_response_time.update(get_LOC_per_reviewer(repo, FILTER_OUTLIERS))
    # Find common reviewers
    common_reviewers_industry = set(industry_backed_num_reviews.keys()) & set(industry_backed_response_time.keys())
    common_reviewers_community = set(community_driven_num_reviews.keys()) & set(community_driven_response_time.keys())
    # Extract values for scatter plot
    industry_backed_num_reviews = [industry_backed_num_reviews[reviewer] for reviewer in common_reviewers_industry]
    community_driven_num_reviews = [community_driven_num_reviews[reviewer] for reviewer in common_reviewers_community]
    industry_backed_response_time = [industry_backed_response_time[reviewer] for reviewer in common_reviewers_industry]
    community_driven_response_time = [community_driven_response_time[reviewer] for reviewer in common_reviewers_community]


    plt.scatter(industry_backed_num_reviews, industry_backed_response_time, alpha=0.5, color="blue", label='Industry')
    plt.scatter(community_driven_num_reviews, community_driven_response_time, alpha=0.5, color="red", label="Community")

    # Fit and plot trend line for Industry
    if len(industry_backed_num_reviews) > 1:
        m_ind, b_ind = np.polyfit(industry_backed_num_reviews, industry_backed_response_time, 1)
        plt.plot(industry_backed_num_reviews, m_ind * np.array(industry_backed_num_reviews) + b_ind, color="blue", linestyle="--")

    # Fit and plot trend line for Community
    if len(community_driven_num_reviews) > 1:
        m_com, b_com = np.polyfit(community_driven_num_reviews, community_driven_response_time, 1)
        plt.plot(community_driven_num_reviews, m_com * np.array(community_driven_num_reviews) + b_com, color="red", linestyle="--")

    plt.xlabel("average response time (hours)")
    plt.ylabel("lines of code")
    plt.legend()
    plt.show()

def scatterplot_review_time_vs_loc():
    industry_backed_num_reviews = {}
    community_driven_num_reviews = {}
    industry_backed_response_time = {}
    community_driven_response_time = {}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            industry_backed_num_reviews.update(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
            industry_backed_response_time.update(get_LOC_per_reviewer(repo))
        else: 
            community_driven_num_reviews.update(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
            community_driven_response_time.update(get_LOC_per_reviewer(repo))
    # Find common reviewers
    common_reviewers_industry = set(industry_backed_num_reviews.keys()) & set(industry_backed_response_time.keys())
    common_reviewers_community = set(community_driven_num_reviews.keys()) & set(community_driven_response_time.keys())
    # Extract values for scatter plot
    industry_backed_num_reviews = [industry_backed_num_reviews[reviewer] for reviewer in common_reviewers_industry]
    community_driven_num_reviews = [community_driven_num_reviews[reviewer] for reviewer in common_reviewers_community]
    industry_backed_response_time = [industry_backed_response_time[reviewer] for reviewer in common_reviewers_industry]
    community_driven_response_time = [community_driven_response_time[reviewer] for reviewer in common_reviewers_community]


    plt.scatter(industry_backed_num_reviews, industry_backed_response_time, alpha=0.5, color="blue", label='Industry')
    plt.scatter(community_driven_num_reviews, community_driven_response_time, alpha=0.5, color="red", label="Community")

    # Fit and plot trend line for Industry
    if len(industry_backed_num_reviews) > 1:
        m_ind, b_ind = np.polyfit(industry_backed_num_reviews, industry_backed_response_time, 1)
        plt.plot(industry_backed_num_reviews, m_ind * np.array(industry_backed_num_reviews) + b_ind, color="blue", linestyle="--")

    # Fit and plot trend line for Community
    if len(community_driven_num_reviews) > 1:
        m_com, b_com = np.polyfit(community_driven_num_reviews, community_driven_response_time, 1)
        plt.plot(community_driven_num_reviews, m_com * np.array(community_driven_num_reviews) + b_com, color="red", linestyle="--")

    plt.xlabel("total review time (hours)")
    plt.ylabel("lines of code")
    plt.legend()
    plt.show()

def scatterplot_review_time_vs_response_time():
    industry_backed_num_reviews = {}
    community_driven_num_reviews = {}
    industry_backed_response_time = {}
    community_driven_response_time = {}
    for repo in get_generated_repositories():
        if repo.is_industry_backed:
            industry_backed_num_reviews.update(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
            industry_backed_response_time.update(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
        else: 
            community_driven_num_reviews.update(get_review_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
            community_driven_response_time.update(get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))
    # Find common reviewers
    common_reviewers_industry = set(industry_backed_num_reviews.keys()) & set(industry_backed_response_time.keys())
    common_reviewers_community = set(community_driven_num_reviews.keys()) & set(community_driven_response_time.keys())
    # Extract values for scatter plot
    industry_backed_num_reviews = [industry_backed_num_reviews[reviewer] for reviewer in common_reviewers_industry]
    community_driven_num_reviews = [community_driven_num_reviews[reviewer] for reviewer in common_reviewers_community]
    industry_backed_response_time = [industry_backed_response_time[reviewer] for reviewer in common_reviewers_industry]
    community_driven_response_time = [community_driven_response_time[reviewer] for reviewer in common_reviewers_community]


    plt.scatter(industry_backed_num_reviews, industry_backed_response_time, alpha=0.5, color="blue", label='Industry')
    plt.scatter(community_driven_num_reviews, community_driven_response_time, alpha=0.5, color="red", label="Community")

    # Fit and plot trend line for Industry
    if len(industry_backed_num_reviews) > 1:
        m_ind, b_ind = np.polyfit(industry_backed_num_reviews, industry_backed_response_time, 1)
        plt.plot(industry_backed_num_reviews, m_ind * np.array(industry_backed_num_reviews) + b_ind, color="blue", linestyle="--")

    # Fit and plot trend line for Community
    if len(community_driven_num_reviews) > 1:
        m_com, b_com = np.polyfit(community_driven_num_reviews, community_driven_response_time, 1)
        plt.plot(community_driven_num_reviews, m_com * np.array(community_driven_num_reviews) + b_com, color="red", linestyle="--")

    plt.xlabel("total review time (hours)")
    plt.ylabel("average response time (hours)")
    plt.legend()
    plt.show()

def main():
    # for repo in get_generated_repositories():
    #     print_date_range(repo)
        # histogram_number_of_reviews_per_reviewer(repo)
        # histogram_number_of_LOC_per_reviewer(repo)
        # histogram_review_time_hours_per_reviewer(repo)
        # histogram_average_response_time_hours_per_reviewer(repo)
    # boxplots_spread_number_of_reviews_per_reviewer_per_repo()
    # boxplots_spread_number_of_LOC_per_reviewer_per_repo()
    # boxplots_spread_review_time_hours_per_reviewer_per_repo()
    # boxplots_spread_average_response_time_hours_per_reviewer_per_repo()
    # boxplots_spread_number_of_reviews_per_reviewer_per_category()
    # boxplots_spread_number_of_LOC_per_reviewer_per_category()
    # boxplots_spread_review_time_hours_per_reviewer_per_category()
    # boxplots_spread_average_response_time_hours_per_reviewer_per_category()

    # histogram_number_of_reviews_per_reviewer_per_category()
    # histogram_number_of_LOC_per_reviewer_per_category()
    # histogram_review_time_hours_per_reviewer_per_category()
    # histogram_average_response_time_hours_per_reviewer_per_category()

    scatterplot_num_reviews_vs_response_time()
    scatterplot_num_reviews_vs_loc()
    scatterplot_num_reviews_vs_review_time()
    scatterplot_review_time_vs_loc()
    scatterplot_review_time_vs_response_time()
    scatterplot_respone_time_vs_loc()
    return


if __name__ == "__main__":
    main()