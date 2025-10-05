"""
Example Network Analysis Script

This script demonstrates how to use the network_utils module to load
data from CSV and perform basic network analysis.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from network_utils import (
    load_csv_data,
    create_graph_from_edges,
    print_graph_stats
)


def main():
    """Main analysis function."""
    print("Twitter Network Analysis")
    print("=" * 50)
    
    # Example: Load CSV data
    # Replace 'data/your_data.csv' with your actual data file
    csv_file = 'data/sample_edges.csv'
    
    if not os.path.exists(csv_file):
        print(f"\nWarning: Sample data file not found at {csv_file}")
        print("Please place your CSV file in the data/ directory.")
        print("\nExpected CSV format:")
        print("  - For edge list: columns like 'source', 'target' (and optionally 'weight')")
        print("  - Adjust column names in the script as needed")
        return
    
    # Load the data
    print(f"\nLoading data from {csv_file}...")
    df = load_csv_data(csv_file)
    
    # Display first few rows
    print("\nFirst few rows of data:")
    print(df.head())
    
    # Create a graph from the data
    # Adjust column names based on your CSV structure
    print("\nCreating network graph...")
    G = create_graph_from_edges(
        df,
        source_col='source',  # Change to match your CSV column name
        target_col='target',  # Change to match your CSV column name
        directed=True,        # Set to False for undirected graph
        weight_col=None       # Set to column name if you have weights
    )
    
    # Print basic statistics
    print_graph_stats(G)
    
    # TODO: Add your analysis code here
    # Examples:
    # - Degree centrality: nx.degree_centrality(G)
    # - Betweenness centrality: nx.betweenness_centrality(G)
    # - Community detection: nx.community.greedy_modularity_communities(G)
    # - Visualization: nx.draw(G)
    
    print("Analysis complete!")


if __name__ == "__main__":
    main()
