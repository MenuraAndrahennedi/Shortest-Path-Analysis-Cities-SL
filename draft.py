"""
Shortest Path Finder for Sri Lankan Cities
Script: sri_lanka_shortest_paths.py

Features:
- Predefined list of Sri Lankan cities with lat/lon coordinates
- Builds a weighted, fully-connected graph using Haversine great-circle distances
- Implements Dijkstra, Bellman-Ford, Floyd-Warshall, and A* (Haversine heuristic)
- Interactive CLI to choose source/destination and algorithm
- Prints shortest path, total distance (km), time taken, and number of steps/relaxations
- Optional Folium visualization (if folium is installed)

Usage:
- Run in terminal or inside a Jupyter cell: python sri_lanka_shortest_paths.py
- Or import functions from this file into a notebook.

Note: For an actual road-network based solution you'd replace the fully-connected graph
with an adjacency list derived from road data (distances along roads).

"""

import math
import heapq
import time
from typing import Dict, Tuple, List, Optional

# Optional visualization
try:
    import folium
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

# ---------------------------
# City coordinates (lat, lon) - approximate
# Source: common geographic knowledge (rounded). These are suitable for Haversine distance.
# ---------------------------
CITIES: Dict[str, Tuple[float, float]] = {
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
# Utilities
# ---------------------------

def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Return distance in kilometers between two (lat, lon) coordinates using Haversine."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def build_full_graph(cities: Dict[str, Tuple[float, float]]) -> Dict[str, Dict[str, float]]:
    """Build a fully-connected weighted undirected graph where edge weight = Haversine distance."""
    graph: Dict[str, Dict[str, float]] = {}
    names = list(cities.keys())
    for i, a in enumerate(names):
        graph.setdefault(a, {})
        for j in range(i + 1, len(names)):
            b = names[j]
            dist = haversine(cities[a], cities[b])
            graph[a][b] = dist
            graph.setdefault(b, {})
            graph[b][a] = dist
    return graph


# ---------------------------
# Algorithms
# ---------------------------

def dijkstra(graph: Dict[str, Dict[str, float]], start: str, goal: str):
    """Dijkstra's algorithm (non-negative weights).
    Returns: (path, distance, steps, elapsed_time)
    steps: number of pops/relaxations performed (an indicator)
    """
    t0 = time.perf_counter()
    pq = []  # (distance, node)
    heapq.heappush(pq, (0.0, start))
    dist = {node: math.inf for node in graph}
    prev: Dict[str, Optional[str]] = {node: None for node in graph}
    dist[start] = 0.0
    steps = 0

    while pq:
        d, u = heapq.heappop(pq)
        steps += 1
        if d > dist[u]:
            continue
        if u == goal:
            break
        for v, w in graph[u].items():
            nd = d + w
            # relaxation
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    elapsed = time.perf_counter() - t0
    path = reconstruct_path(prev, start, goal)
    return path, dist[goal], steps, elapsed


def bellman_ford(graph: Dict[str, Dict[str, float]], start: str, goal: str):
    """Bellman-Ford algorithm for single-source shortest paths.
    Returns (path, distance, steps, elapsed_time, negative_cycle)
    """
    t0 = time.perf_counter()
    nodes = list(graph.keys())
    dist = {node: math.inf for node in nodes}
    prev: Dict[str, Optional[str]] = {node: None for node in nodes}
    dist[start] = 0.0

    edges = []
    for u in graph:
        for v, w in graph[u].items():
            edges.append((u, v, w))

    steps = 0
    for i in range(len(nodes) - 1):
        changed = False
        for u, v, w in edges:
            steps += 1
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                changed = True
        if not changed:
            break

    # check negative cycle
    negative_cycle = False
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            negative_cycle = True
            break

    elapsed = time.perf_counter() - t0
    path = reconstruct_path(prev, start, goal)
    return path, dist[goal], steps, elapsed, negative_cycle


def floyd_warshall(graph: Dict[str, Dict[str, float]]):
    """Floyd-Warshall: All-pairs shortest paths. Returns dist matrix and next matrix for path reconstruction."""
    t0 = time.perf_counter()
    nodes = list(graph.keys())
    n = len(nodes)
    index = {nodes[i]: i for i in range(n)}

    # initialize distance matrix
    dist = [[math.inf] * n for _ in range(n)]
    nxt: List[List[Optional[int]]] = [[None] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0.0
        nxt[i][i] = i

    for u in graph:
        for v, w in graph[u].items():
            i = index[u]
            j = index[v]
            dist[i][j] = w
            nxt[i][j] = j

    steps = 0
    for k in range(n):
        for i in range(n):
            for j in range(n):
                steps += 1
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]

    elapsed = time.perf_counter() - t0
    return nodes, dist, nxt, steps, elapsed


def a_star(graph: Dict[str, Dict[str, float]], coords: Dict[str, Tuple[float, float]], start: str, goal: str):
    """A* search using Haversine distance as heuristic. Returns (path, distance, steps, elapsed).
    """
    t0 = time.perf_counter()
    open_set = []  # (f_score, g_score, node)
    heapq.heappush(open_set, (0.0, 0.0, start))
    came_from: Dict[str, Optional[str]] = {node: None for node in graph}
    g_score = {node: math.inf for node in graph}
    g_score[start] = 0.0

    def heuristic(u: str, v: str) -> float:
        return haversine(coords[u], coords[v])

    steps = 0
    visited = set()
    while open_set:
        f, g, current = heapq.heappop(open_set)
        steps += 1
        if current == goal:
            break
        if current in visited:
            continue
        visited.add(current)
        for neighbor, w in graph[current].items():
            tentative_g = g_score[current] + w
            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, tentative_g, neighbor))
    elapsed = time.perf_counter() - t0
    path = reconstruct_path(came_from, start, goal)
    return path, g_score[goal], steps, elapsed


