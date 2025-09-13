from __future__ import annotations

import sys
import os
from typing import Any, Dict, List, Tuple, Union

# Add project root to sys.path so 'core' and 'algorithms' can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.graph import load_graph, get_weight, get_city_id
from core.vizualize import generate_map, algorithm_color
from algorithms import bellman_ford as b_f
from algorithms import dijkstras as dijk  # make sure you have dijkstra.py
from algorithms import a_star as a_star_module  # your A* implementation

# ----------------------------- Helper ----------------------------- #
def clarify_id(maybe_id_or_name: Union[int, str], nodes: Dict[int, Dict[str, Any]]) -> int:
    if isinstance(maybe_id_or_name, int):
        return maybe_id_or_name
    return get_city_id(maybe_id_or_name, nodes)

# ----------------------------- Run Algorithms ----------------------------- #
def run_all(
    start: Union[int, str],
    goal: Union[int, str],
    *,
    weight_key: str = "distance_km",   # "distance_km" | "travel_time_min"
    undirected: bool = True,
    return_maps: bool = True,
    show_tooltips=False
) -> Tuple[Dict[int, Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any] | None]:

    # Load graph
    nodes, adj = load_graph()

    # Clarify start and goal IDs
    start_id = clarify_id(start, nodes)
    goal_id = clarify_id(goal, nodes)

    # Weight function
    weight_type = get_weight(weight_key)

    # Run Algorithms
    a_star_result = a_star_module.a_star_shortest_path(nodes, adj, start_id, goal_id, weight_fn=weight_type, heuristic_type="distance")
    ##a_star_result = a_star_module.a_star_shortest_path( adj, start_id, goal, weight_fn=weight_type, heuristic_type="distance" )
    dijkstra_result = dijk.dijkstra_shortest_path_compatible(adj, start_id, goal_id, weight_type)
    bellman_result = b_f.bellman_ford_shortest_path(adj, start_id, goal_id, weight_type)

    # Add algorithm names
    a_star_result["algorithm"] = "A*"
    dijkstra_result["algorithm"] = "Dijkstra"
    bellman_result["algorithm"] = "Bellman-Ford"

    results = [a_star_result, dijkstra_result, bellman_result]

    # Build maps for each algorithm
    maps = None
    if return_maps:
        maps = {
            r["algorithm"]: generate_map(
                nodes,
                r["path"],
                line_color=algorithm_color(r["algorithm"]),
                show_tooltips=show_tooltips
            )
            for r in results
        }

    return nodes, results, maps
