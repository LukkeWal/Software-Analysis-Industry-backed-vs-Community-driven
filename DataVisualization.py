"""
Here information about the data is visualized through plots or commandline output
"""

import os
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
    
FILTER_OUTLIERS = False
SHOW_PLOTS = False
SAVE_PLOTS = True
LOG_TRANSFORM = True
REMOVE_IF_LESS_NUM_REVIEWS = 0
DRAW_VERTICAL_LINES_FOR_NUM_REVIEWS = True

def print_date_range(repo: Repository):
    """
    Prints the date of the first pull request in the repo and the last, 
    as well as the amount of time between them.
    """
    metrics = load_repository_metrics(repo)
    start = metrics["created_at"].min()
    end = metrics["closed_at"].max()
    num_unique_reviewers = metrics["reviewers"].explode().nunique()
    print(
        f"{repo.name}, {start.strftime('%d-%m-%Y')}, "
        f"{end.strftime('%d-%m-%Y')}, {end - start}\t "
        f"length:{len(metrics)}\tnum reviewers: {num_unique_reviewers}"
    )

def _save_plot(filename: str):
    """
    Saves the current Matplotlib figure to the 'images' folder with the given filename.
    Creates the folder if it does not exist.
    """
    if not os.path.exists("images"):
        os.makedirs("images")
    plt.savefig(os.path.join("images", filename), bbox_inches="tight")

def maybe_log_transform(values: list[float]) -> list[float]:
    """
    Applies a log10(x+1) transform to the data if LOG_TRANSFORM is True.
    Skips negative values to avoid math domain errors. 
    (You can customize how to handle zeros/negatives as needed.)
    """
    if LOG_TRANSFORM:
        # Only transform non-negative values
        return [np.log10(v + 1) for v in values if v >= 0]
    else:
        return values

def aggregator_num_reviews(repo: Repository, filter_outliers: bool) -> dict:
    """Returns { reviewer_name: num_reviews } for a given repo,
       filtering out reviewers with less than REMOVE_IF_LESS_NUM_REVIEWS reviews.
    """
    data = get_number_of_reviews_per_reviewer(repo, filter_outliers)
    return { reviewer: count for reviewer, count in data.items() if count >= REMOVE_IF_LESS_NUM_REVIEWS }

def aggregator_loc(repo: Repository, filter_outliers: bool) -> dict:
    """Returns { reviewer_name: total_LOC_reviewed } for a given repo,
       filtering out reviewers with less than REMOVE_IF_LESS_NUM_REVIEWS reviews.
    """
    loc_data = get_LOC_per_reviewer(repo, filter_outliers)
    reviews_data = get_number_of_reviews_per_reviewer(repo, filter_outliers)
    return { reviewer: loc for reviewer, loc in loc_data.items() 
             if reviews_data.get(reviewer, 0) >= REMOVE_IF_LESS_NUM_REVIEWS }

def aggregator_review_time(repo: Repository, filter_outliers: bool) -> dict:
    """Returns { reviewer_name: total_review_time_hours } for a given repo,
       filtering out reviewers with less than REMOVE_IF_LESS_NUM_REVIEWS reviews.
    """
    review_time_data = get_review_time_hours_per_reviewer(repo, filter_outliers)
    reviews_data = get_number_of_reviews_per_reviewer(repo, filter_outliers)
    return { reviewer: time_val for reviewer, time_val in review_time_data.items() 
             if reviews_data.get(reviewer, 0) >= REMOVE_IF_LESS_NUM_REVIEWS }

def aggregator_response_time(repo: Repository, filter_outliers: bool) -> dict:
    """Returns { reviewer_name: average_response_time_hours } for a given repo,
       filtering out reviewers with less than REMOVE_IF_LESS_NUM_REVIEWS reviews.
    """
    response_time_data = get_average_response_time_hours_per_reviewer(repo, filter_outliers)
    reviews_data = get_number_of_reviews_per_reviewer(repo, filter_outliers)
    return { reviewer: resp for reviewer, resp in response_time_data.items() 
             if reviews_data.get(reviewer, 0) >= REMOVE_IF_LESS_NUM_REVIEWS }

