import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import time
from typing import List, Tuple, Optional
import sys
import os

# Add the current directory to the path to import from algorithms and core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.dijkstras import find_shortest_path, PathResult
from core.graph import load_graph, city_list, city_names


def load_city_data():
    """Load and cache city data"""
    if 'city_data' not in st.session_state:
        with st.spinner("Loading city data..."):
            nodes, adj = load_graph()
            city_list_data = city_list(nodes)
            st.session_state.city_data = {
                'nodes': nodes,
                'adj': adj,
                'city_list': city_list_data
            }
    return st.session_state.city_data


def create_map_with_path(path_result: PathResult, nodes: dict, start_city: str, end_city: str):
    """Create a Folium map showing the shortest path"""
    if not path_result or not path_result.path:
        return None
    
    # Get coordinates for all cities in the path
    path_coords = []
    for city_name_with_id in path_result.path:
        # Extract city name (remove the ID part)
        city_name = city_name_with_id.split(' (')[0]
        
        # Find the city in nodes
        for node_id, data in nodes.items():
            if data['name'] == city_name:
                path_coords.append((data['lat'], data['lon']))
                break
    
    if not path_coords:
        return None
    
    # Create map centered on the path
    center_lat = sum(coord[0] for coord in path_coords) / len(path_coords)
    center_lon = sum(coord[1] for coord in path_coords) / len(path_coords)
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Add markers for start and end cities
    start_coord = path_coords[0]
    end_coord = path_coords[-1]
    
    folium.Marker(
        start_coord,
        popup=f"<b>Start:</b> {start_city}",
        tooltip=f"Start: {start_city}",
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)
    
    folium.Marker(
        end_coord,
        popup=f"<b>End:</b> {end_city}",
        tooltip=f"End: {end_city}",
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(m)
    
    # Add intermediate city markers
    for i, coord in enumerate(path_coords[1:-1], 1):
        city_name = path_result.path[i].split(' (')[0]
        folium.Marker(
            coord,
            popup=f"<b>Stop {i}:</b> {city_name}",
            tooltip=f"Stop {i}: {city_name}",
            icon=folium.Icon(color='blue', icon='map-marker', prefix='fa')
        ).add_to(m)
    
    # Add path line
    folium.PolyLine(
        path_coords,
        color='red',
        weight=3,
        opacity=0.8,
        popup=f"Shortest Path: {path_result.distance:.2f} km"
    ).add_to(m)
    
    return m


def display_results(path_result: PathResult, start_city: str, end_city: str):
    """Display the path analysis results in a formatted way"""
    if not path_result:
        st.error("No path found between the specified cities.")
        return
    
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Path Analysis Results")
        
        # Main metrics
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric(
                label="Total Distance",
                value=f"{path_result.distance:.2f} km",
                help="Total distance of the shortest path"
            )
        
        with metric_col2:
            st.metric(
                label="Travel Time",
                value=f"{path_result.travel_time:.1f} min",
                help="Estimated travel time"
            )
        
        with metric_col3:
            st.metric(
                label="Algorithm Steps",
                value=f"{path_result.steps:,}",
                help="Number of steps the algorithm took"
            )
        
        # Path details
        st.subheader("🗺️ Route Details")
        
        # Create a nice path display
        path_text = " → ".join([city.split(' (')[0] for city in path_result.path])
        st.info(f"**Route:** {path_text}")
        
        # Detailed path with distances
        st.subheader("📍 Detailed Path")
        for i, city in enumerate(path_result.path):
            city_name = city.split(' (')[0]
            if i == 0:
                st.write(f"🟢 **Start:** {city_name}")
            elif i == len(path_result.path) - 1:
                st.write(f"🔴 **End:** {city_name}")
            else:
                st.write(f"🔵 **Stop {i}:** {city_name}")
    
    with col2:
        st.subheader("⚡ Performance Metrics")
        
        st.metric(
            label="Algorithm Runtime",
            value=f"{path_result.algorithm_time:.4f} s",
            help="Time taken to run the algorithm"
        )
        
        st.metric(
            label="Travel Time (Hours)",
            value=f"{path_result.travel_time/60:.2f} h",
            help="Travel time in hours"
        )
        
        # Additional info
        st.subheader("ℹ️ Additional Info")
        st.info(f"""
        **Cities Visited:** {len(path_result.path)}
        
        **Average Speed:** {path_result.distance/(path_result.travel_time/60):.1f} km/h
        
        **Algorithm Efficiency:** {path_result.steps/len(path_result.path):.1f} steps per city
        """)


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Sri Lanka Shortest Path Analysis",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        justify-content: left;
        align-items: left;
        font-size: 3rem;
        color: #1f77b4;
        text-align: left;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
        justify-content: left;
        align-items: left;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div {
        color: black;    
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🗺️ Sri Lanka Shortest Path Analysis</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: left; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Find the shortest path between any two cities in Sri Lanka using Dijkstra's algorithm
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load city data
    city_data = load_city_data()
    nodes = city_data['nodes']
    city_list_data = city_data['city_list']
    
    # Sidebar for city selection
    st.header("🏙️ City Selection")
    
    # Create searchable select boxes
    city_names_list = [f"{name} ({id})" for id, name in city_list_data]

    col1, col2, col3 = st.columns(3)
    
    start_city = col1.selectbox(
        "Select Starting City:",
        options=city_names_list,
        index=0,
        help="Choose the city where your journey begins"
    )
    
    end_city = col2.selectbox(
        "Select Destination City:",
        options=city_names_list,
        index=1,
        help="Choose your destination city"
    )
    
    # Extract city names (remove IDs)
    start_city_name = start_city.split(' (')[0]
    end_city_name = end_city.split(' (')[0]
    
    # Find shortest path button
    if col3.button("🔍 Find Shortest Path", type="primary", use_container_width=True):
        if start_city_name == end_city_name:
            st.error("Please select different cities for start and destination.")
        else:
            with st.spinner("Calculating shortest path..."):
                try:
                    # Find shortest path
                    path_result = find_shortest_path(start_city_name, end_city_name)
                    
                    # Store result in session state
                    st.session_state.path_result = path_result
                    st.session_state.start_city = start_city_name
                    st.session_state.end_city = end_city_name
                    
                    st.success("Path calculation completed!")
                    
                except Exception as e:
                    st.error(f"Error calculating path: {str(e)}")
    
    # Display results if available
    if 'path_result' in st.session_state and st.session_state.path_result:
        path_result = st.session_state.path_result
        start_city = st.session_state.start_city
        end_city = st.session_state.end_city
        
        # Display results
        display_results(path_result, start_city, end_city)
        
        # Create and display map
        st.markdown('<h2 class="sub-header">🗺️ Interactive Map</h2>', unsafe_allow_html=True)
        
        map_obj = create_map_with_path(path_result, nodes, start_city, end_city)
        if map_obj:
            st_folium(map_obj, width=1200, height=500)
        else:
            st.warning("Could not create map visualization.")
        
        # Additional information
        st.markdown('<h2 class="sub-header">📈 Algorithm Information</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Algorithm Used:** Dijkstra's Algorithm
            
            **Graph Statistics:**
            - Total Cities: {len(nodes):,}
            - Total Edges: {sum(len(edges) for edges in city_data['adj'].values()):,}
            - Path Length: {len(path_result.path)} cities
            """)
        
        with col2:
            st.info(f"""
            **Performance:**
            - Runtime: {path_result.algorithm_time:.6f} seconds
            - Steps: {path_result.steps:,}
            - Efficiency: {path_result.steps/len(path_result.path):.1f} steps per city
            """)
    
    else:
        # Show instructions when no path is calculated
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h3>👆 Select cities and click "Find Shortest Path" to begin</h3>
            <p style="color: #666; font-size: 1.1rem;">
                Choose your starting city and destination from the sidebar, then click the button to find the optimal route.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem;">
        <p style="color: #666;">
            <strong>Sri Lanka Shortest Path Analysis</strong><br>
            Powered by Dijkstra's Algorithm | Built with Streamlit & Folium
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
