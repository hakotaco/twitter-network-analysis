import sys
import os
import networkx as nx

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from network_utils import (
    load_csv_data,
    create_engagement_cascade_graph,
    analyze_cascade_stats,
    get_cascade_roots,
    load_untrusted_domains,
    filter_tweets_with_untrusted_sources,
    quick_export,
)


def analyze_full_network(df, show_plot=False):
    """
    Analyze the full retweet and reply network.

    Args:
        df: DataFrame containing all tweets
        show_plot: Whether to display visualization

    Returns:
        NetworkX DiGraph of the cascade network
    """
    print("\n" + "=" * 70)
    print("FULL NETWORK ANALYSIS: All Retweets and Replies")
    print("=" * 70)

    # Create engagement cascade graph
    G = create_engagement_cascade_graph(
        df,
        author_col="author_id",
        tweet_id_col="tweet_id",
        reference_type_col="reference_type",
        reference_id_col="reference_id",
        like_col="like_count",
        retweet_col="retweet_count",
        show_plot=show_plot,
    )

    if G.number_of_nodes() == 0:
        print("No network to analyze.")
        return G

    # Analyze cascade statistics
    print("\n--- Cascade Statistics ---")
    cascade_stats = analyze_cascade_stats(G)
    for key, value in cascade_stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    # Find and display root tweets
    roots = get_cascade_roots(G)
    print("\n--- Root Tweets (Original Posts) ---")
    print(f"  Found {len(roots)} root tweets that started cascades")

    # Show top users by engagement
    engagement_weights = nx.get_node_attributes(G, "engagement_weight")
    if engagement_weights:
        top_users = sorted(
            engagement_weights.items(), key=lambda x: x[1], reverse=True
        )[:10]
        print("\n--- Top 10 Users by Engagement (Likes + Retweets) ---")
        for i, (user, weight) in enumerate(top_users, 1):
            print(f"  {i}. User {user}: {weight} total engagement")

    # Show degree distribution
    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())

    if in_degrees:
        top_in = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        print("\n--- Top 5 Most Retweeted/Replied-To Users (In-degree) ---")
        for i, (user, degree) in enumerate(top_in, 1):
            print(f"  {i}. User {user}: {degree} incoming edges")

    if out_degrees:
        top_out = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        print("\n--- Top 5 Most Active Retweeters/Repliers (Out-degree) ---")
        for i, (user, degree) in enumerate(top_out, 1):
            print(f"  {i}. User {user}: {degree} outgoing edges")

    return G


def analyze_untrusted_sources_network(df, untrusted_domains_file, show_plot=False):
    """
    Analyze the network of tweets containing untrusted sources.

    Args:
        df: DataFrame containing all tweets
        untrusted_domains_file: Path to untrusted sources CSV
        show_plot: Whether to display visualization

    Returns:
        NetworkX DiGraph of the untrusted sources cascade network
    """
    print("\n" + "=" * 70)
    print("UNTRUSTED SOURCES ANALYSIS: Tweets with Misinformation Domains")
    print("=" * 70)

    # Load untrusted domains
    untrusted_domains = load_untrusted_domains(untrusted_domains_file)

    # Filter tweets containing untrusted sources
    print("\n--- Filtering Tweets ---")
    filtered_df = filter_tweets_with_untrusted_sources(df, untrusted_domains)

    if filtered_df.empty:
        print("No tweets found containing untrusted sources.")
        return nx.DiGraph()

    percentage = (len(filtered_df) / len(df)) * 100
    print(f"  Percentage of tweets with untrusted sources: {percentage:.2f}%")

    # Create cascade graph for untrusted source tweets
    print("\n--- Building Network for Untrusted Source Tweets ---")
    G_untrusted = create_engagement_cascade_graph(
        filtered_df,
        author_col="author_id",
        tweet_id_col="tweet_id",
        reference_type_col="reference_type",
        reference_id_col="reference_id",
        like_col="like_count",
        retweet_col="retweet_count",
        show_plot=show_plot,
    )

    if G_untrusted.number_of_nodes() == 0:
        print("No network relationships found in untrusted source tweets.")
        return G_untrusted

    # Analyze cascade statistics
    print("\n--- Cascade Statistics for Untrusted Sources ---")
    cascade_stats = analyze_cascade_stats(G_untrusted)
    for key, value in cascade_stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    # Find root tweets with untrusted sources
    roots = get_cascade_roots(G_untrusted)
    print("\n--- Root Tweets with Untrusted Sources ---")
    print(f"  Found {len(roots)} root tweets containing untrusted sources")

    # Show top spreaders of untrusted information
    engagement_weights = nx.get_node_attributes(G_untrusted, "engagement_weight")
    if engagement_weights:
        top_spreaders = sorted(
            engagement_weights.items(), key=lambda x: x[1], reverse=True
        )[:10]
        print("\n--- Top 10 Spreaders of Untrusted Sources (by Engagement) ---")
        for i, (user, weight) in enumerate(top_spreaders, 1):
            print(f"  {i}. User {user}: {weight} total engagement")

    return G_untrusted


