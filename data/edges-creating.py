# data/edges-creating.py
import os
import math
import pandas as pd
import networkx as nx
import osmnx as ox
import pyproj  # for projecting city coordinates to the graph CRS

# ---------------- Config ----------------
PLACE_NAME = "Sri Lanka"        # OSM area
NETWORK_TYPE = "drive"          # drivable roads only
N_NEIGHBORS = 15                # candidate neighbors per city (by haversine)
MAX_KM = 150                    # keep edges whose road shortest path <= MAX_KM
MAKE_UNDIRECTED = True          # write each undirected pair once
SKIP_INTERMEDIATE_CITY_NODES = False  # set True later to enforce strict locality

HERE = os.path.dirname(__file__)
INPUT_CSV = os.path.join(HERE, "cities.csv")
OUTPUT_CSV = os.path.join(HERE, "edges.csv")
# ---------------------------------------

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    from math import radians, sin, cos, atan2, sqrt
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))

def main():
    # 1) Load cities
    if not os.path.exists(INPUT_CSV):
        raise SystemExit(f"cities file not found: {INPUT_CSV}")

    cities = pd.read_csv(INPUT_CSV).dropna(subset=["latitude","longitude"]).copy()
    for col in ("id", "latitude", "longitude"):
        if col not in cities.columns:
            raise SystemExit(f"Missing column '{col}' in {INPUT_CSV}")
    cities["id"] = cities["id"].astype(int)

    print(f"[edges-creating] Loaded {len(cities)} cities")
    print(f"[config] N_NEIGHBORS={N_NEIGHBORS}, MAX_KM={MAX_KM}, SKIP_INTERMEDIATE_CITY_NODES={SKIP_INTERMEDIATE_CITY_NODES}")

    # 2) Download Sri Lanka road network (drive) and prepare edge data
    print("[edges-creating] Downloading OSM road network for Sri Lanka (first run may take a while)…")
    G = ox.graph_from_place(PLACE_NAME, network_type=NETWORK_TYPE, simplify=True)
    G = ox.add_edge_speeds(G)          # adds 'speed_kph'
    G = ox.add_edge_travel_times(G)    # adds 'travel_time' (sec)
    if not all("length" in d for _, _, d in G.edges(data=True)):
        G = ox.add_edge_lengths(G)     # adds 'length' (meters) if missing

    # 3) Project the graph to a metric CRS (meters)
    print("[edges-creating] Projecting graph to a metric CRS…")
    G = ox.project_graph(G)  # node coordinates and geometries now in meters
    graph_crs = G.graph["crs"]

    # 4) Match city coordinates to nearest road nodes (project cities first!)
    print("[edges-creating] Matching cities to nearest road nodes…")
    # Cities are in WGS84 (lon/lat). Project them to graph CRS (meters).
    lons = cities["longitude"].to_numpy()
    lats = cities["latitude"].to_numpy()
    transformer = pyproj.Transformer.from_crs("EPSG:4326", graph_crs, always_xy=True)
    xs_proj, ys_proj = transformer.transform(lons, lats)

    # Nearest nodes expects X/Y in the graph's CRS
    nearest_nodes = ox.distance.nearest_nodes(G, xs_proj, ys_proj)

    city_id_to_node = dict(zip(cities["id"].astype(int).to_numpy(), nearest_nodes))
    road_nodes_of_cities = set(city_id_to_node.values())

    # 5) Candidate neighbors via (spherical) haversine distance
    print("[edges-creating] Selecting candidate neighbors…")
    pts = cities[["id", "latitude", "longitude"]].to_numpy()
    cand = {}  # id -> list of neighbor ids
    for i in range(len(pts)):
        cid_i, lat_i, lon_i = pts[i]
        cid_i = int(cid_i)
        pairs = []
        for j in range(len(pts)):
            if i == j:
                continue
            cid_j, lat_j, lon_j = pts[j]
            d = haversine_km(float(lat_i), float(lon_i), float(lat_j), float(lon_j))
            pairs.append((int(cid_j), d))
        pairs.sort(key=lambda x: x[1])
        cand[cid_i] = [c for c, _ in pairs[:N_NEIGHBORS]]

    # 6) Compute shortest road paths and keep edges
    print("[edges-creating] Computing shortest road paths for candidate pairs…")
    kept = set()
    records = []

    # stats
    total_pairs = 0
    no_path = 0
    too_far = 0
    skipped_by_intermediate = 0
    zero_len_paths = 0

    for u in cities["id"].tolist():
        u_node = city_id_to_node[u]
        for v in cand[u]:
            total_pairs += 1
            if MAKE_UNDIRECTED and v < u:
                continue
            v_node = city_id_to_node[v]
            if u_node == v_node:
                continue
            try:
                path = nx.shortest_path(G, u_node, v_node, weight="length")
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                no_path += 1
                continue

            # Sum length and collect highway types + travel time (with fallbacks)
            total_len_m = 0.0
            total_sec = 0.0
            highway_types = set()

            for a, b in zip(path[:-1], path[1:]):
                edata_all = G.get_edge_data(a, b)
                if not edata_all:
                    continue
                # pick the edge with min travel_time; if none, pick arbitrary first
                try:
                    edata = min(edata_all.values(), key=lambda d: d.get("travel_time", float("inf")))
                except ValueError:
                    edata = list(edata_all.values())[0]

                length = edata.get("length", 0.0)
                if not length:
                    geom = edata.get("geometry")
                    if geom is not None:
                        # in projected CRS, geometry.length is meters
                        length = geom.length
                total_len_m += float(length or 0.0)

                total_sec += float(edata.get("travel_time", 0.0))
                hw = edata.get("highway")
                if isinstance(hw, list):
                    highway_types.update(map(str, hw))
                elif hw is not None:
                    highway_types.add(str(hw))

            dist_km = total_len_m / 1000.0
            if dist_km == 0.0:
                zero_len_paths += 1
                continue
            if dist_km > MAX_KM:
                too_far += 1
                continue

            # Optional: Skip if the path goes through another city's road node (keeps locality)
            if SKIP_INTERMEDIATE_CITY_NODES:
                interior = set(path[1:-1])
                if interior & (road_nodes_of_cities - {u_node, v_node}):
                    skipped_by_intermediate += 1
                    continue

            key = (min(u, v), max(u, v)) if MAKE_UNDIRECTED else (u, v)
            if key in kept:
                continue
            kept.add(key)

            records.append({
                "source_id": key[0],
                "target_id": key[1],
                "distance_km": round(dist_km, 3),
                "travel_time_min": round(total_sec / 60.0, 1),
                "highways": ";".join(sorted(highway_types)) if highway_types else ""
            })

    # 7) Save CSV (write headers even if empty)
    columns = ["source_id", "target_id", "distance_km", "travel_time_min", "highways"]
    edges = pd.DataFrame.from_records(records, columns=columns)
    if not edges.empty:
        edges = edges.sort_values(["source_id", "target_id"]).reset_index(drop=True)
    edges.to_csv(OUTPUT_CSV, index=False)

    print(f"[edges-creating] Candidate pairs: {total_pairs}")
    print(f"[edges-creating]   No path: {no_path}")
    print(f"[edges-creating]   Zero-length paths (bad snap): {zero_len_paths}")
    print(f"[edges-creating]   > MAX_KM: {too_far}")
    if SKIP_INTERMEDIATE_CITY_NODES:
        print(f"[edges-creating]   Skipped (path passed another city): {skipped_by_intermediate}")
    print(f"[edges-creating] Wrote {len(edges)} edges to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
