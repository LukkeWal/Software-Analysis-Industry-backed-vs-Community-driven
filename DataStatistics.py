"""
Here information about the data is visualized through plots or commandline output
"""

import pandas as pd
import matplotlib.pyplot as plt

from DataHandler import load_repository_metrics, get_number_of_reviews_per_reviewer, get_generated_repositories, Repository

SHOW_PLOTS = True
SAVE_PLOTS = False


def print_date_range(repo: Repository):
    """
    print the date of the first pull request in the repo and the last, as well as the amount of time between them
    """
    metrics = load_repository_metrics(repo)
    start = metrics["created_at"].min()
    end = metrics["closed_at"].max()
    print(f"{repo.name}, {start.strftime("%d-%m-%Y")}, {end.strftime("%d-%m-%Y")}, {end-start}")

def barplot_number_of_reviews_per_reviewer(repo: Repository):
    """
    create a barplot that plots a bar for every reviewer in the repo, representing
    the amount of reviews they have done
    """
    num_reviews = get_number_of_reviews_per_reviewer(repo)
    # Create bar plot
    plt.figure(figsize=(12, 6))
    plt.barh(num_reviews.keys(), num_reviews.values(), color='steelblue')
    plt.xlabel("Number of Reviews")
    plt.ylabel("Reviewers")
    plt.title("Number of Reviews Per Reviewer")
    plt.gca().invert_yaxis()  # Invert y-axis for better readability
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    
    if SHOW_PLOTS:
        plt.show()
    if SAVE_PLOTS:
        plt.savefig()

def boxplot_spread_number_of_reviews_per_reviewer():
    """
    create boxplots to visualize the spread of the amount of reviews
    per reviewer between all repositories
    """
    repo_data = {}
    colors = []
    for repo in get_generated_repositories():
        repo_data[repo.name] = list(get_number_of_reviews_per_reviewer(repo).values())
        if repo.is_industry_backed:
            colors.append('lightblue')
        else:
            colors.append("#D8BFD8")

    plt.figure(figsize=(12, 6))
    # Create boxplot
    box = plt.boxplot(repo_data.values(), labels=repo_data.keys(), patch_artist=True, boxprops=dict(facecolor='lightblue'))
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


def main():
    boxplot_spread_number_of_reviews_per_reviewer()
    for repo in get_generated_repositories():
        print_date_range(repo)
    return

if __name__ == "__main__":
    main()