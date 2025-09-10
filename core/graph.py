from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple, Callable, Any, Union
import pandas as pd

Edge = Tuple[int, float, float]  # (v, dist_km, time_min)
Adjacency = Dict[int, List[Edge]]  # {"node id": edges}
Node = Dict[str, Any]  # Each node's data = {"name": str, "lat": float, "lon": float, ...}
Nodes = Dict[int, Node]  # {"node id": node data} <- Map city to city's data

WEIGHT_INDEX = {
    "distance_km": 1,
    "travel_time_min": 2,
}

CITY_COLS = {"id", "name_en", "latitude", "longitude"}
EDGE_COLS = {"source_id", "target_id", "distance_km", "travel_time_min"}


# ----------------------------- API ----------------------------- #
def load_graph(
    *,
    undirected: bool = True,
    drop_self_targets: bool = True,
    keep_best_edge: bool = True,
) -> Tuple[Nodes, Adjacency]:

    cities_df = pd.read_csv("data/cities.csv")
    edges_df = pd.read_csv("data/edges.csv")

    cities_df["id"] = cities_df["id"].astype(int)
    edges_df["source_id"] = edges_df["source_id"].astype(int)
    edges_df["target_id"] = edges_df["target_id"].astype(int)
    edges_df["distance_km"] = edges_df["distance_km"].astype(float)
    edges_df["travel_time_min"] = edges_df["travel_time_min"].astype(float)

    # Cities as nodes
    nodes: Nodes = {
        int(row.id): {
            "name": str(row.name_en),
            "lat": float(row.latitude),
            "lon": float(row.longitude),
        }
        for _, row in cities_df.iterrows()
    }
    existing_ids = set(nodes.keys())
    edges_df = edges_df[edges_df["source_id"].isin(existing_ids) & edges_df["target_id"].isin(existing_ids)].copy()
    if drop_self_targets:
        edges_df = edges_df[edges_df["source_id"] != edges_df["target_id"]]
    
    #if have more than one edge between two nodes, keep the one with the smallest distance_km, then travel_time_min
    if keep_best_edge:
        edges_df.sort_values(["source_id", "target_id", "distance_km", "travel_time_min"], inplace=True)
        edges_df = edges_df.drop_duplicates(subset=["source_id", "target_id"], keep="first")


    # Edges(Roads) as adjacency list
    adj: Adjacency = defaultdict(list)

    def add_edge(u: int, v: int, d: float, t: float):
        adj[u].append((v, d, t))
    
    for _, row in edges_df.iterrows():
        u = int(row.source_id)
        v = int(row.target_id)
        d = float(row.distance_km)
        t = float(row.travel_time_min)
        add_edge(u, v, d, t)
        if undirected:
            add_edge(v, u, d, t)

    return nodes, adj

# -------------------------- Get City ID from City name ------------------------- #
def get_city_id(input: Union[int, str], nodes: Nodes) -> int:
    if isinstance(input, int):
        if input in nodes:
            return input
        raise KeyError(f"City id {input} not found.")
    elif isinstance(input, str):
        for node_id, data in nodes.items():
            if data["name"] == input:
                return node_id
        raise KeyError(f"City name '{input}' not found.")
    raise TypeError("Input Error.")

# ----------------------------- Get the Edge's Weight ----------------------------- #
def get_weight(key: str = "distance_km") -> Callable[[Edge], float]:
    if key not in WEIGHT_INDEX:
        valid = ", ".join(WEIGHT_INDEX.keys())
        raise ValueError(f'Invalid weight. Choose one of: {valid}')
    idx = WEIGHT_INDEX[key]

    def getter(edge: Edge) -> float:
        return edge[idx]
    return getter

# ----------------------------- Get List of Cities ----------------------------- #
def city_list(nodes: Nodes) -> List[Tuple[int, str]]:
    return sorted(((node_id, data["name"]) for node_id, data in nodes.items()), key=lambda x: x[1].lower())

# ----------------------------- Get City Names ----------------------------- #
def city_names(node_id: int, nodes: Nodes) -> str:
    data = nodes.get(node_id)
    if not data:
        return f"<unknown:{node_id}>"
    return f'{data["name"]} ({node_id})'







