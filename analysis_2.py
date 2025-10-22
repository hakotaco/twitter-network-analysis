import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from networkx.algorithms.community import louvain_communities
import networkx as nx

def print_cliques_summary(G):
    """
    Analyzes and prints a summary of cliques in the given graph G.
    Generates bar plots of clique counts by size.
    """

    max_size = 40
    max_examples_per_size = 3
    max_cliques_to_scan = 1000000

    # convert to undirected graph
    G_undirected = G.to_undirected()

    # initialize counters and storage for examples
    counts = Counter()
    examples = {s: [] for s in range(1, max_size + 1)}
    clique_iter = nx.find_cliques(G_undirected)
    scanned = 0

    # scan cliques
    for clique in clique_iter:
        scanned += 1
        if scanned > max_cliques_to_scan:
            print("  Reached maximum number of cliques to scan:", max_cliques_to_scan)
            break
        s = len(clique)
        if s <= max_size:
            counts[s] += 1
            if len(examples[s]) < max_examples_per_size:
                examples[s].append(clique)

    # print summary
    print("  Clique counts (size: count) up to size", max_size)
    for s in sorted(counts.keys()):
        print(f"    Size {s}: {counts[s]} cliques")
    if not counts:
        print("  No cliques found up to requested size or graph too large to enumerate.")
        return

    # generate plots
    sizes = sorted(counts.keys())
    values = [counts[s] for s in sizes]

    x, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.bar(sizes, values, color='C0', edgecolor='k', alpha = 0.8)
    ax1.set_xlabel('Clique size (k)')
    ax1.set_ylabel('Number of cliques')
    ax1.set_title('Clique counts by size')

    ax2.bar(sizes, values, color='C1', edgecolor='k', alpha = 0.8)
    ax2.set_yscale('log')
    ax2.set_xlabel('Clique size (k)')
    ax2.set_ylabel('Number of cliques (log scale)')
    ax2.set_title('Clique counts by size (log)')

    xticks = sizes if len(sizes) <= 40 else np.linspace(min(sizes), max(sizes), 20, dtype=int)
    ax1.set_xticks(xticks)
    ax2.set_xticks(xticks)

    plt.tight_layout()
    plt.show()


def detect_communities_and_bridges(G, top_k = 20):
    """
    detects communities in the undirected graph G using the Louvain method, identifies bridge nodes connecting different communities,
    and ranks them by betweenness centrality.
    """
    # convert to undirected graph
    G_undirected = G.to_undirected()
    
    # Louvian algorithm
    print("Running Louvain community detection...")
    communities = louvain_communities(G_undirected, seed=42)
    print(f"Detected {len(communities)} communities.")

    # map nodes to their communities
    node_to_comm = {}
    for i, comm in enumerate(communities):
        for node in comm:
            node_to_comm[node] = i

    # bridge nodes identification
    bridge_nodes = set()
    for u, v in G_undirected.edges():
        if node_to_comm.get(u) != node_to_comm.get(v):
            bridge_nodes.add(u)
            bridge_nodes.add(v)

    print(f"Identified {len(bridge_nodes)} bridge nodes connecting different communities.")

    # rank bridge nodes by betweenness centrality
    print("Computing betweenness centrality for bridge nodes...")
    bc = nx.betweenness_centrality(G_undirected, normalized = True)
    top_bridges = sorted([(n, bc[n]) for n in bridge_nodes], key = lambda x: x[1], reverse = True)[:top_k]

    print(f"\nTop {top_k} bridge nodes by betweenness centrality:")
    for node, score in top_bridges:
        print(f"  Node {node}: {score:.5f}")

    return bridge_nodes, top_bridges, communities


def compute_pagerank(G, top_k=20):
    """
    computes PageRank for the directed graph G and prints the top_k nodes by PageRank score.
    """
    DG = G.to_directed()  
    pagerank = nx.pagerank(DG, alpha=0.85)  

    top_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:top_k]
    print(f"\nTop {top_k} nodes by PageRank:")
    for node, score in top_pr:
        print(f"  Node {node}: {score:.5f}")

    return top_pr


def main():
    G_full = nx.read_graphml("output/full_network.graphml")
    G_untrusted = nx.read_graphml("output/untrusted_sources_network.graphml")

    print("Analyzing full network for cliques:")
    print_cliques_summary(G_full)

    print("\nAnalyzing untrusted sources network for cliques:")
    print_cliques_summary(G_untrusted)

    print("\n" + "=" * 70)
    print("TWITTER UNTRUSTED NETWORK: Communities and Bridges")
    print("=" * 70)

    detect_communities_and_bridges(G_untrusted)

    print("\n" + "=" * 70)
    print("TWITTER FULL NETWORK: PageRank")
    print("=" * 70)

    compute_pagerank(G_full)

    print("\n" + "=" * 70)
    print("TWITTER UNTRUSTED NETWORK: PageRank")
    print("=" * 70)

    compute_pagerank(G_untrusted)
    

    
    print("hello world")

if __name__ == "__main__":
    main()