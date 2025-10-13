"""
Network Analysis Helper Functions

This module provides helper functions for loading and preprocessing data
from CSV files for network analysis using NetworkX.
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def load_csv_data(filepath: str, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Load data from a CSV file.

    Args:
        filepath: Path to the CSV file
        encoding: Encoding of the CSV file (default: 'utf-8')

    Returns:
        DataFrame containing the CSV data

    Raises:
        FileNotFoundError: If the file doesn't exist
        pd.errors.EmptyDataError: If the file is empty
    """
    try:
        df = pd.read_csv(filepath, encoding=encoding)
        print(f"Successfully loaded {len(df)} rows from {filepath}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError(f"CSV file is empty: {filepath}")


def get_basic_stats(G: nx.Graph) -> dict:
    """
    Get basic statistics about a graph.

    Args:
        G: NetworkX graph

    Returns:
        Dictionary containing basic graph statistics
    """
    stats = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "is_directed": G.is_directed(),
        "density": nx.density(G),
    }

    # Add connectivity info for appropriate graph types
    if G.is_directed():
        stats["is_strongly_connected"] = nx.is_strongly_connected(G)
        stats["is_weakly_connected"] = nx.is_weakly_connected(G)
        if nx.is_weakly_connected(G):
            stats["num_strongly_connected_components"] = (
                nx.number_strongly_connected_components(G)
            )
    else:
        stats["is_connected"] = nx.is_connected(G)
        if not nx.is_connected(G):
            stats["num_connected_components"] = nx.number_connected_components(G)

    return stats


def print_graph_stats(G: nx.Graph) -> None:
    """
    Print basic statistics about a graph.

    Args:
        G: NetworkX graph
    """
    stats = get_basic_stats(G)
    print("\n=== Graph Statistics ===")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("========================\n")


