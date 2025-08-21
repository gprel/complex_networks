import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter
from itertools import combinations
from tqdm import tqdm

def plot_top_country_pairs(
    df: pd.DataFrame,
    list_col: str = 'countries_mentioned_list',
    top_n: int = 20,
    figsize: tuple = (10, 4)
):
    """
    Plot a bar chart of the top co-mentioned country pairs.

    Parameters
    ----------
    df : pd.DataFrame
        Your data, must include `list_col` of Python lists.
    list_col : str
        Column name containing lists of country codes.
    top_n : int
        Number of top pairs to display.
    figsize : tuple
        (width, height) of the matplotlib figure.
    """
    # count all co-mentions
    counter = Counter()
    for lst in tqdm(df[list_col].dropna(), desc="Counting co-mentions"):
        uniq = sorted(set(lst))
        for a, b in combinations(uniq, 2):
            counter[(a, b)] += 1

    # grab top_n
    top_series = pd.Series(counter).sort_values(ascending=False).head(top_n)

    # plot
    plt.figure(figsize=figsize)
    top_series.plot(kind='bar')
    plt.xlabel('Country pair')
    plt.ylabel('Number of papers mentioning both')
    plt.title(f'Top {top_n} Country Co-Mention Pairs')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def plot_country_network(
    df: pd.DataFrame,
    list_col: str = 'countries_mentioned_list',
    top_edges: int = 1000,
    figsize: tuple = (15, 6),
    layout_k: float = 0.2,
    layout_seed: int = 42
):
    """
    Plot the spring-layout network of the strongest co-mention edges.

    Parameters
    ----------
    df : pd.DataFrame
        Your data, must include `list_col` of Python lists.
    list_col : str
        Column name containing lists of country codes.
    top_edges : int
        Number of strongest edges to include in the network.
    figsize : tuple
        (width, height) of the matplotlib figure.
    layout_k : float
        Optimal node spacing in spring_layout.
    layout_seed : int
        Random seed for reproducible layout.
    """
    # count all co-mentions
    counter = Counter()
    for lst in tqdm(df[list_col].dropna(), desc="Counting co-mentions"):
        uniq = sorted(set(lst))
        for a, b in combinations(uniq, 2):
            counter[(a, b)] += 1

    # build subgraph of top_edges
    top_dict = dict(pd.Series(counter).sort_values(ascending=False).head(top_edges))
    G = nx.Graph()
    G.add_weighted_edges_from([(a, b, w) for (a, b), w in top_dict.items()])

    # layout & widths
    pos = nx.spring_layout(G, seed=layout_seed, k=layout_k)
    max_w = max(top_dict.values()) if top_dict else 1
    widths = [w / max_w * 20 for *_, w in G.edges(data='weight')]

    # draw
    plt.figure(figsize=figsize)
    nx.draw_networkx_nodes(G, pos, node_size=300, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=widths, alpha=0.6)
    nx.draw_networkx_labels(G, pos, font_size=8)
    plt.title(f'Network of Top {top_edges} Country Co-Mentions')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def plot_pair_mentions_by_subject(
    df: pd.DataFrame,
    country_pair: tuple,
    subj_col: str = 'subjareas',
    list_col: str = 'countries_mentioned_list',
    top_n: int = None,
    figsize: tuple = (10, 5)
):
    """
    For a given pair of countries (e.g. ('usa','gbr')), plot the number of papers
    mentioning both, broken down by subject area.

    Parameters
    ----------
    df : pd.DataFrame
        Your DataFrame, must contain `list_col` (lists of country codes)
        and `subj_col` (comma-separated subjareas).
    country_pair : tuple of str
        Two country codes, e.g. ('usa','gbr').
    subj_col : str
        Column name with comma-separated subject codes.
    list_col : str
        Column name with list of country codes.
    top_n : int or None
        If set, only plot the top_n subject areas by count.
    figsize : tuple
        Size of the matplotlib figure.

    Returns
    -------
    pd.Series
        Counts per subject area (index=subject, value=count).
    """
    c1, c2 = country_pair

    # 1) Filter to rows where both countries appear
    mask = df[list_col].apply(lambda lst: isinstance(lst, (list,tuple)) and c1 in lst and c2 in lst)
    df_pair = df[mask]

    # 2) Count subject-area occurrences
    counter = Counter()
    for entry in df_pair[subj_col].dropna():
        for subj in entry.split(','):
            subj = subj.strip()
            if subj:
                counter[subj] += 1

    if not counter:
        print(f"No records found mentioning both {c1} and {c2}.")
        return pd.Series(dtype=int)

    # 3) Turn into Series and sort
    subj_series = pd.Series(counter).sort_values(ascending=False)
    if top_n:
        subj_series = subj_series.head(top_n)

    # 4) Plot
    plt.figure(figsize=figsize)
    subj_series.plot(kind='bar')
    plt.xlabel('Subject Area')
    plt.ylabel('Number of papers mentioning both')
    plt.title(f"Papers mentioning both {c1.upper()} & {c2.upper()} by Subject")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    return subj_series