def gather_repo_data_for_boxplot(aggregator_func, filter_outliers: bool):
    """
    Returns:
      repo_data: A dictionary { repo_name: [list of (optionally log-transformed) values for that repo] }
      repo_colors: A list of colors aligned with the repos in `repo_data.keys()`
    """
    repo_data = {}
    repo_colors = []
    for repo in get_generated_repositories():
        # 1) use aggregator to get dict {reviewer: value}
        data_dict = aggregator_func(repo, filter_outliers)
        # 2) extract values and optionally transform them
        values = maybe_log_transform(list(data_dict.values()))
        repo_data[repo.name] = values
        # 3) pick a color based on category
        if repo.is_industry_backed:
            repo_colors.append('lightblue')
        else:
            repo_colors.append('#D8BFD8')
    return repo_data, repo_colors

def gather_category_data_for_boxplot(aggregator_func, filter_outliers: bool):
    """
    For category-based plots (Industry-Backed vs. Community-Driven).
    Returns:
      category_data: { "Industry-Backed": [...], "Community-Driven": [...] } with optional log-transform
      category_colors: A list of colors in the order [Industry-Backed, Community-Driven].
    """
    category_data = {
        "Industry-Backed": [],
        "Community-Driven": []
    }
    for repo in get_generated_repositories():
        data_dict = aggregator_func(repo, filter_outliers)
        values = maybe_log_transform(list(data_dict.values()))
        if repo.is_industry_backed:
            category_data["Industry-Backed"].extend(values)
        else:
            category_data["Community-Driven"].extend(values)
    return category_data, ['lightblue', '#D8BFD8']

def plot_boxplot_from_dict(
    data_dict: dict[str, list], 
    colors: list[str], 
    xlabel: str, 
    ylabel: str, 
    rotation: int = 30,
    plot_filename: str = None
):
    """
    Plots a boxplot from a dictionary { x-label: [values] },
    applying the given list of colors to each box.
    If plot_filename is provided and SAVE_PLOTS is True, saves the plot.
    """
    plt.figure(figsize=(12, 6))
    box = plt.boxplot(
        data_dict.values(),
        tick_labels=data_dict.keys(),
        patch_artist=True,   # allows us to set facecolor
        boxprops=dict(facecolor='lightblue')
    )

    # color each box
    for i, patch in enumerate(box['boxes']):
        if i < len(colors):
            patch.set_facecolor(colors[i])

    # formatting
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha="right")
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()

    # Save if requested
    if SAVE_PLOTS and plot_filename:
        _save_plot(plot_filename)

def boxplot_num_reviews_per_reviewer_per_repo():
    repo_data, colors = gather_repo_data_for_boxplot(aggregator_num_reviews, FILTER_OUTLIERS)
    plot_boxplot_from_dict(
        repo_data,
        colors,
        xlabel="Repositories",
        ylabel="Number of Reviews per Reviewer" + (" (log)" if LOG_TRANSFORM else ""),
        plot_filename="boxplot_num_reviews_per_reviewer_per_repo.png"
    )

def boxplot_loc_per_reviewer_per_repo():
    repo_data, colors = gather_repo_data_for_boxplot(aggregator_loc, FILTER_OUTLIERS)
    plot_boxplot_from_dict(
        repo_data,
        colors,
        xlabel="Repositories",
        ylabel="Number of Reviewed LOC per Reviewer" + (" (log)" if LOG_TRANSFORM else ""),
        plot_filename="boxplot_loc_per_reviewer_per_repo.png"
    )

def boxplot_review_time_per_reviewer_per_repo():
    repo_data, colors = gather_repo_data_for_boxplot(aggregator_review_time, FILTER_OUTLIERS)
    plot_boxplot_from_dict(
        repo_data,
        colors,
        xlabel="Repositories",
        ylabel="Total Review Time (hours) per Reviewer" + (" (log)" if LOG_TRANSFORM else ""),
        plot_filename="boxplot_review_time_per_reviewer_per_repo.png"
    )

