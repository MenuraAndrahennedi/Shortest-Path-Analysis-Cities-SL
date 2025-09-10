"""
Graph Data Loader for Sri Lankan Cities using OpenStreetMap

This module:
- Downloads Sri Lanka's road network from OSM using osmnx
- Converts it into an adjacency dictionary (for custom algorithms)
- Maps major cities to nearest road nodes
"""

import osmnx as ox

# ---------------------------
# Cities (lat, lon)
# ---------------------------
CITIES = {
    "Colombo": (6.9271, 79.8612),
    "Kandy": (7.2906, 80.6337),
    "Galle": (6.0535, 80.2210),
    "Jaffna": (9.6615, 80.0255),
    "Negombo": (7.2039, 79.8380),
    "Batticaloa": (7.7100, 81.6926),
    "Trincomalee": (8.5878, 81.2152),
    "Anuradhapura": (8.3114, 80.4037),
    "Polonnaruwa": (7.9406, 81.0000),
    "Matara": (5.9480, 80.5350),
    "Nuwara Eliya": (6.9497, 80.7895),
    "Kurunegala": (7.4865, 80.3644),
}

# ---------------------------
# Download OSM graph
# ---------------------------
def load_osm_graph():
    """
    Download Sri Lanka road network and return as osmnx graph.
    """
    print("Downloading Sri Lanka road network from OpenStreetMap...")
    G = ox.graph_from_place("Sri Lanka", network_type="drive")
    G = ox.utils_graph.get_undirected(G)  # make it undirected for algorithms
    return G

# ---------------------------
# Convert to adjacency dict
# ---------------------------
def convert_osm_to_adj(G):
    """
    Convert osmnx MultiDiGraph to adjacency dictionary.
    Returns: dict[node][neighbor] = distance (meters)
    """
    adj = {}
    for u, v, data in G.edges(data=True):
        w = data.get("length", 1.0)  # edge length in meters
        adj.setdefault(u, {})[v] = w
        adj.setdefault(v, {})[u] = w
    return adj

# ---------------------------
# Map cities to nearest road nodes
# ---------------------------
def map_cities_to_nodes(G, cities=CITIES):
    """
    Map each city to its nearest graph node.
    Returns: dict[city_name] = node_id
    """
    return {
        name: ox.distance.nearest_nodes(G, coord[1], coord[0])  # lon, lat order
        for name, coord in cities.items()
    }

# ---------------------------
# Exported function for other scripts
# ---------------------------
def get_graph_data():
    """
    Main entry point for algorithms.
    Returns:
      - adj: adjacency dict
      - city_nodes: {city: node_id}
    """
    G = load_osm_graph()
    adj = convert_osm_to_adj(G)
    city_nodes = map_cities_to_nodes(G)
    return adj, city_nodes

# Test run
if __name__ == "__main__":
    adj, city_nodes = get_graph_data()
    print("Cities mapped to nodes:")
    for city, node in city_nodes.items():
        print(f"{city} → {node}")
    print(f"Graph has {len(adj)} nodes")