def compare_networks(G_full, G_untrusted):
    """
    Compare the full network with the untrusted sources network.

    Args:
        G_full: Full network graph
        G_untrusted: Untrusted sources network graph
    """
    print("\n" + "=" * 70)
    print("COMPARATIVE ANALYSIS")
    print("=" * 70)

    if G_full.number_of_nodes() == 0 or G_untrusted.number_of_nodes() == 0:
        print("Cannot compare networks - one or both are empty.")
        return

    # Compare basic metrics
    print("\n--- Network Size Comparison ---")
    print(
        f"  Full Network: {G_full.number_of_nodes()} nodes, {G_full.number_of_edges()} edges"
    )
    print(
        f"  Untrusted Sources Network: {G_untrusted.number_of_nodes()} nodes, {G_untrusted.number_of_edges()} edges"
    )
    print(
        f"  Percentage of nodes in untrusted network: {(G_untrusted.number_of_nodes() / G_full.number_of_nodes()) * 100:.2f}%"
    )
    print(
        f"  Percentage of edges in untrusted network: {(G_untrusted.number_of_edges() / G_full.number_of_edges()) * 100:.2f}%"
    )

    # Compare engagement
    full_engagement = sum(nx.get_node_attributes(G_full, "engagement_weight").values())
    untrusted_engagement = sum(
        nx.get_node_attributes(G_untrusted, "engagement_weight").values()
    )

    print("\n--- Engagement Comparison ---")
    print(f"  Total engagement in full network: {full_engagement}")
    print(f"  Total engagement in untrusted sources: {untrusted_engagement}")
    print(
        f"  Percentage of engagement on untrusted sources: {(untrusted_engagement / full_engagement) * 100:.2f}%"
    )

    # Compare cascade characteristics
    full_stats = analyze_cascade_stats(G_full)
    untrusted_stats = analyze_cascade_stats(G_untrusted)

    print("\n--- Cascade Comparison ---")
    print(f"  Avg cascade size (full): {full_stats['avg_cascade_size']:.2f}")
    print(f"  Avg cascade size (untrusted): {untrusted_stats['avg_cascade_size']:.2f}")
    print(f"  Max cascade size (full): {full_stats['max_cascade_size']}")
    print(f"  Max cascade size (untrusted): {untrusted_stats['max_cascade_size']}")


def main():
    """Main analysis function."""
    print("\n" + "=" * 70)
    print("TWITTER NETWORK ANALYSIS: Retweets, Replies & Untrusted Sources")
    print("=" * 70)

    # Configuration
    tweets_file = "data/tweet_ids--2021-03-01.csv"
    untrusted_sources_file = "data/untrusted_sources.csv"

    # Check if files exist
    if not os.path.exists(tweets_file):
        print(f"\nError: Tweet data file not found at {tweets_file}")
        print("Please place your CSV file in the data/ directory.")
        return

    if not os.path.exists(untrusted_sources_file):
        print(
            f"\nWarning: Untrusted sources file not found at {untrusted_sources_file}"
        )
        print("Will only perform full network analysis.")
        untrusted_sources_file = None

    # Load the tweet data
    print(f"\nLoading data from {tweets_file}...")
    df = load_csv_data(tweets_file)

    print("\nDataset info:")
    print(f"  Total tweets: {len(df)}")
    print(f"  Columns: {', '.join(df.columns.tolist())}")

    # PART 1: Analyze full retweet and reply network
    G_full = analyze_full_network(df, show_plot=False)

    # PART 2: Analyze untrusted sources network (if file exists)
    G_untrusted = None
    if untrusted_sources_file:
        G_untrusted = analyze_untrusted_sources_network(
            df, untrusted_sources_file, show_plot=False
        )

        # PART 3: Compare networks
        compare_networks(G_full, G_untrusted)

    # PART 4: Export networks for visualization in Gephi/Cytoscape
    print("\n" + "=" * 70)
    print("EXPORTING NETWORKS FOR VISUALIZATION")
    print("=" * 70)

    print("\nExporting full network...")
    quick_export(G_full, "full_network", "output")

    if G_untrusted and G_untrusted.number_of_nodes() > 0:
        print("\nExporting untrusted sources network...")
        quick_export(G_untrusted, "untrusted_sources_network", "output")

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    print("\nVisualization files saved in 'output/' directory:")
    print("  - Use .gexf files with Gephi (https://gephi.org/)")
    print("  - Use .graphml files with Cytoscape (https://cytoscape.org/)")
    print("  - See _stats.txt for detailed statistics")
    print("  - See _nodes.csv for node-level data")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
