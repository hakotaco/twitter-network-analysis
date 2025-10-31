# twitter-network-analysis
Social network analysis of Twitter retweet and reply cascades during Covid. Includes analysis of misinformation spread from untrusted news sources.

## Features

- **Engagement Cascade Graphs**: Build directed networks of retweets and replies with node weights based on likes + retweets
- **Cascade Tracing**: Trace any retweet/reply back to its original parent tweet
- **Multiple Cluster Analysis**: Handle multiple independent cascades in a single graph
- **Untrusted Source Detection**: Filter and analyze tweets containing domains from untrusted news sources
- **Comprehensive Statistics**: Analyze network properties, engagement patterns, and information spread

## Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/hakotaco/twitter-network-analysis.git
cd twitter-network-analysis
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
twitter-network-analysis/
├── src/
│   └── network_utils.py    # Helper functions for network analysis
├── data/
│   ├── tweet_ids--2021-03-01.csv    # Tweet data
│   └── untrusted_sources.csv       # Untrusted domain list
├── analysis.py             # Main analysis script
├── analysis_2.py           # Second part of the analysis
├── example_usage.py        # Usage examples
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Quick Start

### 1. Run Full Analysis

```bash
python analysis.py
```

This will:
- Create a network of ALL retweets and replies
- Weight nodes by engagement (likes + retweets)
- Filter tweets containing untrusted sources
- Create a separate network for untrusted source tweets
- Compare both networks
- **Export networks to `output/` directory for visualization**

Output files:
- `output/full_network.gexf` - Full network (for Gephi)
- `output/full_network.graphml` - Full network (for Cytoscape)
- `output/full_network_stats.txt` - Network statistics
- `output/full_network_nodes.csv` - Node-level data
- `output/untrusted_sources_network.*` - Untrusted sources network

```bash
python analysis_2.py
```
Run this script only after running analysis.py first.
This will:
- Analyze both networks for cliques
- Apply the PageRank algorithm on both networks
- Apply Louvian community detection on the graphs, identify bridge nodes, and computes clustering coefficients after community detection.

### 2. Visualize Networks

**For large networks (>1000 nodes):** Use exported files with specialized tools
```bash
# Open .gexf files in Gephi: https://gephi.org/
# Open .graphml files in Cytoscape: https://cytoscape.org/
```

## Data Format

### Tweet CSV Format

Your tweet CSV should include these columns:
- `tweet_id`: Unique tweet identifier
- `author_id`: User who posted the tweet
- `reference_type`: Type of reference ('retweeted' or 'replied_to')
- `reference_id`: ID of the original tweet being referenced
- `like_count`: Number of likes
- `retweet_count`: Number of retweets
- `text`: Tweet text content
- `urls`: URLs in the tweet

Example:
```csv
id,tweet_id,author_id,like_count,retweet_count,reference_type,reference_id,text,urls,...
0,1366176845561962503,14914686,4,0,replied_to,1366173564957843458,"@user text...",#,...
```

### Untrusted Sources CSV Format

- `Domain`: Domain name of untrusted source (e.g., '100percentfedup.com')
- Additional metadata columns (optional)

## Key Functions

### `create_engagement_cascade_graph()`
Creates a directed graph where:
- **Edges**: Represent retweets or replies (from current user → original author)
- **Node Weights**: Sum of likes and retweets for each user's tweets
- **Multiple Cascades**: Each weakly connected component is a separate cascade

### `analyze_cascade_stats()`
Returns statistics including:
- Number of cascades
- Average/max/min cascade size
- Total engagement
- Retweet vs reply edge counts

### `filter_tweets_with_untrusted_sources()`
Filters tweets that contain untrusted source domains in:
- Tweet URLs
- Tweet text content

### `get_cascade_roots()`
Identifies original tweets that started cascades (nodes with in-degree=0, out-degree>0)

### `trace_cascade_path()`
Traces a retweet/reply chain back to its original parent tweet

## Network Structure

The networks are **directed graphs** where:
- **Direction**: Edge from A → B means "A retweeted/replied to B"
- **Node Weight**: Total engagement (likes + retweets) for that user's tweets
- **Edge Types**: Labeled as 'retweeted' or 'replied_to'
- **Cascades**: Each weakly connected component represents one cascade/conversation thread

## Example Usage

```python
from src.network_utils import (
    load_csv_data,
    create_engagement_cascade_graph,
    analyze_cascade_stats,
    filter_tweets_with_untrusted_sources,
    load_untrusted_domains
)

# Load and analyze full network
df = load_csv_data('data/tweet_ids--2021-03-01.csv')
G = create_engagement_cascade_graph(df)
stats = analyze_cascade_stats(G)

# Analyze untrusted sources
untrusted_domains = load_untrusted_domains('data/untrusted_sources.csv')
filtered_df = filter_tweets_with_untrusted_sources(df, untrusted_domains)
G_untrusted = create_engagement_cascade_graph(filtered_df)
```

## Use Cases

- Study information diffusion patterns
- Identify influential users and superspreaders
- Analyze misinformation propagation
- Compare engagement between credible and untrusted sources
- Trace viral content back to origins
- Measure cascade depth and breadth

## Dependencies

- NetworkX: Graph analysis library
- Pandas: Data manipulation and CSV loading
- Matplotlib: Visualization (optional, for plotting)

See `requirements.txt` for specific versions.
