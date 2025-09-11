from __future__ import annotations

from typing import Sequence, Dict, Any, Tuple, List, Optional, Mapping
import folium

COORDINATE = Tuple[float, float]
NODES = Dict[int, Dict[str, Any]]

DEFAULT_CENTER: COORDINATE = (7.8731, 80.7718) # Sri Lanka map center

ALGORITHM_COLORS = {
    "A*": "#31AB37",          # green
    "Dijkstra": "#2962FF",    # blue
    "Bellman-Ford": "#7E2FB0" # purple
}

def algorithm_color(name: str, fallback: str = "#000000") -> str:
    return ALGORITHM_COLORS.get(name, fallback)

def path_coordinates(nodes: NODES, path_ids: Sequence[int]) -> List[COORDINATE]:
    return [(float(nodes[node_id]["lat"]), float(nodes[node_id]["lon"])) for node_id in path_ids]

def path_area(coordinates: Sequence[COORDINATE]) -> Optional[Tuple[COORDINATE, COORDINATE]]:
    if not coordinates:
        return None
    lats = [lat for lat, _ in coordinates]
    lons = [lon for _, lon in coordinates]
    south_west = (min(lats), min(lons))
    north_east = (max(lats), max(lons))
    return south_west, north_east

# ----------------------------- Generate Map ----------------------------- #
def generate_map(
    nodes: NODES,
    path_ids: Sequence[int] | None,
    *,
    tiles: str = "OpenStreetMap",
    line_color: str = "#133EFF",
    line_weight: int = 5,
    line_opacity: float = 0.9,
    show_labels: bool = True,
    start_label: str = "Start",
    end_label: str = "End",
    show_tooltips: bool = False,
    fit_to_path: bool = True,
    zoom_start: int = 7,
    control_scale: bool = True,
) -> folium.Map:
    
    # Default center
    center = DEFAULT_CENTER
    coords: List[COORDINATE] = []
    if path_ids:
        coords = path_coordinates(nodes, path_ids)
        if coords:
            center_lat = sum(lat for lat, _ in coords) / len(coords)
            center_lon = sum(lon for _, lon in coords) / len(coords)
            center = (center_lat, center_lon)

    m = folium.Map(location=center, zoom_start=zoom_start, tiles=tiles, control_scale=control_scale)
    # if control_scale:
    #     folium.plugins.Scale().add_to(m)

    # if path_ids:
    #     folium.PolyLine(
    #         locations=coords,
    #         color=line_color,
    #         weight=line_weight,
    #         opacity=line_opacity
    #     ).add_to(m)

    # Start and End Labels
    if coords:
        if show_labels and len(coords) >= 1:
            start = coords[0]
            start_tt = f"{start_label}: {nodes[path_ids[0]]['name']}" if show_tooltips else start_label
            folium.Marker(
                start,
                tooltip=start_tt,
                icon=folium.Icon(color="green"),
            ).add_to(m)

        if show_labels and len(coords) >= 2:
            end = coords[-1]
            end_tt = f"{end_label}: {nodes[path_ids[-1]]['name']}" if show_tooltips else end_label
            folium.Marker(
                end,
                tooltip=end_tt,
                icon=folium.Icon(color="red"),
            ).add_to(m)

    # Path Line
    if len(coords) >= 2:
            folium.PolyLine(coords, weight=line_weight, color=line_color, opacity=line_opacity).add_to(m)

    # Path Tooltips
    if show_tooltips:
        for i, coord in enumerate(coords):
            tt = f"Node {i}: {nodes[path_ids[i]]['name']}"
            folium.Marker(coord, tooltip=tt).add_to(m)

    # Fit Map to path area
    if fit_to_path:
            area = path_area(coords)
            if area:
                south_west, north_east = area
                m.fit_bounds([south_west, north_east], padding=(12, 12))
    
    return m

def save_map(m: folium.Map, filepath: str) -> str:
    m.save(filepath)
    return filepath


def map_to_html(m: folium.Map) -> str:
    return m.get_root().render()


__all__ = ["ALGORITHM_COLORS", "algorithm_color", "generate_map", "save_map", "map_to_html"]