def create_engagement_cascade_graph(
    df: pd.DataFrame,
    author_col: str = "author_id",
    tweet_id_col: str = "tweet_id",
    reference_type_col: str = "reference_type",
    reference_id_col: str = "reference_id",
    like_col: str = "like_count",
    retweet_col: str = "retweet_count",
    show_plot: bool = True,
) -> nx.DiGraph:
    """
    Build a comprehensive retweet and reply cascade graph with weighted nodes.

    Creates a directed graph where:
    - Edges represent retweets or replies (from retweeter/replier to original author)
    - Node weights are the sum of likes and retweets for each tweet
    - Multiple cascades can exist in one graph
    - Each cascade traces back to its parent/root tweet

    Args:
        df: Pandas DataFrame containing tweet metadata
        author_col: Column for tweet author ID
        tweet_id_col: Column for tweet ID
        reference_type_col: Column indicating type of reference ('retweeted' or 'replied_to')
        reference_id_col: Column for the original tweet ID being referenced
        like_col: Column for number of likes
        retweet_col: Column for number of retweets
        show_plot: Whether to show matplotlib visualization

    Returns:
        nx.DiGraph: Directed graph with weighted nodes representing engagement cascades
    """
    # Create a mapping of tweet_id to author_id and engagement metrics
    # AND build node weights for ALL authors
    tweet_info = {}
    node_weights = {}  # Store engagement weights for ALL nodes

    for _, row in df.iterrows():
        tweet_id = row[tweet_id_col]
        author = row[author_col]

        if (
            pd.notna(tweet_id)
            and tweet_id != "#"
            and pd.notna(author)
            and author != "#"
        ):
            likes = row[like_col] if pd.notna(row[like_col]) else 0
            retweets = row[retweet_col] if pd.notna(row[retweet_col]) else 0
            engagement = likes + retweets

            tweet_info[tweet_id] = {
                "author": author,
                "engagement": engagement,
                "likes": likes,
                "retweets": retweets,
            }

            # Add to node weights (every author becomes a node)
            node_weights[author] = node_weights.get(author, 0) + engagement

    print(f"Loaded {len(tweet_info)} tweets from {len(node_weights)} unique authors")

    # Filter rows where reference_type is 'retweeted' or 'replied_to'
    cascade_mask = (
        (df[reference_type_col].isin(["retweeted", "replied_to"]))
        & (df[author_col].notna())
        & (df[author_col] != "#")
        & (df[reference_id_col].notna())
        & (df[reference_id_col] != "#")
    )
    cascade_df = df[cascade_mask]

    if cascade_df.empty:
        print("No retweet or reply relationships found in DataFrame.")
        print(
            f"Creating graph with {len(node_weights)} isolated nodes (original tweets only)."
        )
        G = nx.DiGraph()
        G.add_nodes_from(node_weights.keys())
        nx.set_node_attributes(G, node_weights, "engagement_weight")
        return G

    # Create edges: current author → original author (direction shows flow of influence)
    edges = []
    edge_types = {}  # Store what type of edge it is (retweet vs reply)
    found_in_dataset = 0
    not_in_dataset = 0

    # Check what columns are available for finding original authors
    has_retweet_author = "retweet_author_id" in df.columns
    has_reply_user = "in_reply_to_user_id" in df.columns

    # Create edges where we can determine both authors
    for _, row in cascade_df.iterrows():
        current_author = row[author_col]
        original_tweet_id = row[reference_id_col]
        reference_type = row[reference_type_col]
        original_author = None

        # Method 1: Look up the original author from tweet_info (if tweet is in dataset)
        if original_tweet_id in tweet_info:
            original_author = tweet_info[original_tweet_id]["author"]
            found_in_dataset += 1
        # Method 2: Check for direct author ID columns (retweet_author_id, in_reply_to_user_id)
        elif reference_type == "retweeted" and has_retweet_author:
            original_author = row.get("retweet_author_id")
            if pd.notna(original_author) and original_author != "#":
                not_in_dataset += 1
                # Add this author to node_weights if not already present
                if original_author not in node_weights:
                    node_weights[original_author] = (
                        0  # No engagement data for external tweets
                    )
        elif reference_type == "replied_to" and has_reply_user:
            original_author = row.get("in_reply_to_user_id")
            if pd.notna(original_author) and original_author != "#":
                not_in_dataset += 1
                # Add this author to node_weights if not already present
                if original_author not in node_weights:
                    node_weights[original_author] = (
                        0  # No engagement data for external tweets
                    )

        # Create edge if we found the original author
        if original_author and original_author != "#":
            edges.append((current_author, original_author))
            edge_types[(current_author, original_author)] = reference_type

    print("Edge creation summary:")
    print(f"  References to tweets in dataset: {found_in_dataset}")
    print(f"  References to external tweets: {not_in_dataset}")
    print(f"  Total edges created: {len(edges)}")

    if len(edges) == 0:
        print("\nNote: No edges could be created because:")
        print("  - Referenced tweets are not in this dataset (likely from other days)")
        if not has_retweet_author and not has_reply_user:
            print("  - No retweet_author_id or in_reply_to_user_id columns available")
        print("  - Graph will show isolated nodes only")

    # Build directed graph
    G = nx.DiGraph()

    # Add all nodes first (ensures ALL authors exist, including isolated ones)
    G.add_nodes_from(node_weights.keys())

    # Then add edges
    G.add_edges_from(edges)

    # Add node attributes for engagement weights
    nx.set_node_attributes(G, node_weights, "engagement_weight")

    # Add edge attributes for reference type
    nx.set_edge_attributes(G, edge_types, "reference_type")

    print(
        f"Engagement cascade graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges."
    )
    print(
        f"Total cascades (weakly connected components): {nx.number_weakly_connected_components(G)}"
    )

    # Optional visualization
    if show_plot and G.number_of_edges() > 0:
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=0.5, seed=42)

        # Node sizes based on engagement weight
        node_sizes = [max(50, node_weights.get(n, 1) / 10) for n in G.nodes()]

        # Color edges by type
        edge_colors = [
            "blue" if edge_types.get(e) == "retweeted" else "green" for e in G.edges()
        ]

        nx.draw(
            G,
            pos,
            with_labels=False,
            node_size=node_sizes,
            node_color="skyblue",
            edge_color=edge_colors,
            alpha=0.6,
            arrows=True,
            arrowsize=10,
        )
        plt.title(
            "Retweet & Reply Cascade Graph\n(Blue=Retweet, Green=Reply)", fontsize=14
        )
        plt.show()

    return G


def get_cascade_roots(G: nx.DiGraph) -> list:
    """
    Find root nodes (original tweets) in a cascade graph.

    Root nodes are those with out-degree > 0 and in-degree = 0,
    meaning they were retweeted/replied to but didn't retweet/reply to anyone.

    Args:
        G: Directed graph representing tweet cascades

    Returns:
        List of node IDs that are cascade roots
    """
    roots = [
        node for node in G.nodes() if G.in_degree(node) == 0 and G.out_degree(node) > 0
    ]
    return roots


def trace_cascade_path(G: nx.DiGraph, start_node) -> list:
    """
    Trace the path from a node back to its root tweet.

    Args:
        G: Directed graph representing tweet cascades
        start_node: Node to start tracing from

    Returns:
        List of nodes in the path from start_node to root (inclusive)
    """
    path = [start_node]
    current = start_node

    # Follow edges until we reach a node with no outgoing edges (a leaf)
    # or no incoming edges (a root)
    visited = set()
    while G.out_degree(current) > 0:
        if current in visited:
            # Cycle detected, break
            break
        visited.add(current)

        # Get successors (nodes this node points to)
        successors = list(G.successors(current))
        if successors:
            current = successors[0]  # Follow first successor
            path.append(current)
        else:
            break

    return path


