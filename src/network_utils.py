"""
Network Analysis Helper Functions

This module provides helper functions for loading and preprocessing data
from CSV files for network analysis using NetworkX.
"""

import pandas as pd
import networkx as nx
from typing import Optional, List, Tuple


def load_csv_data(filepath: str, encoding: str = 'utf-8') -> pd.DataFrame:
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


def create_graph_from_edges(
    df: pd.DataFrame,
    source_col: str,
    target_col: str,
    directed: bool = True,
    weight_col: Optional[str] = None
) -> nx.Graph:
    """
    Create a NetworkX graph from edge data in a DataFrame.
    
    Args:
        df: DataFrame containing edge data
        source_col: Name of the column containing source nodes
        target_col: Name of the column containing target nodes
        directed: Whether to create a directed graph (default: True)
        weight_col: Optional name of column containing edge weights
    
    Returns:
        NetworkX Graph (DiGraph if directed=True, Graph otherwise)
    
    Raises:
        KeyError: If specified columns don't exist in DataFrame
    """
    # Validate columns exist
    required_cols = [source_col, target_col]
    if weight_col:
        required_cols.append(weight_col)
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing columns in DataFrame: {missing_cols}")
    
    # Create appropriate graph type
    G = nx.DiGraph() if directed else nx.Graph()
    
    # Add edges
    if weight_col:
        edges = [(row[source_col], row[target_col], row[weight_col]) 
                 for _, row in df.iterrows()]
        G.add_weighted_edges_from(edges)
    else:
        edges = [(row[source_col], row[target_col]) 
                 for _, row in df.iterrows()]
        G.add_edges_from(edges)
    
    print(f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    return G


def get_basic_stats(G: nx.Graph) -> dict:
    """
    Get basic statistics about a graph.
    
    Args:
        G: NetworkX graph
    
    Returns:
        Dictionary containing basic graph statistics
    """
    stats = {
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges(),
        'is_directed': G.is_directed(),
        'density': nx.density(G),
    }
    
    # Add connectivity info for appropriate graph types
    if G.is_directed():
        stats['is_strongly_connected'] = nx.is_strongly_connected(G)
        stats['is_weakly_connected'] = nx.is_weakly_connected(G)
        if nx.is_weakly_connected(G):
            stats['num_strongly_connected_components'] = nx.number_strongly_connected_components(G)
    else:
        stats['is_connected'] = nx.is_connected(G)
        if not nx.is_connected(G):
            stats['num_connected_components'] = nx.number_connected_components(G)
    
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
