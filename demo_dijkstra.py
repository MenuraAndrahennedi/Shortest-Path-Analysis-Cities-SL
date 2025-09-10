#!/usr/bin/env python3
"""
Demo script for Dijkstra's shortest path algorithm
This script demonstrates how to use the Dijkstra implementation to find shortest paths between cities.
"""

from algorithms.dijkstras import find_shortest_path, print_path_result


def main():
    """Main demo function"""
    print("=" * 80)
    print("DIJKSTRA'S SHORTEST PATH ALGORITHM DEMO")
    print("=" * 80)
    print("This demo shows how to find the shortest path between two cities in Sri Lanka.")
    print("The algorithm provides:")
    print("1. Total distance in kilometers")
    print("2. Complete path with city names")
    print("3. Travel time in minutes and hours")
    print("4. Algorithm runtime in seconds")
    print("5. Number of steps the algorithm took")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        ("Akkaraipattu", "Ampara"),
        ("Ampara", "Bakmitiyawa"),
        ("Colombo", "Kandy"),
        ("Galle", "Jaffna"),
    ]
    
    for i, (start, end) in enumerate(test_cases, 1):
        print(f"\n{'='*20} TEST CASE {i} {'='*20}")
        print(f"Finding shortest path from '{start}' to '{end}'...")
        
        try:
            result = find_shortest_path(start, end)
            print_path_result(result)
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETED")
    print("=" * 80)
    print("You can now use the find_shortest_path() function in your own code!")
    print("Example usage:")
    print("  from algorithms.dijkstras import find_shortest_path")
    print("  result = find_shortest_path('Colombo', 'Kandy')")
    print("  print(f'Distance: {result.distance} km')")
    print("  print(f'Path: {\" → \".join(result.path)}')")


if __name__ == "__main__":
    main()