def boxplot_response_time_per_reviewer_per_repo():
    repo_data, colors = gather_repo_data_for_boxplot(aggregator_response_time, FILTER_OUTLIERS)
    plot_boxplot_from_dict(
        repo_data,
        colors,
        xlabel="Repositories",
        ylabel="Average Response Time (hours) per Reviewer" + (" (log)" if LOG_TRANSFORM else ""),
        plot_filename="boxplot_response_time_per_reviewer_per_repo.png"
    )

def plot_boxplot_for_categories(data_dict: dict[str, list], colors: list[str], ylabel: str, plot_filename: str = None):
    """
    data_dict has keys like {"Industry-Backed": [...], "Community-Driven": [...]}
    colors is a list of length 2, e.g. ['lightblue', '#D8BFD8'].
    """
    plt.figure(figsize=(12, 6))
    box = plt.boxplot(
        data_dict.values(),
        tick_labels=data_dict.keys(),
        patch_artist=True,
        boxprops=dict(facecolor='lightblue')
    )
    for i, patch in enumerate(box['boxes']):
        if i < len(colors):
            patch.set_facecolor(colors[i])

    plt.xlabel("Categories")
    plt.ylabel(ylabel)
    plt.xticks(rotation=30, ha="right")
    plt.subplots_adjust(bottom=0.2)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if SHOW_PLOTS:
        plt.show()

    if SAVE_PLOTS and plot_filename:
        _save_plot(plot_filename)

def boxplot_num_reviews_per_reviewer_per_category():
    data_dict, colors = gather_category_data_for_boxplot(aggregator_num_reviews, FILTER_OUTLIERS)
    plot_boxplot_for_categories(
        data_dict, 
        colors, 
        ylabel="Number of Reviews per Reviewer" + (" (log)" if LOG_TRANSFORM else ""),
        plot_filename="boxplot_num_reviews_per_reviewer_per_category.png"
    )

def boxplot_loc_per_reviewer_per_category():
    data_dict, colors = gather_category_data_for_boxplot(aggregator_loc, FILTER_OUTLIERS)
    plot_boxplot_for_categories(
        data_dict, 
        colors, 
        ylabel="Number of Reviewed LOC per Reviewer" + (" (log)" if LOG_TRANSFORM else ""),
        plot_filename="boxplot_loc_per_reviewer_per_category.png"
    )

def boxplot_review_time_per_reviewer_per_category():
    data_dict, colors = gather_category_data_for_boxplot(aggregator_review_time, FILTER_OUTLIERS)
    plot_boxplot_for_categories(
        data_dict, 
        colors, 
        ylabel="Total Review Time (hours) per Reviewer" + (" (log)" if LOG_TRANSFORM else ""),
        plot_filename="boxplot_review_time_per_reviewer_per_category.png"
    )

def boxplot_response_time_per_reviewer_per_category():
    data_dict, colors = gather_category_data_for_boxplot(aggregator_response_time, FILTER_OUTLIERS)
    plot_boxplot_for_categories(
        data_dict, 
        colors, 
        ylabel="Average Response Time (hours) per Reviewer" + (" (log)" if LOG_TRANSFORM else ""),
        plot_filename="boxplot_response_time_per_reviewer_per_category.png"
    )

def plot_density(values: list[float], label: str, color="blue", plot_filename=None):
    """
    Plots a density of one distribution (optionally log-transformed already).
    """
    plt.figure(figsize=(12, 6))
    plt.hist(values, bins=40, alpha=0.7, color=color, edgecolor='black')
    plt.xlabel(label)
    plt.ylabel('Frequency')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    if SHOW_PLOTS:
        plt.show()

    if SAVE_PLOTS and plot_filename:
        _save_plot(plot_filename)

def density_num_reviews_per_reviewer(repo: Repository):
    dist = aggregator_num_reviews(repo, FILTER_OUTLIERS).values()
    dist = maybe_log_transform(list(dist))
    color = "lightblue" if repo.is_industry_backed else "#D8BFD8"
    filename = f"density_num_reviews_per_reviewer_{repo.name}.png"
    plot_density(
        dist, 
        f"Number of Reviews per Reviewer in {repo.name}" + (" (log)" if LOG_TRANSFORM else ""), 
        color=color, 
        plot_filename=filename
    )

