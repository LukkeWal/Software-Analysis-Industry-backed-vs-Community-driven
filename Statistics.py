from scipy.stats import mannwhitneyu, shapiro, kruskal, spearmanr
import matplotlib.pyplot as plt
import numpy as np

FILTER_OUTLIERS = False

from DataHandler import (
    get_number_of_reviews_per_reviewer, 
    get_LOC_per_reviewer,
    get_average_response_time_hours_per_reviewer,
    get_reviewer_categories_by_num_reviews,
    repositories
)

def run_mannwhitney_test(metric_name, metric_func):
    industry = {}
    community = {}
    for repo in repositories:
        data = metric_func(repo)
        if repo.is_industry_backed:
            industry.update(data)
        else:
            community.update(data)
    industry_values = list(industry.values())
    community_values = list(community.values())
    
    result = mannwhitneyu(industry_values, community_values, alternative='two-sided')
    total_pairs = len(industry_values) * len(community_values)
    print(f"Mann-Whitney U statistic for {metric_name}: {result.statistic} / {total_pairs}")
    print(f"P-value: {result.pvalue}\n")

def test_num_reviews():
    run_mannwhitney_test("num reviews", 
                         lambda repo: get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))

def test_loc():
    run_mannwhitney_test("loc", get_LOC_per_reviewer)

def test_response_time():
    run_mannwhitney_test("response time", 
                         lambda repo: get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))

def run_shapiro_test(metric_name, metric_func):
    industry = {}
    community = {}
    for repo in repositories:
        data = metric_func(repo)
        if repo.is_industry_backed:
            industry.update(data)
        else:
            community.update(data)
    industry_values = list(industry.values())
    community_values = list(community.values())
    
    stat_industry, p_industry = shapiro(industry_values)
    stat_community, p_community = shapiro(community_values)
    
    print(f"Shapiro-Wilk test for {metric_name}:")
    print(f"  Industry - Statistic: {stat_industry}, P-value: {p_industry}")
    print(f"  Community - Statistic: {stat_community}, P-value: {p_community}\n")

def normality_test_num_reviews():
    run_shapiro_test("num reviews", 
                     lambda repo: get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))

def normality_test_loc():
    run_shapiro_test("loc", get_LOC_per_reviewer)

def normality_test_response_time():
    run_shapiro_test("response time", 
                     lambda repo: get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))

def run_kruskal_test(metric_name, metric_func):
    """
    Performs a Kruskal-Wallis test on the specified metric, comparing the industry and community groups.
    """
    industry = {}
    community = {}
    for repo in repositories:
        data = metric_func(repo)
        if repo.is_industry_backed:
            industry.update(data)
        else:
            community.update(data)
    industry_values = list(industry.values())
    community_values = list(community.values())
    
    result = kruskal(industry_values, community_values)
    print(f"Kruskal-Wallis test for {metric_name}:")
    print(f"  Statistic: {result.statistic}, P-value: {result.pvalue}\n")

def kruskal_test_num_reviews():
    run_kruskal_test("num reviews", 
                     lambda repo: get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))

def kruskal_test_loc():
    run_kruskal_test("loc", get_LOC_per_reviewer)

def kruskal_test_response_time():
    run_kruskal_test("response time", 
                     lambda repo: get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))

