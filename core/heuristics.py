from __future__ import annotations

from functools import lru_cache
from typing import Callable, Dict, Any
from geographiclib.geodesic import Geodesic

# ----------------------------- Get distance using logitude and latitude ----------------------------- #
def geodesic_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    g = Geodesic.WGS84.Inverse(float(lat1), float(lon1), float(lat2), float(lon2))
    return g["s12"] / 1000.0


# ----------------------------- Heuristics ----------------------------- #
def a_star_distance_heuristic(goal_id: int, nodes: Dict[int, Dict[str, Any]]) -> Callable[[int], float]:
    goal_lat = float(nodes[goal_id]["lat"])
    goal_lon = float(nodes[goal_id]["lon"])
    @lru_cache(maxsize=None)
    def h_distance(node_id: int) -> float:
        node = nodes[node_id]
        return geodesic_km(float(node["lat"]), float(node["lon"]), goal_lat, goal_lon)
    return h_distance

def astar_time_heuristic(
    goal_id: int,
    nodes: Dict[int, Dict[str, Any]],
    max_kmh: float = 70.0,
) -> Callable[[int], float]:
    if max_kmh <= 0:
        raise ValueError("vmax_kmh must be > 0")
    goal_lat = float(nodes[goal_id]["lat"])
    goal_lon = float(nodes[goal_id]["lon"])
    km_per_min = max_kmh / 60.0

    @lru_cache(maxsize=None)
    def h_time(node_id: int) -> float:
        node = nodes[node_id]
        distance_km = geodesic_km(float(node["lat"]), float(node["lon"]), goal_lat, goal_lon)
        return distance_km / km_per_min

    return h_time

# ----------------------------- Straight Distance ----------------------------- #
def node_distance_km(a_id: int, b_id: int, nodes: Dict[int, Dict[str, Any]]) -> float:
    a = nodes[a_id]
    b = nodes[b_id]
    return geodesic_km(float(a["lat"]), float(a["lon"]), float(b["lat"]), float(b["lon"]))



__all__ = [
    "geodesic_km",
    "astar_heuristic",
    "astar_time_heuristic",
    "node_distance_km",
]