def density_loc_per_reviewer(repo: Repository):
    dist = aggregator_loc(repo, FILTER_OUTLIERS).values()
    dist = maybe_log_transform(list(dist))
    color = "lightblue" if repo.is_industry_backed else "#D8BFD8"
    filename = f"density_loc_per_reviewer_{repo.name}.png"
    plot_density(
        dist, 
        f"Number of Lines of Code per Reviewer in {repo.name}" + (" (log)" if LOG_TRANSFORM else ""), 
        color=color, 
        plot_filename=filename
    )

def density_review_time_per_reviewer(repo: Repository):
    dist = aggregator_review_time(repo, FILTER_OUTLIERS).values()
    dist = maybe_log_transform(list(dist))
    color = "lightblue" if repo.is_industry_backed else "#D8BFD8"
    filename = f"density_review_time_per_reviewer_{repo.name}.png"
    plot_density(
        dist, 
        f"Total Review Time per Reviewer in {repo.name}" + (" (log)" if LOG_TRANSFORM else ""), 
        color=color, 
        plot_filename=filename
    )

def density_response_time_per_reviewer(repo: Repository):
    dist = aggregator_response_time(repo, FILTER_OUTLIERS).values()
    dist = maybe_log_transform(list(dist))
    color = "lightblue" if repo.is_industry_backed else "#D8BFD8"
    filename = f"density_response_time_per_reviewer_{repo.name}.png"
    plot_density(
        dist, 
        f"Average Response Time per Reviewer in {repo.name}" + (" (log)" if LOG_TRANSFORM else ""), 
        color=color, 
        plot_filename=filename
    )

def plot_two_densitys_or_kde(
    dist_a: list[float], 
    dist_b: list[float], 
    xlabel: str, 
    label_a="Industry", 
    label_b="Community", 
    plot_filename=None
):
    """
    Plots 2 distributions as KDE curves (already log-transformed if LOG_TRANSFORM is True).
    """
    plt.figure(figsize=(12, 6))

    sns.kdeplot(dist_a, label=label_a, color="blue", linewidth=2)
    sns.kdeplot(dist_b, label=label_b, color="red", linewidth=2)

    plt.xlabel(xlabel + (" (log)" if LOG_TRANSFORM else ""))
    plt.xlim(left=0)
    plt.ylabel("Density")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()

    if SHOW_PLOTS:
        plt.show()

    if SAVE_PLOTS and plot_filename:
        _save_plot(plot_filename)

def density_num_reviews_per_reviewer_per_category():
    cat_data, _ = gather_category_data_for_boxplot(aggregator_num_reviews, FILTER_OUTLIERS)
    dist_ind = cat_data["Industry-Backed"]
    dist_com = cat_data["Community-Driven"]
    plot_two_densitys_or_kde(
        dist_ind, 
        dist_com, 
        xlabel="Number of Reviews per Reviewer",
        plot_filename="density_num_reviews_per_reviewer_per_category.png"
    )

def density_number_of_LOC_per_reviewer_per_category():
    cat_data, _ = gather_category_data_for_boxplot(aggregator_loc, FILTER_OUTLIERS)
    dist_ind = cat_data["Industry-Backed"]
    dist_com = cat_data["Community-Driven"]
    plot_two_densitys_or_kde(
        dist_ind, 
        dist_com, 
        xlabel="Number of Lines of Code per Reviewer",
        plot_filename="density_loc_per_reviewer_per_category.png"
    )

def density_review_time_hours_per_reviewer_per_category():
    cat_data, _ = gather_category_data_for_boxplot(aggregator_review_time, FILTER_OUTLIERS)
    dist_ind = cat_data["Industry-Backed"]
    dist_com = cat_data["Community-Driven"]
    plot_two_densitys_or_kde(
        dist_ind, 
        dist_com, 
        xlabel="Total Review Time per Reviewer",
        plot_filename="density_review_time_per_reviewer_per_category.png"
    )

