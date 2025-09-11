from __future__ import annotations

from typing import Dict, List, Tuple, Callable, Any, Set
from math import inf
import time
from collections import deque

#from core.graph import get_weight

Edge = Tuple[int, float, float]     # (node_id, distance_km, travel_time_min)
Adjacency = Dict[int, List[Edge]]   # node_id -> list of edges

def path_reconstruct(parent: Dict[int, int], start: int, goal: int) -> List[int]:
    path: List[int] = []
    current = goal
    while current != start:
        path.append(current)
        current = parent[current]
    path.append(start)
    path.reverse()
    return path

def is_can_reach_goal(adj: Adjacency, sources: Set[int], goal: int) -> bool:
    if not sources:
        return False
    visited: Set[int] = set()
    queue: deque[int] = deque(sources)
    
    while queue:
        current_node = queue.popleft()
        if current_node in visited:
            continue
        visited.add(current_node)
        if current_node == goal:
            return True
        for neighbor, _, _ in adj.get(current_node, []):
            if neighbor not in visited:
                queue.append(neighbor)
    
    return False



def bellman_ford_shortest_path(
    adj: Adjacency,
    start: int,
    goal: int,
    weight_fn: Callable[[Edge], float]
) -> Dict[str, Any]:

    t0 = time.perf_counter()

    # Get a list of node ids
    nodes: List[int] = list(adj.keys())
    n = len(nodes)

    # Initialize distances to infinity and parent to zero
    weights: Dict[int, float] = {node_id: inf for node_id in nodes}
    parent: Dict[int, int] = {}
    weights[start] = 0.0

    iterations = 0
    relaxations_done = 0
    edges_scanned = 0

    # Relax edges up to n-1 times
    for single_iteration in range(n - 1):
        iterations += 1
        any_relaxed = False
        for u in nodes:
            current_weight = weights[u]
            if current_weight == inf:
                continue
            for edge in adj.get(u, []):
                edges_scanned += 1
                v, _, _ = edge
                weight = weight_fn(edge)
                new_dist = current_weight + weight
                if new_dist < weights[v]:
                    weights[v] = new_dist
                    parent[v] = u
                    any_relaxed = True
                    relaxations_done += 1
        if not any_relaxed:
            break

    # Negative-cycle detection 
    negative_cycle = False
    goal_affected = False
    changed_nodes: Set[int] = set()

    if iterations == n - 1:
        for u in nodes:
            current_weight = weights[u]
            if current_weight == inf:
                continue
            for e in adj.get(u, []):
                edges_scanned += 1  # counting scans during detection as well
                v, _, _ = e
                weight = weight_fn(e)
                if current_weight + weight < weights.get(v, inf):
                    negative_cycle = True
                    changed_nodes.add(v)
                    if negative_cycle:
                        goal_affected = is_can_reach_goal(adj, changed_nodes, goal)

    t1 = time.perf_counter()

    # If negative cycle detected
    if weights.get(goal, inf) == inf:
        return {
            "algorithm": "Bellman-Ford",
            "path": [],
            "total": float("inf"),
            "runtime_sec": t1 - t0,
            "iterations": iterations,
            "relaxations_done": relaxations_done,
            "edges_scanned": edges_scanned,
            "negative_cycle": negative_cycle,
            "goal_affected_by_neg_cycle": goal_affected,
        }

    path = path_reconstruct(parent, start, goal)

    return {
        "algorithm": "Bellman-Ford",
        "path": path,
        "total": weights[goal],
        "runtime_sec": t1 - t0,
        "iterations": iterations,
        "relaxations_done": relaxations_done,
        "edges_scanned": edges_scanned,
        "negative_cycle": negative_cycle,
        "goal_affected_by_neg_cycle": goal_affected,
    }