def analyze_cascade_stats(G: nx.DiGraph) -> dict:
    """
    Analyze cascade statistics in the graph.

    Args:
        G: Directed graph representing tweet cascades

    Returns:
        Dictionary with cascade statistics
    """
    # Get weakly connected components (each is a separate cascade)
    cascades = list(nx.weakly_connected_components(G))

    # Find roots
    roots = get_cascade_roots(G)

    # Calculate cascade sizes
    cascade_sizes = [len(c) for c in cascades]

    # Get engagement weights
    engagement_weights = nx.get_node_attributes(G, "engagement_weight")
    total_engagement = sum(engagement_weights.values())

    # Count edge types
    edge_types = nx.get_edge_attributes(G, "reference_type")
    retweet_count = sum(1 for t in edge_types.values() if t == "retweeted")
    reply_count = sum(1 for t in edge_types.values() if t == "replied_to")

    stats = {
        "num_cascades": len(cascades),
        "num_roots": len(roots),
        "avg_cascade_size": sum(cascade_sizes) / len(cascade_sizes)
        if cascade_sizes
        else 0,
        "max_cascade_size": max(cascade_sizes) if cascade_sizes else 0,
        "min_cascade_size": min(cascade_sizes) if cascade_sizes else 0,
        "total_engagement": total_engagement,
        "num_retweet_edges": retweet_count,
        "num_reply_edges": reply_count,
    }

    return stats


def load_untrusted_domains(filepath: str) -> set:
    """
    Load untrusted domain names from CSV file.

    Args:
        filepath: Path to the untrusted sources CSV file

    Returns:
        Set of untrusted domain names (lowercase)
    """
    df = pd.read_csv(filepath)
    domains = set(df["Domain"].str.lower().tolist())
    print(f"Loaded {len(domains)} untrusted domains")
    return domains


def check_tweet_contains_untrusted_source(
    urls: str, text: str, untrusted_domains: set
) -> bool:
    """
    Check if a tweet contains any untrusted source domains.

    Args:
        urls: URLs from the tweet (may be '#' or comma-separated)
        text: Tweet text content
        untrusted_domains: Set of untrusted domain names

    Returns:
        True if tweet contains untrusted source, False otherwise
    """
    if pd.isna(urls) or urls == "#":
        urls_to_check = []
    else:
        urls_to_check = [u.strip() for u in str(urls).split(",")]

    # Check URLs
    for url in urls_to_check:
        url_lower = url.lower()
        for domain in untrusted_domains:
            if domain in url_lower:
                return True

    # Check text content
    if pd.notna(text):
        text_lower = str(text).lower()
        for domain in untrusted_domains:
            if domain in text_lower:
                return True

    return False


def filter_tweets_with_untrusted_sources(
    df: pd.DataFrame,
    untrusted_domains: set,
    url_col: str = "urls",
    text_col: str = "text",
) -> pd.DataFrame:
    """
    Filter tweets that contain untrusted source domains.

    Args:
        df: DataFrame containing tweet data
        untrusted_domains: Set of untrusted domain names
        url_col: Column containing URLs
        text_col: Column containing tweet text

    Returns:
        DataFrame containing only tweets with untrusted sources
    """
    mask = df.apply(
        lambda row: check_tweet_contains_untrusted_source(
            row[url_col], row[text_col], untrusted_domains
        ),
        axis=1,
    )

    filtered_df = df[mask]
    print(
        f"Found {len(filtered_df)} tweets containing untrusted sources out of {len(df)} total tweets"
    )

    return filtered_df