def cliffs_delta(x, y):
    """
    Computes Cliff's delta for two arrays.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    n1 = len(x)
    n2 = len(y)
    # Compute all pairwise differences using broadcasting
    diff_matrix = np.subtract.outer(x, y)
    num_greater = np.sum(diff_matrix > 0)
    num_less = np.sum(diff_matrix < 0)
    delta = (num_greater - num_less) / (n1 * n2)
    return delta

def run_cliffs_delta(metric_name, metric_func):
    """
    Calculates Cliff's delta comparing the industry and community groups.
    """
    industry = {}
    community = {}
    for repo in repositories:
        data = metric_func(repo)
        if repo.is_industry_backed:
            industry.update(data)
        else:
            community.update(data)
    industry_values = np.array(list(industry.values()))
    community_values = np.array(list(community.values()))
    
    delta = cliffs_delta(industry_values, community_values)
    print(f"Cliff's delta for {metric_name}: {delta}\n")

def cliffs_delta_num_reviews():
    run_cliffs_delta("num reviews", 
                     lambda repo: get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS))

def cliffs_delta_loc():
    run_cliffs_delta("loc", get_LOC_per_reviewer)

def cliffs_delta_response_time():
    run_cliffs_delta("response time", 
                     lambda repo: get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS))

def run_spearman_corr(metric1_name, metric1_func, metric2_name, metric2_func):
    """
    Calculates Spearman's rank correlation coefficient between two metrics,
    separately for industry-backed and community-driven projects.
    
    The metric functions should return dictionaries (e.g., mapping reviewer to value).
    Only common reviewers (intersection) between the two metrics are considered.
    """
    industry_data1, industry_data2 = {}, {}
    community_data1, community_data2 = {}, {}

    for repo in repositories:
        data1 = metric1_func(repo)
        data2 = metric2_func(repo)

        if repo.is_industry_backed:
            industry_data1.update(data1)
            industry_data2.update(data2)
        else:
            community_data1.update(data1)
            community_data2.update(data2)

    # Industry-backed correlation
    common_industry_reviewers = set(industry_data1.keys()) & set(industry_data2.keys())
    if common_industry_reviewers:
        values1_ind = [industry_data1[k] for k in common_industry_reviewers]
        values2_ind = [industry_data2[k] for k in common_industry_reviewers]
        corr_ind, p_value_ind = spearmanr(values1_ind, values2_ind)
        print(f"Industry-backed Spearman correlation ({metric1_name} vs {metric2_name}):")
        print(f"  Correlation coefficient: {corr_ind:.4f}, P-value: {p_value_ind:.4f}")
    else:
        print("No common reviewers found in industry-backed data.")

    # Community-driven correlation
    common_community_reviewers = set(community_data1.keys()) & set(community_data2.keys())
    if common_community_reviewers:
        values1_com = [community_data1[k] for k in common_community_reviewers]
        values2_com = [community_data2[k] for k in common_community_reviewers]
        corr_com, p_value_com = spearmanr(values1_com, values2_com)
        print(f"\nCommunity-driven Spearman correlation ({metric1_name} vs {metric2_name}):")
        print(f"  Correlation coefficient: {corr_com:.4f}, P-value: {p_value_com:.4f}\n")
    else:
        print("No common reviewers found in community-driven data.")

def spearman_corr_num_reviews_vs_loc():
    run_spearman_corr(
        "num reviews",
        lambda repo: get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS),
        "lines of code",
        get_LOC_per_reviewer
    )

def spearman_corr_num_reviews_vs_response_time():
    run_spearman_corr(
        "num reviews",
        lambda repo: get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS),
        "response time",
        lambda repo: get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS)
    )

def spearman_corr_loc_vs_response_time():
    run_spearman_corr(
        "lines of code",
        get_LOC_per_reviewer,
        "response time",
        lambda repo: get_average_response_time_hours_per_reviewer(repo, FILTER_OUTLIERS)
    )

def highest_number_reviews(N):
    all_reviewers = {}  # Dictionary to store reviewer -> (review count, set of repositories)
    
    for repo in repositories:
        repo_reviews = get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS)
        for reviewer, count in repo_reviews.items():
            if reviewer not in all_reviewers:
                all_reviewers[reviewer] = [0, set()]  # Initialize count and repo set
            all_reviewers[reviewer][0] += count  # Update review count
            all_reviewers[reviewer][1].add(repo.name)  # Track repositories
    
    # Get the top 10 reviewers sorted by number of reviews in descending order
    top_reviewers = sorted(all_reviewers.items(), key=lambda x: x[1][0], reverse=True)[:N]

    # Print the top reviewers along with their review count and repositories
    for reviewer, (count, repos) in top_reviewers:
        repo_list = ', '.join(repos)
        print(f"{reviewer}: {count} reviews from repos: {repo_list}")

def aggregate_num_reviews_by_category():
    """
    Aggregates the number of reviews per reviewer from all repositories into categories.
    For each repository, the function uses get_reviewer_categories_by_num_reviews(repo)
    to split reviewers into "Low", "Medium", and "High" based on their log-transformed review count.
    The review counts (from get_number_of_reviews_per_reviewer) for each reviewer are then collected
    into overall lists for industry-backed and community-driven repos.
    
    Returns:
      A dictionary of the form:
        {
          "Low": {"industry": [..], "community": [..]},
          "Medium": {"industry": [..], "community": [..]},
          "High": {"industry": [..], "community": [..]}
        }
    """
    categories = {
        "Low": {"industry": [], "community": []},
        "Medium": {"industry": [], "community": []},
        "High": {"industry": [], "community": []}
    }
    
    for repo in repositories:
        # Get review counts for this repo (as a dict: reviewer -> count)
        reviews = get_number_of_reviews_per_reviewer(repo, FILTER_OUTLIERS)
        # Split reviewers into categories (this function expects a repo argument)
        low_list, medium_list, high_list = get_reviewer_categories_by_num_reviews(repo)
        group = "industry" if repo.is_industry_backed else "community"
        
        for reviewer in low_list:
            if reviewer in reviews:
                categories["Low"][group].append(reviews[reviewer])
        for reviewer in medium_list:
            if reviewer in reviews:
                categories["Medium"][group].append(reviews[reviewer])
        for reviewer in high_list:
            if reviewer in reviews:
                categories["High"][group].append(reviews[reviewer])
                
    return categories

def test_shapiro_num_reviews_categories():
    """
    For each num_reviews category (Low, Medium, High), performs the Shapiro–Wilk test for normality
    separately on the industry-backed and community-driven data.
    (Requires at least 3 data points to run the test.)
    """
    cat_data = aggregate_num_reviews_by_category()
    print("=== Shapiro–Wilk Tests by Num Reviews Category ===")
    for cat in ["Low", "Medium", "High"]:
        ind_values = cat_data[cat]["industry"]
        com_values = cat_data[cat]["community"]
        print(f"\nCategory: {cat}")
        if len(ind_values) >= 3:
            stat, p = shapiro(ind_values)
            print(f"  Industry-backed: Statistic = {stat:.4f}, p-value = {p:.4f}")
        else:
            print("  Industry-backed: Not enough data for Shapiro–Wilk test.")
        if len(com_values) >= 3:
            stat, p = shapiro(com_values)
            print(f"  Community-driven: Statistic = {stat:.4f}, p-value = {p:.4f}")
        else:
            print("  Community-driven: Not enough data for Shapiro–Wilk test.")

def test_mannwhitney_num_reviews_categories():
    """
    For each num_reviews category (Low, Medium, High), performs the Mann–Whitney U test to compare
    the industry-backed and community-driven groups.
    """
    cat_data = aggregate_num_reviews_by_category()
    print("\n=== Mann–Whitney U Tests by Num Reviews Category ===")
    for cat in ["Low", "Medium", "High"]:
        ind_values = cat_data[cat]["industry"]
        com_values = cat_data[cat]["community"]

        print(f"\nCategory: {cat}")
        if ind_values and com_values:
            result = mannwhitneyu(ind_values, com_values, alternative='two-sided')
            total_pairs = len(ind_values) * len(com_values)
            print(f"  Mann–Whitney U statistic: {result.statistic} / {total_pairs}")
            print(f"  p-value: {result.pvalue:.4f}")
        else:
            print("  Not enough data to perform Mann–Whitney U test.")

def test_cliffs_delta_num_reviews_categories():
    """
    For each num_reviews category (Low, Medium, High), computes Cliff's delta comparing
    the industry-backed and community-driven groups.
    """
    cat_data = aggregate_num_reviews_by_category()
    print("\n=== Cliff's Delta by Num Reviews Category ===")
    for cat in ["Low", "Medium", "High"]:
        ind_values = cat_data[cat]["industry"]
        com_values = cat_data[cat]["community"]
        print(f"\nCategory: {cat}")
        if ind_values and com_values:
            delta = cliffs_delta(ind_values, com_values)
            print(f"  Cliff's delta: {delta:.4f}")
        else:
            print("  Not enough data to compute Cliff's delta.")

if __name__ == "__main__":
    # Mann-Whitney tests
    # test_num_reviews()
    # test_loc()
    # test_response_time()
    
    # # Normality tests using Shapiro-Wilk
    # normality_test_num_reviews()
    # normality_test_loc()
    # normality_test_response_time()
    
    # # Kruskal-Wallis tests
    # kruskal_test_num_reviews()
    # kruskal_test_loc()
    # kruskal_test_response_time()
    
    # # Cliff's delta calculations
    # cliffs_delta_num_reviews()
    # cliffs_delta_loc()
    # cliffs_delta_response_time()
    
    # Spearman's rank correlation calculations
    spearman_corr_num_reviews_vs_loc()
    spearman_corr_num_reviews_vs_response_time()
    spearman_corr_loc_vs_response_time()

    # test_shapiro_num_reviews_categories()
    # test_mannwhitney_num_reviews_categories()
    # test_cliffs_delta_num_reviews_categories()

    # highest_number_reviews(100)