def density_average_response_time_hours_per_reviewer_per_category():
    cat_data, _ = gather_category_data_for_boxplot(aggregator_response_time, FILTER_OUTLIERS)
    dist_ind = cat_data["Industry-Backed"]
    dist_com = cat_data["Community-Driven"]
    plot_two_densitys_or_kde(
        dist_ind, 
        dist_com, 
        xlabel="Average Response Time per Reviewer",
        plot_filename="density_response_time_per_reviewer_per_category.png"
    )

def plot_scatter_with_fit(
    x_values: list[float],
    y_values: list[float],
    color: str,
    label: str
):
    """
    Plots a scatter of x_values vs y_values, then draws a linear regression line. 
    """
    plt.scatter(x_values, y_values, alpha=0.5, color=color, label=label)
    if len(x_values) > 1:
        m, b = np.polyfit(x_values, y_values, 1)
        plt.plot(x_values, [m * x + b for x in x_values], color=color, linestyle="--")

def scatterplot_metric_vs_metric(
    aggregator_x,             
    aggregator_y,             
    x_label: str, 
    y_label: str,
    plot_filename: str = None
):
    """
    Creates a scatterplot (with linear fit) for Industry vs Community 
    data for two aggregator functions, applying log transform if requested.
    """
    industry_x = {}
    industry_y = {}
    community_x = {}
    community_y = {}

    for repo in get_generated_repositories():
        data_x = aggregator_x(repo, FILTER_OUTLIERS)
        data_y = aggregator_y(repo, FILTER_OUTLIERS)

        # Put them into the correct dict
        if repo.is_industry_backed:
            for k, v in data_x.items():
                industry_x[k] = v
            for k, v in data_y.items():
                industry_y[k] = v
        else:
            for k, v in data_x.items():
                community_x[k] = v
            for k, v in data_y.items():
                community_y[k] = v

    # Intersect keys so we only pair up reviewers that appear in both aggregator dicts
    industry_reviewers = set(industry_x.keys()) & set(industry_y.keys())
    community_reviewers = set(community_x.keys()) & set(community_y.keys())

    # Convert to lists
    x_ind = [industry_x[r] for r in industry_reviewers]
    y_ind = [industry_y[r] for r in industry_reviewers]
    x_com = [community_x[r] for r in community_reviewers]
    y_com = [community_y[r] for r in community_reviewers]

    # Apply optional log transform
    x_ind = maybe_log_transform(x_ind)
    y_ind = maybe_log_transform(y_ind)
    x_com = maybe_log_transform(x_com)
    y_com = maybe_log_transform(y_com)

    plt.figure(figsize=(12, 6))
    plot_scatter_with_fit(x_ind, y_ind, "blue", "Industry")
    plot_scatter_with_fit(x_com, y_com, "red", "Community")

    plt.xlabel(x_label + (" (log)" if LOG_TRANSFORM else ""))
    plt.ylabel(y_label + (" (log)" if LOG_TRANSFORM else ""))
    plt.legend()
    plt.grid(axis='both', linestyle='--', alpha=0.7)

    if SHOW_PLOTS:
        plt.show()

    if SAVE_PLOTS and plot_filename:
        _save_plot(plot_filename)

def scatterplot_num_reviews_vs_response_time():
    scatterplot_metric_vs_metric(
        aggregator_num_reviews,
        aggregator_response_time,
        x_label="Number of Reviews",
        y_label="Average Response Time (hours)",
        plot_filename="scatter_num_reviews_vs_response_time.png"
    )

def scatterplot_num_reviews_vs_loc():
    scatterplot_metric_vs_metric(
        aggregator_num_reviews,
        aggregator_loc,
        x_label="Number of Reviews",
        y_label="Number of Lines of Code",
        plot_filename="scatter_num_reviews_vs_loc.png"
    )

def scatterplot_respone_time_vs_loc():
    scatterplot_metric_vs_metric(
        aggregator_response_time,
        aggregator_loc,
        x_label="Average Response Time (hours)",
        y_label="Number of Lines of Code",
        plot_filename="scatter_response_time_vs_loc.png"
    )