def export_graph(G: nx.Graph, base_filename: str, formats: list = None) -> list:
    """
    Export a NetworkX graph to multiple file formats for visualization.

    Recommended for large networks instead of matplotlib plotting.

    Args:
        G: NetworkX graph to export
        base_filename: Base filename without extension (e.g., 'network')
        formats: List of formats to export. Options: 'gexf', 'graphml', 'gml', 'edgelist', 'pajek'
                Default: ['gexf', 'graphml'] (best for Gephi and Cytoscape)

    Returns:
        List of created filenames

    Example:
        files = export_graph(G, 'output/my_network', formats=['gexf', 'edgelist'])
    """
    import os

    if formats is None:
        formats = ["gexf", "graphml"]  # Most compatible formats

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(base_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    created_files = []

    for fmt in formats:
        filename = f"{base_filename}.{fmt}"

        try:
            if fmt == "gexf":
                # GEXF - Best for Gephi
                nx.write_gexf(G, filename)
            elif fmt == "graphml":
                # GraphML - Good for Cytoscape, yEd
                nx.write_graphml(G, filename)
            elif fmt == "gml":
                # GML - General purpose
                nx.write_gml(G, filename)
            elif fmt == "edgelist":
                # Simple edge list (CSV-like)
                nx.write_edgelist(G, filename, data=True)
            elif fmt == "pajek":
                # Pajek format
                nx.write_pajek(G, filename)
            else:
                print(f"Warning: Unknown format '{fmt}', skipping")
                continue

            file_size = os.path.getsize(filename) / (1024 * 1024)  # Size in MB
            print(f"  ✓ Saved {fmt.upper()}: {filename} ({file_size:.2f} MB)")
            created_files.append(filename)

        except Exception as e:
            print(f"  ✗ Error saving {fmt.upper()}: {e}")

    return created_files


def export_network_summary(G: nx.Graph, filename: str) -> None:
    """
    Export a text summary of network statistics to a file.

    Args:
        G: NetworkX graph
        filename: Output filename (e.g., 'network_stats.txt')
    """
    stats = get_basic_stats(G)

    with open(filename, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("NETWORK STATISTICS SUMMARY\n")
        f.write("=" * 60 + "\n\n")

        for key, value in stats.items():
            f.write(f"{key.replace('_', ' ').title()}: {value}\n")

        # Add cascade stats if it's a cascade graph
        if G.is_directed():
            f.write("\n--- Cascade Analysis ---\n")
            cascade_stats = analyze_cascade_stats(G)
            for key, value in cascade_stats.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")

        # Top nodes by degree
        f.write("\n--- Top 10 Nodes by Degree ---\n")
        degrees = dict(G.degree())
        top_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (node, degree) in enumerate(top_degrees, 1):
            f.write(f"{i:2d}. Node {node}: {degree} connections\n")

        # Top nodes by engagement (if available)
        engagement = nx.get_node_attributes(G, "engagement_weight")
        if engagement:
            f.write("\n--- Top 10 Nodes by Engagement ---\n")
            top_eng = sorted(engagement.items(), key=lambda x: x[1], reverse=True)[:10]
            for i, (node, weight) in enumerate(top_eng, 1):
                f.write(f"{i:2d}. Node {node}: {weight:,} engagement\n")

    print(f"  ✓ Network summary saved to: {filename}")


def export_node_data(G: nx.Graph, filename: str) -> None:
    """
    Export node data with all attributes to CSV for further analysis.

    Args:
        G: NetworkX graph
        filename: Output CSV filename (e.g., 'nodes.csv')
    """
    import csv

    # Get all node attributes
    node_attrs = {}
    for attr_name in ["engagement_weight"]:  # Add more attribute names as needed
        attrs = nx.get_node_attributes(G, attr_name)
        if attrs:
            node_attrs[attr_name] = attrs

    # Calculate degree metrics
    if G.is_directed():
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())
    else:
        degrees = dict(G.degree())

    # Write to CSV
    with open(filename, "w", newline="") as f:
        if G.is_directed():
            fieldnames = ["node_id", "in_degree", "out_degree", "total_degree"]
        else:
            fieldnames = ["node_id", "degree"]

        # Add attribute columns
        for attr_name in node_attrs:
            fieldnames.append(attr_name)

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for node in G.nodes():
            row = {"node_id": node}

            if G.is_directed():
                row["in_degree"] = in_degrees.get(node, 0)
                row["out_degree"] = out_degrees.get(node, 0)
                row["total_degree"] = row["in_degree"] + row["out_degree"]
            else:
                row["degree"] = degrees.get(node, 0)

            # Add attributes
            for attr_name, attr_dict in node_attrs.items():
                row[attr_name] = attr_dict.get(node, 0)

            writer.writerow(row)

    print(f"  ✓ Node data exported to: {filename} ({len(G.nodes())} nodes)")


def quick_export(
    G: nx.Graph, name: str = "network", output_dir: str = "output"
) -> None:
    """
    Quick export function that saves graph in multiple formats plus summaries.

    Args:
        G: NetworkX graph
        name: Base name for files
        output_dir: Directory to save files (will be created if doesn't exist)

    Example:
        quick_export(G, 'full_network')
        # Creates: output/full_network.gexf, output/full_network.graphml, etc.
    """
    import os

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_path = os.path.join(output_dir, name)

    print(f"\nExporting {name}...")

    # Export graph files
    export_graph(G, base_path, formats=["gexf", "graphml"])

    # Export statistics
    export_network_summary(G, f"{base_path}_stats.txt")

    # Export node data
    export_node_data(G, f"{base_path}_nodes.csv")

    print(f"\n✓ All files saved to {output_dir}/ directory")
