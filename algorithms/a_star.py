from __future__ import annotations
from typing import Dict, List, Tuple, Callable, Any
from math import inf
import time
import heapq
from core.heuristics import (
    a_star_distance_heuristic,
    a_star_time_heuristic,
)

Edge = Tuple[int, float, float]     # (node_id, distance_km, travel_time_min)
Adjacency = Dict[int, List[Edge]]   # node_id -> list of edges
Nodes = Dict[int, Dict[str, Any]]   # node_id -> node data


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
    adj: Adjacency,
    nodes: Nodes,
    start: int,
    goal: int,
    weight_fn: Callable[[Edge], float],
    weight_key: str = "distance_km",
    max_kmh: float = 70.0,
) -> Dict[str, Any]:
    
    t0 = time.perf_counter()
    
    # Choose heuristic function
    if weight_key == "distance_km":
        heuristic = a_star_distance_heuristic(goal, nodes)
    elif weight_key == "time_min":
        heuristic = a_star_time_heuristic(goal, nodes, max_kmh=max_kmh)
    else:
        raise ValueError("weight_key must be 'distance_km' or 'time_min'")
    
    # Initialize data structures
    g_score: Dict[int, float] = {node_id: inf for node_id in nodes.keys()}
    g_score[start] = 0.0
    
    f_score: Dict[int, float] = {node_id: inf for node_id in nodes.keys()}
    f_score[start] = heuristic(start)
    
    # Priority queue: (f_score, node_id)
    open_set = [(f_score[start], start)]
    closed_set: set[int] = set()
    parent: Dict[int, int] = {}
    
    explored = 0
    edges_scanned = 0
    nodes_expanded = 0
    
    while open_set:
        explored += 1
        
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
            
            tentative_g = g_score[current] + weight_fn(edge)

            if tentative_g < g_score[neighbor]:
                parent[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)

                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    t1 = time.perf_counter()
    
    if g_score[goal] == inf:
        return {
            "algorithm": "A*",
            "path": [],
            "total": float("inf"),
            "runtime_sec": t1 - t0,
            "explored": explored,
            "edges_scanned": edges_scanned,
            "negative_cycle": False,  # N/A for A*
            "goal_affected_by_neg_cycle": False, # N/A for A*
        }
    
    path = path_reconstruct(parent, start, goal)
    
    return {
        "algorithm": "A*",
        "path": path,
        "total": g_score[goal],
        "runtime_sec": t1 - t0,
        "explored": explored,
        "relaxations_done": "Undefined",
        "edges_scanned": edges_scanned,
        "negative_cycle": False,  # N/A for A*
        "goal_affected_by_neg_cycle": False, # N/A for A*            
    }

__all__ = [
    "a_star_shortest_path",
    "node_distance_km",
]