def plot_histogram(values: list[float], xlabel: str, category_label: str, color: str, plot_filename=None, draw_vertical_lines: bool = False):
    """
    Plots a histogram for a single distribution.
    """
    plt.figure(figsize=(12, 6))
    plt.hist(values, bins=40, alpha=0.7, color=color, edgecolor='black')
    plt.xlabel(xlabel + (" (log)" if LOG_TRANSFORM else ""))
    plt.ylabel('Frequency')
    plt.title(f"{xlabel} for {category_label}")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # If enabled, compute quantile boundaries and draw vertical lines.
    if draw_vertical_lines and values:
        # Compute 33.33rd and 66.66th percentiles
        q1, q2 = np.percentile(values, [33.33, 66.66])
        plt.axvline(q1, color='black', linestyle='--', linewidth=1)
        plt.axvline(q2, color='black', linestyle='--', linewidth=1)
        
        # Add text labels: compute midpoints for each category
        ax = plt.gca()
        y_max = ax.get_ylim()[1]
        min_val = min(values)
        max_val = max(values)
        low_mid = (min_val + q1) / 2
        med_mid = (q1 + q2) / 2
        high_mid = (q2 + max_val) / 2
        plt.text(low_mid, y_max * 0.95, "Low", horizontalalignment='center')
        plt.text(med_mid, y_max * 0.95, "Medium", horizontalalignment='center')
        plt.text(high_mid, y_max * 0.95, "High", horizontalalignment='center')
    
    if SHOW_PLOTS:
        plt.show()

    if SAVE_PLOTS and plot_filename:
        _save_plot(plot_filename)

def generate_histograms_per_category(aggregator_func, xlabel: str, metric_name: str):
    category_data, _ = gather_category_data_for_boxplot(aggregator_func, FILTER_OUTLIERS)

    for category, values in category_data.items():
        color = 'lightblue' if category == "Industry-Backed" else '#D8BFD8'
        safe_category = category.lower().replace("-", "_").replace(" ", "_")
        # Enable vertical lines only for the num_reviews metric if the global flag is on.
        draw_vlines = DRAW_VERTICAL_LINES_FOR_NUM_REVIEWS if metric_name == "num_reviews" else False
        plot_histogram(
            values,
            xlabel=xlabel,
            category_label=category,
            color=color,
            plot_filename=f"histogram_{metric_name}_{safe_category}.png",
            draw_vertical_lines=draw_vlines
        )

def histogram_num_reviews_per_category():
    generate_histograms_per_category(
        aggregator_num_reviews,
        xlabel="Number of Reviews per Reviewer",
        metric_name="num_reviews"
    )

def histogram_loc_per_category():
    generate_histograms_per_category(
        aggregator_loc,
        xlabel="Number of Lines of Code per Reviewer",
        metric_name="loc"
    )


def histogram_response_time_per_category():
    generate_histograms_per_category(
        aggregator_response_time,
        xlabel="Average Response Time (hours) per Reviewer",
        metric_name="response_time"
    )

def main():
    for repo in get_generated_repositories():
        print_date_range(repo)

    # boxplot_num_reviews_per_reviewer_per_repo()
    # boxplot_loc_per_reviewer_per_repo()
    # boxplot_response_time_per_reviewer_per_repo()

    # boxplot_num_reviews_per_reviewer_per_category()
    # boxplot_loc_per_reviewer_per_category()
    # boxplot_response_time_per_reviewer_per_category()

    # density_num_reviews_per_reviewer_per_category()
    # density_number_of_LOC_per_reviewer_per_category()
    # density_average_response_time_hours_per_reviewer_per_category()

    # # scatterplots
    # scatterplot_num_reviews_vs_response_time()
    # scatterplot_num_reviews_vs_loc()
    # scatterplot_respone_time_vs_loc()

    #  histograms
    histogram_num_reviews_per_category()
    # histogram_loc_per_category()
    # histogram_response_time_per_category()


if __name__ == "__main__":
    main()
