from __future__ import annotations

from typing import Dict, List, Tuple, Callable, Any, Set
import time
import heapq
from math import inf

Edge = Tuple[int, float, float]     # (node_id, distance_km, travel_time_min)
Adjacency = Dict[int, List[Edge]]   # node_id -> list of edges
Nodes = Dict[int, Dict[str, Any]]   # node_id -> node data


def _reconstruct(parent: Dict[int, int], start: int, goal: int) -> List[int]:
    if start == goal:
        return [start]
    path: List[int] = []
    cur = goal
    seen: Set[int] = set()
    while cur != start:
        if cur not in parent or cur in seen:
            return []  
        seen.add(cur)
        path.append(cur)
        cur = parent[cur]
    path.append(start)
    path.reverse()
    return path


def dijkstras_shortest_path(
    adj: Adjacency,
    nodes: Nodes,
    start: int,
    goal: int,
    weight_fn: Callable[[Edge], float],
    *,
    weight_key: str = "distance_km",  # keep for API compatibility
) -> Dict[str, Any]:
    t0 = time.perf_counter()

    node_set: Set[int] = set(nodes.keys())
    for u, edges in adj.items():
        for v, *_ in edges:
            node_set.add(v)
    node_set.add(start)
    node_set.add(goal)

    # g = best-known cost from start
    g: Dict[int, float] = {nid: inf for nid in node_set}
    parent: Dict[int, int] = {}
    g[start] = 0.0

    # Min-heap of (g, node). 
    pq: List[Tuple[float, int]] = [(0.0, start)]
    closed: Set[int] = set()

    explored = 0           
    relaxations_done = 0    
    edges_scanned = 0       

    while pq:
        g_u, u = heapq.heappop(pq)
        if u in closed:
            continue
        if g_u > g.get(u, inf):
            continue

        closed.add(u)
        explored += 1

        if u == goal:
            t1 = time.perf_counter()
            path = _reconstruct(parent, start, goal)
            return {
                "algorithm": "Dijkstra",
                "path": path,
                "total": g[goal],
                "runtime_sec": t1 - t0,
                "explored": explored,
                "relaxations_done": relaxations_done,
                "edges_scanned": edges_scanned,
                "negative_cycle": False,
                "goal_affected_by_neg_cycle": False,
            }

        # Relax outgoing edges
        for e in adj.get(u, []):
            edges_scanned += 1
            v, *_ = e
            if v in closed:
                continue
            w = weight_fn(e)
            tentative = g[u] + w
            if tentative < g.get(v, inf):
                g[v] = tentative
                parent[v] = u
                relaxations_done += 1
                heapq.heappush(pq, (tentative, v))

    t1 = time.perf_counter()
    
    return {
        "algorithm": "Dijkstra",
        "path": [],
        "total": float("inf"),
        "runtime_sec": t1 - t0,
        "explored": explored,
        "relaxations_done": relaxations_done,
        "edges_scanned": edges_scanned,
        "negative_cycle": False,
        "goal_affected_by_neg_cycle": False,
    }


__all__ = ["dijkstras_shortest_path"]
