# twitter-network-analysis
Social network analysis performed on a dataset of tweets from one day during Covid. Part of the Social Network Analysis course.

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
│   └── sample_edges.csv    # Sample data (replace with your own)
├── analysis.py             # Main analysis script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Usage

### Preparing Your Data

Place your CSV data file in the `data/` directory. The CSV should contain edge information with at least two columns:
- A source node column (e.g., 'source', 'from', 'user')
- A target node column (e.g., 'target', 'to', 'mentioned_user')
- Optionally, a weight column for weighted graphs

Example CSV format:
```csv
source,target
user1,user2
user1,user3
user2,user3
```

### Running the Analysis

1. Update `analysis.py` to point to your CSV file and specify the correct column names
2. Run the analysis:
```bash
python analysis.py
```

### Using the Helper Functions

The `src/network_utils.py` module provides several helper functions:

- `load_csv_data(filepath)`: Load data from a CSV file
- `create_graph_from_edges(df, source_col, target_col, directed, weight_col)`: Create a NetworkX graph from edge data
- `get_basic_stats(G)`: Get basic statistics about a graph
- `print_graph_stats(G)`: Print graph statistics

Example usage:
```python
from src.network_utils import load_csv_data, create_graph_from_edges, print_graph_stats

# Load data
df = load_csv_data('data/your_data.csv')

# Create graph
G = create_graph_from_edges(df, source_col='source', target_col='target', directed=True)

# Print statistics
print_graph_stats(G)

# Perform your analysis
# ...
```

## Dependencies

- NetworkX: Graph analysis library
- Pandas: Data manipulation and CSV loading
- NumPy: Numerical computations
- Matplotlib: Visualization (optional, for plotting)

See `requirements.txt` for specific versions.
