from __future__ import annotations
from typing import Dict, List, Tuple, Callable, Any
from math import inf
import time
import heapq
from functools import lru_cache
from geographiclib.geodesic import Geodesic

Edge = Tuple[int, float, float]     # (node_id, distance_km, travel_time_min)
Adjacency = Dict[int, List[Edge]]   # node_id -> list of edges
Nodes = Dict[int, Dict[str, Any]]   # node_id -> node data

# ----------------------------- Geodesic Distance Calculation ----------------------------- #
def geodesic_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    g = Geodesic.WGS84.Inverse(float(lat1), float(lon1), float(lat2), float(lon2))
    return g["s12"] / 1000.0

# ----------------------------- Heuristics ----------------------------- #
def a_star_distance_heuristic(goal_id: int, nodes: Nodes) -> Callable[[int], float]:
    goal_lat = float(nodes[goal_id]["lat"])
    goal_lon = float(nodes[goal_id]["lon"])
    
    @lru_cache(maxsize=None)
    def h_distance(node_id: int) -> float:
        node = nodes[node_id]
        return geodesic_km(float(node["lat"]), float(node["lon"]), goal_lat, goal_lon)
    
    return h_distance

def a_star_time_heuristic(
    goal_id: int,
    nodes: Nodes,
    max_kmh: float = 70.0,
) -> Callable[[int], float]:
    if max_kmh <= 0:
        raise ValueError("max_kmh must be > 0")
    
    goal_lat = float(nodes[goal_id]["lat"])
    goal_lon = float(nodes[goal_id]["lon"])
    km_per_min = max_kmh / 60.0
    
    @lru_cache(maxsize=None)
    def h_time(node_id: int) -> float:
        node = nodes[node_id]
        distance_km = geodesic_km(float(node["lat"]), float(node["lon"]), goal_lat, goal_lon)
        return distance_km / km_per_min
    
    return h_time

# ----------------------------- Path Reconstruction ----------------------------- #
def path_reconstruct(parent: Dict[int, int], start: int, goal: int) -> List[int]:
    path: List[int] = []
    current = goal
    while current != start:
        path.append(current)
        current = parent[current]
    path.append(start)
    path.reverse()
    return path

# ----------------------------- A* Algorithm ----------------------------- #
def a_star_shortest_path(
    nodes: Nodes,
    adj: Adjacency,
    start: int,
    goal: int,
    weight_fn: Callable[[Edge], float],
    heuristic_type: str = "distance"  # "distance" or "time"
) -> Dict[str, Any]:
    
    t0 = time.perf_counter()
    
    # Choose heuristic function
    if heuristic_type == "distance":
        heuristic = a_star_distance_heuristic(goal, nodes)
    elif heuristic_type == "time":
        heuristic = a_star_time_heuristic(goal, nodes)
    else:
        raise ValueError("heuristic_type must be 'distance' or 'time'")
    
    # Initialize data structures
    g_score: Dict[int, float] = {node_id: inf for node_id in nodes.keys()}
    g_score[start] = 0.0
    
    f_score: Dict[int, float] = {node_id: inf for node_id in nodes.keys()}
    f_score[start] = heuristic(start)
    
    # Priority queue: (f_score, node_id)
    open_set = [(f_score[start], start)]
    closed_set: set[int] = set()
    parent: Dict[int, int] = {}
    
    # Statistics
    iterations = 0
    edges_scanned = 0
    nodes_expanded = 0
    
    while open_set:
        iterations += 1
        
        # Get node with lowest f_score
        current_f, current = heapq.heappop(open_set)
        
        # Skip if we've already processed this node with a better score
        if current in closed_set:
            continue
            
        # Skip if this is an outdated entry in the priority queue
        if current_f > f_score[current]:
            continue
        
        closed_set.add(current)
        nodes_expanded += 1
        
        # Goal reached
        if current == goal:
            break
        
        # Explore neighbors
        for edge in adj.get(current, []):
            edges_scanned += 1
            neighbor, _, _ = edge
            
            if neighbor in closed_set:
                continue
            
            # Calculate tentative g_score
            tentative_g = g_score[current] + weight_fn(edge)
            
            # If this path is better than any previous one
            if tentative_g < g_score[neighbor]:
                parent[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                
                # Add to open set
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    t1 = time.perf_counter()
    
    # Check if goal is reachable
    if g_score[goal] == inf:
        return {
            "algorithm": "A*",
            "path": [],
            "total": float("inf"),
            "runtime_sec": t1 - t0,
            "iterations": iterations,
            "edges_scanned": edges_scanned,
            "nodes_expanded": nodes_expanded,
            "heuristic_type": heuristic_type,
        }
    
    # Reconstruct path
    path = path_reconstruct(parent, start, goal)
    
    return {
        "algorithm": "A*",
        "path": path,
        "total": g_score[goal],
        "runtime_sec": t1 - t0,
        "iterations": iterations,
        "edges_scanned": edges_scanned,
        "nodes_expanded": nodes_expanded,
        "heuristic_type": heuristic_type,
    }

# ----------------------------- Utility Functions ----------------------------- #
def node_distance_km(a_id: int, b_id: int, nodes: Nodes) -> float:
    a = nodes[a_id]
    b = nodes[b_id]
    return geodesic_km(float(a["lat"]), float(a["lon"]), float(b["lat"]), float(b["lon"]))

__all__ = [
    "geodesic_km",
    "a_star_distance_heuristic",
    "a_star_time_heuristic",
    "a_star_shortest_path",
    "node_distance_km",
]