# ---------------------------
# Helpers
# ---------------------------

def reconstruct_path(prev: Dict[str, Optional[str]], start: str, goal: str) -> List[str]:
    """Reconstruct a path from prev pointers. If no path, returns empty list."""
    if prev.get(goal) is None and start != goal:
        # Might still be reachable if start == goal
        # But prev may be None if unreachable
        # We'll attempt to handle direct start==goal
        if start == goal:
            return [start]
        return []
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        if cur == start:
            break
        cur = prev.get(cur)
    path.reverse()
    if path and path[0] == start:
        return path
    return []


def print_path_and_stats(path: List[str], distance: float, algorithm: str, steps: int, elapsed: float):
    if not path:
        print(f"No path found using {algorithm}.")
        return
    print("\n=== Result ===")
    print(f"Algorithm: {algorithm}")
    print(f"Path: {' -> '.join(path)}")
    print(f"Total distance: {distance:.2f} km")
    print(f"Steps (algorithm-dependent): {steps}")
    print(f"Time taken: {elapsed*1000:.3f} ms")
    print("===============\n")


# ---------------------------
# Visualization (optional)
# ---------------------------

def visualize_route(path: List[str], coords: Dict[str, Tuple[float, float]], map_filename: str = "route_map.html") -> Optional[str]:
    if not FOLIUM_AVAILABLE:
        print("Folium is not installed. To enable visualization: pip install folium")
        return None
    if not path:
        print("No path to visualize.")
        return None

    # Center the map roughly at the first city
    start_coord = coords[path[0]]
    m = folium.Map(location=start_coord, zoom_start=7)

    # Add markers and polyline
    locations = []
    for city in path:
        lat, lon = coords[city]
        folium.Marker(location=(lat, lon), popup=city).add_to(m)
        locations.append((lat, lon))

    folium.PolyLine(locations, weight=4, opacity=0.8).add_to(m)
    m.save(map_filename)
    print(f"Map saved to {map_filename}")
    return map_filename


# ---------------------------
# Interactive CLI
# ---------------------------

def choose_city(prompt: str, cities: Dict[str, Tuple[float, float]]) -> str:
    names = list(cities.keys())
    for idx, name in enumerate(names, start=1):
        print(f"{idx}. {name}")
    while True:
        choice = input(prompt)
        if choice.isdigit():
            i = int(choice) - 1
            if 0 <= i < len(names):
                return names[i]
        # allow name input directly
        if choice in cities:
            return choice
        print("Invalid selection. Enter a number or a city name exactly as shown.")


def main():
    print("Shortest Path Finder — Sri Lankan Cities")
    print("Using Haversine distances on predefined city coordinates.")

    graph = build_full_graph(CITIES)

    print("\nAvailable cities:")
    src = choose_city("Select source (number or name): ", CITIES)
    dst = choose_city("Select destination (number or name): ", CITIES)

    print("\nChoose algorithm:")
    algo_list = ["Dijkstra", "Bellman-Ford", "Floyd-Warshall (all-pairs)", "A* (Haversine heuristic)"]
    for i, a in enumerate(algo_list, start=1):
        print(f"{i}. {a}")
    alg_choice = input("Enter algorithm number: ")

    if alg_choice == "1":
        path, dist, steps, elapsed = dijkstra(graph, src, dst)
        print_path_and_stats(path, dist, "Dijkstra", steps, elapsed)
    elif alg_choice == "2":
        path, dist, steps, elapsed, neg_cycle = bellman_ford(graph, src, dst)
        if neg_cycle:
            print("Graph contains a negative-weight cycle. Results may be invalid.")
        print_path_and_stats(path, dist, "Bellman-Ford", steps, elapsed)
    elif alg_choice == "3":
        nodes, dist_matrix, nxt, steps, elapsed = floyd_warshall(graph)
        # reconstruct path using nxt
        if src not in nodes or dst not in nodes:
            print("Cities not in nodes list — unexpected.")
            return
        i = nodes.index(src)
        j = nodes.index(dst)
        if math.isinf(dist_matrix[i][j]):
            path = []
            dist = math.inf
        else:
            # rebuild path
            path = []
            u = i
            while u != j:
                if u is None:
                    path = []
                    break
                path.append(nodes[u])
                u = nxt[u][j]
                if u is None:
                    path = []
                    break
            if u is not None:
                path.append(nodes[j])
            dist = dist_matrix[i][j]
        print_path_and_stats(path, dist, "Floyd-Warshall (all-pairs)", steps, elapsed)
    elif alg_choice == "4":
        path, dist, steps, elapsed = a_star(graph, CITIES, src, dst)
        print_path_and_stats(path, dist, "A* (Haversine)", steps, elapsed)
    else:
        print("Invalid algorithm choice. Running Dijkstra by default.")
        path, dist, steps, elapsed = dijkstra(graph, src, dst)
        print_path_and_stats(path, dist, "Dijkstra", steps, elapsed)

    # Offer visualization
    if FOLIUM_AVAILABLE:
        vis = input("Would you like to visualize the path on a map? (y/n): ")
        if vis.lower().startswith("y"):
            mapfile = visualize_route(path, CITIES)
            if mapfile:
                print(f"Open {mapfile} in a browser to view the route.")


if __name__ == "__main__":
    main()
