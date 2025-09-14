from __future__ import annotations

from typing import Any, Dict, List, Tuple, Union

from core.graph import load_graph, get_weight, get_city_id
from core.vizualize import generate_map, algorithm_color
from algorithms import bellman_ford as b_f
from algorithms import a_star as astar
from algorithms import dijkstras as dij

def clarify_id(maybe_id_or_name: Union[int, str], nodes: Dict[int, Dict[str, Any]]) -> int:
    if isinstance(maybe_id_or_name, int):
        return maybe_id_or_name #id
    return get_city_id(maybe_id_or_name, nodes) # get id from name

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

    # Load graph (once for fairness)
    nodes, adj = load_graph(undirected=undirected)

    # Clarify start and goal IDs
    start_id = clarify_id(start, nodes)
    goal_id = clarify_id(goal, nodes)

    # Weight function
    weight_type = get_weight(weight_key)


    # Run Algorithms
    a_star       = astar.a_star_shortest_path(adj, nodes, start_id, goal_id, weight_type, weight_key=weight_key)
    dijkstra     = dij.dijkstras_shortest_path(adj, nodes, start_id, goal_id, weight_type, weight_key=weight_key)
    bellman_ford = b_f.bellman_ford_shortest_path(adj, start_id, goal_id, weight_type)

    # # ------ TESTING -----------------
    # a_star["algorithm"]  = "A*"
    # dijkstra["algorithm"]  = "Dijkstra"
    # bellman_ford["algorithm"] = "Bellman-Ford"

    results = [a_star, dijkstra, bellman_ford]

    # Build maps for each "algorithm"
    maps = None
    if return_maps:
        maps = {
            r["algorithm"]: generate_map(nodes, r["path"], line_color=algorithm_color(r["algorithm"]), show_tooltips=show_tooltips)
            for r in results
        }

    return nodes, results, maps