# Sri Lanka Shortest Path Analysis

A comprehensive web application for finding the shortest path between cities in Sri Lanka using Dijkstra's algorithm, with interactive map visualization.

## Features

- 🗺️ **Interactive Map Visualization** - See your route on an interactive Folium map
- 📊 **Comprehensive Analysis** - Get distance, travel time, algorithm performance metrics
- 🏙️ **2,155+ Cities** - Access to all major cities and towns in Sri Lanka
- ⚡ **Fast Algorithm** - Efficient Dijkstra's implementation with performance tracking
- 🎨 **Beautiful UI** - Modern, responsive Streamlit interface

## What You Get

For each path calculation, the application provides:

1. **Total Distance** - Complete route distance in kilometers
2. **Path/Nodes** - Step-by-step route with city names
3. **Travel Time** - Estimated travel time in minutes and hours
4. **Algorithm Runtime** - Time taken to calculate the path
5. **Algorithm Steps** - Number of computational steps performed

## Installation

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd Shortest-Path-Analysis-Cities-SL
   ```

2. **Create a venv:**

   ```bash
   python -m venv .venv
      # Windows PowerShell:
         .\.venv\Scripts\Activate.ps1
      # macOS/Linux:
         source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   streamlit run app.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## Usage

1. **Select Cities**: Use the sidebar to choose your starting city and destination
2. **Find Path**: Click "Find Shortest Path" to calculate the optimal route
3. **View Results**: See detailed analysis including distance, time, and performance metrics
4. **Explore Map**: Interact with the map to see your route visually

## Data Structure

The application uses two main data files:

- **`data/cities.csv`** - Contains 2,155 cities with coordinates and metadata
- **`data/edges.csv`** - Contains 29,600+ road connections with distances and travel times

## Algorithm Details

- **Algorithm**: Dijkstra's shortest path algorithm
- **Graph Representation**: Adjacency list with bidirectional edges
- **Optimization**: Priority queue (heapq) for efficient pathfinding
- **Performance**: Typically finds paths in milliseconds

## Example Results

```
From: Akkaraipattu → To: Ampara
Distance: 27.56 km
Travel Time: 36.20 minutes
Algorithm Runtime: 0.001 seconds
Steps: 16
```

## File Structure

```
project/
├── app.py                 # Main Streamlit application
├── algorithms/
│   └── dijkstras.py      # Dijkstra's algorithm implementation
├── core/
│   └── graph.py          # Graph data structure and loading
├── data/
│   ├── cities.csv        # City data
│   └── edges.csv         # Road connections
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Future Enhancements

- [ ] Add A\* algorithm for comparison
- [ ] Add Bellman-Ford algorithm for negative weights
- [ ] Implement algorithm performance comparison
- [ ] Add route optimization options
- [ ] Export results to various formats

## Technologies Used

- **Streamlit** - Web application framework
- **Folium** - Interactive map visualization
- **Pandas** - Data manipulation
- **Python** - Core programming language

## Contributing

Feel free to contribute by:

- Adding new algorithms
- Improving the UI/UX
- Optimizing performance
- Adding new features

## License

This project is open source and available under the MIT License.
