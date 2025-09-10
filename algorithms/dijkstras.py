import time
import heapq
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import sys
import os

# Add the parent directory to the path to import from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.graph import load_graph, get_city_id, city_names, Nodes, Adjacency, Edge


@dataclass
class PathResult:
    """Result of shortest path calculation"""
    distance: float
    path: List[str]
    travel_time: float
    algorithm_time: float
    steps: int


def dijkstra_shortest_path(nodes: Nodes, adj: Adjacency, start_city: str, end_city: str) -> Optional[PathResult]:
    """
    Find shortest path between two cities using Dijkstra's algorithm
    
    Args:
        nodes: Dictionary mapping city IDs to city data
        adj: Adjacency list representation of the graph
        start_city: Name of starting city
        end_city: Name of destination city
    
    Returns:
        PathResult object with distance, path, travel_time, algorithm_time, and steps
    """
    # Find city IDs
    try:
        start_id = get_city_id(start_city, nodes)
        end_id = get_city_id(end_city, nodes)
    except KeyError as e:
        raise ValueError(str(e))
    
    if start_id == end_id:
        return PathResult(
            distance=0.0,
            path=[city_names(start_id, nodes)],
            travel_time=0.0,
            algorithm_time=0.0,
            steps=0
        )
    
    # Start timing the algorithm
    start_time = time.time()
    
    # Dijkstra's algorithm
    distances = {city_id: float('inf') for city_id in nodes.keys()}
    distances[start_id] = 0.0
    
    # Priority queue: (distance, city_id)
    pq = [(0.0, start_id)]
    visited = set()
    previous = {}
    steps = 0
    
    while pq:
        current_distance, current_id = heapq.heappop(pq)
        steps += 1
        
        if current_id in visited:
            continue
        
        visited.add(current_id)
        
        # If we reached the destination, we can stop
        if current_id == end_id:
            break
        
        # Check all neighbors
        for edge in adj.get(current_id, []):
            neighbor_id, edge_distance, edge_travel_time = edge
            if neighbor_id in visited:
                continue
            
            new_distance = current_distance + edge_distance
            
            if new_distance < distances[neighbor_id]:
                distances[neighbor_id] = new_distance
                previous[neighbor_id] = current_id
                heapq.heappush(pq, (new_distance, neighbor_id))
    
    # End timing
    algorithm_time = time.time() - start_time
    
    # Reconstruct path
    if end_id not in previous and start_id != end_id:
        return None  # No path found
    
    path = []
    current = end_id
    total_travel_time = 0.0
    
    while current is not None:
        path.append(city_names(current, nodes))
        if current in previous:
            # Calculate travel time for this edge
            prev_id = previous[current]
            for edge in adj.get(prev_id, []):
                neighbor_id, edge_distance, edge_travel_time = edge
                if neighbor_id == current:
                    total_travel_time += edge_travel_time
                    break
        current = previous.get(current)
    
    path.reverse()
    
    return PathResult(
        distance=distances[end_id],
        path=path,
        travel_time=total_travel_time,
        algorithm_time=algorithm_time,
        steps=steps
    )


def find_shortest_path(start_city: str, end_city: str) -> Optional[PathResult]:
    """
    Main function to find shortest path between two cities
    
    Args:
        start_city: Name of starting city
        end_city: Name of destination city
    
    Returns:
        PathResult object with all required information
    """
    # Load graph data using the existing graph.py
    print("Loading graph data...")
    nodes, adj = load_graph()
    print(f"Loaded {len(nodes)} cities and {sum(len(edges) for edges in adj.values())} edges")
    
    # Find shortest path
    result = dijkstra_shortest_path(nodes, adj, start_city, end_city)
    
    return result


def print_path_result(result: PathResult):
    """Print the path result in a formatted way"""
    if result is None:
        print("No path found between the specified cities.")
        return
    
    print("=" * 60)
    print("SHORTEST PATH ANALYSIS RESULTS")
    print("=" * 60)
    print(f"1. Total Distance: {result.distance:.2f} km")
    print(f"2. Path: {' → '.join(result.path)}")
    print(f"3. Travel Time: {result.travel_time:.2f} minutes ({result.travel_time/60:.2f} hours)")
    print(f"4. Algorithm Runtime: {result.algorithm_time:.6f} seconds")
    print(f"5. Algorithm Steps: {result.steps}")
    print("=" * 60)


if __name__ == "__main__":
    # Example usage
    try:
        # Test with some cities
        result = find_shortest_path("Akkaraipattu", "Ampara")
        print_path_result(result)
        
        print("\n" + "="*60)
        print("Testing with another pair...")
        result2 = find_shortest_path("Ampara", "Bakmitiyawa")
        print_path_result(result2)
        
    except Exception as e:
        print(f"Error: {e}")
